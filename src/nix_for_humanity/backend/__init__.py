"""
Backend module for Nix for Humanity

Provides the core backend implementations including the enhanced backend
with Error Intelligence integration.
"""

from .enhanced_backend import EnhancedBackend

__all__ = ['EnhancedBackend']