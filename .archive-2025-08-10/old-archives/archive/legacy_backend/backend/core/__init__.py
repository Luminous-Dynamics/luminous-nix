"""
v1.0 exports - Core functionality only
"""

# v1.0 components
from .backend import NixForHumanityBackend
from .error_handler import ErrorHandler
from .executor import SafeExecutor
from .intents import Intent, IntentRecognizer, IntentType
from .knowledge import KnowledgeBase
from .personality import PersonalityManager as PersonalitySystem

__all__ = [
    "NixForHumanityBackend",
    "IntentRecognizer",
    "Intent",
    "IntentType",
    "SafeExecutor",
    "KnowledgeBase",
    "ErrorHandler",
    "PersonalitySystem",
]
