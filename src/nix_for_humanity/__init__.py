# Nix for Humanity - Core Package
"""
Nix for Humanity: Natural language interface for NixOS
Making NixOS accessible through conversation
"""

__version__ = "0.9.0"
__author__ = "Luminous Dynamics"

from .core import NixForHumanityCore
from .core.interface import Query
from .core.types import Response

__all__ = ["NixForHumanityCore", "Query", "Response"]