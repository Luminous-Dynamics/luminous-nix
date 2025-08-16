"""
from typing import List, Dict, Optional, Union
Data models for the Causal XAI Engine
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import networkx as nx


class ExplanationLevel(Enum):
    """Level of detail for explanations"""

    SIMPLE = "simple"  # One sentence for all users
    DETAILED = "detailed"  # Paragraph with reasoning
    EXPERT = "expert"  # Full causal analysis


class InferenceMethod(Enum):
    """Methods for causal inference"""

    BACKDOOR_ADJUSTMENT = "backdoor_adjustment"
    FRONTDOOR_ADJUSTMENT = "frontdoor_adjustment"
    INSTRUMENTAL_VARIABLES = "instrumental_variables"
    PROPENSITY_SCORE_MATCHING = "propensity_score_matching"
    LINEAR_REGRESSION = "linear_regression"
    STRATIFICATION = "stratification"


@dataclass
class CausalFactor:
    """Represents a factor in the causal decision"""

    name: str
    value: str | float | bool
    influence: float  # -1.0 to 1.0, negative means decreases likelihood
    confidence: float  # 0.0 to 1.0, how sure we are about this factor
    description: str | None = None

    def __post_init__(self):
        """Validate factor values"""
        if not -1.0 <= self.influence <= 1.0:
            raise ValueError(
                f"Influence must be between -1.0 and 1.0, got {self.influence}"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )


@dataclass
class Decision:
    """Represents an AI decision to be explained"""

    action: str  # e.g., "install", "update", "remove"
    target: str  # e.g., "firefox", "system"
    context: dict[str, Any]  # All contextual information
    confidence: float  # Overall confidence in decision
    alternatives: list[dict[str, Any]] = field(default_factory=list)
    timestamp: float | None = None
    user_input: str | None = None

    def __post_init__(self):
        """Validate decision values"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )


@dataclass
class AlternativeExplanation:
    """Explanation for why an alternative was rejected"""

    alternative: str
    reason_rejected: str
    confidence_difference: float
    key_factor: CausalFactor | None = None


@dataclass
class Explanation:
    """Multi-level explanation for a decision"""

    simple: str  # One-sentence explanation
    detailed: str  # Paragraph with reasoning steps
    expert: dict[str, Any]  # Full technical details
    confidence: float  # Overall confidence
    factors: list[CausalFactor]  # All causal factors
    alternatives_rejected: list[
        AlternativeExplanation
    ]  # Why alternatives weren't chosen
    causal_graph: nx.DiGraph | None = None  # The causal model
    inference_methods: list[str] = field(default_factory=list)  # Methods used

    def get_primary_factor(self) -> CausalFactor | None:
        """Get the most influential factor"""
        if not self.factors:
            return None
        return max(self.factors, key=lambda f: abs(f.influence) * f.confidence)

    def get_positive_factors(self) -> list[CausalFactor]:
        """Get factors that support the decision"""
        return [f for f in self.factors if f.influence > 0]

    def get_negative_factors(self) -> list[CausalFactor]:
        """Get factors that oppose the decision"""
        return [f for f in self.factors if f.influence < 0]


@dataclass
class CausalEstimate:
    """Result from a causal estimation method"""

    method: str  # e.g., "propensity_score_matching"
    effect: float  # The estimated causal effect
    confidence_interval: tuple[float, float]  # CI for the effect
    p_value: float | None = None
    standard_error: float | None = None
    sample_size: int | None = None


@dataclass
class RefutationResult:
    """Result from a refutation test"""

    method: str  # e.g., "random_common_cause"
    original_effect: float
    new_effect: float
    passed: bool  # Whether the estimate is robust to this test
    message: str


@dataclass
class CausalEffects:
    """Combined results from causal analysis"""

    estimates: list[CausalEstimate]
    refutations: list[RefutationResult]
    confidence: float  # Overall confidence based on all analyses
    identified_estimand: str | None = None  # The causal estimand
    graph: nx.DiGraph | None = None  # The causal graph used

    def get_consensus_effect(self) -> float:
        """Get the consensus causal effect across methods"""
        if not self.estimates:
            return 0.0
        effects = [e.effect for e in self.estimates]
        return sum(effects) / len(effects)

    def get_robustness_score(self) -> float:
        """Calculate how robust the estimates are"""
        if not self.refutations:
            return 1.0
        passed = sum(1 for r in self.refutations if r.passed)
        return passed / len(self.refutations)


@dataclass
class CausalRelationship:
    """Represents a causal relationship between two variables"""

    source: str
    target: str
    strength: float  # 0.0 to 1.0
    relationship_type: str  # 'direct', 'indirect', 'confounding'
    description: str | None = None

    def __post_init__(self):
        """Validate relationship values"""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(
                f"Strength must be between 0.0 and 1.0, got {self.strength}"
            )
