"""
Explainable AI (XAI) module for Nix for Humanity
Provides causal explanations for AI decisions
"""

from .causal_engine import (
    CausalXAI,
    ExplanationLevel,
    CausalExplanation,
    ConfidenceLevel,
    DecisionNode,
    CausalGraph,
)
from .explanation_formatter import (
    ExplanationFormatter,
    PersonaExplanationAdapter,
)
from .confidence_calculator import (
    ConfidenceCalculator,
    ConfidenceMetrics,
)

__all__ = [
    # Core engine
    'CausalXAI',
    'ExplanationLevel',
    'CausalExplanation',
    'ConfidenceLevel',
    'DecisionNode',
    'CausalGraph',
    
    # Formatting
    'ExplanationFormatter',
    'PersonaExplanationAdapter',
    
    # Confidence
    'ConfidenceCalculator',
    'ConfidenceMetrics',
]