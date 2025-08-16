"""
from typing import List, Optional
Causal Model Builder for XAI Engine

Constructs causal models for different types of decisions.
"""

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel

from .knowledge_base import CausalKnowledgeBase
from .models import CausalEdge, Decision


class CausalModelBuilder:
    """
    Builds causal models for different decision types.

    This class takes a decision and constructs an appropriate
    causal model that can be used for inference and explanation.
    """

    def __init__(self, knowledge_base: CausalKnowledgeBase | None = None):
        self.knowledge_base = knowledge_base or CausalKnowledgeBase()
        self.model_cache = {}

    def build_model(self, decision: Decision) -> CausalModel:
        """
        Build a causal model for a specific decision.

        Args:
            decision: The decision to build a model for

        Returns:
            A DoWhy CausalModel ready for inference
        """
        # Classify the decision type
        decision_type = self._classify_decision(decision)

        # Get the appropriate model template
        model_template = self.knowledge_base.get_model(decision_type)
        if not model_template:
            raise ValueError(
                f"No causal model template for decision type: {decision_type}"
            )

        # Build the causal graph
        causal_graph = self._build_causal_graph(model_template, decision.context)

        # Prepare data for the model
        data = self._prepare_data(decision, model_template)

        # Identify treatment and outcome
        treatment = self._identify_treatment(decision, model_template)
        outcome = self._identify_outcome(decision, model_template)

        # Get common causes (confounders)
        common_causes = self._identify_common_causes(causal_graph, treatment, outcome)

        # Create the DoWhy causal model
        model = CausalModel(
            data=data,
            treatment=treatment,
            outcome=outcome,
            common_causes=common_causes,
            graph=self._graph_to_dot(causal_graph),
            proceed_when_unidentifiable=True,
        )

        # Cache the model
        cache_key = f"{decision_type}_{hash(str(decision.context))}"
        self.model_cache[cache_key] = model

        return model

    def _classify_decision(self, decision: Decision) -> str:
        """Classify the decision into a known type"""
        action_mapping = {
            "install": "install_package",
            "add": "install_package",
            "get": "install_package",
            "update": "update_system",
            "upgrade": "update_system",
            "remove": "remove_package",
            "uninstall": "remove_package",
            "delete": "remove_package",
            "rollback": "rollback_system",
            "revert": "rollback_system",
            "search": "search_package",
            "find": "search_package",
            "status": "check_status",
            "check": "check_status",
            "info": "check_status",
        }

        # Try direct mapping
        decision_type = action_mapping.get(decision.action.lower())
        if decision_type:
            return decision_type

        # Try to infer from context
        if "package" in decision.context:
            if decision.action in ["add", "get"]:
                return "install_package"
            if decision.action in ["remove", "delete"]:
                return "remove_package"

        # Default to install if unclear
        return "install_package"

    def _build_causal_graph(self, template: dict, context: dict) -> nx.DiGraph:
        """
        Construct causal graph based on template and context.

        Args:
            template: Model template from knowledge base
            context: Decision context

        Returns:
            NetworkX directed graph representing causal relationships
        """
        graph = nx.DiGraph()

        # Add nodes from template
        for node in template["nodes"]:
            graph.add_node(
                node.id,
                name=node.name,
                node_type=node.node_type,
                description=node.description,
                value_type=node.value_type,
                possible_values=node.possible_values,
            )

        # Add edges with causal relationships
        for edge in template["edges"]:
            graph.add_edge(
                edge.from_node,
                edge.to_node,
                mechanism=edge.mechanism,
                strength=edge.strength,
                description=edge.description,
            )

        # Adapt based on context
        self._adapt_to_context(graph, context)

        return graph

    def _adapt_to_context(self, graph: nx.DiGraph, context: dict):
        """
        Adapt the causal graph based on specific context.

        This allows the model to be more specific to the actual decision.
        """
        # Example: If user has limited disk space, increase edge strength
        if context.get("low_disk_space", False):
            if graph.has_edge("disk_space", "installation_success"):
                graph["disk_space"]["installation_success"]["strength"] = 0.9

        # Example: If user is beginner, installation method matters more
        if context.get("user_level") == "beginner":
            if graph.has_edge("installation_method", "installation_success"):
                graph["installation_method"]["installation_success"]["strength"] = 0.7

        # Add context-specific nodes if needed
        if "network_quality" in context and context["network_quality"] < 0.5:
            graph.add_node(
                "network_quality",
                name="Network Quality",
                node_type="observed",
                description="Quality of network connection",
                value_type="numeric",
            )
            if "installation_success" in graph:
                graph.add_edge(
                    "network_quality",
                    "installation_success",
                    mechanism="direct",
                    strength=0.6,
                    description="Poor network affects downloads",
                )

    def _prepare_data(self, decision: Decision, template: dict) -> pd.DataFrame:
        """
        Prepare data frame for causal model.

        This creates synthetic data that represents the decision context
        and possible counterfactuals.
        """
        n_samples = 1000  # Number of synthetic samples
        data = {}

        # Generate data for each node
        for node in template["nodes"]:
            node_id = node.id
            node_type = node.value_type

            if node_type == "boolean":
                # Generate boolean data based on context
                if node_id in decision.context:
                    # Use actual value with some noise
                    actual = decision.context[node_id]
                    data[node_id] = np.random.choice(
                        [actual, not actual],
                        size=n_samples,
                        p=[0.8, 0.2] if actual else [0.2, 0.8],
                    )
                else:
                    # Random boolean
                    data[node_id] = np.random.choice([True, False], size=n_samples)

            elif node_type == "numeric":
                # Generate numeric data
                if node_id in decision.context:
                    # Use actual value as mean
                    mean = float(decision.context[node_id])
                    data[node_id] = np.random.normal(mean, mean * 0.2, n_samples)
                else:
                    # Random numeric
                    data[node_id] = np.random.normal(0.5, 0.2, n_samples)

            elif node_type == "categorical":
                # Generate categorical data
                possible_values = node.possible_values or ["A", "B", "C"]
                if node_id in decision.context:
                    # Use actual value with higher probability
                    actual = decision.context[node_id]
                    if actual in possible_values:
                        probs = [
                            0.7 if v == actual else 0.3 / (len(possible_values) - 1)
                            for v in possible_values
                        ]
                    else:
                        probs = [1 / len(possible_values)] * len(possible_values)
                else:
                    # Uniform distribution
                    probs = [1 / len(possible_values)] * len(possible_values)

                data[node_id] = np.random.choice(
                    possible_values, size=n_samples, p=probs
                )

        # Create relationships based on edges
        df = pd.DataFrame(data)
        self._apply_causal_relationships(df, template["edges"])

        return df

    def _apply_causal_relationships(self, df: pd.DataFrame, edges: list[CausalEdge]):
        """Apply causal relationships to make data realistic"""
        for edge in edges:
            if edge.from_node in df.columns and edge.to_node in df.columns:
                # Apply causal effect based on edge strength
                strength = edge.strength

                # Simple linear relationship for now
                from_values = df[edge.from_node]
                to_values = df[edge.to_node]

                # Convert to numeric if needed
                if from_values.dtype == "bool":
                    from_values = from_values.astype(int)
                if to_values.dtype == "bool":
                    to_values = to_values.astype(int)

                # Apply causal effect
                noise = np.random.normal(0, 0.1, len(df))
                effect = strength * from_values + noise

                # Update target variable
                if df[edge.to_node].dtype == "bool":
                    df[edge.to_node] = (to_values + effect) > 0.5
                else:
                    df[edge.to_node] = to_values + effect

    def _identify_treatment(self, decision: Decision, template: dict) -> str:
        """Identify the treatment variable"""
        treatments = [
            node.id for node in template["nodes"] if node.node_type == "treatment"
        ]

        if not treatments:
            raise ValueError("No treatment variable found in model")

        # For now, return the first treatment
        # In future, could be more sophisticated
        return treatments[0]

    def _identify_outcome(self, decision: Decision, template: dict) -> str:
        """Identify the primary outcome variable"""
        outcomes = [
            node.id for node in template["nodes"] if node.node_type == "outcome"
        ]

        if not outcomes:
            raise ValueError("No outcome variable found in model")

        # Choose based on decision type
        if "success" in decision.context.get("desired_outcome", ""):
            for outcome in outcomes:
                if "success" in outcome:
                    return outcome

        # Default to first outcome
        return outcomes[0]

    def _identify_common_causes(
        self, graph: nx.DiGraph, treatment: str, outcome: str
    ) -> list[str]:
        """Identify common causes (confounders) of treatment and outcome"""
        common_causes = []

        # Find nodes that affect both treatment and outcome
        for node in graph.nodes():
            if node == treatment or node == outcome:
                continue

            # Check if node affects treatment
            affects_treatment = graph.has_edge(node, treatment) or nx.has_path(
                graph, node, treatment
            )

            # Check if node affects outcome
            affects_outcome = graph.has_edge(node, outcome) or nx.has_path(
                graph, node, outcome
            )

            # If affects both, it's a confounder
            if affects_treatment and affects_outcome:
                common_causes.append(node)

        return common_causes

    def _graph_to_dot(self, graph: nx.DiGraph) -> str:
        """Convert NetworkX graph to DOT format for DoWhy"""
        dot_lines = ["digraph {"]

        # Add nodes
        for node in graph.nodes():
            dot_lines.append(f'  "{node}";')

        # Add edges
        for edge in graph.edges():
            dot_lines.append(f'  "{edge[0]}" -> "{edge[1]}";')

        dot_lines.append("}")

        return "\n".join(dot_lines)

    def visualize_model(self, model: CausalModel) -> str:
        """
        Generate a text representation of the causal model.

        Useful for debugging and understanding the model structure.
        """
        lines = ["Causal Model Structure:"]
        lines.append(f"Treatment: {model.treatment}")
        lines.append(f"Outcome: {model.outcome}")
        lines.append(f"Common Causes: {', '.join(model.common_causes)}")
        lines.append("\nCausal Graph:")
        lines.append(model.graph)

        return "\n".join(lines)
