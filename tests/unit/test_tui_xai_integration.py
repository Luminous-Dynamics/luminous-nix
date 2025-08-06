#!/usr/bin/env python3
"""
Unit tests for TUI XAI Integration

Tests the integration between the TUI application and the XAI (Explainable AI) engine,
focusing on:
- XAI explanation panel rendering
- Keyboard shortcuts for XAI features
- Interactive explanation feedback
- Confidence-based styling
- Explanation level cycling
- Integration with symbiotic learning
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys

# Mock textual and rich before import
textual_mock = MagicMock()
textual_app_mock = MagicMock()
textual_widgets_mock = MagicMock()
textual_containers_mock = MagicMock()
rich_mock = MagicMock()

# Create mock widgets
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
        
    def remove(self):
        pass
        
    def remove_children(self):
        self.children = []

class MockStatic(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = args[0] if args else ''

class MockHorizontal(MockWidget):
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass

class MockButton(MockWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = args[0] if args else ''

# Set up mocks
textual_widgets_mock.Static = MockStatic
textual_widgets_mock.Button = MockButton
textual_containers_mock.Horizontal = MockHorizontal
rich_mock.panel = Mock()
rich_mock.Panel = Mock()

sys_modules = {
    'textual': textual_mock,
    'textual.app': textual_app_mock,
    'textual.widgets': textual_widgets_mock,
    'textual.containers': textual_containers_mock,
    'textual.screen': MagicMock(),
    'textual.reactive': MagicMock(),
    'textual.events': MagicMock(),
    'textual.message': MagicMock(),
    'textual.binding': MagicMock(),
    'rich': rich_mock,
    'rich.markdown': MagicMock(),
    'rich.panel': rich_mock.panel,
    'rich.syntax': MagicMock(),
    'rich.table': MagicMock(),
    'rich.text': MagicMock(),
}

with patch.dict('sys.modules', sys_modules):
    from nix_for_humanity.tui.app import XAIExplanationPanel, NixHumanityApp
    from nix_for_humanity.ai.xai_engine import (
        XAIEngine, ExplanationLevel, ConfidenceLevel, 
        Explanation, CausalFactor
    )
    from nix_for_humanity.core import PersonalityStyle


class TestXAIExplanationPanel(unittest.TestCase):
    """Test the XAI explanation panel widget"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock explanation
        self.mock_explanation = Mock()
        self.mock_explanation.simple_explanation = "I chose Firefox because it's popular"
        self.mock_explanation.detailed_explanation = "Firefox was selected based on popularity (70%) and user preferences (30%)"
        self.mock_explanation.technical_explanation = "Decision: package_selection -> firefox\nFactors: popularity=0.7, user_pref=0.3"
        self.mock_explanation.primary_reason = "High popularity score"
        self.mock_explanation.confidence = ConfidenceLevel.HIGH
        
    def test_panel_creation_simple(self):
        """Test creating explanation panel with simple level"""
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.SIMPLE
        )
        
        self.assertEqual(panel.explanation, self.mock_explanation)
        self.assertEqual(panel.level, ExplanationLevel.SIMPLE)
        
    def test_panel_creation_detailed(self):
        """Test creating explanation panel with detailed level"""
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.DETAILED
        )
        
        self.assertEqual(panel.level, ExplanationLevel.DETAILED)
        
    def test_panel_creation_technical(self):
        """Test creating explanation panel with technical level"""
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.TECHNICAL
        )
        
        self.assertEqual(panel.level, ExplanationLevel.TECHNICAL)
        
    def test_compose_high_confidence(self):
        """Test composing panel with high confidence styling"""
        self.mock_explanation.confidence = ConfidenceLevel.HIGH
        
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.SIMPLE
        )
        
        widgets = list(panel.compose())
        self.assertEqual(len(widgets), 1)
        self.assertIsInstance(widgets[0], MockStatic)
        
    def test_compose_medium_confidence(self):
        """Test composing panel with medium confidence styling"""
        self.mock_explanation.confidence = ConfidenceLevel.MEDIUM
        
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.DETAILED
        )
        
        widgets = list(panel.compose())
        self.assertEqual(len(widgets), 1)
        
    def test_compose_low_confidence(self):
        """Test composing panel with low confidence styling"""
        self.mock_explanation.confidence = ConfidenceLevel.LOW
        
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.TECHNICAL
        )
        
        widgets = list(panel.compose())
        self.assertEqual(len(widgets), 1)
        
    def test_compose_uncertain_confidence(self):
        """Test composing panel with uncertain confidence styling"""
        self.mock_explanation.confidence = ConfidenceLevel.UNCERTAIN
        
        panel = XAIExplanationPanel(
            explanation=self.mock_explanation,
            level=ExplanationLevel.SIMPLE
        )
        
        widgets = list(panel.compose())
        self.assertEqual(len(widgets), 1)


