"""
Theme Definitions for Nix for Humanity TUI.

Beautiful color schemes and styling.

Since: v1.0.0
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Theme:
    """
    Theme definition for TUI.

    Since: v1.0.0
    """

    name: str
    colors: dict[str, str]
    styles: dict[str, Any]


# Sacred Theme - Mystical and consciousness-focused
SACRED_THEME = Theme(
    name="sacred",
    colors={
        "primary": "#9D4EDD",  # Purple
        "secondary": "#7209B7",  # Deep purple
        "accent": "#F72585",  # Pink
        "accent-light": "#F72585",  # Light pink
        "surface": "#10002B",  # Deep dark
        "surface-light": "#240046",  # Dark purple
        "text": "#E0AAFF",  # Light purple
        "success": "#06FFA5",  # Green
        "error": "#FF006E",  # Red
        "warning": "#FFBE0B",  # Yellow
        "info": "#3A86FF",  # Blue
    },
    styles={
        "border_style": "double",
        "padding": 1,
        "margin": 1,
    },
)

# Minimal Theme - Clean and focused
MINIMAL_THEME = Theme(
    name="minimal",
    colors={
        "primary": "#2E3440",  # Nord dark
        "secondary": "#3B4252",  # Nord gray
        "accent": "#88C0D0",  # Nord cyan
        "accent-light": "#8FBCBB",  # Nord light cyan
        "surface": "#2E3440",  # Nord dark
        "surface-light": "#434C5E",  # Nord light dark
        "text": "#ECEFF4",  # Nord white
        "success": "#A3BE8C",  # Nord green
        "error": "#BF616A",  # Nord red
        "warning": "#EBCB8B",  # Nord yellow
        "info": "#5E81AC",  # Nord blue
    },
    styles={
        "border_style": "solid",
        "padding": 1,
        "margin": 0,
    },
)

# Accessible Theme - High contrast for visibility
ACCESSIBLE_THEME = Theme(
    name="accessible",
    colors={
        "primary": "#000000",  # Black
        "secondary": "#333333",  # Dark gray
        "accent": "#0066CC",  # Blue
        "accent-light": "#3399FF",  # Light blue
        "surface": "#FFFFFF",  # White
        "surface-light": "#F5F5F5",  # Light gray
        "text": "#000000",  # Black
        "success": "#008000",  # Green
        "error": "#CC0000",  # Red
        "warning": "#FF8800",  # Orange
        "info": "#0066CC",  # Blue
    },
    styles={
        "border_style": "thick",
        "padding": 2,
        "margin": 1,
    },
)
