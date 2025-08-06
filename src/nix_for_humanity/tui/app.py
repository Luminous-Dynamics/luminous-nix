# Nix for Humanity TUI Application
"""
Beautiful Textual-based terminal interface for Nix for Humanity
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

from ..core import (
    NixForHumanityCore, 
    Query, 
    Plan,
    ExecutionMode,
    PersonalityStyle
)
from ..ai.xai_engine import XAIEngine, ExplanationLevel, ConfidenceLevel
from ..xai.causal_engine import CausalXAI, CausalExplanation
from ..xai.confidence_calculator import ConfidenceCalculator, ConfidenceLevel as XAIConfidenceLevel
from ..xai.explanation_formatter import PersonaExplanationAdapter
from .persona_styles import PersonaStyleManager, PersonaType, detect_persona_from_input, get_persona_specific_help_text


class ChatMessage(Static):
    """A single message in the chat"""
    
    def __init__(self, content: str, is_user: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.is_user = is_user
        
    def compose(self) -> ComposeResult:
        if self.is_user:
            yield Static(f"🧑 You: {self.content}", classes="user-message")
        else:
            # Assistant messages can contain markdown
            yield Static(Markdown(self.content), classes="assistant-message")


class CommandPreview(Static):
    """Preview of command to be executed"""
    
    def __init__(self, command_text: str, **kwargs):
        super().__init__(**kwargs)
        self.command_text = command_text
        
    def compose(self) -> ComposeResult:
        yield Static(
            Panel(
                Syntax(self.command_text, "bash", theme="monokai"),
                title="💻 Command Preview",
                border_style="yellow"
            )
        )


class HelpScreen(Screen):
    """Help screen showing available commands and shortcuts"""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Close"),
        Binding("q", "pop_screen", "Close"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Static(
            Panel(
                """# 🌟 Nix for Humanity Help

## Commands You Can Use

### Package Management
- **Install**: "install firefox", "I need a browser", "get me vim"
- **Remove**: "remove firefox", "uninstall vim", "delete emacs"
- **Search**: "search python", "find text editors", "what browsers are available?"
- **Info**: "tell me about firefox", "what is vim?", "describe emacs"

### System Management
- **Update**: "update my system", "upgrade everything", "check for updates"
- **Rollback**: "go back", "undo last update", "previous generation"
- **Clean**: "free up space", "garbage collect", "clean old generations"
- **Status**: "system info", "disk usage", "what's installed?"

### Network & Troubleshooting
- **WiFi**: "connect to wifi", "my internet isn't working", "show networks"
- **Diagnostics**: "check system health", "what's wrong?", "diagnose issues"

## Keyboard Shortcuts

- **Ctrl+P**: Toggle personality style
- **Ctrl+X**: Toggle XAI explanations on/off
- **Ctrl+E**: Cycle explanation detail level (Simple → Detailed → Technical)
- **Ctrl+H**: Show this help
- **Ctrl+C**: Clear chat
- **Ctrl+Q**: Quit application
- **Tab**: Focus next element
- **Enter**: Send message

## Personality Styles

Press Ctrl+P to cycle through:
- **Minimal**: Just the facts
- **Friendly**: Warm and helpful (default)
- **Encouraging**: Supportive for beginners
- **Technical**: Detailed explanations
- **Symbiotic**: Learning together mode

## XAI Explanations 🧠

Press Ctrl+X to toggle "explainable AI" mode:
- **Simple**: One-sentence explanations
- **Detailed**: Paragraph with reasoning
- **Technical**: Full decision analysis
- Learn why the system made its choices
- Build trust through transparency

## Tips

1. **Be natural** - Say things however feels right
2. **Ask questions** - "What's the difference between X and Y?"
3. **Make mistakes** - Typos are handled automatically
4. **Give feedback** - In symbiotic mode, help the system learn

## Privacy