class TestTUIXAIIntegration(unittest.TestCase):
    """Test TUI integration with XAI engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the core engine
        self.mock_core = Mock()
        self.mock_core.personality_system = Mock()
        self.mock_core.learning_system = Mock()
        
        # Mock XAI engine
        self.mock_xai_engine = Mock()
        
        # Patch dependencies
        self.core_patcher = patch('nix_for_humanity.tui.app.NixForHumanityCore')
        self.mock_core_class = self.core_patcher.start()
        self.mock_core_class.return_value = self.mock_core
        
        self.xai_patcher = patch('nix_for_humanity.tui.app.XAIEngine')
        self.mock_xai_class = self.xai_patcher.start()
        self.mock_xai_class.return_value = self.mock_xai_engine
        
        self.uuid_patcher = patch('nix_for_humanity.tui.app.uuid')
        self.mock_uuid = self.uuid_patcher.start()
        self.mock_uuid.uuid4.return_value.hex = "test-session"
        
    def tearDown(self):
        """Clean up patches"""
        self.core_patcher.stop()
        self.xai_patcher.stop()
        self.uuid_patcher.stop()
        
    def test_app_initialization_with_xai(self):
        """Test app initializes with XAI engine"""
        app = NixHumanityApp()
        
        # Check XAI engine was initialized
        self.mock_xai_class.assert_called_once()
        
        # Check XAI state initialized
        self.assertFalse(app.show_explanations)
        self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)
        self.assertIsNone(app.current_explanation)
        
    def test_app_bindings_include_xai(self):
        """Test app includes XAI keyboard bindings"""
        app = NixHumanityApp()
        
        binding_keys = [b.key for b in app.BINDINGS]
        self.assertIn("ctrl+x", binding_keys)  # Toggle explanations
        self.assertIn("ctrl+e", binding_keys)  # Cycle explanation level
        
        binding_actions = [b.action for b in app.BINDINGS]
        self.assertIn("toggle_explanations", binding_actions)
        self.assertIn("cycle_explanation_level", binding_actions)
        
    def test_process_query_with_explanations_enabled(self):
        """Test processing query with XAI explanations enabled"""
        app = NixHumanityApp()
        app.show_explanations = True
        
        # Set up mocks
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': Mock(),
            'command-preview': Mock()
        }
        
        # Mock plan with decision info
        mock_plan = Mock()
        mock_plan.text = "Installing Firefox..."
        mock_plan.command = None
        mock_plan.decision_info = {"intent": "install", "package": "firefox"}
        mock_plan.intent = "install"
        self.mock_core.plan.return_value = mock_plan
        
        # Mock XAI explanation
        mock_explanation = Mock()
        self.mock_xai_engine.explain_decision.return_value = mock_explanation
        
        # Patch show_xai_explanation
        with patch.object(app, 'show_xai_explanation') as mock_show:
            app.process_query("install firefox")
            
            # Check XAI explanation was generated
            self.mock_xai_engine.explain_decision.assert_called_once()
            
            # Check explanation was shown
            mock_show.assert_called_once_with(mock_explanation)
            
            # Check explanation was stored
            self.assertEqual(app.current_explanation, mock_explanation)
            
    def test_process_query_with_explanations_disabled(self):
        """Test processing query with XAI explanations disabled"""
        app = NixHumanityApp()
        app.show_explanations = False
        
        # Set up mocks
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': Mock(),
            'command-preview': Mock()
        }
        
        # Mock plan
        mock_plan = Mock()
        mock_plan.text = "Installing Firefox..."
        mock_plan.command = None
        self.mock_core.plan.return_value = mock_plan
        
        app.process_query("install firefox")
        
        # Check XAI was not called
        self.mock_xai_engine.explain_decision.assert_not_called()
        
    def test_show_xai_explanation(self):
        """Test showing XAI explanation panel"""
        app = NixHumanityApp()
        app.explanation_level = ExplanationLevel.DETAILED
        
        # Mock preview container
        mock_preview = Mock()
        mock_preview.children = []  # No existing children
        app._widgets = {'command-preview': mock_preview}
        
        # Mock explanation
        mock_explanation = Mock()
        
        # Show explanation
        app.show_xai_explanation(mock_explanation)
        
        # Check explanation panel was mounted
        self.assertEqual(mock_preview.mount.call_count, 1)
        
        # Check the mounted widget is an XAI panel
        mounted_widget = mock_preview.mount.call_args[0][0]
        self.assertIsInstance(mounted_widget, XAIExplanationPanel)
        self.assertEqual(mounted_widget.explanation, mock_explanation)
        self.assertEqual(mounted_widget.level, ExplanationLevel.DETAILED)
        
    def test_show_xai_explanation_with_symbiotic_feedback(self):
        """Test showing XAI explanation includes feedback buttons in symbiotic mode"""
        app = NixHumanityApp()
        app.personality = PersonalityStyle.SYMBIOTIC
        
        # Mock preview container
        mock_preview = Mock()
        mock_preview.children = []
        app._widgets = {'command-preview': mock_preview}
        
        # Mock explanation
        mock_explanation = Mock()
        
        # Show explanation
        app.show_xai_explanation(mock_explanation)
        
        # Check both explanation panel and feedback buttons were mounted
        self.assertEqual(mock_preview.mount.call_count, 2)  # Panel + buttons
        
        # Check feedback buttons were created
        button_row = mock_preview.mount.call_args_list[1][0][0]
        self.assertIsInstance(button_row, MockHorizontal)
        
    def test_show_xai_explanation_removes_existing(self):
        """Test showing XAI explanation removes existing explanation"""
        app = NixHumanityApp()
        
        # Mock preview container with existing XAI panel
        existing_panel = Mock(spec=XAIExplanationPanel)
        mock_preview = Mock()
        mock_preview.children = [existing_panel]
        app._widgets = {'command-preview': mock_preview}
        
        # Mock explanation
        mock_explanation = Mock()
        
        # Show explanation
        app.show_xai_explanation(mock_explanation)
        
        # Check existing panel was removed
        existing_panel.remove.assert_called_once()
        
    def test_handle_explanation_feedback_helpful(self):
        """Test handling helpful explanation feedback"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        
        # Mock widgets
        mock_chat = Mock()
        mock_preview = Mock()
        app._widgets = {
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Handle helpful feedback
        app.handle_explanation_feedback("explanation-helpful")
        
        # Check positive message was added
        chat_calls = mock_chat.mount.call_args_list
        self.assertEqual(len(chat_calls), 1)
        message = chat_calls[0][0][0]
        self.assertIn("Great! I'm glad that explanation was helpful", message.content)
        
    def test_handle_explanation_feedback_confusing(self):
        """Test handling confusing explanation feedback"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Handle confusing feedback
        app.handle_explanation_feedback("explanation-confusing")
        
        # Check awaiting explanation flag set
        self.assertTrue(app.awaiting_feedback_explanation)
        
        # Check clarification request message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("I understand that was confusing", message.content)
        
    def test_handle_explanation_feedback_more_detail_simple_to_detailed(self):
        """Test requesting more detail upgrades from simple to detailed"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        app.explanation_level = ExplanationLevel.SIMPLE
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Patch show_xai_explanation to verify refresh
        with patch.object(app, 'show_xai_explanation') as mock_show:
            app.handle_explanation_feedback("explanation-more-detail")
            
            # Check level upgraded
            self.assertEqual(app.explanation_level, ExplanationLevel.DETAILED)
            
            # Check explanation refreshed
            mock_show.assert_called_once_with(app.current_explanation)
            
            # Check upgrade message
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("detailed explanations", message.content)
            
    def test_handle_explanation_feedback_more_detail_detailed_to_technical(self):
        """Test requesting more detail upgrades from detailed to technical"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        app.explanation_level = ExplanationLevel.DETAILED
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Patch show_xai_explanation
        with patch.object(app, 'show_xai_explanation') as mock_show:
            app.handle_explanation_feedback("explanation-more-detail")
            
            # Check level upgraded
            self.assertEqual(app.explanation_level, ExplanationLevel.TECHNICAL)
            
            # Check message mentions technical
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("technical explanations", message.content)
            
    def test_handle_explanation_feedback_more_detail_at_maximum(self):
        """Test requesting more detail when already at technical level"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        app.explanation_level = ExplanationLevel.TECHNICAL
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        app.handle_explanation_feedback("explanation-more-detail")
        
        # Check level stays technical
        self.assertEqual(app.explanation_level, ExplanationLevel.TECHNICAL)
        
        # Check maximum message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("maximum explanations", message.content)
        
    def test_handle_explanation_feedback_no_current_explanation(self):
        """Test handling explanation feedback with no current explanation"""
        app = NixHumanityApp()
        app.current_explanation = None
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Handle feedback - should do nothing
        app.handle_explanation_feedback("explanation-helpful")
        
        # Check no messages added
        mock_chat.mount.assert_not_called()
        
    def test_action_toggle_explanations_enable(self):
        """Test toggling explanations from disabled to enabled"""
        app = NixHumanityApp()
        app.show_explanations = False
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Toggle explanations
        app.action_toggle_explanations()
        
        # Check explanations enabled
        self.assertTrue(app.show_explanations)
        
        # Check notification message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("XAI explanations enabled", message.content)
        self.assertIn("explain my reasoning", message.content)
        
    def test_action_toggle_explanations_disable(self):
        """Test toggling explanations from enabled to disabled"""
        app = NixHumanityApp()
        app.show_explanations = True
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Toggle explanations
        app.action_toggle_explanations()
        
        # Check explanations disabled
        self.assertFalse(app.show_explanations)
        
        # Check notification message
        chat_calls = mock_chat.mount.call_args_list
        message = chat_calls[0][0][0]
        self.assertIn("XAI explanations disabled", message.content)
        self.assertIn("work silently", message.content)
        
    def test_action_cycle_explanation_level_simple_to_detailed(self):
        """Test cycling explanation level from simple to detailed"""
        app = NixHumanityApp()
        app.explanation_level = ExplanationLevel.SIMPLE
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Patch refresh_explanation
        with patch.object(app, 'refresh_explanation') as mock_refresh:
            app.action_cycle_explanation_level()
            
            # Check level cycled
            self.assertEqual(app.explanation_level, ExplanationLevel.DETAILED)
            
            # Check notification
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("Explanation level: Detailed", message.content)
            
            # Check explanation refreshed
            mock_refresh.assert_called_once()
            
    def test_action_cycle_explanation_level_detailed_to_technical(self):
        """Test cycling explanation level from detailed to technical"""
        app = NixHumanityApp()
        app.explanation_level = ExplanationLevel.DETAILED
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Patch refresh_explanation
        with patch.object(app, 'refresh_explanation') as mock_refresh:
            app.action_cycle_explanation_level()
            
            # Check level cycled
            self.assertEqual(app.explanation_level, ExplanationLevel.TECHNICAL)
            
            # Check notification mentions technical
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("Explanation level: Technical", message.content)
            
    def test_action_cycle_explanation_level_technical_to_simple(self):
        """Test cycling explanation level from technical back to simple"""
        app = NixHumanityApp()
        app.explanation_level = ExplanationLevel.TECHNICAL
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # Patch refresh_explanation
        with patch.object(app, 'refresh_explanation') as mock_refresh:
            app.action_cycle_explanation_level()
            
            # Check level cycled back to simple
            self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)
            
            # Check notification mentions simple
            chat_calls = mock_chat.mount.call_args_list
            message = chat_calls[0][0][0]
            self.assertIn("Explanation level: Simple", message.content)
            
    def test_refresh_explanation(self):
        """Test refreshing current explanation with new detail level"""
        app = NixHumanityApp()
        app.explanation_level = ExplanationLevel.TECHNICAL
        app.current_explanation = Mock()
        
        # Mock preview container with existing XAI panel
        existing_panel = Mock(spec=XAIExplanationPanel)
        existing_panel.explanation = app.current_explanation
        mock_preview = Mock()
        mock_preview.children = [existing_panel]
        app._widgets = {'command-preview': mock_preview}
        
        # Refresh explanation
        app.refresh_explanation()
        
        # Check existing panel was removed
        existing_panel.remove.assert_called_once()
        
        # Check new panel was mounted with updated level
        mock_preview.mount.assert_called_once()
        new_panel = mock_preview.mount.call_args[0][0]
        self.assertIsInstance(new_panel, XAIExplanationPanel)
        self.assertEqual(new_panel.level, ExplanationLevel.TECHNICAL)
        self.assertEqual(new_panel.explanation, app.current_explanation)
        
    def test_refresh_explanation_no_existing_panel(self):
        """Test refreshing explanation when no panel exists"""
        app = NixHumanityApp()
        app.current_explanation = Mock()
        
        # Mock preview container with no XAI panel
        mock_preview = Mock()
        mock_preview.children = [Mock()]  # Some other widget
        app._widgets = {'command-preview': mock_preview}
        
        # Refresh explanation - should do nothing
        app.refresh_explanation()
        
        # Check nothing was mounted
        mock_preview.mount.assert_not_called()
        
    def test_hide_explanation(self):
        """Test hiding current XAI explanation"""
        app = NixHumanityApp()
        
        # Mock preview container
        mock_preview = Mock()
        app._widgets = {'command-preview': mock_preview}
        
        # Hide explanation
        app.hide_explanation()
        
        # Check preview container was cleared
        mock_preview.remove_children.assert_called_once()
        
    def test_button_pressed_explanation_feedback(self):
        """Test handling explanation feedback button presses"""
        app = NixHumanityApp()
        
        explanation_buttons = [
            "explanation-helpful", 
            "explanation-confusing", 
            "explanation-more-detail"
        ]
        
        for button_id in explanation_buttons:
            mock_event = Mock()
            mock_event.button = Mock(id=button_id)
            
            with patch.object(app, 'handle_explanation_feedback') as mock_feedback:
                app.on_button_pressed(mock_event)
                
                # Check feedback handler called
                mock_feedback.assert_called_once_with(button_id)


