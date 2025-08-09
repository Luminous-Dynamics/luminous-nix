"""
Causal XAI Engine for Nix for Humanity

Provides transparent explanations for AI decisions using causal inference.
"""

from .engine import CausalXAIEngine
from .models import (
    ExplanationLevel,
    CausalFactor,
    Decision,
    Explanation,
    CausalEffects
)
from .builder import CausalModelBuilder
from .inference import CausalInferenceEngine
from .explainer import ExplanationGenerator
from .knowledge_base import CausalKnowledgeBase

__all__ = [
    'CausalXAIEngine',
    'ExplanationLevel',
    'CausalFactor',
    'Decision',
    'Explanation',
    'CausalEffects',
    'CausalModelBuilder',
    'CausalInferenceEngine',
    'ExplanationGenerator',
    'CausalKnowledgeBase'
]

__version__ = '0.1.0'