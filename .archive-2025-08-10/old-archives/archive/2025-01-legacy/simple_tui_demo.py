#!/usr/bin/env python3
"""Simple TUI demo that works without all dependencies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from datetime import datetime

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.widgets import Footer, Header, Input, Label, Static


class SimpleResponse(Static):
    """Simple response display."""

    def __init__(self, query: str, response: str):
        super().__init__()
        self.query = query
        self.response = response

    def render(self) -> Text:
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append(f"Q: {self.query}\n", style="bold cyan")
        text.append(f"A: {self.response}\n", style="green")
        return text


class SimpleTUI(App):
    """Simplified Nix for Humanity TUI Demo."""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #input-container {
        height: 3;
        dock: bottom;
        margin: 1;
    }
    
    #responses {
        margin: 1;
        overflow-y: scroll;
    }
    
    SimpleResponse {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear", "Clear"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("🌟 Nix for Humanity v1.1 - TUI Demo", id="title"),
            Container(id="responses"),
            id="main",
        )
        yield Container(
            Input(placeholder="Ask me anything about NixOS...", id="input"),
            id="input-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus input on mount."""
        self.query_one("#input").focus()

    def on_input_submitted(self, event) -> None:
        """Handle input submission."""
        input_widget = self.query_one("#input", Input)
        query = event.value.strip()

        if query:
            # Simple mock responses
            response = self.get_mock_response(query)

            # Add to display
            responses = self.query_one("#responses", Container)
            responses.mount(SimpleResponse(query, response))

            # Clear input
            input_widget.value = ""

            # Scroll to bottom
            responses.scroll_end(animate=True)

    def get_mock_response(self, query: str) -> str:
        """Get a mock response for demo."""
        query_lower = query.lower()

        if "install" in query_lower:
            if "firefox" in query_lower:
                return "✅ Command: nix-env -iA nixos.firefox\n📦 Firefox will be installed system-wide"
            if "vim" in query_lower:
                return (
                    "✅ Command: nix-env -iA nixos.vim\n📝 Vim editor will be installed"
                )
            return "💡 To install packages, use: nix-env -iA nixos.[package-name]"

        if "search" in query_lower:
            return "🔍 Use: nix search nixpkgs [term]\n💡 Example: nix search nixpkgs markdown"

        if "update" in query_lower:
            return "🔄 Commands:\n  • Update channel: sudo nix-channel --update\n  • Update system: sudo nixos-rebuild switch"

        if "help" in query_lower:
            return "📚 Available commands:\n  • install [package]\n  • search [term]\n  • update system\n  • list installed\n  • remove [package]"

        return f"🤔 I understand you want to: {query}\n💡 Try asking about installing, searching, or updating packages!"

    def action_clear(self) -> None:
        """Clear the response area."""
        responses = self.query_one("#responses", Container)
        responses.remove_children()

    def action_quit(self) -> None:
        """Quit the app."""
        self.exit()


if __name__ == "__main__":
    app = SimpleTUI()
    app.run()
