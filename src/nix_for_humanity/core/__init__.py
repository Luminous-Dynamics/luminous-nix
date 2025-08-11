"""
v1.0 exports - Core functionality only
"""

# v1.0 components
from nix_for_humanity.core.error_handler import ErrorHandler
from nix_for_humanity.core.intents import Intent, IntentRecognizer, IntentType

from .backend import NixForHumanityBackend
from .executor import SafeExecutor
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
