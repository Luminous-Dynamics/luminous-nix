"""
DEPRECATED: Backend compatibility layer - redirects to consolidated_backend.py

This file is kept for backward compatibility only.
All functionality has been moved to consolidated_backend.py
"""

import warnings

# Import from the consolidated backend
from .consolidated_backend import (
    ConsolidatedBackend as NixForHumanityBackend,
    get_backend as create_backend,
    Request,
    Response,
    Intent,
    IntentType
)

# Show deprecation warning
warnings.warn(
    "backend.py is deprecated. Use consolidated_backend.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# For backward compatibility
Backend = NixForHumanityBackend

__all__ = ["Backend", "NixForHumanityBackend", "create_backend"]
