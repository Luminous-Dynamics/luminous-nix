# AI Enhancement Module
"""
Advanced AI features for Nix for Humanity including:
- Explainable AI (XAI) for transparent decision making
- Advanced learning systems with DPO/LoRA capabilities
- Symbiotic intelligence framework
"""

from .xai_engine import (
    XAIEngine,
    Explanation,
    CausalFactor,
    ExplanationLevel,
    ConfidenceLevel,
    create_causal_factor,
    analyze_intent_recognition
)

from .advanced_learning import (
    AdvancedLearningSystem,
    LearningMode,
    PreferencePair,
    LearningMetrics
)

__all__ = [
    'XAIEngine',
    'Explanation', 
    'CausalFactor',
    'ExplanationLevel',
    'ConfidenceLevel',
    'create_causal_factor',
    'analyze_intent_recognition',
    'AdvancedLearningSystem',
    'LearningMode',
    'PreferencePair',
    'LearningMetrics'
]