"""
from typing import Dict, List
Explanation generator for creating human-readable explanations from causal analysis
"""

from typing import Any

from .knowledge_base import CausalKnowledgeBase
from .models import (
    AlternativeExplanation,
    CausalEffects,
    CausalFactor,
    CausalRelationship,
    Decision,
    Explanation,
)


class ExplanationGenerator:
    """Generates multi-level explanations from causal analysis results"""

    def __init__(self, knowledge_base: CausalKnowledgeBase):
        self.knowledge_base = knowledge_base

    def generate_explanation(
        self,
        decision: Decision,
        causal_effects: CausalEffects,
        causal_path: list[CausalRelationship],
        alternatives: list[dict[str, Any]],
    ) -> Explanation:
        """Generate a complete multi-level explanation"""

        # Extract causal factors from the analysis
        factors = self._extract_causal_factors(causal_effects, causal_path)

        # Generate explanations at each level
        simple = self._generate_simple_explanation(decision, factors)
        detailed = self._generate_detailed_explanation(decision, factors, causal_path)
        expert = self._generate_expert_explanation(
            decision, causal_effects, causal_path
        )

        # Analyze why alternatives were rejected
        alternatives_rejected = self._analyze_alternatives(decision, alternatives)

        # Calculate overall confidence
        confidence = self._calculate_confidence(causal_effects)

        return Explanation(
            simple=simple,
            detailed=detailed,
            expert=expert,
            confidence=confidence,
            factors=factors,
            alternatives_rejected=alternatives_rejected,
            causal_graph=causal_effects.graph,
            inference_methods=[e.method for e in causal_effects.estimates],
        )

    def _extract_causal_factors(
        self, causal_effects: CausalEffects, causal_path: list[CausalRelationship]
    ) -> list[CausalFactor]:
        """Extract causal factors from the analysis"""
        factors = []

        # Extract factors from causal path
        for relationship in causal_path:
            factor = CausalFactor(
                name=relationship.target,
                value=True,  # Simplified - in reality would extract actual value
                influence=relationship.strength,
                confidence=causal_effects.confidence,
                description=relationship.description,
            )
            factors.append(factor)

        # Add overall causal effect as a factor
        if causal_effects.estimates:
            consensus_effect = causal_effects.get_consensus_effect()
            factors.append(
                CausalFactor(
                    name="overall_causal_effect",
                    value=consensus_effect,
                    influence=consensus_effect,
                    confidence=causal_effects.confidence,
                    description="The average causal effect across all estimation methods",
                )
            )

        return factors

    def _generate_simple_explanation(
        self, decision: Decision, factors: list[CausalFactor]
    ) -> str:
        """Generate a one-sentence explanation for all users"""
        primary_factor = (
            max(factors, key=lambda f: abs(f.influence) * f.confidence)
            if factors
            else None
        )

        if primary_factor:
            return f"I chose to {decision.action} {decision.target} because {primary_factor.name.replace('_', ' ')} indicated it was the best option."
        return f"I chose to {decision.action} {decision.target} based on the available information."

    def _generate_detailed_explanation(
        self,
        decision: Decision,
        factors: list[CausalFactor],
        causal_path: list[CausalRelationship],
    ) -> str:
        """Generate a paragraph with reasoning steps"""
        explanation_parts = []

        # Start with the decision
        explanation_parts.append(
            f"I decided to {decision.action} {decision.target} based on careful analysis of the situation."
        )

        # Explain the causal path
        if causal_path:
            path_description = self._describe_causal_path(causal_path)
            explanation_parts.append(
                f"The decision follows this reasoning: {path_description}"
            )

        # Mention key factors
        positive_factors = [f for f in factors if f.influence > 0]
        negative_factors = [f for f in factors if f.influence < 0]

        if positive_factors:
            factor_names = [f.name.replace("_", " ") for f in positive_factors[:3]]
            explanation_parts.append(
                f"Supporting factors include: {', '.join(factor_names)}."
            )

        if negative_factors:
            factor_names = [f.name.replace("_", " ") for f in negative_factors[:2]]
            explanation_parts.append(
                f"Some concerns were: {', '.join(factor_names)}, but these were outweighed by the benefits."
            )

        # Add confidence statement
        confidence = factors[0].confidence if factors else 0.5
        if confidence > 0.8:
            explanation_parts.append("I'm very confident this is the right choice.")
        elif confidence > 0.6:
            explanation_parts.append("I'm reasonably confident in this decision.")
        else:
            explanation_parts.append(
                "There's some uncertainty, but this seems like the best option."
            )

        return " ".join(explanation_parts)

    def _generate_expert_explanation(
        self,
        decision: Decision,
        causal_effects: CausalEffects,
        causal_path: list[CausalRelationship],
    ) -> dict[str, Any]:
        """Generate full technical details for expert users"""
        expert_data = {
            "decision": {
                "action": decision.action,
                "target": decision.target,
                "confidence": decision.confidence,
            },
            "causal_analysis": {
                "identified_estimand": causal_effects.identified_estimand,
                "consensus_effect": causal_effects.get_consensus_effect(),
                "robustness_score": causal_effects.get_robustness_score(),
            },
            "estimation_results": [],
            "refutation_results": [],
            "causal_path": [],
        }

        # Add detailed estimation results
        for estimate in causal_effects.estimates:
            expert_data["estimation_results"].append(
                {
                    "method": estimate.method,
                    "effect": estimate.effect,
                    "confidence_interval": estimate.confidence_interval,
                    "p_value": estimate.p_value,
                    "standard_error": estimate.standard_error,
                }
            )

        # Add refutation results
        for refutation in causal_effects.refutations:
            expert_data["refutation_results"].append(
                {
                    "method": refutation.method,
                    "original_effect": refutation.original_effect,
                    "new_effect": refutation.new_effect,
                    "passed": refutation.passed,
                    "message": refutation.message,
                }
            )

        # Add causal path details
        for relationship in causal_path:
            expert_data["causal_path"].append(
                {
                    "source": relationship.source,
                    "target": relationship.target,
                    "strength": relationship.strength,
                    "type": relationship.relationship_type,
                    "description": relationship.description,
                }
            )

        return expert_data

    def _describe_causal_path(self, causal_path: list[CausalRelationship]) -> str:
        """Create a human-readable description of the causal path"""
        if not causal_path:
            return "direct analysis of the situation"

        path_parts = []
        for i, relationship in enumerate(causal_path):
            if i == 0:
                path_parts.append(f"{relationship.source.replace('_', ' ')}")
            path_parts.append(f"leads to {relationship.target.replace('_', ' ')}")

        return " → ".join(path_parts)

    def _analyze_alternatives(
        self, decision: Decision, alternatives: list[dict[str, Any]]
    ) -> list[AlternativeExplanation]:
        """Analyze why alternatives were rejected"""
        rejected = []

        for alt in alternatives:
            if (
                alt.get("action") == decision.action
                and alt.get("target") == decision.target
            ):
                continue  # Skip the chosen option

            explanation = AlternativeExplanation(
                alternative=f"{alt.get('action', 'unknown')} {alt.get('target', 'unknown')}",
                reason_rejected=self._get_rejection_reason(decision, alt),
                confidence_difference=decision.confidence - alt.get("confidence", 0.0),
                key_factor=None,  # Could be enhanced to identify specific factors
            )
            rejected.append(explanation)

        return rejected

    def _get_rejection_reason(
        self, chosen: Decision, alternative: dict[str, Any]
    ) -> str:
        """Determine why an alternative was rejected"""
        if alternative.get("confidence", 0) < chosen.confidence * 0.5:
            return "Much lower confidence in success"
        if alternative.get("risk", 0) > 0.7:
            return "Too risky compared to chosen option"
        if alternative.get("complexity", 0) > 0.8:
            return "More complex than necessary"
        return "The chosen option better matches your needs"

    def _calculate_confidence(self, causal_effects: CausalEffects) -> float:
        """Calculate overall confidence from causal analysis"""
        base_confidence = causal_effects.confidence
        robustness = causal_effects.get_robustness_score()

        # Weight confidence by robustness
        return base_confidence * (0.7 + 0.3 * robustness)
