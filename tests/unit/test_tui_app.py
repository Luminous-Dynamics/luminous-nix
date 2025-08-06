#!/usr/bin/env python3
"""
Unit tests for the Nix for Humanity TUI Application

This tests the Textual-based terminal user interface, focusing on:
- Component rendering and composition
- Event handling and user interactions
- Integration with core engine
- State management and updates
- Accessibility features
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import uuid

# Mock textual before import
textual_mock = MagicMock()
textual_app_mock = MagicMock()
textual_widgets_mock = MagicMock()
textual_containers_mock = MagicMock()
textual_screen_mock = MagicMock()
textual_reactive_mock = MagicMock()
textual_events_mock = MagicMock()
textual_message_mock = MagicMock()
textual_binding_mock = MagicMock()

# Create all necessary widget mocks
class MockWidget:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.children = []
        self.id = kwargs.get('id', '')
        self.classes = kwargs.get('classes', '')
        self.value = kwargs.get('value', '')
        
    def mount(self, widget):
        self.children.append(widget)
        
    def remove_children(self):
        self.children = []
        
    def focus(self):
        pass
        
    def scroll_end(self):
        pass
        
    def update(self, text):
        self.value = text

# Create specific widget types
class MockInput(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = kwargs.get('placeholder', '')
        self.value = ''

class MockButton(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = args[0] if args else ''
        self.variant = kwargs.get('variant', 'default')

class MockStatic(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = args[0] if args else ''

class MockRichLog(MockWidget):
    pass

class MockLabel(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = args[0] if args else ''
        
    def update(self, text):
        self.text = text

class MockHeader(MockWidget):
    pass

class MockFooter(MockWidget):
    pass

class MockContainer(MockWidget):
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass
        
    def yield_child(self, widget):
        self.children.append(widget)

class MockScreen:
    pass

class MockBinding:
    def __init__(self, key, action, description):
        self.key = key
        self.action = action
        self.description = description

# Set up mock modules
textual_widgets_mock.Header = MockHeader
textual_widgets_mock.Footer = MockFooter
textual_widgets_mock.Input = MockInput
textual_widgets_mock.Static = MockStatic
textual_widgets_mock.RichLog = MockRichLog
textual_widgets_mock.Button = MockButton
textual_widgets_mock.LoadingIndicator = MockWidget
textual_widgets_mock.Label = MockLabel
textual_widgets_mock.Rule = MockWidget

textual_containers_mock.Container = MockContainer
textual_containers_mock.Horizontal = MockContainer
textual_containers_mock.Vertical = MockContainer
textual_containers_mock.ScrollableContainer = MockContainer

textual_screen_mock.Screen = MockScreen
textual_binding_mock.Binding = MockBinding

# Mock App base class
class MockApp:
    CSS = ""
    TITLE = ""
    SUB_TITLE = ""
    BINDINGS = []
    
    def __init__(self):
        self.screens = []
        self._widgets = {}
        
    def query_one(self, selector, widget_type=None):
        # Simple selector matching for tests
        if selector.startswith('#'):
            widget_id = selector[1:]
            return self._widgets.get(widget_id, MockWidget())
        return MockWidget()
        
    def push_screen(self, screen):
        self.screens.append(screen)
        
    def exit(self):
        self._exit_called = True

textual_app_mock.App = MockApp
textual_app_mock.ComposeResult = list

# Mock rich
rich_mock = MagicMock()
rich_markdown_mock = MagicMock()
rich_panel_mock = MagicMock()
rich_syntax_mock = MagicMock()
rich_table_mock = MagicMock()
rich_text_mock = MagicMock()

rich_markdown_mock.Markdown = Mock
rich_panel_mock.Panel = Mock
rich_syntax_mock.Syntax = Mock
rich_table_mock.Table = Mock
rich_text_mock.Text = Mock

# Apply all mocks
sys_modules = {
    'textual': textual_mock,
    'textual.app': textual_app_mock,
    'textual.widgets': textual_widgets_mock,
    'textual.containers': textual_containers_mock,
    'textual.screen': textual_screen_mock,
    'textual.reactive': textual_reactive_mock,
    'textual.events': textual_events_mock,
    'textual.message': textual_message_mock,
    'textual.binding': textual_binding_mock,
    'rich': rich_mock,
    'rich.markdown': rich_markdown_mock,
    'rich.panel': rich_panel_mock,
    'rich.syntax': rich_syntax_mock,
    'rich.table': rich_table_mock,
    'rich.text': rich_text_mock,
}

with patch.dict('sys.modules', sys_modules):
    from nix_for_humanity.tui.app import (
        NixHumanityApp, ChatMessage, CommandPreview, 
        HelpScreen, run
    )
    from nix_for_humanity.core import (
        Query, ExecutionMode, PersonalityStyle
    )
    from nix_for_humanity.core.planning import Plan


class TestChatMessage(unittest.TestCase):
    """Test the ChatMessage widget"""
    
    def test_user_message_creation(self):
        """Test creating a user message"""
        msg = ChatMessage("Hello, world!", is_user=True)
        self.assertEqual(msg.content, "Hello, world!")
        self.assertTrue(msg.is_user)
        
    def test_assistant_message_creation(self):
        """Test creating an assistant message"""
        msg = ChatMessage("I can help with that!", is_user=False)
        self.assertEqual(msg.content, "I can help with that!")
        self.assertFalse(msg.is_user)
        
    def test_compose_user_message(self):
        """Test composing a user message"""
        msg = ChatMessage("Test message", is_user=True)
        widgets = list(msg.compose())
        
        self.assertEqual(len(widgets), 1)
        self.assertIsInstance(widgets[0], MockStatic)
        self.assertIn("🧑 You: Test message", widgets[0].content)
        self.assertEqual(widgets[0].classes, "user-message")
        
    def test_compose_assistant_message(self):
        """Test composing an assistant message with markdown"""
        msg = ChatMessage("**Bold** message", is_user=False)
        widgets = list(msg.compose())
        
        self.assertEqual(len(widgets), 1)
        self.assertIsInstance(widgets[0], MockStatic)
        self.assertEqual(widgets[0].classes, "assistant-message")


class TestCommandPreview(unittest.TestCase):
    """Test the CommandPreview widget"""
    
    def test_command_preview_creation(self):
        """Test creating a command preview"""
        preview = CommandPreview("sudo nixos-rebuild switch")
        self.assertEqual(preview.command_text, "sudo nixos-rebuild switch")
        
    def test_compose_preview(self):
        """Test composing command preview with syntax highlighting"""
        preview = CommandPreview("nix-env -iA nixos.firefox")
        widgets = list(preview.compose())
        
        self.assertEqual(len(widgets), 1)
        # Would check for Panel and Syntax in real implementation


class TestHelpScreen(unittest.TestCase):
    """Test the HelpScreen"""
    
    def test_help_screen_bindings(self):
        """Test help screen has proper key bindings"""
        screen = HelpScreen()
        
        # Check bindings
        self.assertEqual(len(screen.BINDINGS), 2)
        self.assertEqual(screen.BINDINGS[0].key, "escape")
        self.assertEqual(screen.BINDINGS[0].action, "pop_screen")
        self.assertEqual(screen.BINDINGS[1].key, "q")
        
    def test_help_screen_content(self):
        """Test help screen displays help content"""
        screen = HelpScreen()
        widgets = list(screen.compose())
        
        self.assertEqual(len(widgets), 1)
        self.assertEqual(widgets[0].id, "help-text")


class TestNixHumanityApp(unittest.TestCase):
    """Test the main TUI application"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the core engine
        self.mock_core = Mock()
        self.mock_core.personality_system = Mock()
        self.mock_core.learning_system = Mock()
        
        # Patch NixForHumanityCore
        self.core_patcher = patch('nix_for_humanity.tui.app.NixForHumanityCore')
        self.mock_core_class = self.core_patcher.start()
        self.mock_core_class.return_value = self.mock_core
        
        # Patch uuid
        self.uuid_patcher = patch('nix_for_humanity.tui.app.uuid')
        self.mock_uuid = self.uuid_patcher.start()
        self.mock_uuid.uuid4.return_value.hex = "12345678"
        
    def tearDown(self):
        """Clean up patches"""
        self.core_patcher.stop()
        self.uuid_patcher.stop()
        
    def test_app_initialization(self):
        """Test app initializes with correct settings"""
        app = NixHumanityApp()
        
        # Check core was initialized
        self.mock_core_class.assert_called_once_with({
            'dry_run': False,
            'default_personality': 'friendly',
            'enable_learning': True,
            'collect_feedback': True
        })
        
        # Check initial state
        self.assertEqual(app.session_id, "12345678")
        self.assertIsNone(app.current_plan)
        self.assertEqual(app.personality, PersonalityStyle.FRIENDLY)
        self.assertEqual(app.last_query, "")
        self.assertEqual(app.last_response, "")
        self.assertFalse(app.awaiting_feedback_explanation)
        
    def test_app_metadata(self):
        """Test app has correct metadata"""
        app = NixHumanityApp()
        
        self.assertEqual(app.TITLE, "Nix for Humanity")
        self.assertEqual(app.SUB_TITLE, "Natural language interface for NixOS")
        
        # Check bindings
        self.assertEqual(len(app.BINDINGS), 4)
        binding_keys = [b.key for b in app.BINDINGS]
        self.assertIn("ctrl+p", binding_keys)
        self.assertIn("ctrl+h", binding_keys)
        self.assertIn("ctrl+c", binding_keys)
        self.assertIn("ctrl+q", binding_keys)
        
    def test_compose_widgets(self):
        """Test app composes all necessary widgets"""
        app = NixHumanityApp()
        app._widgets = {}  # Track widgets for testing
        
        widgets = list(app.compose())
        
        # Should have header, chat container, command preview, input area, status bar, footer
        widget_types = [type(w).__name__ for w in widgets]
        self.assertIn('MockHeader', widget_types)
        self.assertIn('MockFooter', widget_types)
        self.assertIn('MockContainer', widget_types)
        self.assertIn('MockLabel', widget_types)
        
        # Check specific IDs are present
        widget_ids = [w.id for w in widgets if hasattr(w, 'id')]
        self.assertIn('chat-container', widget_ids)
        self.assertIn('command-preview', widget_ids)
        self.assertIn('input-area', widget_ids)
        self.assertIn('status-bar', widget_ids)
        
    def test_on_mount_focuses_input(self):
        """Test that input is focused on mount"""
        app = NixHumanityApp()
        
        # Create mock input widget
        mock_input = Mock()
        app._widgets = {'user-input': mock_input}
        
        app.on_mount()
        
        # Should focus the input
        mock_input.focus.assert_called_once()
        
    def test_process_query_empty(self):
        """Test processing empty query does nothing"""
        app = NixHumanityApp()
        
        # Mock widgets
        mock_input = Mock()
        mock_input.value = "  "  # Empty/whitespace
        app._widgets = {'user-input': mock_input}
        
        app.process_query("  ")
        
        # Should not call core
        self.mock_core.plan.assert_not_called()
        
    def test_process_query_normal(self):
        """Test processing a normal query"""
        app = NixHumanityApp()
        
        # Set up mocks
        mock_input = Mock()
        mock_input.value = "install firefox"
        mock_chat = Mock()
        app._widgets = {
            'user-input': mock_input,
            'chat-container': mock_chat
        }
        
        # Mock plan response
        mock_plan = Mock()
        mock_plan.text = "I'll help you install Firefox"
        mock_plan.command = None
        self.mock_core.plan.return_value = mock_plan
        
        # Process query
        app.process_query("install firefox")
        
        # Check input was cleared
        self.assertEqual(mock_input.value, "")
        
        # Check chat messages were added
        self.assertEqual(mock_chat.mount.call_count, 2)  # User + assistant
        
        # Check query was sent to core
        self.mock_core.plan.assert_called_once()
        query_arg = self.mock_core.plan.call_args[0][0]
        self.assertEqual(query_arg.text, "install firefox")
        self.assertEqual(query_arg.personality, "friendly")
        self.assertEqual(query_arg.mode, ExecutionMode.DRY_RUN)
        
        # Check plan was stored
        self.assertEqual(app.current_plan, mock_plan)
        
    def test_process_query_with_command(self):
        """Test processing query that returns a command"""
        app = NixHumanityApp()
        
        # Set up mocks
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Mock plan with command
        mock_command = Mock()
        mock_command.program = "nix-env"
        mock_command.args = ["-iA", "nixos.firefox"]
        mock_command.requires_sudo = False
        
        mock_plan = Mock()
        mock_plan.text = "Installing Firefox..."
        mock_plan.command = mock_command
        mock_plan.requires_confirmation = False
        
        self.mock_core.plan.return_value = mock_plan
        
        # Patch show_command_preview
        with patch.object(app, 'show_command_preview') as mock_show:
            app.process_query("install firefox")
            
            # Should show command preview
            mock_show.assert_called_once_with(mock_plan)
            
    def test_process_query_symbiotic_mode(self):
        """Test processing query in symbiotic mode shows feedback UI"""
        app = NixHumanityApp()
        app.personality = PersonalityStyle.SYMBIOTIC
        
        # Set up mocks
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': Mock()
        }
        
        # Mock plan without command
        mock_plan = Mock()
        mock_plan.text = "Here's how to do that..."
        mock_plan.command = None
        self.mock_core.plan.return_value = mock_plan
        
        # Patch show_feedback_ui
        with patch.object(app, 'show_feedback_ui') as mock_feedback:
            app.process_query("how do I update?")
            
            # Should show feedback UI
            mock_feedback.assert_called_once_with("how do I update?", "Here's how to do that...")
            
    def test_show_command_preview(self):
        """Test showing command preview with buttons"""
        app = NixHumanityApp()
        
        # Mock preview container
        mock_preview = Mock()
        app._widgets = {'command-preview': mock_preview}
        
        # Create plan with command
        mock_command = Mock()
        mock_command.program = "nixos-rebuild"
        mock_command.args = ["switch"]
        mock_command.requires_sudo = True
        
        mock_plan = Mock()
        mock_plan.command = mock_command
        mock_plan.requires_confirmation = True
        
        # Show preview
        app.show_command_preview(mock_plan)
        
        # Should clear and add new content
        mock_preview.remove_children.assert_called_once()
        
        # Should add preview and buttons
        # In real test would check specific widgets added
        
    def test_execute_current_plan_success(self):
        """Test executing a plan successfully"""
        app = NixHumanityApp()
        
        # Set up current plan
        mock_command = Mock()
        app.current_plan = Mock(command=mock_command)
        
        # Mock widgets
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Mock execution result
        mock_result = Mock()
        mock_result.success = True
        mock_result.output = "Package installed successfully"
        self.mock_core.execute_plan.return_value = mock_result
        
        # Execute
        app.execute_current_plan()
        
        # Check execution
        self.mock_core.execute_plan.assert_called_once_with(app.current_plan, "tui-user")
        
        # Check success message added
        chat_calls = mock_chat.mount.call_args_list
        self.assertEqual(len(chat_calls), 1)
        message = chat_calls[0][0][0]
        self.assertIsInstance(message, ChatMessage)
        self.assertIn("✅ Command executed successfully", message.content)
        
        # Check preview cleared
        mock_preview.remove_children.assert_called_once()
        
        # Check plan reset
        self.assertIsNone(app.current_plan)
        
    def test_execute_current_plan_failure(self):
        """Test executing a plan that fails"""
        app = NixHumanityApp()
        
        # Set up current plan
        app.current_plan = Mock(command=Mock())
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': Mock()
        }
        
        # Mock execution failure
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Package not found"
        self.mock_core.execute_plan.return_value = mock_result
        
        # Execute
        app.execute_current_plan()
        
        # Check error message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("❌ Command failed", message.content)
        self.assertIn("Package not found", message.content)
        
    def test_cancel_current_plan(self):
        """Test canceling current plan"""
        app = NixHumanityApp()
        app.current_plan = Mock()
        
        # Mock widgets
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Cancel
        app.cancel_current_plan()
        
        # Check preview cleared
        mock_preview.remove_children.assert_called_once()
        
        # Check cancellation message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("❌ Command cancelled", message.content)
        
        # Check plan reset
        self.assertIsNone(app.current_plan)
        
    def test_show_feedback_ui(self):
        """Test showing feedback UI in symbiotic mode"""
        app = NixHumanityApp()
        
        # Mock preview container
        mock_preview = Mock()
        app._widgets = {'command-preview': mock_preview}
        
        # Show feedback UI
        app.show_feedback_ui("test query", "test response")
        
        # Check state saved
        self.assertEqual(app.last_query, "test query")
        self.assertEqual(app.last_response, "test response")
        
        # Check UI updated
        mock_preview.remove_children.assert_called_once()
        # Would check specific widgets in real test
        
    def test_handle_feedback_helpful(self):
        """Test handling helpful feedback"""
        app = NixHumanityApp()
        app.last_query = "install vim"
        app.last_response = "Installing vim..."
        
        # Mock widgets
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Mock Interaction class
        with patch('nix_for_humanity.tui.app.Interaction') as mock_interaction:
            # Handle feedback
            app.handle_feedback_button("feedback-helpful")
            
            # Check interaction recorded
            mock_interaction.assert_called_once()
            interaction_args = mock_interaction.call_args[1]
            self.assertEqual(interaction_args['query'], "install vim")
            self.assertEqual(interaction_args['response'], "Installing vim...")
            self.assertTrue(interaction_args['success'])
            
            # Check learning system called
            self.mock_core.learning_system.record_interaction.assert_called_once()
            
            # Check thank you message
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("Thank you", message.content)
            
    def test_handle_feedback_not_helpful(self):
        """Test handling not helpful feedback"""
        app = NixHumanityApp()
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': Mock()
        }
        
        # Handle feedback
        app.handle_feedback_button("feedback-not-helpful")
        
        # Check awaiting explanation
        self.assertTrue(app.awaiting_feedback_explanation)
        
        # Check prompt for explanation
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("What would have been a better response?", message.content)
        
    def test_handle_feedback_explanation(self):
        """Test handling detailed feedback explanation"""
        app = NixHumanityApp()
        app.last_query = "update system"
        app.last_response = "Run nixos-rebuild"
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Mock Interaction
        with patch('nix_for_humanity.tui.app.Interaction') as mock_interaction:
            # Provide explanation
            app.handle_feedback_explanation("Should explain what nixos-rebuild does")
            
            # Check interaction recorded with feedback
            interaction_args = mock_interaction.call_args[1]
            self.assertEqual(interaction_args['feedback_text'], "Should explain what nixos-rebuild does")
            self.assertFalse(interaction_args['success'])
            
            # Check thank you message
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("Thank you so much for explaining", message.content)
            
    def test_update_status(self):
        """Test updating status bar"""
        app = NixHumanityApp()
        app.session_id = "test-123"
        app.personality = PersonalityStyle.TECHNICAL
        
        # Mock status bar
        mock_status = Mock()
        app._widgets = {'status-bar': mock_status}
        
        # Update status
        app.update_status("Processing...")
        
        # Check update called with correct format
        mock_status.update.assert_called_once()
        status_text = mock_status.update.call_args[0][0]
        self.assertIn("Session: test-123", status_text)
        self.assertIn("Personality: technical", status_text)
        self.assertIn("Processing...", status_text)
        
    def test_toggle_personality(self):
        """Test toggling through personality styles"""
        app = NixHumanityApp()
        app.personality = PersonalityStyle.MINIMAL
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'status-bar': Mock()
        }
        
        # Toggle personality
        app.action_toggle_personality()
        
        # Check personality changed
        self.assertEqual(app.personality, PersonalityStyle.FRIENDLY)
        
        # Check core updated
        self.mock_core.personality_system.set_style.assert_called_once_with(PersonalityStyle.FRIENDLY)
        
        # Check notification shown
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("Personality changed to: friendly", message.content)
        
    def test_show_help(self):
        """Test showing help screen"""
        app = NixHumanityApp()
        app.screens = []
        
        # Show help
        app.action_show_help()
        
        # Check help screen pushed
        self.assertEqual(len(app.screens), 1)
        self.assertIsInstance(app.screens[0], HelpScreen)
        
    def test_clear_chat(self):
        """Test clearing chat history"""
        app = NixHumanityApp()
        
        # Mock widgets
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': mock_preview,
            'status-bar': Mock()
        }
        
        # Clear chat
        app.action_clear_chat()
        
        # Check chat cleared
        mock_chat.remove_children.assert_called_once()
        
        # Check welcome message added
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("Chat cleared", message.content)
        
        # Check preview cleared
        mock_preview.remove_children.assert_called_once()
        
    def test_quit_action(self):
        """Test quit action"""
        app = NixHumanityApp()
        app._exit_called = False
        
        # Quit
        app.action_quit()
        
        # Check exit called
        self.assertTrue(app._exit_called)
        
    def test_on_input_submitted(self):
        """Test handling input submission event"""
        app = NixHumanityApp()
        
        # Mock event
        mock_event = Mock()
        mock_event.value = "test query"
        
        # Patch process_query
        with patch.object(app, 'process_query') as mock_process:
            app.on_input_submitted(mock_event)
            
            # Check query processed
            mock_process.assert_called_once_with("test query")
            
    def test_on_button_pressed_send(self):
        """Test handling send button press"""
        app = NixHumanityApp()
        
        # Mock widgets
        mock_input = Mock()
        mock_input.value = "button query"
        app._widgets = {'user-input': mock_input}
        
        # Mock event
        mock_event = Mock()
        mock_event.button = Mock(id="send-button")
        
        # Patch process_query
        with patch.object(app, 'process_query') as mock_process:
            app.on_button_pressed(mock_event)
            
            # Check query processed
            mock_process.assert_called_once_with("button query")
            
    def test_on_button_pressed_execute(self):
        """Test handling execute button press"""
        app = NixHumanityApp()
        
        # Mock event
        mock_event = Mock()
        mock_event.button = Mock(id="execute-button")
        
        # Patch execute method
        with patch.object(app, 'execute_current_plan') as mock_execute:
            app.on_button_pressed(mock_event)
            
            # Check execution called
            mock_execute.assert_called_once()
            
    def test_on_button_pressed_cancel(self):
        """Test handling cancel button press"""
        app = NixHumanityApp()
        
        # Mock event
        mock_event = Mock()
        mock_event.button = Mock(id="cancel-button")
        
        # Patch cancel method
        with patch.object(app, 'cancel_current_plan') as mock_cancel:
            app.on_button_pressed(mock_event)
            
            # Check cancel called
            mock_cancel.assert_called_once()
            
    def test_on_button_pressed_feedback(self):
        """Test handling feedback button presses"""
        app = NixHumanityApp()
        
        # Test each feedback button
        feedback_buttons = ["feedback-helpful", "feedback-not-helpful", "feedback-explain"]
        
        for button_id in feedback_buttons:
            mock_event = Mock()
            mock_event.button = Mock(id=button_id)
            
            with patch.object(app, 'handle_feedback_button') as mock_feedback:
                app.on_button_pressed(mock_event)
                
                # Check feedback handler called
                mock_feedback.assert_called_once_with(button_id)


