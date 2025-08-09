"""
from typing import List, Dict, Optional, Union
Data models for the Causal XAI Engine
"""

from typing import List, Dict, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx


class ExplanationLevel(Enum):
    """Level of detail for explanations"""
    SIMPLE = "simple"      # One sentence for all users
    DETAILED = "detailed"  # Paragraph with reasoning
    EXPERT = "expert"      # Full causal analysis


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
    value: Union[str, float, bool]
    influence: float  # -1.0 to 1.0, negative means decreases likelihood
    confidence: float  # 0.0 to 1.0, how sure we are about this factor
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate factor values"""
        if not -1.0 <= self.influence <= 1.0:
            raise ValueError(f"Influence must be between -1.0 and 1.0, got {self.influence}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class Decision:
    """Represents an AI decision to be explained"""
    action: str  # e.g., "install", "update", "remove"
    target: str  # e.g., "firefox", "system"
    context: Dict[str, Any]  # All contextual information
    confidence: float  # Overall confidence in decision
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: Optional[float] = None
    user_input: Optional[str] = None
    
    def __post_init__(self):
        """Validate decision values"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class AlternativeExplanation:
    """Explanation for why an alternative was rejected"""
    alternative: str
    reason_rejected: str
    confidence_difference: float
    key_factor: Optional[CausalFactor] = None


@dataclass
class Explanation:
    """Multi-level explanation for a decision"""
    simple: str  # One-sentence explanation
    detailed: str  # Paragraph with reasoning steps
    expert: Dict[str, Any]  # Full technical details
    confidence: float  # Overall confidence
    factors: List[CausalFactor]  # All causal factors
    alternatives_rejected: List[AlternativeExplanation]  # Why alternatives weren't chosen
    causal_graph: Optional[nx.DiGraph] = None  # The causal model
    inference_methods: List[str] = field(default_factory=list)  # Methods used
    
    def get_primary_factor(self) -> Optional[CausalFactor]:
        """Get the most influential factor"""
        if not self.factors:
            return None
        return max(self.factors, key=lambda f: abs(f.influence) * f.confidence)
    
    def get_positive_factors(self) -> List[CausalFactor]:
        """Get factors that support the decision"""
        return [f for f in self.factors if f.influence > 0]
    
    def get_negative_factors(self) -> List[CausalFactor]:
        """Get factors that oppose the decision"""
        return [f for f in self.factors if f.influence < 0]


@dataclass
class CausalEstimate:
    """Result from a causal estimation method"""
    method: str  # e.g., "propensity_score_matching"
    effect: float  # The estimated causal effect
    confidence_interval: tuple[float, float]  # CI for the effect
    p_value: Optional[float] = None
    standard_error: Optional[float] = None
    sample_size: Optional[int] = None


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
    estimates: List[CausalEstimate]
    refutations: List[RefutationResult]
    confidence: float  # Overall confidence based on all analyses
    identified_estimand: Optional[str] = None  # The causal estimand
    graph: Optional[nx.DiGraph] = None  # The causal graph used
    
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
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate relationship values"""
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Strength must be between 0.0 and 1.0, got {self.strength}")