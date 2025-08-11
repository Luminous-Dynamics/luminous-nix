"""
🌟 TUI Frontend for Nix for Humanity

Beautiful terminal interface with consciousness orb visualization.
Uses the unified backend for all operations.
"""

import asyncio
import math
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widgets import Button, Footer, Header, Input, RichLog, Static

from ..core.unified_backend import Context, NixForHumanityBackend, get_backend
from ..plugins.config_generator import ConfigGeneratorPlugin, SmartSearchPlugin


class ConsciousnessOrb(Static):
    """
    🔮 The consciousness orb - visual representation of system state

    Pulses with life, changes color based on activity.
    """

    phase = reactive(0.0)
    activity = reactive("idle")

    RENDER_STATES = {
        "idle": ("🔮", "cyan"),
        "thinking": ("🌟", "yellow"),
        "executing": ("⚡", "green"),
        "error": ("❌", "red"),
        "success": ("✨", "bright_green"),
    }

    def on_mount(self) -> None:
        """Start the consciousness animation"""
        self.update_timer = self.set_interval(0.1, self.animate)

    def animate(self) -> None:
        """Animate the orb's pulsing"""
        self.phase += 0.1
        if self.phase > 2 * math.pi:
            self.phase = 0
        self.refresh()

    def compose(self) -> ComposeResult:
        """Compose the orb visualization"""
        yield Static("", id="orb-visual")

    def render(self) -> str:
        """Render the consciousness orb"""
        symbol, color = self.RENDER_STATES.get(self.activity, ("🔮", "cyan"))

        # Create pulsing effect
        intensity = abs(math.sin(self.phase))
        padding = " " * int(3 * intensity)

        # Multi-line orb visualization
        orb_lines = [
            "╭─────────────╮",
            f"│{padding}{symbol}{padding}│",
            "│ Consciousness│",
            "╰─────────────╯",
        ]

        # Apply color based on state
        colored_orb = f"[{color}]" + "\n".join(orb_lines) + "[/]"

        return colored_orb

    def set_activity(self, state: str) -> None:
        """Update the orb's activity state"""
        self.activity = state


