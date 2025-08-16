"""
Terminal User Interface for Nix for Humanity.

Provides a rich, interactive terminal interface using Textual framework.
Features real-time search, command history, progress visualization,
and educational tooltips.

Since: v1.0.0
"""

from .app import NixForHumanityTUI, run_tui
from .widgets import CommandInput, HelpPanel, HistoryPanel, ResultsPanel, StatusBar

__all__ = [
    "NixForHumanityTUI",
    "run_tui",
    "CommandInput",
    "ResultsPanel",
    "HistoryPanel",
    "StatusBar",
    "HelpPanel",
]