class TestRunFunction(unittest.TestCase):
    """Test the run function"""
    
    def test_run_creates_and_runs_app(self):
        """Test run function creates app and calls run"""
        with patch('nix_for_humanity.tui.app.NixHumanityApp') as mock_app_class:
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Run
            run()
            
            # Check app created and run
            mock_app_class.assert_called_once()
            mock_app.run.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests for TUI components"""
    
    def test_full_query_flow(self):
        """Test complete flow from query to execution"""
        app = NixHumanityApp()
        
        # Set up all necessary mocks
        app._widgets = {
            'user-input': Mock(value="install neovim"),
            'chat-container': Mock(),
            'command-preview': Mock(),
            'status-bar': Mock()
        }
        
        # Mock plan with command
        mock_command = Mock()
        mock_command.program = "nix-env"
        mock_command.args = ["-iA", "nixos.neovim"]
        mock_command.requires_sudo = False
        
        mock_plan = Mock()
        mock_plan.text = "Installing Neovim..."
        mock_plan.command = mock_command
        mock_plan.requires_confirmation = True
        
        self.mock_core.plan.return_value = mock_plan
        
        # Mock execution result
        mock_result = Mock()
        mock_result.success = True
        mock_result.output = "Neovim installed"
        self.mock_core.execute_plan.return_value = mock_result
        
        # Process query
        app.process_query("install neovim")
        
        # Verify plan created
        self.assertIsNotNone(app.current_plan)
        
        # Execute plan
        app.execute_current_plan()
        
        # Verify execution
        self.mock_core.execute_plan.assert_called_once()
        self.assertIsNone(app.current_plan)  # Should be cleared
        
    def test_symbiotic_feedback_flow(self):
        """Test complete symbiotic mode feedback flow"""
        app = NixHumanityApp()
        app.personality = PersonalityStyle.SYMBIOTIC
        
        # Set up mocks
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': Mock(),
            'command-preview': Mock()
        }
        
        # Mock plan
        mock_plan = Mock()
        mock_plan.text = "Here's the answer"
        mock_plan.command = None
        self.mock_core.plan.return_value = mock_plan
        
        # Process query
        app.process_query("how to update?")
        
        # Should store for feedback
        self.assertEqual(app.last_query, "how to update?")
        self.assertEqual(app.last_response, "Here's the answer")
        
        # Simulate not helpful feedback
        app.handle_feedback_button("feedback-not-helpful")
        self.assertTrue(app.awaiting_feedback_explanation)
        
        # Provide explanation
        with patch('nix_for_humanity.tui.app.Interaction'):
            app.handle_feedback_explanation("Need more detail")
            
            # Should record feedback
            self.mock_core.learning_system.record_interaction.assert_called()


if __name__ == '__main__':
    unittest.main()