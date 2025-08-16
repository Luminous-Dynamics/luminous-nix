"""
Backend compatibility layer - redirects to engine.py

This file provides backward compatibility for old imports.
All functionality is implemented in engine.py
"""

import warnings

# Import from the engine (the actual backend implementation)
from .engine import (
    NixForHumanityBackend,
    get_backend,
    create_backend,
)

# Import common types
from luminous_nix.api.schema import Request, Response
from .intents import Intent, IntentType

# Show deprecation warning
warnings.warn(
    "backend.py is deprecated. Use consolidated_backend.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility
Backend = NixForHumanityBackend

__all__ = ["Backend", "NixForHumanityBackend", "create_backend"]
