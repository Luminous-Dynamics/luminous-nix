"""
from typing import Tuple, Dict, List, Optional
Causal Inference Engine for XAI

Performs causal analysis using DoWhy to understand the relationships
between factors and outcomes in NixOS operations.
"""

from typing import Any

from dowhy import CausalModel

from .builder import CausalModelBuilder
from .knowledge_base import CausalKnowledgeBase
from .models import CausalFactor, CausalRelationship, Decision, InferenceMethod


class CausalInferenceEngine:
    """
    Performs causal inference on decisions to understand why certain
    recommendations are made and what factors influence outcomes.
    """

    def __init__(
        self,
        knowledge_base: CausalKnowledgeBase | None = None,
        model_builder: CausalModelBuilder | None = None,
    ):
        self.knowledge_base = knowledge_base or CausalKnowledgeBase()
        self.model_builder = model_builder or CausalModelBuilder(self.knowledge_base)
        self.inference_cache = {}

    def analyze_decision(
        self, decision: Decision
    ) -> tuple[list[CausalFactor], list[InferenceMethod]]:
        """
        Analyze a decision to identify causal factors and their influence.

        Args:
            decision: The decision to analyze

        Returns:
            Tuple of (causal factors, inference methods used)
        """
        # Build causal model
        model = self.model_builder.build_model(decision)

        # Identify causal effect
        identified_estimand = self._identify_causal_effect(model)

        # Estimate causal effects using multiple methods
        estimates = self._estimate_effects(model, identified_estimand)

        # Extract causal factors from analysis
        causal_factors = self._extract_causal_factors(model, estimates, decision)

        # Get inference methods used
        inference_methods = self._get_inference_methods(estimates)

        return causal_factors, inference_methods

    def _identify_causal_effect(self, model: CausalModel) -> Any:
        """Identify the causal effect using DoWhy"""
        try:
            # Identify causal effect
            identified_estimand = model.identify_effect(
                proceed_when_unidentifiable=True
            )
            return identified_estimand
        except Exception as e:
            # Log error and return None
            print(f"Failed to identify causal effect: {e}")
            return None

    def _estimate_effects(
        self, model: CausalModel, identified_estimand: Any
    ) -> list[dict]:
        """Estimate causal effects using multiple methods"""
        estimates = []

        # Methods to try
        estimation_methods = [
            {
                "method_name": "backdoor.propensity_score_matching",
                "method_params": {"num_matches_per_unit": 5},
            },
            {"method_name": "backdoor.linear_regression", "method_params": {}},
            {"method_name": "backdoor.propensity_score_weighting", "method_params": {}},
        ]

        for method in estimation_methods:
            try:
                estimate = model.estimate_effect(
                    identified_estimand,
                    method_name=method["method_name"],
                    method_params=method["method_params"],
                )

                estimates.append(
                    {
                        "method": method["method_name"],
                        "estimate": estimate,
                        "value": estimate.value if hasattr(estimate, "value") else None,
                        "confidence_intervals": self._extract_confidence_intervals(
                            estimate
                        ),
                    }
                )
            except Exception:
                # Some methods may fail depending on data
                continue

        return estimates

    def _extract_confidence_intervals(
        self, estimate: Any
    ) -> tuple[float, float] | None:
        """Extract confidence intervals from estimate if available"""
        try:
            if hasattr(estimate, "get_confidence_intervals"):
                ci = estimate.get_confidence_intervals()
                if ci is not None and len(ci) >= 2:
                    return (float(ci[0]), float(ci[1]))
        except Exception:
            # TODO: Add proper error handling
            pass  # Silent for now, should log error
        return None

    def _extract_causal_factors(
        self, model: CausalModel, estimates: list[dict], decision: Decision
    ) -> list[CausalFactor]:
        """Extract and rank causal factors from analysis"""
        factors = []

        # Get model data
        data = model.data

        # Analyze each variable's influence
        for col in data.columns:
            if col == model.outcome[0] or col == model.treatment[0]:
                continue

            # Calculate correlation with outcome
            if data[col].dtype in ["float64", "int64", "bool"]:
                correlation = data[col].corr(data[model.outcome[0]])

                # Determine influence based on correlation and domain knowledge
                influence = self._calculate_influence(col, correlation, model, decision)

                # Get actual value from decision context
                value = decision.context.get(col, data[col].mode()[0])

                # Calculate confidence based on estimates
                confidence = self._calculate_confidence(estimates)

                factor = CausalFactor(
                    name=col,
                    value=value,
                    influence=influence,
                    confidence=confidence,
                    description=self._get_factor_description(col, model),
                )

                factors.append(factor)

        # Sort by influence (absolute value)
        factors.sort(key=lambda f: abs(f.influence), reverse=True)

        # Keep top factors
        return factors[:5]

    def _calculate_influence(
        self, variable: str, correlation: float, model: CausalModel, decision: Decision
    ) -> float:
        """Calculate influence score for a variable"""
        # Base influence from correlation
        influence = correlation

        # Adjust based on causal graph structure
        graph = model._graph
        if graph:
            # Variables closer to outcome have higher influence
            try:
                import networkx as nx

                G = nx.DiGraph(graph.edges())

                # Calculate path length to outcome
                if nx.has_path(G, variable, model.outcome[0]):
                    path_length = nx.shortest_path_length(G, variable, model.outcome[0])
                    # Closer variables have higher influence
                    influence *= 1.0 / path_length
            except Exception:
                # TODO: Add proper error handling
                pass  # Silent for now, should log error

        # Adjust based on domain knowledge
        if variable in ["package_availability", "system_compatibility"]:
            # These are critical factors
            influence = max(influence, 0.8)
        elif variable in ["user_preference", "user_level"]:
            # These are important but not critical
            influence = min(influence, 0.6)

        # Clamp to [-1, 1]
        return max(-1.0, min(1.0, influence))

    def _calculate_confidence(self, estimates: list[dict]) -> float:
        """Calculate overall confidence from estimates"""
        if not estimates:
            return 0.5

        # Average confidence across methods
        confidences = []
        for est in estimates:
            if est.get("confidence_intervals"):
                ci_lower, ci_upper = est["confidence_intervals"]
                # Tighter intervals = higher confidence
                interval_width = ci_upper - ci_lower
                confidence = 1.0 - min(interval_width, 1.0)
                confidences.append(confidence)
            elif est.get("value") is not None:
                # If we have a value but no CI, moderate confidence
                confidences.append(0.7)

        if confidences:
            return sum(confidences) / len(confidences)
        return 0.5

    def _get_factor_description(self, variable: str, model: CausalModel) -> str:
        """Get human-readable description for a factor"""
        descriptions = {
            "package_availability": "Package exists in nixpkgs",
            "system_compatibility": "System meets package requirements",
            "disk_space": "Sufficient disk space available",
            "user_preference": "Matches user preferences",
            "user_level": "Appropriate for user skill level",
            "package_match": "How well package matches need",
            "security_updates": "Security updates available",
            "system_stability": "Current system stability",
            "package_unused": "Package is not actively used",
            "dependencies": "Other packages depend on this",
        }

        return descriptions.get(variable, f"Factor: {variable}")

    def _get_inference_methods(self, estimates: list[dict]) -> list[InferenceMethod]:
        """Convert estimation methods to InferenceMethod enums"""
        methods = []

        method_mapping = {
            "backdoor.propensity_score_matching": InferenceMethod.PROPENSITY_MATCHING,
            "backdoor.linear_regression": InferenceMethod.LINEAR_REGRESSION,
            "backdoor.propensity_score_weighting": InferenceMethod.PROPENSITY_WEIGHTING,
        }

        for est in estimates:
            method_name = est.get("method", "")
            if method_name in method_mapping:
                methods.append(method_mapping[method_name])

        # Always include backdoor adjustment as base method
        if InferenceMethod.BACKDOOR_ADJUSTMENT not in methods:
            methods.append(InferenceMethod.BACKDOOR_ADJUSTMENT)

        return methods

    def perform_counterfactual_analysis(
        self, decision: Decision, counterfactual_context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze what would happen with different context.

        Args:
            decision: Original decision
            counterfactual_context: Alternative context to analyze

        Returns:
            Analysis of counterfactual scenario
        """
        # Create counterfactual decision
        cf_decision = Decision(
            action=decision.action,
            target=decision.target,
            context={**decision.context, **counterfactual_context},
            confidence=0.0,  # Will be recalculated
            alternatives=decision.alternatives,
        )

        # Analyze both scenarios
        original_factors, _ = self.analyze_decision(decision)
        cf_factors, _ = self.analyze_decision(cf_decision)

        # Compare outcomes
        analysis = {
            "original_confidence": decision.confidence,
            "counterfactual_confidence": self._estimate_confidence(cf_factors),
            "changed_factors": [],
            "recommendation_change": False,
        }

        # Find changed factors
        for orig, cf in zip(original_factors, cf_factors, strict=False):
            if abs(orig.influence - cf.influence) > 0.1:
                analysis["changed_factors"].append(
                    {
                        "factor": orig.name,
                        "original_influence": orig.influence,
                        "counterfactual_influence": cf.influence,
                        "change": cf.influence - orig.influence,
                    }
                )

        # Check if recommendation would change
        if analysis["counterfactual_confidence"] < 0.5:
            analysis["recommendation_change"] = True

        return analysis

    def _estimate_confidence(self, factors: list[CausalFactor]) -> float:
        """Estimate decision confidence from causal factors"""
        if not factors:
            return 0.5

        # Weighted average of positive influences
        total_weight = 0.0
        weighted_sum = 0.0

        for factor in factors:
            if factor.influence > 0:
                weight = abs(factor.influence) * factor.confidence
                weighted_sum += factor.influence * weight
                total_weight += weight

        if total_weight > 0:
            return min(0.95, weighted_sum / total_weight)
        return 0.5

    def explain_causal_path(
        self, decision: Decision, from_factor: str, to_outcome: str
    ) -> list[CausalRelationship]:
        """
        Explain the causal path from a factor to an outcome.

        Args:
            decision: The decision context
            from_factor: Starting factor
            to_outcome: Target outcome

        Returns:
            List of causal relationships forming the path
        """
        model = self.model_builder.build_model(decision)

        # Get causal graph
        import networkx as nx

        G = nx.DiGraph()

        # Build graph from model
        if hasattr(model, "_graph") and model._graph:
            for edge in model._graph.edges():
                G.add_edge(edge[0], edge[1])

        # Find path
        try:
            path = nx.shortest_path(G, from_factor, to_outcome)
            relationships = []

            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]

                # Get edge data from knowledge base
                kb_model = self.knowledge_base.get_model(
                    self.model_builder._classify_decision(decision)
                )

                edge_desc = "causes"
                edge_strength = 0.5

                if kb_model:
                    for edge in kb_model["edges"]:
                        if edge.from_node == from_node and edge.to_node == to_node:
                            edge_desc = edge.description
                            edge_strength = edge.strength
                            break

                relationships.append(
                    CausalRelationship(
                        from_factor=from_node,
                        to_factor=to_node,
                        relationship_type=edge_desc,
                        strength=edge_strength,
                    )
                )

            return relationships

        except nx.NetworkXNoPath:
            return []
