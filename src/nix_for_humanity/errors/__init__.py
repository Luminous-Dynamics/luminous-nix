"""
Error handling module for Nix for Humanity
"""

from .intelligent_errors import (
    ErrorContext,
    ErrorEducator,
    IntelligentErrorHandler,
    get_error_educator,
)

__all__ = [
    "ErrorContext",
    "IntelligentErrorHandler",
    "ErrorEducator",
    "get_error_educator",
]
