# Nix for Humanity Enhanced TUI Application with Error Intelligence
"""
Enhanced Textual-based terminal interface with integrated Error Intelligence
"""

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, Input, Static, RichLog, 
    Button, LoadingIndicator, Label, Rule
)
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.screen import Screen
from textual.reactive import reactive
from textual import events
from textual.message import Message
from textual.binding import Binding
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
import uuid
from datetime import datetime
from typing import Optional, List

from ..backend.enhanced_backend import EnhancedBackend
from ..core.types import (
    Request, Response, Intent, PersonalityStyle,
    ExecutionMode
)
from ..ai.xai_engine import XAIEngine, ExplanationLevel, ConfidenceLevel
from ..xai.causal_engine import CausalXAI, CausalExplanation
from ..xai.confidence_calculator import ConfidenceCalculator, ConfidenceLevel as XAIConfidenceLevel
from ..xai.explanation_formatter import PersonaExplanationAdapter
from .persona_styles import PersonaStyleManager, PersonaType, detect_persona_from_input, get_persona_specific_help_text

# Import Error Intelligence UI components
from ..error_intelligence import (
    ErrorCategory, ErrorSeverity, EducationalError,
    PreventiveSuggestion, ErrorSolution
)


class ErrorIntelligencePanel(Static):
    """Display educational errors with persona adaptation"""
    
    def __init__(self, error: EducationalError, persona: PersonaType, **kwargs):
        super().__init__(**kwargs)
        self.error = error
        self.persona = persona
        
    def compose(self) -> ComposeResult:
        # Severity indicator
        severity_emoji = {
            ErrorSeverity.LOW: "💡",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "🚨",
            ErrorSeverity.CRITICAL: "🔥"
        }.get(self.error.severity, "❓")
        
        # Build error content
        content = [
            f"{severity_emoji} **{self.error.headline}**",
            "",
            self.error.explanation
        ]
        
        # Add learning point
        if self.error.learning_point:
            content.extend([
                "",
                "📚 **What we can learn:**",
                self.error.learning_point
            ])
        
        # Add solutions
        if self.error.solutions:
            content.extend([
                "",
                "💡 **Try these solutions:**"
            ])
            for i, solution in enumerate(self.error.solutions, 1):
                content.append(f"{i}. {solution}")
        
        # Add examples if available
        if self.error.examples:
            content.extend([
                "",
                "📝 **Examples:**"
            ])
            for example in self.error.examples:
                content.append(f"• {example}")
        
        # Add diagram if available
        if self.error.diagram:
            content.extend([
                "",
                "📊 **Visualization:**",
                f"```\n{self.error.diagram}\n```"
            ])
        
        # Add confidence message
        if self.error.confidence_message:
            content.extend([
                "",
                f"🎯 {self.error.confidence_message}"
            ])
        
        # Create styled panel based on severity
        border_style = {
            ErrorSeverity.LOW: "blue",
            ErrorSeverity.MEDIUM: "yellow", 
            ErrorSeverity.HIGH: "red",
            ErrorSeverity.CRITICAL: "bold red"
        }.get(self.error.severity, "white")
        
        yield Static(
            Panel(
                Markdown("\n".join(content)),
                title="Error Intelligence",
                border_style=border_style,
                expand=True
            ),
            classes="error-intelligence-panel"
        )


class PreventiveSuggestionCard(Static):
    """Display a preventive suggestion"""
    
    def __init__(self, suggestion: PreventiveSuggestion, **kwargs):
        super().__init__(**kwargs)
        self.suggestion = suggestion
        
    def compose(self) -> ComposeResult:
        # Urgency indicator
        urgency_emoji = "🔴" if self.suggestion.urgency > 0.8 else "🟡" if self.suggestion.urgency > 0.5 else "🟢"
        
        content = [
            f"{urgency_emoji} **{self.suggestion.title}**",
            "",
            f"**Why:** {self.suggestion.reason}",
            f"**Action:** {self.suggestion.action}",
            f"**Confidence:** {self.suggestion.confidence:.0%}"
        ]
        
        yield Static(
            Panel(
                Markdown("\n".join(content)),
                title=f"Preventive Tip - {self.suggestion.type.value}",
                border_style="green" if self.suggestion.urgency < 0.5 else "yellow"
            ),
            classes="preventive-suggestion"
        )


