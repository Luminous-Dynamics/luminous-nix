"""
Nix for Humanity Backend
========================

Unified Python backend serving multiple frontend adapters.
This backend provides direct integration with nixos-rebuild-ng API.
"""

__version__ = "0.1.0"
__author__ = "Luminous Dynamics"

from .core.backend import NixForHumanityBackend
from .api.schema import Request, Response, Context

__all__ = ["NixForHumanityBackend", "Request", "Response", "Context"]