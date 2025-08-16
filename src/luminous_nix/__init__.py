"""
Nix for Humanity - Making NixOS accessible through natural conversation.

A revolutionary AI partner that transforms NixOS from command-line complexity
into natural conversation. Consciousness-first design with local-first privacy.
"""

__version__ = "1.3.0"
__author__ = "Tristan Stoltz"
__email__ = "tristan.stoltz@gmail.com"

# Core exports
# API exports
from luminous_nix.api.schema import Request, Response, Result
from luminous_nix.core.backend import NixForHumanityBackend
from luminous_nix.core.executor import SafeExecutor
from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.core.knowledge import KnowledgeBase
from luminous_nix.core.personality import PersonalityManager, PersonalityStyle


# Helper function
def create_backend():
    """Create a new backend instance."""
    return NixForHumanityBackend()


__all__ = [
    # Version
    "__version__",
    # Core classes
    "NixForHumanityBackend",
    "create_backend",
    "Intent",
    "IntentType",
    "SafeExecutor",
    "KnowledgeBase",
    "PersonalityManager",
    "PersonalityStyle",
    # API types
    "Request",
    "Response",
    "Result",
]

# Package metadata
__doc__ = """
Nix for Humanity makes NixOS accessible to everyone through natural language.

Key Features:
- Natural language understanding for NixOS commands
- 10 adaptive personality styles
- Local-first privacy with all processing on-device
- Revolutionary Python-Nix integration (10x-1500x faster)
- Beautiful TUI with Textual
- Voice interface support
- Consciousness-first design

Usage:
    from luminous_nix import create_backend

    backend = create_backend()
    response = backend.process(Request(query="install firefox"))
    print(response.text)
"""