class EnhancedChatMessage(Static):
    """Enhanced chat message with error intelligence support"""
    
    def __init__(self, content: str, is_user: bool = True, 
                 error_info: Optional[EducationalError] = None,
                 preventive_suggestions: Optional[List[PreventiveSuggestion]] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_user = is_user
        self.error_info = error_info
        self.preventive_suggestions = preventive_suggestions
        
    def compose(self) -> ComposeResult:
        if self.is_user:
            yield Static(f"🧑 You: {self.content}", classes="user-message")
        else:
            # Assistant messages with potential error info
            if self.error_info:
                # Show error intelligence panel instead of regular message
                yield ErrorIntelligencePanel(
                    self.error_info, 
                    PersonaType.DAVID  # Will be dynamically set
                )
            else:
                yield Static(Markdown(self.content), classes="assistant-message")
            
            # Show preventive suggestions if any
            if self.preventive_suggestions:
                yield Static("💡 **Preventive Tips:**", classes="preventive-header")
                for suggestion in self.preventive_suggestions[:3]:  # Limit to 3
                    yield PreventiveSuggestionCard(suggestion)


class EnhancedNixForHumanityTUI(App):
    """Enhanced TUI application with Error Intelligence"""
    
    CSS = """
    #chat-container {
        height: 1fr;
        border: solid green;
        padding: 1;
    }
    
    .user-message {
        color: cyan;
        margin: 1 0;
    }
    
    .assistant-message {
        color: white;
        margin: 1 0;
    }
    
    .error-intelligence-panel {
        margin: 1 0;
    }
    
    .preventive-suggestion {
        margin: 0.5 0;
        max-width: 60;
    }
    
    .preventive-header {
        color: yellow;
        margin-top: 1;
    }
    
    .solution-button {
        margin: 0 1;
    }
    
    #command-preview {
        height: auto;
        max-height: 10;
        margin: 1 0;
    }
    
    #input-area {
        height: 3;
        margin: 1 0;
    }
    
    #user-input {
        width: 1fr;
        margin-right: 1;
    }
    
    #status-bar {
        height: 1;
        background: $primary-darken-3;
        color: $text;
        padding: 0 1;
    }
    
    .button-row {
        height: 3;
        align: center middle;
        margin: 1 0;
    }
    
    .warning {
        color: yellow;
        margin-right: 2;
    }
    
    .xai-panel {
        border: solid $primary;
        margin: 1 0;
        padding: 1;
        max-height: 20;
    }
    
    .error-solution-row {
        height: 3;
        margin: 0.5 0;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+p", "toggle_personality", "Toggle personality"),
        Binding("ctrl+u", "cycle_persona", "Cycle persona"),
        Binding("ctrl+x", "toggle_explanations", "Toggle XAI explanations"),
        Binding("ctrl+e", "cycle_explanation_level", "Cycle explanation level"),
        Binding("ctrl+h", "show_help", "Help"),
        Binding("ctrl+c", "clear_chat", "Clear chat"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+r", "retry_with_solution", "Retry with solution"),
    ]
    
    def __init__(self):
        super().__init__()
        
        # Initialize enhanced backend with error intelligence
        self.backend = EnhancedBackend({
            'personality': PersonalityStyle.FRIENDLY,
            'learning_enabled': True,
            'native_api': True,
            'progress_callback': self.update_progress
        })
        
        # Initialize XAI components
        self.xai_engine = XAIEngine()
        self.causal_xai = CausalXAI()
        self.confidence_calculator = ConfidenceCalculator()
        self.explanation_adapter = PersonaExplanationAdapter()
        
        # Initialize persona system
        self.persona_manager = PersonaStyleManager(PersonaType.DAVID)
        
        # Session state
        self.session_id = str(uuid.uuid4())[:8]
        self.current_response = None
        self.personality = PersonalityStyle.FRIENDLY
        self.last_error = None
        self.suggested_solutions = []
        
        # XAI state
        self.show_explanations = True
        self.explanation_level = ExplanationLevel.SIMPLE
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        
        # Main chat area
        with ScrollableContainer(id="chat-container"):
            yield EnhancedChatMessage(
                "👋 Welcome to Nix for Humanity with Error Intelligence!\n\n"
                "I'll help you manage NixOS and learn from any issues we encounter.\n\n"
                "Features:\n"
                "• 🎓 Educational error explanations\n"
                "• 💡 Preventive suggestions\n"
                "• 🔍 XAI-powered error analysis\n"
                "• 🎯 Persona-adaptive help\n\n"
                "Just tell me what you need!",
                is_user=False
            )
        
        # Command preview area
        yield Container(id="command-preview")
        
        # Solution buttons area
        yield Container(id="solution-buttons")
        
        # Input area
        with Horizontal(id="input-area"):
            yield Input(
                placeholder="Ask me anything about NixOS...",
                id="user-input"
            )
            yield Button("Send", variant="primary", id="send-button")
            
        # Status bar
        yield Label(
            f"Session: {self.session_id} | {self.personality.value} | {self.persona_manager.current_persona.value} | Ready",
            id="status-bar"
        )
        
        yield Footer()
        
    def on_mount(self) -> None:
        """Focus input on mount"""
        self.query_one("#user-input", Input).focus()
        
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        self.process_query(event.value)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "send-button":
            input_widget = self.query_one("#user-input", Input)
            self.process_query(input_widget.value)
            
        elif button_id == "execute-button":
            self.execute_current_plan()
            
        elif button_id == "cancel-button":
            self.cancel_current_plan()
            
        elif button_id.startswith("solution-"):
            # Handle solution button clicks
            solution_index = int(button_id.split("-")[1])
            self.apply_solution(solution_index)
            
    def process_query(self, query_text: str) -> None:
        """Process user query with error intelligence"""
        if not query_text.strip():
            return
            
        # Clear input
        input_widget = self.query_one("#user-input", Input)
        input_widget.value = ""
        
        # Add user message to chat
        chat = self.query_one("#chat-container")
        chat.mount(EnhancedChatMessage(query_text, is_user=True))
        
        # Update status
        self.update_status("Processing...")
        
        # Create request
        request = Request(
            query=query_text,
            context={
                'session_id': self.session_id,
                'personality': self.personality,
                'persona': self.persona_manager.current_persona.value,
                'explanation_level': self.explanation_level
            },
            dry_run=True,  # Always preview first
            execute=False
        )
        
        # Process through enhanced backend
        response = self.backend.process(request)
        self.current_response = response
        
        # Handle response with error intelligence
        if response.success:
            # Normal response
            message_content = response.message or "I've understood your request."
            preventive = response.preventive_suggestions if hasattr(response, 'preventive_suggestions') else None
            
            chat.mount(EnhancedChatMessage(
                message_content,
                is_user=False,
                preventive_suggestions=preventive
            ))
            
            # Show command preview if available
            if response.plan and response.plan.commands:
                self.show_command_preview(response.plan)
                
        else:
            # Error response with educational formatting
            if hasattr(response, 'educational_error'):
                chat.mount(EnhancedChatMessage(
                    response.message,
                    is_user=False,
                    error_info=response.educational_error
                ))
                
                # Store error context
                self.last_error = response.analyzed_error
                self.suggested_solutions = response.educational_error.solutions
                
                # Show solution buttons if available
                if self.suggested_solutions:
                    self.show_solution_buttons(self.suggested_solutions)
            else:
                # Fallback for non-educational errors
                chat.mount(EnhancedChatMessage(
                    f"❌ {response.message or response.error}",
                    is_user=False
                ))
        
        # Show XAI explanation if enabled
        if self.show_explanations and response.explanation:
            self.show_xai_explanation(response.explanation)
        
        # Update status
        self.update_status("Ready")
        
        # Scroll to bottom
        chat.scroll_end()
        
    def show_solution_buttons(self, solutions: List[str]) -> None:
        """Show clickable solution buttons"""
        solution_container = self.query_one("#solution-buttons")
        solution_container.remove_children()
        
        with solution_container:
            yield Static("🛠️ **Quick Actions:**", classes="solution-header")
            with Horizontal(classes="error-solution-row"):
                for i, solution in enumerate(solutions[:3]):  # Max 3 buttons
                    yield Button(
                        f"Try: {solution[:30]}...",
                        variant="warning",
                        id=f"solution-{i}",
                        classes="solution-button"
                    )
                    
    def apply_solution(self, solution_index: int) -> None:
        """Apply a suggested solution"""
        if solution_index < len(self.suggested_solutions):
            solution = self.suggested_solutions[solution_index]
            # Process the solution as a new query
            self.process_query(solution)
            
    def show_command_preview(self, plan) -> None:
        """Show command preview with confirmation"""
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        if plan.commands:
            command = plan.commands[0]
            command_str = command.get('command', 'Unknown command')
            
            # Add preview
            preview_container.mount(Static(
                Panel(
                    Syntax(command_str, "bash", theme="monokai"),
                    title="💻 Command Preview",
                    border_style="yellow"
                )
            ))
            
            # Add buttons
            with preview_container:
                with Horizontal(classes="button-row"):
                    yield Button("✅ Execute", variant="success", id="execute-button")
                    yield Button("❌ Cancel", variant="error", id="cancel-button")
                    
    def execute_current_plan(self) -> None:
        """Execute with error intelligence"""
        if not self.current_response or not self.current_response.plan:
            return
            
        # Update status
        self.update_status("Executing...")
        
        # Create execution request
        request = Request(
            query=self.current_response.intent.raw_input,
            context=self.current_response.request.context,
            dry_run=False,
            execute=True
        )
        
        # Execute through backend
        result = self.backend.process(request)
        
        # Display result with error intelligence
        chat = self.query_one("#chat-container")
        
        if result.success:
            chat.mount(EnhancedChatMessage(
                "✅ Command executed successfully!",
                is_user=False
            ))
        else:
            # Show educational error
            if hasattr(result, 'educational_error'):
                chat.mount(EnhancedChatMessage(
                    "Command failed, but I can help you fix it:",
                    is_user=False,
                    error_info=result.educational_error
                ))
            else:
                chat.mount(EnhancedChatMessage(
                    f"❌ Command failed: {result.error}",
                    is_user=False
                ))
                
        # Clear command preview
        self.query_one("#command-preview").remove_children()
        self.update_status("Ready")
        
    def cancel_current_plan(self) -> None:
        """Cancel current plan"""
        self.query_one("#command-preview").remove_children()
        self.query_one("#solution-buttons").remove_children()
        self.current_response = None
        self.update_status("Cancelled")
        
    def update_status(self, status: str) -> None:
        """Update status bar"""
        status_bar = self.query_one("#status-bar", Label)
        status_bar.update(
            f"Session: {self.session_id} | "
            f"{self.personality.value} | "
            f"{self.persona_manager.current_persona.value} | "
            f"{status}"
        )
        
    def update_progress(self, message: str, progress: float) -> None:
        """Update progress from backend"""
        self.update_status(f"{message} ({progress:.0%})")
        
    def show_xai_explanation(self, explanation) -> None:
        """Show XAI explanation panel"""
        chat = self.query_one("#chat-container")
        
        # Format explanation based on level
        if self.explanation_level == ExplanationLevel.SIMPLE:
            content = f"💭 **Why:** {explanation}"
        elif self.explanation_level == ExplanationLevel.DETAILED:
            content = f"🔍 **Detailed Analysis:**\n{explanation}"
        else:  # TECHNICAL
            content = f"🔬 **Technical Explanation:**\n{explanation}"
            
        chat.mount(Static(
            Panel(
                Markdown(content),
                title="XAI Explanation",
                border_style="blue"
            ),
            classes="xai-panel"
        ))
        
    def action_toggle_personality(self) -> None:
        """Toggle personality style"""
        styles = list(PersonalityStyle)
        current_index = styles.index(self.personality)
        self.personality = styles[(current_index + 1) % len(styles)]
        self.update_status("Ready")
        
    def action_cycle_persona(self) -> None:
        """Cycle through personas"""
        personas = list(PersonaType)
        current_index = personas.index(self.persona_manager.current_persona)
        new_persona = personas[(current_index + 1) % len(personas)]
        self.persona_manager.set_persona(new_persona)
        self.update_status("Ready")
        
    def action_toggle_explanations(self) -> None:
        """Toggle XAI explanations"""
        self.show_explanations = not self.show_explanations
        status = "enabled" if self.show_explanations else "disabled"
        self.update_status(f"XAI explanations {status}")
        
    def action_cycle_explanation_level(self) -> None:
        """Cycle explanation detail level"""
        levels = list(ExplanationLevel)
        current_index = levels.index(self.explanation_level)
        self.explanation_level = levels[(current_index + 1) % len(levels)]
        self.update_status(f"Explanation level: {self.explanation_level.value}")
        
    def action_clear_chat(self) -> None:
        """Clear chat history"""
        chat = self.query_one("#chat-container")
        chat.remove_children()
        chat.mount(EnhancedChatMessage(
            "💬 Chat cleared. How can I help you?",
            is_user=False
        ))
        
    def action_show_help(self) -> None:
        """Show help screen"""
        self.push_screen(HelpScreen())
        
    def action_retry_with_solution(self) -> None:
        """Retry last operation with first suggested solution"""
        if self.suggested_solutions:
            self.apply_solution(0)


class HelpScreen(Screen):
    """Enhanced help screen with error intelligence info"""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Close"),
        Binding("q", "pop_screen", "Close"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Static(
            Panel(
                """# 🌟 Nix for Humanity Enhanced Help

## Error Intelligence Features

### 🎓 Educational Errors
When something goes wrong, I'll:
- Explain what happened in simple terms
- Show you why it happened (with XAI)
- Suggest solutions you can try
- Teach you how to prevent it next time

### 💡 Preventive Suggestions
I'll warn you before problems occur:
- Low disk space warnings
- Permission issues ahead of time
- Network problems before they block you
- System health recommendations

### 🎯 Persona-Adaptive Help
Errors are explained based on who you are:
- **Grandma Rose**: Simple, friendly explanations
- **Maya (ADHD)**: Quick, focused solutions
- **Dr. Sarah**: Technical details when needed
- **Everyone**: Clear, actionable help

## Keyboard Shortcuts

- **Ctrl+X**: Toggle XAI explanations
- **Ctrl+E**: Cycle explanation detail level
- **Ctrl+R**: Retry with suggested solution
- **Ctrl+P**: Toggle personality style
- **Ctrl+U**: Cycle through personas
- **Ctrl+C**: Clear chat
- **Ctrl+H**: This help screen
- **Ctrl+Q**: Quit

## Error Solutions

When you see solution buttons:
1. Click any button to try that solution
2. Or press Ctrl+R for the first suggestion
3. The system learns from what works!

## Examples

**Permission Error:**
```
You: install firefox
System: [Shows educational error panel]
         - Explains sudo is needed
         - Shows exact command to run
         - Teaches about system vs user packages
```

**Package Not Found:**
```
You: install fierfix
System: [Detects typo, shows suggestions]
         - Did you mean 'firefox'?
         - Shows similar packages
         - One-click correction
```

Press ESC or Q to close this help.
""",
                title="Enhanced Help",
                border_style="green"
            )
        )