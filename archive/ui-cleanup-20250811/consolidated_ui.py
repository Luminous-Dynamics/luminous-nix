"""
Consolidated UI Module for Nix for Humanity v1.3.0+

This single module replaces all duplicate UI implementations:
- main_app.py
- enhanced_main_app.py
- enhanced_main_app_with_demo.py
- enhanced_tui.py
- All other UI variants

Design Principles:
- One UI to rule them all
- Modular features via configuration
- < 500ms startup time
- Clean, maintainable code
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

# Use try/except for optional dependencies
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import Button, Header, Footer, Input, Static, Label
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    # Provide dummy classes for import compatibility
    class App:
        pass
    class ComposeResult:
        pass


@dataclass
class UIConfig:
    """Configuration for the unified UI."""
    show_consciousness_orb: bool = False  # Disable fancy features by default
    show_voice_widget: bool = False
    show_demo_mode: bool = False
    theme: str = "default"
    startup_message: str = "Welcome to Nix for Humanity"


class ConsolidatedUI(App if TEXTUAL_AVAILABLE else object):
    """
    The ONE unified UI implementation.
    
    Features:
    - Clean, simple interface
    - Optional consciousness orb (disabled by default)
    - Optional voice widget (disabled by default)
    - Fast startup (< 500ms)
    - Modular configuration
    """
    
    CSS = """
    #input-area {
        height: 3;
        margin: 1;
    }
    
    #output-area {
        border: solid green;
        height: 100%;
        margin: 1;
        padding: 1;
    }
    
    .button {
        margin: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("h", "help", "Help"),
        Binding("c", "clear", "Clear"),
    ]
    
    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize the consolidated UI."""
        super().__init__()
        self.config = config or UIConfig()
        self.output_lines: List[str] = []
        
        # Import backend lazily
        from ..core.consolidated_backend import get_backend
        self.backend = get_backend()
    
    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        if not TEXTUAL_AVAILABLE:
            return
        
        yield Header()
        
        with Container():
            # Main output area
            yield Static(
                self.config.startup_message,
                id="output-area"
            )
            
            # Input area
            with Horizontal():
                yield Input(
                    placeholder="Enter command (e.g., 'install firefox')",
                    id="input-area"
                )
                yield Button("Execute", variant="primary", id="execute-btn")
                
                # Optional features based on config
                if self.config.show_voice_widget:
                    yield Button("🎤 Voice", id="voice-btn")
        
        yield Footer()
    
    async def on_input_submitted(self, event) -> None:
        """Handle input submission."""
        query = event.value
        if not query:
            return
        
        # Clear input
        event.input.value = ""
        
        # Process with backend
        await self.process_command(query)
    
    async def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id == "execute-btn":
            input_widget = self.query_one("#input-area", Input)
            query = input_widget.value
            if query:
                input_widget.value = ""
                await self.process_command(query)
        elif event.button.id == "voice-btn":
            await self.handle_voice_input()
    
    async def process_command(self, query: str) -> None:
        """Process a command through the backend."""
        from ..core.consolidated_backend import Request
        
        # Add to output
        self.add_output(f"> {query}")
        
        # Create request
        request = Request(query=query, dry_run=True)
        
        # Process with backend
        try:
            response = await self.backend.process_async(request)
            
            if response.success:
                self.add_output(f"✅ {response.message}")
                if response.data:
                    for key, value in response.data.items():
                        if isinstance(value, list) and len(value) <= 5:
                            self.add_output(f"  {key}: {', '.join(map(str, value))}")
            else:
                self.add_output(f"❌ {response.message}")
                if response.suggestions:
                    self.add_output("Suggestions:")
                    for suggestion in response.suggestions:
                        self.add_output(f"  • {suggestion}")
        except Exception as e:
            self.add_output(f"❌ Error: {str(e)}")
    
    def add_output(self, text: str) -> None:
        """Add text to output area."""
        self.output_lines.append(text)
        
        # Keep only last 100 lines for performance
        if len(self.output_lines) > 100:
            self.output_lines = self.output_lines[-100:]
        
        # Update display
        output_widget = self.query_one("#output-area", Static)
        output_widget.update("\n".join(self.output_lines))
    
    async def handle_voice_input(self) -> None:
        """Handle voice input (stub for now)."""
        self.add_output("🎤 Voice input not implemented in consolidated UI")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_help(self) -> None:
        """Show help."""
        help_text = """
Commands:
  install <package>  - Install a package
  remove <package>   - Remove a package
  search <term>      - Search for packages
  list               - List installed packages
  help               - Show this help
  quit               - Exit application

Shortcuts:
  q - Quit
  h - Help  
  c - Clear output
"""
        self.add_output(help_text)
    
    def action_clear(self) -> None:
        """Clear the output."""
        self.output_lines = []
        self.add_output(self.config.startup_message)


class SimpleCLI:
    """
    Simple CLI interface when Textual is not available.
    
    This provides a basic REPL for environments without TUI support.
    """
    
    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize the simple CLI."""
        self.config = config or UIConfig()
        
        # Import backend lazily
        from ..core.consolidated_backend import get_backend, Request
        self.backend = get_backend()
        self.Request = Request
    
    def run(self) -> None:
        """Run the simple CLI loop."""
        print(self.config.startup_message)
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                query = input("> ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                
                if query.lower() == "help":
                    self.show_help()
                    continue
                
                # Process command
                self.process_command(query)
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                break
    
    def process_command(self, query: str) -> None:
        """Process a command through the backend."""
        request = self.Request(query=query, dry_run=True)
        
        try:
            response = self.backend.process(request)
            
            if response.success:
                print(f"✅ {response.message}")
                if response.data and "packages" in response.data:
                    packages = response.data["packages"][:10]  # Limit output
                    if packages:
                        print(f"   Packages: {', '.join(packages)}")
            else:
                print(f"❌ {response.message}")
                if response.suggestions:
                    print("Suggestions:")
                    for suggestion in response.suggestions:
                        print(f"  • {suggestion}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def show_help(self) -> None:
        """Show help message."""
        print("""
Commands:
  install <package>  - Install a package
  remove <package>   - Remove a package
  search <term>      - Search for packages
  list               - List installed packages
  help               - Show this help
  quit               - Exit application
""")


def create_ui(config: Optional[UIConfig] = None) -> Any:
    """
    Factory function to create the appropriate UI.
    
    Returns ConsolidatedUI if Textual is available,
    otherwise returns SimpleCLI.
    """
    if TEXTUAL_AVAILABLE:
        return ConsolidatedUI(config)
    else:
        return SimpleCLI(config)


def run_ui(config: Optional[UIConfig] = None) -> None:
    """
    Run the appropriate UI based on availability.
    """
    ui = create_ui(config)
    
    if isinstance(ui, SimpleCLI):
        ui.run()
    else:
        ui.run()


# Compatibility exports for old imports
def main_app():
    """Compatibility function for old main_app imports."""
    run_ui()

def enhanced_main_app():
    """Compatibility function for old enhanced_main_app imports."""
    config = UIConfig(show_consciousness_orb=True)
    run_ui(config)

def enhanced_tui():
    """Compatibility function for old enhanced_tui imports."""
    config = UIConfig(show_consciousness_orb=True, show_voice_widget=True)
    run_ui(config)


__all__ = [
    "ConsolidatedUI",
    "SimpleCLI",
    "UIConfig",
    "create_ui",
    "run_ui",
    # Compatibility exports
    "main_app",
    "enhanced_main_app",
    "enhanced_tui",
]