✅ Everything runs locally
✅ No data leaves your computer
✅ Learning is optional
✅ You own all your data
""",
                title="Help",
                border_style="bright_blue"
            ),
            id="help-text"
        )


class XAIExplanationPanel(Static):
    """Panel showing XAI explanations for decisions"""
    
    def __init__(self, explanation, level: ExplanationLevel = ExplanationLevel.SIMPLE, 
                 persona: PersonaType = PersonaType.DAVID, **kwargs):
        super().__init__(**kwargs)
        self.explanation = explanation
        self.level = level
        self.persona = persona
        
    def compose(self) -> ComposeResult:
        # Adapt explanation for persona if it's a CausalExplanation
        if hasattr(self.explanation, 'factors'):
            adapted = self.explanation_adapter.adapt_for_persona(self.explanation, self.persona)
            explanation_text = adapted['text']
            primary_reason = adapted['primary_reason']
            confidence_emoji = adapted['confidence_emoji']
            border_style = adapted['style']
        else:
            # Fallback for old-style explanations
            if self.level == ExplanationLevel.SIMPLE:
                explanation_text = self.explanation.simple_explanation
            elif self.level == ExplanationLevel.DETAILED:
                explanation_text = self.explanation.detailed_explanation
            else:  # TECHNICAL
                explanation_text = self.explanation.technical_explanation
            
            primary_reason = getattr(self.explanation, 'primary_reason', 'Decision Analysis')
            
            # Style based on confidence
            if hasattr(self.explanation, 'confidence'):
                if self.explanation.confidence == ConfidenceLevel.HIGH:
                    border_style = "green"
                    confidence_emoji = "🟢"
                elif self.explanation.confidence == ConfidenceLevel.MEDIUM:
                    border_style = "yellow"
                    confidence_emoji = "🟡"
                elif self.explanation.confidence == ConfidenceLevel.LOW:
                    border_style = "orange"
                    confidence_emoji = "🟠"
                else:  # UNCERTAIN
                    border_style = "red"
                    confidence_emoji = "🔴"
            else:
                border_style = "blue"
                confidence_emoji = "ℹ️"
        
        # Build content with confidence details if available
        content = f"{confidence_emoji} **{primary_reason}**\n\n{explanation_text}"
        
        # Add confidence breakdown for detailed/technical levels
        if hasattr(self.explanation, 'confidence_details') and self.level != ExplanationLevel.SIMPLE:
            details = self.explanation.confidence_details
            if details and hasattr(details, 'sources'):
                content += "\n\n📊 **Confidence Sources:**"
                for source, conf in details.sources.items():
                    source_name = source.replace('_', ' ').title()
                    bar_length = int(conf * 10)
                    bar = "█" * bar_length + "░" * (10 - bar_length)
                    content += f"\n  {source_name}: {bar} {conf:.0%}"
                
                content += f"\n\n  **Overall**: {details.overall_confidence:.0%}"
        
        # Add decision tree for technical level
        if hasattr(self.explanation, 'decision_tree') and self.level == ExplanationLevel.TECHNICAL:
            content += "\n\n🌳 **Decision Tree:**\n"
            content += str(self.explanation.decision_tree)
        
        yield Static(
            Panel(
                content,
                title=f"🧠 Why I decided this ({self.level.value})",
                border_style=border_style
            )
        )
    
    @property
    def explanation_adapter(self):
        """Get the explanation adapter from the app"""
        return self.app.explanation_adapter


class NixHumanityApp(App):
    """Main TUI Application"""
    
    # Base CSS - will be enhanced with persona-specific styles
    BASE_CSS = """
    Screen {
        background: $surface;
    }
    
    #chat-container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }
    
    .user-message {
        color: $text;
        margin-bottom: 1;
    }
    
    .assistant-message {
        color: $success;
        margin-bottom: 1;
        padding-left: 2;
    }
    
    #input-area {
        dock: bottom;
        height: 3;
        margin: 1;
    }
    
    #command-preview {
        height: auto;
        margin: 1;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel;
        color: $text-muted;
        padding: 0 1;
    }
    
    .button-row {
        height: 3;
        align: center middle;
        margin: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    #help-text {
        margin: 2;
    }
    """
    
    TITLE = "Nix for Humanity"
    SUB_TITLE = "Natural language interface for NixOS"
    
    BINDINGS = [
        Binding("ctrl+p", "toggle_personality", "Toggle personality"),
        Binding("ctrl+u", "cycle_persona", "Cycle persona"),
        Binding("ctrl+x", "toggle_explanations", "Toggle XAI explanations"),
        Binding("ctrl+e", "cycle_explanation_level", "Cycle explanation level"),
        Binding("ctrl+h", "show_help", "Help"),
        Binding("ctrl+c", "clear_chat", "Clear chat"),
        Binding("ctrl+q", "quit", "Quit"),
    ]
    
    @property 
    def CSS(self) -> str:
        """Combine base CSS with persona-specific styles"""
        return self.BASE_CSS + "\n" + self.persona_manager.get_css_styles()
    
    def __init__(self):
        super().__init__()
        
        # Initialize core engine
        self.core = NixForHumanityCore({
            'dry_run': False,
            'default_personality': 'friendly',
            'enable_learning': True,
            'collect_feedback': True
        })
        
        # Initialize XAI components
        self.xai_engine = XAIEngine()  # Keep for backward compatibility
        self.causal_xai = CausalXAI()
        self.confidence_calculator = ConfidenceCalculator()
        self.explanation_adapter = PersonaExplanationAdapter()
        
        # Initialize persona system
        self.persona_manager = PersonaStyleManager(PersonaType.DAVID)  # Default to David (balanced)
        
        self.session_id = str(uuid.uuid4())[:8]
        self.current_plan = None
        self.personality = PersonalityStyle.FRIENDLY
        self.last_query = ""
        self.last_response = ""
        self.awaiting_feedback_explanation = False
        
        # XAI state
        self.show_explanations = False
        self.explanation_level = ExplanationLevel.SIMPLE
        self.current_explanation = None
        
    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()
        
        # Main chat area
        with ScrollableContainer(id="chat-container"):
            yield ChatMessage(
                "👋 Welcome to Nix for Humanity! I'll help you manage NixOS using natural conversation.\n\n"
                "Just tell me what you want to do, like:\n"
                "• 'install firefox'\n"
                "• 'update my system'\n"
                "• 'search for python'\n\n"
                "Type your request below and press Enter!",
                is_user=False
            )
        
        # Command preview area (hidden initially)
        yield Container(id="command-preview")
        
        # Input area
        with Horizontal(id="input-area"):
            yield Input(
                placeholder="Ask me anything about NixOS...",
                id="user-input"
            )
            yield Button("Send", variant="primary", id="send-button")
            
        # Status bar
        yield Label(
            f"Session: {self.session_id} | Personality: {self.personality.value} | Ready",
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
        if event.button.id == "send-button":
            input_widget = self.query_one("#user-input", Input)
            self.process_query(input_widget.value)
            
        elif event.button.id == "execute-button":
            self.execute_current_plan()
            
        elif event.button.id == "cancel-button":
            self.cancel_current_plan()
            
        elif event.button.id in ["feedback-helpful", "feedback-not-helpful", "feedback-explain"]:
            self.handle_feedback_button(event.button.id)
            
        elif event.button.id in ["explanation-helpful", "explanation-confusing", "explanation-more-detail"]:
            self.handle_explanation_feedback(event.button.id)
            
    def process_query(self, query_text: str) -> None:
        """Process user query through the core"""
        if not query_text.strip():
            return
            
        # Clear input
        input_widget = self.query_one("#user-input", Input)
        input_widget.value = ""
        
        # Add user message to chat
        chat = self.query_one("#chat-container")
        chat.mount(ChatMessage(query_text, is_user=True))
        
        # Handle feedback explanation if we're waiting for it
        if self.awaiting_feedback_explanation:
            self.handle_feedback_explanation(query_text)
            self.awaiting_feedback_explanation = False
            return
        
        # Update status
        self.update_status("Processing...")
        
        # Create query
        query = Query(
            text=query_text,
            personality=self.personality.value,
            mode=ExecutionMode.DRY_RUN,  # Always plan first in TUI
            session_id=self.session_id,
            user_id="tui-user"
        )
        
        # Get plan from core
        plan = self.core.plan(query)
        self.current_plan = plan
        
        # Add assistant response
        chat.mount(ChatMessage(plan.text, is_user=False))
        
        # Generate XAI explanation if enabled
        if self.show_explanations:
            # Extract decision factors from the plan
            factors = []
            if hasattr(plan, 'intent') and plan.intent:
                factors.append(('intent_match', 0.8, {'type': plan.intent}))
            if hasattr(plan, 'command') and plan.command:
                factors.append(('command_confidence', 0.9, {'command': plan.command.program}))
            
            # Generate causal explanation
            causal_explanation = self.causal_xai.explain_decision(
                decision_type="intent_recognition",
                decision_value=plan.intent or "unknown",
                context={
                    "user_input": query_text,
                    "session_id": self.session_id,
                    "user_id": "tui-user",
                    "personality": self.personality.value,
                    "persona": self.persona_manager.current_persona.value
                },
                factors=factors,
                level=self.explanation_level
            )
            
            # Calculate detailed confidence
            confidence_metrics = self.confidence_calculator.calculate_confidence(
                decision=plan.intent or "unknown",
                context={
                    "user_input": query_text,
                    "session_id": self.session_id,
                    "factors": factors
                },
                detailed=True
            )
            
            # Enhance explanation with confidence details
            causal_explanation.confidence_details = confidence_metrics
            
            # Add decision tree if in technical mode
            if self.explanation_level == ExplanationLevel.TECHNICAL:
                causal_explanation.decision_tree = self.causal_xai._build_decision_tree(
                    decision_type="intent_recognition",
                    decision_value=plan.intent or "unknown",
                    factors=factors
                )
            
            self.current_explanation = causal_explanation
            self.show_xai_explanation(causal_explanation)
        
        # Show command preview if there's a command
        if plan.command:
            self.show_command_preview(plan)
            
        # Show feedback UI if in symbiotic mode
        elif self.personality == PersonalityStyle.SYMBIOTIC:
            self.show_feedback_ui(query_text, plan.text)
        
        # Update status
        self.update_status("Ready")
        
        # Scroll to bottom
        chat.scroll_end()
        
    def show_command_preview(self, plan: Plan) -> None:
        """Show command preview with confirmation buttons"""
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        # Build command string
        cmd_parts = [plan.command.program] + plan.command.args
        if plan.command.requires_sudo:
            cmd_parts = ['sudo'] + cmd_parts
        command_str = ' '.join(cmd_parts)
        
        # Add preview
        preview_container.mount(CommandPreview(command_str))
        
        # Add confirmation buttons
        with preview_container:
            with Horizontal(classes="button-row"):
                if plan.requires_confirmation:
                    yield Static("⚠️  This action requires confirmation", classes="warning")
                yield Button("✅ Execute", variant="success", id="execute-button")
                yield Button("❌ Cancel", variant="error", id="cancel-button")
                
    def execute_current_plan(self) -> None:
        """Execute the current plan"""
        if not self.current_plan or not self.current_plan.command:
            return
            
        # Update status
        self.update_status("Executing command...")
        
        # Execute through core
        result = self.core.execute_plan(self.current_plan, "tui-user")
        
        # Add result to chat
        chat = self.query_one("#chat-container")
        
        if result.success:
            message = "✅ Command executed successfully!"
            if result.output:
                message += f"\n\nOutput:\n```\n{result.output[:500]}...\n```"
        else:
            message = f"❌ Command failed!\n\nError: {result.error}"
            
        chat.mount(ChatMessage(message, is_user=False))
        
        # Clear command preview
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        # Reset plan
        self.current_plan = None
        
        # Update status
        self.update_status("Ready")
        
        # Scroll to bottom
        chat.scroll_end()
        
    def cancel_current_plan(self) -> None:
        """Cancel the current plan"""
        # Clear command preview
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        # Add cancellation message
        chat = self.query_one("#chat-container")
        chat.mount(ChatMessage("❌ Command cancelled", is_user=False))
        
        # Reset plan
        self.current_plan = None
        
        # Update status
        self.update_status("Ready")
        
    def show_feedback_ui(self, query: str, response: str) -> None:
        """Show feedback collection UI for symbiotic mode"""
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        # Store for feedback
        self.last_query = query
        self.last_response = response
        
        # Add feedback panel
        preview_container.mount(
            Static(
                Panel(
                    "🤝 I'm learning! Was this response helpful?",
                    title="Symbiotic Learning",
                    border_style="cyan"
                )
            )
        )
        
        # Add feedback buttons
        button_row = Horizontal(classes="button-row")
        button_row.mount(Button("👍 Helpful", variant="success", id="feedback-helpful"))
        button_row.mount(Button("👎 Not helpful", variant="error", id="feedback-not-helpful"))
        button_row.mount(Button("✏️ I'll explain", variant="primary", id="feedback-explain"))
        preview_container.mount(button_row)
                
    def handle_feedback_button(self, button_id: str) -> None:
        """Handle feedback button clicks"""
        from ..core.learning_system import Interaction
        
        if button_id == "feedback-helpful":
            # Record positive feedback
            interaction = Interaction(
                query=self.last_query,
                intent="unknown",  # Will be extracted by learning system
                response=self.last_response,
                success=True,
                user_id="tui-user"
            )
            self.core.learning_system.record_interaction(interaction)
            
            # Show thanks
            chat = self.query_one("#chat-container")
            chat.mount(ChatMessage(
                "Thank you! I'll remember that this worked well. 🌟",
                is_user=False
            ))
            
        elif button_id == "feedback-not-helpful":
            # Ask for improvement
            chat = self.query_one("#chat-container")
            chat.mount(ChatMessage(
                "I appreciate your feedback! What would have been a better response?",
                is_user=False
            ))
            self.awaiting_feedback_explanation = True
            
        elif button_id == "feedback-explain":
            # Ask for explanation
            chat = self.query_one("#chat-container")
            chat.mount(ChatMessage(
                "I'd love to learn! Please tell me what you expected or what went wrong:",
                is_user=False
            ))
            self.awaiting_feedback_explanation = True
            
        # Clear feedback UI
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
    def show_xai_explanation(self, explanation) -> None:
        """Show XAI explanation panel"""
        preview_container = self.query_one("#command-preview")
        
        # Remove existing explanation if any
        for child in list(preview_container.children):
            if isinstance(child, XAIExplanationPanel):
                child.remove()
        
        # Add new explanation panel with persona adaptation
        explanation_panel = XAIExplanationPanel(
            explanation=explanation, 
            level=self.explanation_level,
            persona=self.persona_manager.current_persona
        )
        preview_container.mount(explanation_panel)
        
        # Add feedback buttons for explanation quality
        if self.personality == PersonalityStyle.SYMBIOTIC:
            button_row = Horizontal(classes="button-row")
            button_row.mount(Button("🎯 Helpful explanation", variant="success", id="explanation-helpful"))
            button_row.mount(Button("🤔 Confusing", variant="error", id="explanation-confusing"))
            button_row.mount(Button("📝 Need more detail", variant="primary", id="explanation-more-detail"))
            preview_container.mount(button_row)
        
    def handle_feedback_explanation(self, explanation: str) -> None:
        """Handle detailed feedback explanation from user"""
        from ..core.learning_system import Interaction
        
        # Record feedback with explanation
        interaction = Interaction(
            query=self.last_query,
            intent="unknown",
            response=self.last_response,
            success=False,
            user_id="tui-user",
            feedback_text=explanation
        )
        self.core.learning_system.record_interaction(interaction)
        
        # Thank the user
        chat = self.query_one("#chat-container")
        chat.mount(ChatMessage(
            "Thank you so much for explaining! This helps me improve. "
            "I've recorded your feedback and will learn from it. 🙏",
            is_user=False
        ))
        
    def handle_explanation_feedback(self, button_id: str) -> None:
        """Handle feedback on XAI explanations"""
        if not self.current_explanation:
            return
            
        chat = self.query_one("#chat-container")
        
        if button_id == "explanation-helpful":
            # Record positive feedback on explanation quality
            chat.mount(ChatMessage(
                "Great! I'm glad that explanation was helpful. I'll continue providing similar detail. 🎯",
                is_user=False
            ))
            
        elif button_id == "explanation-confusing":
            # Record negative feedback and offer to clarify
            chat.mount(ChatMessage(
                "I understand that was confusing. Let me try to explain differently. What part didn't make sense?",
                is_user=False
            ))
            self.awaiting_feedback_explanation = True
            
        elif button_id == "explanation-more-detail":
            # Automatically increase detail level
            if self.explanation_level == ExplanationLevel.SIMPLE:
                self.explanation_level = ExplanationLevel.DETAILED
                level_name = "detailed"
            elif self.explanation_level == ExplanationLevel.DETAILED:
                self.explanation_level = ExplanationLevel.TECHNICAL
                level_name = "technical"
            else:
                level_name = "maximum"
                
            chat.mount(ChatMessage(
                f"Sure! I've switched to {level_name} explanations. Here's more detail:",
                is_user=False
            ))
            
            # Refresh the explanation with new level
            if self.current_explanation:
                # Re-generate explanation with new level
                if hasattr(self.current_explanation, 'factors'):
                    # It's a CausalExplanation, regenerate with new level
                    self.current_explanation = self.causal_xai.explain_decision(
                        decision_type=self.current_explanation.decision_type,
                        decision_value=self.current_explanation.decision,
                        context=self.current_explanation.context,
                        factors=self.current_explanation.factors,
                        level=self.explanation_level
                    )
                self.show_xai_explanation(self.current_explanation)
        
        # Clear explanation feedback UI after a moment
        if button_id != "explanation-more-detail":  # Keep UI for more detail
            preview_container = self.query_one("#command-preview")
            # Remove feedback buttons but keep explanation
            for child in list(preview_container.children):
                if isinstance(child, Horizontal) and "button-row" in child.classes:
                    child.remove()
        
    def update_status(self, status: str) -> None:
        """Update status bar"""
        status_bar = self.query_one("#status-bar", Label)
        status_bar.update(
            f"Session: {self.session_id} | "
            f"Personality: {self.personality.value} | "
            f"{status}"
        )
        
    def action_toggle_personality(self) -> None:
        """Toggle through personality styles"""
        styles = list(PersonalityStyle)
        current_index = styles.index(self.personality)
        self.personality = styles[(current_index + 1) % len(styles)]
        self.core.personality_system.set_style(self.personality)
        self.update_status("Ready")
        
        # Show notification
        chat = self.query_one("#chat-container")
        chat.mount(ChatMessage(
            f"✨ Personality changed to: {self.personality.value}",
            is_user=False
        ))
        
    def action_cycle_persona(self) -> None:
        """Cycle through user personas for adaptive styling"""
        personas = list(PersonaType)
        current_index = personas.index(self.persona_manager.current_persona)
        new_persona = personas[(current_index + 1) % len(personas)]
        
        # Switch to new persona
        self.persona_manager.set_persona(new_persona)
        
        # Apply new styles immediately
        self.refresh_css()
        
        # Show persona-specific notification
        chat = self.query_one("#chat-container")
        profile = self.persona_manager.profile
        
        # Adapt the notification message for the new persona
        if new_persona == PersonaType.GRANDMA_ROSE:
            message = f"🌻 Hello! I'm now set up for {profile.name}. I'll use simple words and be very patient with you."
        elif new_persona == PersonaType.MAYA:
            message = f"⚡ Switched to {profile.name} mode! Fast responses, minimal text. Let's go!"
        elif new_persona == PersonaType.ALEX:
            message = f"🎧 Now in {profile.name} mode. All responses optimized for screen readers with clear navigation."
        elif new_persona == PersonaType.DR_SARAH:
            message = f"🔬 Switched to {profile.name} mode. Technical details and precise information available."
        elif new_persona == PersonaType.CARLOS:
            message = f"🌟 Welcome {profile.name}! I'll be encouraging and explain things step by step."
        elif new_persona == PersonaType.VIKTOR:
            message = f"👋 Hello! Now speaking clearly for {profile.name}. Simple words, easy to understand."
        elif new_persona == PersonaType.LUNA:
            message = f"🎯 Switched to {profile.name} mode. Consistent, detailed responses you can count on."
        else:
            message = f"👤 Persona changed to: {profile.name} ({profile.age} years old)"
            
        chat.mount(ChatMessage(message, is_user=False))
        
        # Update status bar to show current persona
        self.update_status("Ready")
        
    def refresh_css(self) -> None:
        """Refresh CSS to apply persona-specific styling"""
        # This triggers the CSS property to be re-evaluated
        self.refresh()
        
    def refresh_explanation(self) -> None:
        """Refresh the current XAI explanation with new detail level"""
        preview_container = self.query_one("#command-preview")
        
        # Find the current explanation panel
        for child in preview_container.children:
            if isinstance(child, XAIExplanationPanel):
                # Replace with new level
                new_panel = XAIExplanationPanel(
                    explanation=child.explanation,
                    level=self.explanation_level
                )
                child.remove()
                preview_container.mount(new_panel)
                break
                
    def hide_explanation(self) -> None:
        """Hide the current XAI explanation"""
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
    def action_toggle_explanations(self) -> None:
        """Toggle XAI explanations on/off"""
        self.show_explanations = not self.show_explanations
        
        # Show notification
        chat = self.query_one("#chat-container")
        status = "enabled" if self.show_explanations else "disabled"
        chat.mount(ChatMessage(
            f"🧠 XAI explanations {status}. I'll {'explain my reasoning' if self.show_explanations else 'work silently'}.",
            is_user=False
        ))
        
        # Update status
        self.update_status("Ready")
        
    def action_cycle_explanation_level(self) -> None:
        """Cycle through explanation detail levels"""
        levels = [ExplanationLevel.SIMPLE, ExplanationLevel.DETAILED, ExplanationLevel.TECHNICAL]
        current_index = levels.index(self.explanation_level)
        self.explanation_level = levels[(current_index + 1) % len(levels)]
        
        # Show notification
        chat = self.query_one("#chat-container")
        level_names = {ExplanationLevel.SIMPLE: "Simple", ExplanationLevel.DETAILED: "Detailed", ExplanationLevel.TECHNICAL: "Technical"}
        chat.mount(ChatMessage(
            f"🔍 Explanation level: {level_names[self.explanation_level]}",
            is_user=False
        ))
        
        # Refresh current explanation if visible
        self.refresh_explanation()
        
        # Update status
        self.update_status("Ready")
        
    def action_show_help(self) -> None:
        """Show help screen"""
        self.push_screen(HelpScreen())
        
    def action_clear_chat(self) -> None:
        """Clear chat history"""
        chat = self.query_one("#chat-container")
        chat.remove_children()
        
        # Add welcome message again
        chat.mount(ChatMessage(
            "👋 Chat cleared! How can I help you with NixOS?",
            is_user=False
        ))
        
        # Clear command preview if any
        preview_container = self.query_one("#command-preview")
        preview_container.remove_children()
        
        # Update status
        self.update_status("Ready")
        
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def run():
    """Run the TUI application"""
    app = NixHumanityApp()
    app.run()


if __name__ == "__main__":
    run()