"""
Causal XAI Engine for Nix for Humanity

Provides transparent explanations for AI decisions using causal inference.
"""

from .builder import CausalModelBuilder
from .engine import CausalXAIEngine
from .explainer import ExplanationGenerator
from .inference import CausalInferenceEngine
from .knowledge_base import CausalKnowledgeBase
from .models import CausalEffects, CausalFactor, Decision, Explanation, ExplanationLevel

__all__ = [
    "CausalXAIEngine",
    "ExplanationLevel",
    "CausalFactor",
    "Decision",
    "Explanation",
    "CausalEffects",
    "CausalModelBuilder",
    "CausalInferenceEngine",
    "ExplanationGenerator",
    "CausalKnowledgeBase",
]

__version__ = "0.1.0"
