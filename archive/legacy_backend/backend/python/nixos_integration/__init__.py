"""
NixOS Python Backend Integration for Nix for Humanity

This package provides:
- Direct Python API integration with nixos-rebuild (NixOS 25.11+)
- Intelligent fallback to subprocess for older versions
- Real-time progress callbacks
- Natural language processing integration
- Learning and caching systems
"""

from .nixos_python_backend import (
    NixOSPythonBackend,
    HybridNixOSBackend,
    Action,
    BuildResult
)

from .nix_humanity_integration import (
    NixForHumanityBackend
)

__all__ = [
    'NixOSPythonBackend',
    'HybridNixOSBackend', 
    'NixForHumanityBackend',
    'Action',
    'BuildResult'
]

__version__ = '0.5.0'