class TestXAIIntegrationEnd2End(unittest.TestCase):
    """End-to-end integration tests for XAI in TUI"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock all dependencies
        self.core_patcher = patch('nix_for_humanity.tui.app.NixForHumanityCore')
        self.mock_core_class = self.core_patcher.start()
        self.mock_core = Mock()
        self.mock_core_class.return_value = self.mock_core
        
        self.xai_patcher = patch('nix_for_humanity.tui.app.XAIEngine')
        self.mock_xai_class = self.xai_patcher.start()
        self.mock_xai_engine = Mock()
        self.mock_xai_class.return_value = self.mock_xai_engine
        
        self.uuid_patcher = patch('nix_for_humanity.tui.app.uuid')
        self.mock_uuid = self.uuid_patcher.start()
        self.mock_uuid.uuid4.return_value.hex = "test-session"
        
    def tearDown(self):
        """Clean up patches"""
        self.core_patcher.stop()
        self.xai_patcher.stop()
        self.uuid_patcher.stop()
        
    def test_complete_xai_explanation_flow(self):
        """Test complete flow of XAI explanation from query to feedback"""
        app = NixHumanityApp()
        app.show_explanations = True
        app.explanation_level = ExplanationLevel.SIMPLE
        app.personality = PersonalityStyle.SYMBIOTIC
        
        # Set up widgets
        mock_chat = Mock()
        mock_preview = Mock()
        mock_preview.children = []
        app._widgets = {
            'user-input': Mock(value=""),
            'chat-container': mock_chat,
            'command-preview': mock_preview
        }
        
        # Mock plan with decision info
        mock_plan = Mock()
        mock_plan.text = "Installing Firefox..."
        mock_plan.command = None
        mock_plan.decision_info = {"intent": "install"}
        mock_plan.intent = "install"
        self.mock_core.plan.return_value = mock_plan
        
        # Mock XAI explanation
        mock_explanation = Mock()
        mock_explanation.simple_explanation = "I chose Firefox because it's popular"
        mock_explanation.confidence = ConfidenceLevel.HIGH
        mock_explanation.primary_reason = "High popularity"
        self.mock_xai_engine.explain_decision.return_value = mock_explanation
        
        # 1. Process query
        app.process_query("install firefox")
        
        # Check explanation was generated and shown
        self.mock_xai_engine.explain_decision.assert_called_once()
        self.assertEqual(app.current_explanation, mock_explanation)
        
        # Check explanation panel and feedback buttons were mounted
        self.assertEqual(mock_preview.mount.call_count, 2)  # Panel + buttons
        
        # 2. User requests more detail
        app.handle_explanation_feedback("explanation-more-detail")
        
        # Check level upgraded to detailed
        self.assertEqual(app.explanation_level, ExplanationLevel.DETAILED)
        
        # 3. User finds it helpful
        app.handle_explanation_feedback("explanation-helpful")
        
        # Check positive feedback message
        help_message = mock_chat.mount.call_args_list[-1][0][0]
        self.assertIn("glad that explanation was helpful", help_message.content)
        
    def test_xai_toggle_and_cycle_workflow(self):
        """Test workflow of toggling explanations and cycling levels"""
        app = NixHumanityApp()
        app.show_explanations = False
        app.explanation_level = ExplanationLevel.SIMPLE
        
        # Mock widgets
        mock_chat = Mock()
        app._widgets = {'chat-container': mock_chat}
        
        # 1. Toggle explanations on
        app.action_toggle_explanations()
        
        self.assertTrue(app.show_explanations)
        enable_message = mock_chat.mount.call_args_list[-1][0][0]
        self.assertIn("XAI explanations enabled", enable_message.content)
        
        # 2. Cycle through explanation levels
        app.action_cycle_explanation_level()  # Simple -> Detailed
        self.assertEqual(app.explanation_level, ExplanationLevel.DETAILED)
        
        app.action_cycle_explanation_level()  # Detailed -> Technical
        self.assertEqual(app.explanation_level, ExplanationLevel.TECHNICAL)
        
        app.action_cycle_explanation_level()  # Technical -> Simple
        self.assertEqual(app.explanation_level, ExplanationLevel.SIMPLE)
        
        # 3. Toggle explanations off
        app.action_toggle_explanations()
        
        self.assertFalse(app.show_explanations)
        disable_message = mock_chat.mount.call_args_list[-1][0][0]
        self.assertIn("XAI explanations disabled", disable_message.content)


if __name__ == '__main__':
    unittest.main()