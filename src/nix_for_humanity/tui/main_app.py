"""
Main TUI Application for Nix for Humanity
Beautiful, accessible terminal interface with screen reader support
"""

from typing import Optional, List, Dict, Any
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label
from textual.reactive import reactive
from textual.binding import Binding
from textual import events
from textual.message import Message
import asyncio

from .accessible_widgets import (
    AccessibleButton,
    AccessibleInput,
    AccessibleList,
    AccessibleNotification,
    create_accessible_widget
)
from ..accessibility import (
    ScreenReaderSupport,
    AriaLivePriority,
    PersonaAccessibilityAdapter,
    PersonaType,
    get_persona_accessibility_settings
)


class CommandResponse(Message):
    """Message sent when a command produces a response"""
    def __init__(self, command: str, response: str, success: bool = True):
        super().__init__()
        self.command = command
        self.response = response
        self.success = success


class NixForHumanityApp(App):
    """Main TUI application for Nix for Humanity"""
    
    CSS_PATH = "styles.css"  # We'll define styles separately
    
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+h", "help", "Help", show=True),
        Binding("ctrl+t", "toggle_theme", "Theme", show=True),
        Binding("ctrl+p", "change_persona", "Persona", show=True),
        Binding("ctrl+r", "toggle_screen_reader", "Screen Reader", show=False),
        Binding("f1", "show_shortcuts", "Shortcuts", show=True),
    ]
    
    # Reactive properties
    current_persona = reactive(PersonaType.GRANDMA_ROSE)
    screen_reader_enabled = reactive(True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize accessibility components
        self.screen_reader = ScreenReaderSupport()
        self.persona_adapter = PersonaAccessibilityAdapter()
        self.persona_adapter.set_persona(self.current_persona)
        
        # Command history
        self.command_history: List[Dict[str, Any]] = []
        self.history_index = -1
        
        # Set up keyboard navigation
        self._setup_keyboard_navigation()
    
    def _setup_keyboard_navigation(self):
        """Set up keyboard navigation for accessibility"""
        # Register skip links
        self.screen_reader.keyboard_nav.register_skip_link(
            '1', 'main_input', 'Main command input'
        )
        self.screen_reader.keyboard_nav.register_skip_link(
            '2', 'response_area', 'Response display'
        )
        self.screen_reader.keyboard_nav.register_skip_link(
            '3', 'help_button', 'Help section'
        )
    
    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header(show_clock=True)
        
        with Container(id="app-container"):
            # Main content area
            with Vertical(id="main-content"):
                # Welcome message
                yield Static(
                    self._get_welcome_message(),
                    id="welcome-message",
                    classes="welcome"
                )
                
                # Command input area
                with Horizontal(id="input-area", classes="input-container"):
                    yield AccessibleInput(
                        placeholder=self._get_input_placeholder(),
                        id="main_input",
                        aria_label="Command input",
                        aria_description="Type your natural language command here",
                        screen_reader=self.screen_reader
                    )
                    yield AccessibleButton(
                        "Send",
                        id="send_button",
                        variant="primary",
                        aria_label="Send command",
                        screen_reader=self.screen_reader
                    )
                
                # Response display area
                yield ScrollableContainer(
                    Static("", id="response_display"),
                    id="response_area",
                    classes="response-container"
                )
                
                # Quick action buttons
                with Horizontal(id="quick-actions", classes="actions"):
                    yield AccessibleButton(
                        "Help",
                        id="help_button",
                        variant="default",
                        aria_label="Show help",
                        screen_reader=self.screen_reader
                    )
                    yield AccessibleButton(
                        "Examples",
                        id="examples_button",
                        variant="default",
                        aria_label="Show example commands",
                        screen_reader=self.screen_reader
                    )
                    yield AccessibleButton(
                        "Clear",
                        id="clear_button",
                        variant="default",
                        aria_label="Clear response area",
                        screen_reader=self.screen_reader
                    )
        
        yield Footer()
    
    def _get_welcome_message(self) -> str:
        """Get persona-appropriate welcome message"""
        messages = {
            PersonaType.GRANDMA_ROSE: "👋 Hello dear! I'm here to help you with your computer. Just tell me what you need in your own words.",
            PersonaType.MAYA_ADHD: "Hey! Quick help for NixOS. Type what you need. Fast responses guaranteed.",
            PersonaType.ALEX_BLIND: "Welcome to Nix for Humanity. Screen reader optimized. Natural language commands ready.",
            PersonaType.DR_SARAH: "Nix for Humanity - Professional NixOS management via natural language.",
            PersonaType.LUNA_AUTISTIC: "Welcome. This is a predictable, consistent interface for NixOS. Type your commands naturally.",
        }
        return messages.get(self.current_persona, "Welcome to Nix for Humanity! 🌟")
    
    def _get_input_placeholder(self) -> str:
        """Get persona-appropriate input placeholder"""
        placeholders = {
            PersonaType.GRANDMA_ROSE: "Type what you need help with...",
            PersonaType.MAYA_ADHD: "Quick command...",
            PersonaType.ALEX_BLIND: "Enter command",
            PersonaType.DR_SARAH: "NixOS command",
            PersonaType.LUNA_AUTISTIC: "Type command here",
        }
        return placeholders.get(self.current_persona, "Type your command...")
    
    async def on_mount(self) -> None:
        """Called when app is mounted"""
        # Announce app start to screen reader
        self.screen_reader.announce(
            "Nix for Humanity is ready. Press F1 for keyboard shortcuts.",
            AriaLivePriority.ASSERTIVE
        )
        
        # Focus on main input
        await self.query_one("#main_input").focus()
    
    def watch_current_persona(self, old_persona: PersonaType, new_persona: PersonaType) -> None:
        """React to persona changes"""
        # Update persona adapter
        self.persona_adapter.set_persona(new_persona)
        
        # Update UI elements
        profile = self.persona_adapter.get_current_profile()
        
        # Update welcome message
        welcome = self.query_one("#welcome-message", Static)
        welcome.update(self._get_welcome_message())
        
        # Update input placeholder
        input_field = self.query_one("#main_input", AccessibleInput)
        input_field.placeholder = self._get_input_placeholder()
        
        # Apply accessibility settings
        if profile.large_text:
            self.add_class("large-text")
        else:
            self.remove_class("large-text")
            
        if profile.high_contrast:
            self.add_class("high-contrast")
        else:
            self.remove_class("high-contrast")
            
        if profile.reduced_motion:
            self.add_class("reduced-motion")
        else:
            self.remove_class("reduced-motion")
        
        # Announce change
        self.screen_reader.announce(
            f"Switched to {new_persona.value} mode",
            AriaLivePriority.ASSERTIVE
        )
    
    def watch_screen_reader_enabled(self, was_enabled: bool, is_enabled: bool) -> None:
        """React to screen reader toggle"""
        if is_enabled:
            self.screen_reader.announce(
                "Screen reader enabled",
                AriaLivePriority.ASSERTIVE
            )
        else:
            # One last announcement before disabling
            self.screen_reader.announce(
                "Screen reader disabled",
                AriaLivePriority.ASSERTIVE
            )
    
    async def on_button_pressed(self, event: AccessibleButton.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "send_button":
            await self._process_command()
        elif button_id == "help_button":
            await self._show_help()
        elif button_id == "examples_button":
            await self._show_examples()
        elif button_id == "clear_button":
            await self._clear_responses()
    
    async def on_input_submitted(self, event: AccessibleInput.Submitted) -> None:
        """Handle input submission (Enter key)"""
        await self._process_command()
    
    async def _process_command(self) -> None:
        """Process the command from input"""
        input_field = self.query_one("#main_input", AccessibleInput)
        command = input_field.value.strip()
        
        if not command:
            return
            
        # Add to history
        self.command_history.append({
            'command': command,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        # Clear input
        input_field.value = ""
        
        # Show processing indicator
        response_display = self.query_one("#response_display", Static)
        response_display.update(f"Processing: {command}...")
        
        # Announce processing
        self.screen_reader.announce(
            f"Processing command: {command}",
            AriaLivePriority.POLITE
        )
        
        # Backend integration - Phase 3 Technical Debt Sprint Implementation
        # Import the backend at the module level to use here
        from ..backend import EnhancedBackend
        
        # Initialize backend if not already done
        if not hasattr(self, '_backend'):
            self._backend = EnhancedBackend()
        
        try:
            # Process command through the real backend
            backend_response = await self._backend.process_async(command)
            
            # Extract the response text from backend response structure
            if isinstance(backend_response, dict):
                response = backend_response.get('response', str(backend_response))
                # Include XAI explanation if available
                if 'explanation' in backend_response:
                    response += f"\n\n💡 Why: {backend_response['explanation']}"
            else:
                response = str(backend_response)
        except Exception as e:
            # Fallback to simulation if backend fails
            response = f"⚠️ Backend processing failed: {str(e)}\n"
            response += "Falling back to simulated response:\n\n"
            response += self._simulate_response(command)
        
        # Update display
        current_content = response_display.renderable
        new_content = f"{current_content}\n\n> {command}\n{response}"
        response_display.update(new_content)
        
        # Announce response
        self.screen_reader.announce(response, AriaLivePriority.ASSERTIVE)
        
        # Scroll to bottom
        container = self.query_one("#response_area", ScrollableContainer)
        container.scroll_end()
    
    def _simulate_response(self, command: str) -> str:
        """Simulate a response (to be replaced with real backend)"""
        command_lower = command.lower()
        
        if "install" in command_lower:
            if "firefox" in command_lower:
                return "✓ Firefox installed successfully! You can find it in your applications menu."
            return "I'll help you install that. Which package would you like to install?"
            
        elif "update" in command_lower:
            return "✓ System is up to date! No new packages available."
            
        elif "help" in command_lower:
            return self._get_help_text()
            
        else:
            return f"I understood '{command}'. Let me help you with that..."
    
    def _get_help_text(self) -> str:
        """Get help text for current persona"""
        base_help = """
I can help you with:
• Installing software ("install firefox")
• System updates ("update my system")
• Package searches ("find text editors")
• System information ("check disk space")
        """
        
        if self.current_persona == PersonaType.GRANDMA_ROSE:
            return base_help + "\n\nJust tell me what you need in your own words, dear!"
        elif self.current_persona == PersonaType.MAYA_ADHD:
            return base_help + "\n\nQuick tip: Press ↑ for command history"
        else:
            return base_help
    
    async def _show_help(self) -> None:
        """Show help information"""
        help_text = self._get_help_text()
        response_display = self.query_one("#response_display", Static)
        response_display.update(help_text)
        self.screen_reader.announce("Help information displayed", AriaLivePriority.POLITE)
    
    async def _show_examples(self) -> None:
        """Show example commands"""
        examples = """
Example commands:
• "I need a web browser" → installs Firefox
• "update everything" → updates system
• "my wifi isn't working" → network troubleshooting
• "install that code editor everyone uses" → installs VS Code
• "make text bigger" → adjusts display settings
        """
        response_display = self.query_one("#response_display", Static)
        response_display.update(examples)
        self.screen_reader.announce("Example commands displayed", AriaLivePriority.POLITE)
    
    async def _clear_responses(self) -> None:
        """Clear the response area"""
        response_display = self.query_one("#response_display", Static)
        response_display.update("")
        self.screen_reader.announce("Response area cleared", AriaLivePriority.POLITE)
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.screen_reader.announce("Goodbye!", AriaLivePriority.ASSERTIVE)
        self.exit()
    
    def action_help(self) -> None:
        """Show help"""
        asyncio.create_task(self._show_help())
    
    def action_toggle_theme(self) -> None:
        """Toggle between light and dark theme"""
        # Textual handles theme toggling
        self.dark = not self.dark
        theme = "dark" if self.dark else "light"
        self.screen_reader.announce(f"Switched to {theme} theme", AriaLivePriority.POLITE)
    
    def action_change_persona(self) -> None:
        """Cycle through personas"""
        personas = list(PersonaType)
        current_index = personas.index(self.current_persona)
        next_index = (current_index + 1) % len(personas)
        self.current_persona = personas[next_index]
    
    def action_toggle_screen_reader(self) -> None:
        """Toggle screen reader on/off"""
        self.screen_reader_enabled = not self.screen_reader_enabled
    
    def action_show_shortcuts(self) -> None:
        """Show keyboard shortcuts"""
        shortcuts = """
Keyboard Shortcuts:
• F1 - Show this help
• Ctrl+Q - Quit
• Ctrl+H - Help
• Ctrl+T - Toggle theme
• Ctrl+P - Change persona
• Tab - Navigate between elements
• Enter - Submit command
• ↑/↓ - Command history
• 1 - Jump to input
• 2 - Jump to responses
• 3 - Jump to help button
        """
        response_display = self.query_one("#response_display", Static)
        response_display.update(shortcuts)
        self.screen_reader.announce("Keyboard shortcuts displayed", AriaLivePriority.POLITE)
    
    async def on_key(self, event: events.Key) -> None:
        """Handle key presses for navigation"""
        # Command history navigation
        if event.key == "up":
            input_field = self.query_one("#main_input", AccessibleInput)
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                input_field.value = self.command_history[-(self.history_index + 1)]['command']
                self.screen_reader.announce(
                    f"Previous command: {input_field.value}",
                    AriaLivePriority.POLITE
                )
        elif event.key == "down":
            input_field = self.query_one("#main_input", AccessibleInput)
            if self.history_index > -1:
                self.history_index -= 1
                if self.history_index == -1:
                    input_field.value = ""
                else:
                    input_field.value = self.command_history[-(self.history_index + 1)]['command']
                self.screen_reader.announce(
                    f"Next command: {input_field.value}" if input_field.value else "Command cleared",
                    AriaLivePriority.POLITE
                )
        
        # Let keyboard navigator handle other keys
        elif self.screen_reader.keyboard_nav.handle_key(event.key):
            # Key was handled by navigator
            pass
        else:
            # Pass to parent
            await super().on_key(event)


if __name__ == "__main__":
    app = NixForHumanityApp()
    app.run()