class CommandHistory(RichLog):
    """Scrollable command history with rich formatting"""

    def add_command(self, command: str) -> None:
        """Add a command to history"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write(f"[dim]{timestamp}[/] [bold cyan]>[/] {command}")

    def add_result(self, result: str, success: bool = True) -> None:
        """Add a result to history"""
        color = "green" if success else "red"
        self.write(f"[{color}]{result}[/]")
        self.write("")  # Empty line for spacing


class NixForHumanityTUI(App):
    """
    🕉️ The Sacred TUI - Beautiful terminal interface

    Features:
    - Consciousness orb visualization
    - Natural language input
    - Rich command history
    - Real-time feedback
    - Plugin-powered features
    """

    CSS = """
    Screen {
        background: $surface;
    }

    #orb-container {
        width: 20;
        height: 6;
        border: solid cyan;
        margin: 1;
    }

    #input-container {
        height: 3;
        margin: 1;
    }

    #history-container {
        border: solid $primary;
        margin: 1;
    }

    #status-bar {
        height: 1;
        background: $accent;
        color: $text;
        padding: 0 1;
    }

    CommandHistory {
        padding: 1;
    }

    Input {
        margin: 0 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear_history", "Clear"),
        ("f1", "show_help", "Help"),
        ("f2", "toggle_dry_run", "Toggle Dry Run"),
    ]

    def __init__(self):
        super().__init__()
        self.backend: NixForHumanityBackend | None = None
        self.context = Context(user_id="tui_user")
        self.dry_run = True

    async def on_mount(self) -> None:
        """Initialize when TUI is mounted"""
        # Setup backend
        self.backend = get_backend({"dry_run": self.dry_run})
        self.backend.register_plugin(ConfigGeneratorPlugin())
        self.backend.register_plugin(SmartSearchPlugin())
        await self.backend.initialize()

        # Update status
        self.update_status("Ready")

    def compose(self) -> ComposeResult:
        """Compose the TUI layout"""
        yield Header(show_clock=True)

        with Container():
            # Top section with orb and status
            with Horizontal():
                with Container(id="orb-container"):
                    yield ConsciousnessOrb(id="consciousness-orb")

                with Vertical():
                    yield Static(
                        "🕉️ [bold cyan]Nix for Humanity[/] - Natural Language NixOS\n"
                        "Type your request in natural language below.",
                        id="title",
                    )
                    yield Static(
                        f"Mode: [yellow]{'DRY RUN' if self.dry_run else 'EXECUTE'}[/]",
                        id="status-bar",
                    )

            # Command history
            with ScrollableContainer(id="history-container"):
                yield CommandHistory(id="history", highlight=True, markup=True)

            # Input section
            with Container(id="input-container"):
                with Horizontal():
                    yield Input(
                        placeholder="Enter natural language command...",
                        id="command-input",
                    )
                    yield Button("Execute", variant="primary", id="execute-btn")

        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        await self.execute_command(event.value)
        event.input.value = ""

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "execute-btn":
            input_widget = self.query_one("#command-input", Input)
            if input_widget.value:
                await self.execute_command(input_widget.value)
                input_widget.value = ""

    async def execute_command(self, command: str) -> None:
        """Execute a natural language command"""
        if not command.strip():
            return

        # Update UI state
        orb = self.query_one("#consciousness-orb", ConsciousnessOrb)
        history = self.query_one("#history", CommandHistory)

        # Add command to history
        history.add_command(command)

        # Update orb state
        orb.set_activity("thinking")

        try:
            # Execute through backend
            self.backend.config["dry_run"] = self.dry_run
            orb.set_activity("executing")

            result = await self.backend.execute(command, self.context)

            # Display result
            if result.success:
                orb.set_activity("success")
                if result.output:
                    # Format output nicely
                    output_lines = result.output.split("\n")
                    for line in output_lines:
                        if line.strip():
                            history.add_result(line, success=True)
                else:
                    history.add_result("✅ Command executed successfully", success=True)
            else:
                orb.set_activity("error")
                history.add_result(f"❌ Error: {result.error}", success=False)
                if result.suggestions:
                    history.add_result("💡 Suggestions:", success=True)
                    for suggestion in result.suggestions:
                        history.add_result(f"  • {suggestion}", success=True)

            # Reset orb after delay
            await asyncio.sleep(2)
            orb.set_activity("idle")

        except Exception as e:
            orb.set_activity("error")
            history.add_result(f"❌ Unexpected error: {str(e)}", success=False)
            await asyncio.sleep(2)
            orb.set_activity("idle")

    def action_clear_history(self) -> None:
        """Clear command history"""
        history = self.query_one("#history", CommandHistory)
        history.clear()
        history.write("[dim]History cleared[/]")

    def action_toggle_dry_run(self) -> None:
        """Toggle between dry run and execute modes"""
        self.dry_run = not self.dry_run
        status = self.query_one("#status-bar", Static)
        mode_text = "DRY RUN" if self.dry_run else "EXECUTE"
        color = "yellow" if self.dry_run else "red"
        status.update(f"Mode: [{color}]{mode_text}[/]")

        history = self.query_one("#history", CommandHistory)
        history.add_result(f"🔄 Switched to {mode_text} mode", success=True)

    def action_show_help(self) -> None:
        """Show help information"""
        history = self.query_one("#history", CommandHistory)
        help_text = """
[bold cyan]Available Commands:[/]
• "install [package]" - Install a package
• "search for [description]" - Smart search by description
• "web server with [services]" - Generate configuration
• "list packages" - List installed packages
• "update system" - Update NixOS

[bold cyan]Keyboard Shortcuts:[/]
• F1 - Show this help
• F2 - Toggle dry run mode
• Ctrl+L - Clear history
• Q or Ctrl+C - Quit
        """
        history.write(help_text)

    def update_status(self, message: str) -> None:
        """Update status bar message"""
        status = self.query_one("#status-bar", Static)
        mode_text = "DRY RUN" if self.dry_run else "EXECUTE"
        color = "yellow" if self.dry_run else "red"
        status.update(f"Mode: [{color}]{mode_text}[/] | {message}")

    async def on_unmount(self) -> None:
        """Cleanup on exit"""
        if self.backend:
            await self.backend.cleanup()


def run():
    """Run the TUI application"""
    app = NixForHumanityTUI()
    app.run()


if __name__ == "__main__":
    run()
