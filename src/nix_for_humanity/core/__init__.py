# Core Engine Module
"""
The headless core engine that powers all Nix for Humanity interfaces
"""

from .engine import NixForHumanityCore
from .interface import Query, ExecutionMode
from .planning import Plan
from .personality_system import PersonalityStyle

# Import the standardized types (using types.py as single source of truth)
from .types import (
    Request,
    Response,
    Context,
    Intent,
    IntentType,
    ExecutionResult,
    Command,
    Package,
    FeedbackItem,
    CommandList,
    PackageList,
    ErrorMessage
)

__all__ = [
    # Core engine
    "NixForHumanityCore",
    
    # Request/Response types
    "Request",
    "Response", 
    "Context",
    
    # Domain types
    "Intent",
    "IntentType",
    "Command",
    "ExecutionMode",
    "Plan",
    "ExecutionResult",
    "Package",
    "FeedbackItem",
    
    # Type aliases
    "CommandList",
    "PackageList",
    "ErrorMessage",
    
    # Other
    "Query",
    "PersonalityStyle"
]