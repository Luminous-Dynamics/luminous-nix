"""
Core module - v1.3.0+ Consolidated Backend
"""

# Import from the new consolidated backend (single source of truth)
from .consolidated_backend import (
    ConsolidatedBackend,
    NixForHumanityBackend,  # Alias for compatibility
    get_backend,
    create_backend,
    Intent,
    IntentType,
    Request,
    Response
)

# Keep other imports for compatibility
from .executor import SafeExecutor
from .knowledge import KnowledgeBase
from .personality import PersonalityManager as PersonalitySystem
from .error_handler import ErrorHandler
from .intents import IntentRecognizer  # Keep for compatibility

# Alias for backward compatibility
Backend = ConsolidatedBackend

__all__ = [
    # Main backend (single implementation)
    "ConsolidatedBackend",
    "NixForHumanityBackend",  # Alias
    "Backend",  # Alias
    "get_backend",
    "create_backend",
    # Types
    "Intent",
    "IntentType",
    "IntentRecognizer",  # Keep for compatibility
    "Request",
    "Response",
    # Other components
    "SafeExecutor",
    "KnowledgeBase",
    "ErrorHandler",
    "PersonalitySystem",
]
