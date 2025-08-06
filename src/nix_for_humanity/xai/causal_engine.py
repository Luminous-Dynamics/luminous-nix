"""
Causal XAI Engine using DoWhy framework
Provides transparent explanations for AI decisions in Nix for Humanity
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime

# Note: DoWhy import is optional for basic functionality
try:
    import dowhy
    from dowhy import CausalModel
    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    logging.warning("DoWhy not available. Using simplified causal reasoning.")

# Note: Numpy import is optional for basic functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create mock numpy for basic operations
    class MockNumpy:
        def array(self, data):
            return data
        def mean(self, data):
            return sum(data) / len(data) if data else 0
        def std(self, data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            return variance ** 0.5
    np = MockNumpy()
    logging.warning("Numpy not available. Using simplified numerical operations.")


class ExplanationLevel(Enum):
    """Depth of explanation detail"""
    SIMPLE = "simple"      # Basic why for all users
    DETAILED = "detailed"  # More context for interested users
    EXPERT = "expert"      # Full causal graph for power users


class ConfidenceLevel(Enum):
    """Confidence in the explanation"""
    LOW = "low"           # < 50% confidence
    MEDIUM = "medium"     # 50-80% confidence
    HIGH = "high"         # > 80% confidence
    CERTAIN = "certain"   # > 95% confidence


@dataclass
class DecisionNode:
    """A node in the decision tree"""
    id: str
    description: str
    confidence: float
    contributing_factors: List[str]
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'description': self.description,
            'confidence': self.confidence,
            'contributing_factors': self.contributing_factors,
            'weight': self.weight
        }


@dataclass
class CausalExplanation:
    """Complete causal explanation for a decision"""
    decision: str
    primary_reason: str
    confidence: ConfidenceLevel
    confidence_score: float
    contributing_factors: List[DecisionNode]
    alternative_paths: List[Dict[str, Any]]
    timestamp: datetime
    explanation_level: ExplanationLevel
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'decision': self.decision,
            'primary_reason': self.primary_reason,
            'confidence': self.confidence.value,
            'confidence_score': self.confidence_score,
            'contributing_factors': [f.to_dict() for f in self.contributing_factors],
            'alternative_paths': self.alternative_paths,
            'timestamp': self.timestamp.isoformat(),
            'explanation_level': self.explanation_level.value
        }


class CausalGraph:
    """Represents the causal relationships in a decision"""
    
    def __init__(self):
        self.nodes: Dict[str, DecisionNode] = {}
        self.edges: List[Tuple[str, str, float]] = []  # (from, to, weight)
    
    def add_node(self, node: DecisionNode):
        """Add a decision node to the graph"""
        self.nodes[node.id] = node
    
    def add_edge(self, from_id: str, to_id: str, weight: float = 1.0):
        """Add a causal edge between nodes"""
        self.edges.append((from_id, to_id, weight))
    
    def get_path_strength(self, path: List[str]) -> float:
        """Calculate the strength of a causal path"""
        if len(path) < 2:
            return 1.0
        
        strength = 1.0
        for i in range(len(path) - 1):
            edge_weight = self._get_edge_weight(path[i], path[i + 1])
            strength *= edge_weight
        
        return strength
    
    def _get_edge_weight(self, from_id: str, to_id: str) -> float:
        """Get the weight of an edge"""
        for f, t, w in self.edges:
            if f == from_id and t == to_id:
                return w
        return 0.0


class CausalXAI:
    """Main Causal XAI Engine for Nix for Humanity"""
    
    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base
        self.logger = logging.getLogger(__name__)
        self.decision_history: List[CausalExplanation] = []
        
        # Pre-defined causal patterns for NixOS operations
        self.causal_patterns = self._initialize_causal_patterns()
    
    def explain_decision(
        self,
        decision: str,
        context: Dict[str, Any],
        level: ExplanationLevel = ExplanationLevel.SIMPLE
    ) -> CausalExplanation:
        """
        Generate a causal explanation for an AI decision
        
        Args:
            decision: The decision/action taken
            context: Context information about the decision
            level: Level of detail for the explanation
            
        Returns:
            CausalExplanation object
        """
        # Build causal graph for this decision
        graph = self._build_causal_graph(decision, context)
        
        # Calculate confidence
        confidence_score = self._calculate_confidence(graph, context)
        confidence_level = self._score_to_level(confidence_score)
        
        # Generate explanation based on level
        if level == ExplanationLevel.SIMPLE:
            explanation = self._generate_simple_explanation(decision, graph, context)
        elif level == ExplanationLevel.DETAILED:
            explanation = self._generate_detailed_explanation(decision, graph, context)
        else:  # EXPERT
            explanation = self._generate_expert_explanation(decision, graph, context)
        
        # Store in history
        self.decision_history.append(explanation)
        
        return explanation
    
    def _initialize_causal_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common causal patterns for NixOS operations"""
        return {
            "install_package": {
                "factors": [
                    {"id": "user_request", "description": "User requested installation", "weight": 0.4},
                    {"id": "package_exists", "description": "Package exists in nixpkgs", "weight": 0.3},
                    {"id": "dependencies_available", "description": "All dependencies available", "weight": 0.2},
                    {"id": "system_compatible", "description": "Compatible with system", "weight": 0.1}
                ],
                "confidence_modifiers": {
                    "exact_match": 0.2,
                    "typo_corrected": -0.1,
                    "multiple_options": -0.15
                }
            },
            "update_system": {
                "factors": [
                    {"id": "update_request", "description": "User requested update", "weight": 0.3},
                    {"id": "updates_available", "description": "Updates are available", "weight": 0.3},
                    {"id": "channel_stable", "description": "Channel is stable", "weight": 0.2},
                    {"id": "disk_space", "description": "Sufficient disk space", "weight": 0.2}
                ],
                "confidence_modifiers": {
                    "regular_schedule": 0.1,
                    "security_updates": 0.15,
                    "major_version": -0.1
                }
            },
            "fix_error": {
                "factors": [
                    {"id": "error_identified", "description": "Error correctly identified", "weight": 0.4},
                    {"id": "solution_known", "description": "Known solution exists", "weight": 0.3},
                    {"id": "safe_to_apply", "description": "Solution is safe", "weight": 0.2},
                    {"id": "user_context", "description": "Matches user context", "weight": 0.1}
                ],
                "confidence_modifiers": {
                    "exact_error_match": 0.2,
                    "similar_error": -0.1,
                    "first_time_error": -0.15
                }
            }
        }
    
    def _build_causal_graph(self, decision: str, context: Dict[str, Any]) -> CausalGraph:
        """Build a causal graph for the decision"""
        graph = CausalGraph()
        
        # Determine decision type
        decision_type = self._classify_decision(decision, context)
        
        if decision_type in self.causal_patterns:
            pattern = self.causal_patterns[decision_type]
            
            # Add nodes from pattern
            for factor in pattern["factors"]:
                node = DecisionNode(
                    id=factor["id"],
                    description=factor["description"],
                    confidence=self._evaluate_factor(factor["id"], context),
                    contributing_factors=[],
                    weight=factor["weight"]
                )
                graph.add_node(node)
            
            # Add edges to create causal relationships
            # For now, simple linear causation
            factors = pattern["factors"]
            for i in range(len(factors) - 1):
                graph.add_edge(factors[i]["id"], factors[i + 1]["id"], 0.8)
            
            # Add final edge to decision
            if factors:
                decision_node = DecisionNode(
                    id="final_decision",
                    description=decision,
                    confidence=self._calculate_overall_confidence(graph),
                    contributing_factors=[f["id"] for f in factors]
                )
                graph.add_node(decision_node)
                graph.add_edge(factors[-1]["id"], "final_decision", 0.9)
        
        return graph
    
    def _classify_decision(self, decision: str, context: Dict[str, Any]) -> str:
        """Classify the type of decision being made"""
        decision_lower = decision.lower()
        
        if any(word in decision_lower for word in ["install", "add", "get"]):
            return "install_package"
        elif any(word in decision_lower for word in ["update", "upgrade"]):
            return "update_system"
        elif any(word in decision_lower for word in ["fix", "error", "problem"]):
            return "fix_error"
        else:
            return "unknown"
    
    def _evaluate_factor(self, factor_id: str, context: Dict[str, Any]) -> float:
        """Evaluate the confidence in a specific factor"""
        # Simplified evaluation - in production would use more sophisticated logic
        evaluations = {
            "user_request": 0.95,  # We're confident the user asked
            "package_exists": context.get("package_found", 0.8),
            "dependencies_available": context.get("deps_available", 0.85),
            "system_compatible": context.get("compatible", 0.9),
            "update_request": 0.95,
            "updates_available": context.get("updates_found", 0.7),
            "channel_stable": context.get("channel_stable", 0.8),
            "disk_space": context.get("disk_space_ok", 0.9),
            "error_identified": context.get("error_match", 0.75),
            "solution_known": context.get("solution_confidence", 0.7),
            "safe_to_apply": context.get("safety_score", 0.85),
            "user_context": context.get("context_match", 0.8)
        }
        
        return evaluations.get(factor_id, 0.5)
    
    def _calculate_confidence(self, graph: CausalGraph, context: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        if not graph.nodes:
            return 0.5
        
        # Weighted average of node confidences
        total_weight = 0.0
        weighted_confidence = 0.0
        
        for node in graph.nodes.values():
            if node.id != "final_decision":
                weighted_confidence += node.confidence * node.weight
                total_weight += node.weight
        
        if total_weight > 0:
            base_confidence = weighted_confidence / total_weight
        else:
            base_confidence = 0.5
        
        # Apply modifiers based on context
        modifiers = context.get("confidence_modifiers", {})
        for modifier, value in modifiers.items():
            base_confidence = min(1.0, max(0.0, base_confidence + value))
        
        return base_confidence
    
    def _calculate_overall_confidence(self, graph: CausalGraph) -> float:
        """Calculate confidence for the overall decision"""
        confidences = [node.confidence for node in graph.nodes.values() 
                      if node.id != "final_decision"]
        if confidences:
            return np.mean(confidences)
        return 0.5
    
    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """Convert confidence score to level"""
        if score >= 0.95:
            return ConfidenceLevel.CERTAIN
        elif score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _generate_simple_explanation(
        self, 
        decision: str, 
        graph: CausalGraph, 
        context: Dict[str, Any]
    ) -> CausalExplanation:
        """Generate a simple explanation suitable for all users"""
        # Find the most important factor
        primary_factor = None
        max_weight = 0.0
        
        for node in graph.nodes.values():
            if node.id != "final_decision" and node.weight > max_weight:
                primary_factor = node
                max_weight = node.weight
        
        if primary_factor:
            primary_reason = f"I decided to {decision} because {primary_factor.description.lower()}"
        else:
            primary_reason = f"I decided to {decision} based on the current context"
        
        return CausalExplanation(
            decision=decision,
            primary_reason=primary_reason,
            confidence=self._score_to_level(self._calculate_confidence(graph, context)),
            confidence_score=self._calculate_confidence(graph, context),
            contributing_factors=[primary_factor] if primary_factor else [],
            alternative_paths=[],
            timestamp=datetime.now(),
            explanation_level=ExplanationLevel.SIMPLE
        )
    
    def _generate_detailed_explanation(
        self, 
        decision: str, 
        graph: CausalGraph, 
        context: Dict[str, Any]
    ) -> CausalExplanation:
        """Generate a detailed explanation with contributing factors"""
        # Get top 3 factors
        factors = sorted(
            [n for n in graph.nodes.values() if n.id != "final_decision"],
            key=lambda x: x.weight * x.confidence,
            reverse=True
        )[:3]
        
        primary_reason = f"I decided to {decision} based on multiple factors"
        
        # Generate alternative paths
        alternatives = self._generate_alternatives(decision, context)
        
        return CausalExplanation(
            decision=decision,
            primary_reason=primary_reason,
            confidence=self._score_to_level(self._calculate_confidence(graph, context)),
            confidence_score=self._calculate_confidence(graph, context),
            contributing_factors=factors,
            alternative_paths=alternatives,
            timestamp=datetime.now(),
            explanation_level=ExplanationLevel.DETAILED
        )
    
    def _generate_expert_explanation(
        self, 
        decision: str, 
        graph: CausalGraph, 
        context: Dict[str, Any]
    ) -> CausalExplanation:
        """Generate an expert-level explanation with full causal graph"""
        # Include all factors and their relationships
        all_factors = [n for n in graph.nodes.values() if n.id != "final_decision"]
        
        primary_reason = f"Decision tree analysis for: {decision}"
        
        # Include causal paths
        alternatives = self._generate_alternatives(decision, context)
        
        # Add causal path information
        for alt in alternatives:
            alt['causal_strength'] = graph.get_path_strength(alt.get('path', []))
        
        return CausalExplanation(
            decision=decision,
            primary_reason=primary_reason,
            confidence=self._score_to_level(self._calculate_confidence(graph, context)),
            confidence_score=self._calculate_confidence(graph, context),
            contributing_factors=all_factors,
            alternative_paths=alternatives,
            timestamp=datetime.now(),
            explanation_level=ExplanationLevel.EXPERT
        )
    
    def _generate_alternatives(self, decision: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alternative decision paths"""
        alternatives = []
        
        # Example alternatives based on decision type
        if "install" in decision.lower():
            alternatives.append({
                "decision": "Use declarative configuration",
                "reason": "More reproducible and follows NixOS best practices",
                "confidence": 0.85,
                "path": ["user_request", "declarative_option", "final_decision"]
            })
            alternatives.append({
                "decision": "Install in user environment",
                "reason": "Doesn't require system rebuild",
                "confidence": 0.70,
                "path": ["user_request", "user_env_option", "final_decision"]
            })
        
        return alternatives
    
    def get_explanation_history(self, limit: int = 10) -> List[CausalExplanation]:
        """Get recent explanation history"""
        return self.decision_history[-limit:]
    
    def export_explanation(self, explanation: CausalExplanation, format: str = "json") -> str:
        """Export explanation in various formats"""
        if format == "json":
            return json.dumps(explanation.to_dict(), indent=2)
        elif format == "text":
            return self._format_as_text(explanation)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _format_as_text(self, explanation: CausalExplanation) -> str:
        """Format explanation as human-readable text"""
        lines = [
            f"Decision: {explanation.decision}",
            f"Reason: {explanation.primary_reason}",
            f"Confidence: {explanation.confidence.value} ({explanation.confidence_score:.1%})",
            ""
        ]
        
        if explanation.contributing_factors:
            lines.append("Contributing factors:")
            for factor in explanation.contributing_factors:
                lines.append(f"  • {factor.description} (confidence: {factor.confidence:.1%})")
            lines.append("")
        
        if explanation.alternative_paths:
            lines.append("Alternative approaches:")
            for alt in explanation.alternative_paths:
                lines.append(f"  • {alt['decision']}: {alt['reason']}")
            lines.append("")
        
        return "\n".join(lines)