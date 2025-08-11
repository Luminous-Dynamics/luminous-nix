"""
Nix for Humanity UI Module - Consciousness-First Terminal Interface
"""

# Only import TUI components if textual is available
try:
    from textual import __version__

    TEXTUAL_AVAILABLE = True
    from .adaptive_interface import AdaptiveInterface
    from .consciousness_orb import ConsciousnessOrb
    from .main_app import NixForHumanityTUI

    __all__ = [
        "ConsciousnessOrb",
        "AdaptiveInterface",
        "NixForHumanityTUI",
        "Spinner",
        "ProgressBar",
        "PhaseProgress",
    ]
except ImportError:
    TEXTUAL_AVAILABLE = False
    __all__ = ["Spinner", "ProgressBar", "PhaseProgress"]

# Always available progress indicators (no external deps)
from .progress import PhaseProgress, ProgressBar, Spinner
