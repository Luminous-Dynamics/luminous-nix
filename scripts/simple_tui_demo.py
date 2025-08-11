#!/usr/bin/env python3
"""Simple working TUI demo for Nix for Humanity v1.1"""

import asyncio

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header, Input, RichLog, Static


class SimpleNixTUI(App):
    """A simple working TUI for Nix for Humanity"""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #input-area {
        height: 3;
        margin: 1 2;
    }
    
    #output-area {
        margin: 1 2;
        border: solid $primary;
    }
    
    .orb-container {
        height: 7;
        align: center middle;
        border: solid $success;
        margin: 1 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header(show_clock=True)

        # Simple consciousness orb
        yield Container(
            Static("🌟 Nix for Humanity v1.1 🌟", id="orb"), classes="orb-container"
        )

        # Main output area
        yield RichLog(id="output-area", highlight=True, markup=True)

        # Input area
        yield Container(
            Input(placeholder="Ask me anything about NixOS...", id="input"),
            id="input-area",
        )

        yield Footer()

    async def on_mount(self) -> None:
        """When app starts"""
        output = self.query_one("#output-area", RichLog)
        output.write(Text("🎉 Welcome to Nix for Humanity v1.1!", style="bold cyan"))
        output.write("")
        output.write("✨ Natural language interface for NixOS")
        output.write("💬 Type your questions below")
        output.write("🚀 Examples:")
        output.write("   - install firefox")
        output.write("   - find markdown editor")
        output.write("   - update my system")
        output.write("")

        # Focus on input
        input_widget = self.query_one("#input", Input)
        input_widget.focus()

    async def on_input_submitted(self, event) -> None:
        """Handle input submission"""
        input_widget = self.query_one("#input", Input)
        output = self.query_one("#output-area", RichLog)

        query = event.value.strip()
        if not query:
            return

        # Show user input
        output.write(Text(f"You: {query}", style="cyan"))

        # Clear input
        input_widget.value = ""

        # Simulate processing
        output.write(Text("🤔 Processing...", style="yellow"))
        await asyncio.sleep(0.5)

        # Simple responses
        if "install" in query.lower():
            output.write(Text("💡 To install a package:", style="green"))
            output.write(f"   nix-env -iA nixpkgs.{query.split()[-1]}")
            output.write("   Or add to configuration.nix")
        elif "find" in query.lower() or "search" in query.lower():
            output.write(Text("🔍 Searching packages...", style="green"))
            output.write(f"   nix search nixpkgs {' '.join(query.split()[1:])}")
        elif "update" in query.lower():
            output.write(Text("🔄 To update NixOS:", style="green"))
            output.write("   sudo nix-channel --update")
            output.write("   sudo nixos-rebuild switch")
        else:
            output.write(Text("🌟 Here's what I understand:", style="green"))
            output.write(f"   You want help with: {query}")
            output.write("   Try: 'install <package>' or 'find <description>'")

        output.write("")


if __name__ == "__main__":
    app = SimpleNixTUI()
    app.run()
