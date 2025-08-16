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

from luminous_nix.api.schema import Context, Response
from luminous_nix.service_simple import LuminousNixService, ServiceOptions
from .voice_widget import VoiceInterfaceWidget, VoiceState


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
        ("f3", "toggle_voice", "Toggle Voice"),
        ("v", "start_voice", "Voice Input"),
    ]

    def __init__(self):
        super().__init__()
        self.service: LuminousNixService | None = None
        self.dry_run = True
        self.voice_enabled = False
        self.voice_widget = None

    async def on_mount(self) -> None:
        """Initialize when TUI is mounted"""
        # Setup service layer
        options = ServiceOptions(
            execute=not self.dry_run,
            interface="tui",
            verbose=False
        )
        self.service = LuminousNixService(options)
        await self.service.initialize()

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

            # Voice interface widget (initially hidden)
            self.voice_widget = VoiceInterfaceWidget(id="voice-widget")
            self.voice_widget.display = False  # Hidden by default
            yield self.voice_widget

            # Input section
            with Container(id="input-container"):
                with Horizontal():
                    yield Input(
                        placeholder="Enter natural language command... (Press 'V' for voice)",
                        id="command-input",
                    )
                    yield Button("Execute", variant="primary", id="execute-btn")
                    yield Button("🎤 Voice", variant="success", id="voice-btn")

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
        elif event.button.id == "voice-btn":
            await self.action_start_voice()

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
            # Execute through service layer
            orb.set_activity("executing")
            
            # Update service options if dry_run changed
            self.service.options.execute = not self.dry_run

            result = await self.service.execute_command(command)

            # Display result
            if result.success:
                orb.set_activity("success")
                if result.text:
                    # Format output nicely
                    output_lines = result.text.split("\n")
                    for line in output_lines:
                        if line.strip():
                            history.add_result(line, success=True)
                else:
                    history.add_result("✅ Command executed successfully", success=True)
            else:
                orb.set_activity("error")
                error_msg = result.text or "Unknown error"
                history.add_result(f"❌ Error: {error_msg}", success=False)
                # Check for suggestions in data
                if result.data and "suggestions" in result.data:
                    history.add_result("💡 Suggestions:", success=True)
                    for suggestion in result.data["suggestions"]:
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

    def action_toggle_voice(self) -> None:
        """Toggle voice interface visibility"""
        if self.voice_widget:
            self.voice_enabled = not self.voice_enabled
            self.voice_widget.display = self.voice_enabled
            
            history = self.query_one("#history", CommandHistory)
            if self.voice_enabled:
                history.add_result("🎤 Voice interface enabled", success=True)
                self.voice_widget.on_voice_state_change(VoiceState.IDLE)
            else:
                history.add_result("🔇 Voice interface disabled", success=True)
                self.voice_widget.stop_listening()

    async def action_start_voice(self) -> None:
        """Start voice input"""
        if not self.voice_widget:
            return
            
        # Enable voice if not already
        if not self.voice_enabled:
            self.action_toggle_voice()
        
        # Start listening
        self.voice_widget.start_listening()
        
        # Simulate voice input for demo
        history = self.query_one("#history", CommandHistory)
        history.add_result("🎤 Listening... (Demo mode - say 'install firefox')", success=True)
        
        # Simulate a voice command after a delay
        await asyncio.sleep(2)
        self.voice_widget.on_transcription("install firefox", is_user=True)
        await self.execute_command("install firefox")
        self.voice_widget.stop_listening()

    async def on_unmount(self) -> None:
        """Cleanup on exit"""
        if self.service:
            await self.service.cleanup()
        if self.voice_widget:
            self.voice_widget.stop_listening()


def run():
    """Run the TUI application"""
    app = NixForHumanityTUI()
    app.run()


def run_tui():
    """Alias for run() to match expected interface"""
    run()


if __name__ == "__main__":
    run()
