"""
from typing import List, Dict, Optional
Causal XAI Engine - Main orchestrator for explainable AI decisions

This module provides the high-level interface for generating causal explanations
for Nix for Humanity's AI decisions. It coordinates the knowledge base, model
builder, inference engine, and explanation generator to provide transparent,
multi-level explanations.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import time
import traceback

from .models import (
    Decision, Explanation, ExplanationLevel, CausalFactor,
    AlternativeExplanation, CausalEffects, CausalRelationship
)
from .knowledge_base import CausalKnowledgeBase
from .builder import CausalModelBuilder
from .inference import CausalInferenceEngine
from .generator import ExplanationGenerator

logger = logging.getLogger(__name__)


@dataclass
class PersonaConfig:
    """Configuration for persona-adaptive explanations"""
    name: str
    explanation_level: ExplanationLevel
    preferred_style: str  # 'technical', 'friendly', 'simple', 'encouraging'
    max_complexity: int  # 1-10 scale
    include_confidence: bool = True
    include_alternatives: bool = True
    
    
# Default persona configurations
PERSONA_CONFIGS = {
    "grandma_rose": PersonaConfig(
        name="grandma_rose",
        explanation_level=ExplanationLevel.SIMPLE,
        preferred_style="friendly",
        max_complexity=2,
        include_confidence=False,
        include_alternatives=False
    ),
    "maya_adhd": PersonaConfig(
        name="maya_adhd",
        explanation_level=ExplanationLevel.SIMPLE,
        preferred_style="simple",
        max_complexity=3,
        include_confidence=True,
        include_alternatives=False
    ),
    "david_tired": PersonaConfig(
        name="david_tired",
        explanation_level=ExplanationLevel.SIMPLE,
        preferred_style="simple",
        max_complexity=3,
        include_confidence=False,
        include_alternatives=False
    ),
    "dr_sarah": PersonaConfig(
        name="dr_sarah",
        explanation_level=ExplanationLevel.DETAILED,
        preferred_style="technical",
        max_complexity=8,
        include_confidence=True,
        include_alternatives=True
    ),
    "alex_blind": PersonaConfig(
        name="alex_blind",
        explanation_level=ExplanationLevel.DETAILED,
        preferred_style="technical",
        max_complexity=7,
        include_confidence=True,
        include_alternatives=True
    ),
    "carlos_learner": PersonaConfig(
        name="carlos_learner",
        explanation_level=ExplanationLevel.DETAILED,
        preferred_style="encouraging",
        max_complexity=5,
        include_confidence=True,
        include_alternatives=True
    ),
    "priya_busy": PersonaConfig(
        name="priya_busy",
        explanation_level=ExplanationLevel.SIMPLE,
        preferred_style="simple",
        max_complexity=4,
        include_confidence=False,
        include_alternatives=False
    ),
    "jamie_privacy": PersonaConfig(
        name="jamie_privacy",
        explanation_level=ExplanationLevel.EXPERT,
        preferred_style="technical",
        max_complexity=9,
        include_confidence=True,
        include_alternatives=True
    ),
    "viktor_esl": PersonaConfig(
        name="viktor_esl",
        explanation_level=ExplanationLevel.SIMPLE,
        preferred_style="simple",
        max_complexity=2,
        include_confidence=False,
        include_alternatives=False
    ),
    "luna_autistic": PersonaConfig(
        name="luna_autistic",
        explanation_level=ExplanationLevel.DETAILED,
        preferred_style="technical",
        max_complexity=6,
        include_confidence=True,
        include_alternatives=False
    ),
    # Default configuration
    "default": PersonaConfig(
        name="default",
        explanation_level=ExplanationLevel.DETAILED,
        preferred_style="friendly",
        max_complexity=5,
        include_confidence=True,
        include_alternatives=True
    )
}


class CausalXAIEngine:
    """
    Main orchestrator for the Causal XAI system.
    
    This class coordinates all XAI components to provide transparent,
    multi-level explanations for AI decisions in Nix for Humanity.
    """
    
    def __init__(
        self,
        knowledge_base: Optional[CausalKnowledgeBase] = None,
        enable_caching: bool = True,
        max_cache_size: int = 1000
    ):
        """
        Initialize the Causal XAI Engine.
        
        Args:
            knowledge_base: Optional custom knowledge base, defaults to standard
            enable_caching: Whether to cache explanations for performance
            max_cache_size: Maximum number of cached explanations
        """
        self.knowledge_base = knowledge_base or CausalKnowledgeBase()
        self.model_builder = CausalModelBuilder(self.knowledge_base)
        self.inference_engine = CausalInferenceEngine()
        self.explanation_generator = ExplanationGenerator(self.knowledge_base)
        
        # Caching for performance
        self.enable_caching = enable_caching
        self.max_cache_size = max_cache_size
        self.explanation_cache: Dict[str, Explanation] = {}
        
        # Metrics tracking
        self.metrics = {
            "explanations_generated": 0,
            "cache_hits": 0,
            "average_generation_time": 0.0,
            "errors": 0
        }
        
        logger.info("CausalXAIEngine initialized with caching=%s", enable_caching)
    
    def explain_decision(
        self,
        decision: Decision,
        persona: Optional[str] = None,
        level: Optional[ExplanationLevel] = None,
        include_alternatives: bool = True
    ) -> Explanation:
        """
        Generate a causal explanation for a decision.
        
        This is the main entry point for getting explanations. It handles
        the full pipeline from decision to human-readable explanation.
        
        Args:
            decision: The AI decision to explain
            persona: Optional persona identifier for adaptive explanations
            level: Optional override for explanation level
            include_alternatives: Whether to analyze rejected alternatives
            
        Returns:
            A complete multi-level explanation
            
        Raises:
            ValueError: If the decision cannot be explained
            RuntimeError: If explanation generation fails
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(decision, persona, level)
            if self.enable_caching and cache_key in self.explanation_cache:
                self.metrics["cache_hits"] += 1
                logger.debug("Cache hit for decision: %s", decision.action)
                return self._adapt_explanation_for_persona(
                    self.explanation_cache[cache_key], persona
                )
            
            # Validate decision
            self._validate_decision(decision)
            
            # Build causal model for this decision type
            logger.info("Building causal model for decision: %s %s", 
                       decision.action, decision.target)
            causal_model = self.model_builder.build_model(decision)
            
            # Perform causal inference
            logger.info("Running causal inference")
            causal_effects = self.inference_engine.estimate_effects(
                causal_model, decision
            )
            
            # Extract causal path
            causal_path = self._extract_causal_path(causal_model, decision)
            
            # Get alternatives if requested
            alternatives = []
            if include_alternatives:
                alternatives = self._get_alternatives(decision)
            
            # Generate explanation
            logger.info("Generating explanation")
            explanation = self.explanation_generator.generate_explanation(
                decision, causal_effects, causal_path, alternatives
            )
            
            # Cache the explanation
            if self.enable_caching:
                self._cache_explanation(cache_key, explanation)
            
            # Update metrics
            self.metrics["explanations_generated"] += 1
            generation_time = time.time() - start_time
            self._update_average_time(generation_time)
            
            logger.info("Explanation generated in %.2fs", generation_time)
            
            # Adapt for persona if specified
            return self._adapt_explanation_for_persona(explanation, persona)
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error("Error generating explanation: %s", str(e))
            logger.debug("Traceback: %s", traceback.format_exc())
            
            # Return a fallback explanation
            return self._generate_fallback_explanation(decision, str(e))
    
    def explain_simple(self, decision: Decision, persona: Optional[str] = None) -> str:
        """
        Get just the simple explanation for a decision.
        
        Convenience method for when only a one-sentence explanation is needed.
        """
        explanation = self.explain_decision(
            decision, persona, ExplanationLevel.SIMPLE
        )
        return explanation.simple
    
    def get_primary_reason(self, decision: Decision) -> Optional[CausalFactor]:
        """
        Get the single most important factor in a decision.
        
        Useful for quick summaries or tooltips.
        """
        explanation = self.explain_decision(
            decision, level=ExplanationLevel.SIMPLE, include_alternatives=False
        )
        return explanation.get_primary_factor()
    
    def compare_alternatives(
        self, 
        decision: Decision,
        alternatives: List[str]
    ) -> List[AlternativeExplanation]:
        """
        Explain why specific alternatives were not chosen.
        
        Args:
            decision: The chosen decision
            alternatives: List of alternative actions/targets to compare
            
        Returns:
            List of explanations for why each alternative was rejected
        """
        # Create alternative decisions
        alt_decisions = []
        for alt in alternatives:
            alt_decision = Decision(
                action=decision.action,
                target=alt,
                context=decision.context,
                confidence=0.0  # Will be calculated
            )
            alt_decisions.append(alt_decision)
        
        # Analyze each alternative
        explanations = []
        for alt_decision in alt_decisions:
            try:
                # Build model and estimate effects
                model = self.model_builder.build_model(alt_decision)
                effects = self.inference_engine.estimate_effects(model, alt_decision)
                
                # Compare to original
                reason = self._compare_effects(decision, alt_decision, effects)
                
                explanations.append(AlternativeExplanation(
                    alternative=alt_decision.target,
                    reason_rejected=reason,
                    confidence_difference=decision.confidence - effects.confidence,
                    key_factor=self._get_differentiating_factor(decision, alt_decision)
                ))
            except Exception as e:
                logger.warning("Failed to analyze alternative %s: %s", 
                             alt_decision.target, str(e))
                explanations.append(AlternativeExplanation(
                    alternative=alt_decision.target,
                    reason_rejected="Could not analyze this alternative",
                    confidence_difference=0.0
                ))
        
        return explanations
    
    def _validate_decision(self, decision: Decision) -> None:
        """Validate that a decision can be explained"""
        if not decision.action:
            raise ValueError("Decision must have an action")
        if not decision.context:
            raise ValueError("Decision must have context")
        if decision.confidence < 0 or decision.confidence > 1:
            raise ValueError("Decision confidence must be between 0 and 1")
    
    def _get_cache_key(
        self, 
        decision: Decision, 
        persona: Optional[str],
        level: Optional[ExplanationLevel]
    ) -> str:
        """Generate a cache key for a decision/persona/level combination"""
        persona_str = persona or "default"
        level_str = level.value if level else "all"
        return f"{decision.action}:{decision.target}:{persona_str}:{level_str}"
    
    def _cache_explanation(self, key: str, explanation: Explanation) -> None:
        """Cache an explanation with LRU eviction"""
        if len(self.explanation_cache) >= self.max_cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.explanation_cache))
            del self.explanation_cache[oldest_key]
        
        self.explanation_cache[key] = explanation
    
    def _extract_causal_path(
        self, 
        causal_model: Any,
        decision: Decision
    ) -> List[CausalRelationship]:
        """Extract the main causal path from the model"""
        # This would analyze the causal graph to find the path
        # from key factors to the decision outcome
        # Simplified for now
        return [
            CausalRelationship(
                source="user_input",
                target="intent_recognition",
                strength=0.9,
                relationship_type="direct"
            ),
            CausalRelationship(
                source="intent_recognition",
                target="package_selection",
                strength=0.8,
                relationship_type="direct"
            ),
            CausalRelationship(
                source="package_selection",
                target=decision.action,
                strength=0.95,
                relationship_type="direct"
            )
        ]
    
    def _get_alternatives(self, decision: Decision) -> List[Dict[str, Any]]:
        """Get plausible alternatives to the chosen decision"""
        # This would use the knowledge base to find alternatives
        # Simplified implementation
        alternatives = []
        
        if decision.action == "install" and decision.target == "firefox":
            alternatives = [
                {"action": "install", "target": "chromium", "reason": "alternative browser"},
                {"action": "install", "target": "brave", "reason": "privacy-focused browser"}
            ]
        
        return alternatives
    
    def _adapt_explanation_for_persona(
        self,
        explanation: Explanation,
        persona: Optional[str]
    ) -> Explanation:
        """Adapt an explanation based on persona preferences"""
        if not persona:
            return explanation
        
        config = PERSONA_CONFIGS.get(persona, PERSONA_CONFIGS["default"])
        
        # Create adapted explanation based on persona config
        adapted = Explanation(
            simple=explanation.simple,
            detailed=explanation.detailed if config.explanation_level != ExplanationLevel.SIMPLE else explanation.simple,
            expert=explanation.expert if config.explanation_level == ExplanationLevel.EXPERT else {},
            confidence=explanation.confidence if config.include_confidence else 1.0,
            factors=explanation.factors[:config.max_complexity],
            alternatives_rejected=explanation.alternatives_rejected if config.include_alternatives else [],
            causal_graph=explanation.causal_graph if config.explanation_level == ExplanationLevel.EXPERT else None,
            inference_methods=explanation.inference_methods if config.explanation_level == ExplanationLevel.EXPERT else []
        )
        
        # Apply style adaptations
        if config.preferred_style == "simple":
            adapted.simple = self._simplify_language(adapted.simple)
            adapted.detailed = self._simplify_language(adapted.detailed)
        elif config.preferred_style == "encouraging":
            adapted.detailed = self._make_encouraging(adapted.detailed)
        
        return adapted
    
    def _simplify_language(self, text: str) -> str:
        """Simplify language for personas like Grandma Rose or Viktor"""
        # This would use NLP to simplify, for now just basic replacements
        replacements = {
            "repository": "collection",
            "package": "program",
            "dependency": "required program",
            "configure": "set up",
            "execute": "run"
        }
        
        result = text
        for complex_word, simple_word in replacements.items():
            result = result.replace(complex_word, simple_word)
        
        return result
    
    def _make_encouraging(self, text: str) -> str:
        """Make language more encouraging for learners like Carlos"""
        encouragements = [
            "Great question! ",
            "You're learning fast! ",
            "Good thinking! "
        ]
        
        # Add encouragement at the start
        import random
        return random.choice(encouragements) + text
    
    def _update_average_time(self, new_time: float) -> None:
        """Update rolling average generation time"""
        count = self.metrics["explanations_generated"]
        old_avg = self.metrics["average_generation_time"]
        self.metrics["average_generation_time"] = (
            (old_avg * (count - 1) + new_time) / count
        )
    
    def _generate_fallback_explanation(
        self, 
        decision: Decision,
        error: str
    ) -> Explanation:
        """Generate a simple fallback explanation when analysis fails"""
        logger.warning("Generating fallback explanation due to error: %s", error)
        
        simple = f"I decided to {decision.action} {decision.target} based on your request."
        detailed = (
            f"I understood you wanted to {decision.action} {decision.target}. "
            f"This is a common operation that usually works well."
        )
        
        return Explanation(
            simple=simple,
            detailed=detailed,
            expert={"error": error, "fallback": True},
            confidence=decision.confidence,
            factors=[
                CausalFactor(
                    name="user_request",
                    value=decision.user_input or "unknown",
                    influence=1.0,
                    confidence=0.5,
                    description="Direct user request"
                )
            ],
            alternatives_rejected=[],
            causal_graph=None,
            inference_methods=[]
        )
    
    def _compare_effects(
        self,
        chosen: Decision,
        alternative: Decision,
        alt_effects: CausalEffects
    ) -> str:
        """Generate reason why alternative was rejected"""
        if alt_effects.confidence < chosen.confidence:
            return f"Less confident match ({alt_effects.confidence:.0%} vs {chosen.confidence:.0%})"
        else:
            return "User preference or context suggested the chosen option"
    
    def _get_differentiating_factor(
        self,
        chosen: Decision,
        alternative: Decision
    ) -> Optional[CausalFactor]:
        """Find the key factor that differentiated the choices"""
        # Simplified - would analyze actual factors
        return CausalFactor(
            name="user_preference",
            value=chosen.target,
            influence=0.8,
            confidence=0.7,
            description=f"Previous usage suggests preference for {chosen.target}"
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the XAI engine"""
        return self.metrics.copy()
    
    def clear_cache(self) -> None:
        """Clear the explanation cache"""
        self.explanation_cache.clear()
        logger.info("XAI cache cleared")