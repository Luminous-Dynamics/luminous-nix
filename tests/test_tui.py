#!/usr/bin/env python3
"""
Tests for Nix for Humanity TUI
Ensuring beautiful, accessible, and functional interface
"""

from textual.pilot import Pilot
from textual.widgets import Input, Button
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tui.app import NixForHumanityTUI
from tui.enhanced_app import NixForHumanityEnhanced
from tui.widgets import (
    ConversationMessage, StatusIndicator, PersonalitySelector,
    CommandPreview, EducationalPanel
)


@pytest.mark.asyncio
async def test_app_startup():
    """Test that the app starts correctly"""
    app = NixForHumanityTUI()
    async with app.run_test() as pilot:
        # Check that header exists
        self.assertTrue(app.query_one("Header"))
        
        # Check that input exists
        self.assertTrue(app.query_one("#user-input", Input))
        
        # Check that conversation area exists
        self.assertTrue(app.query_one("#conversation"))


@pytest.mark.asyncio
async def test_message_sending():
    """Test sending a message"""
    app = NixForHumanityTUI()
    async with app.run_test() as pilot:
        # Get input widget
        input_widget = app.query_one("#user-input", Input)
        
        # Type a message
        input_widget.value = "test message"
        
        # Send it
        await pilot.press("enter")
        
        # Check that input was cleared
        self.assertEqual(input_widget.value, "")
        
        # Check that message appears in conversation
        # (This would need backend mocking for full test)


@pytest.mark.asyncio
async def test_quick_actions():
    """Test quick action buttons"""
    app = NixForHumanityTUI()
    async with app.run_test() as pilot:
        # Find update button
        update_btn = app.query_one("#btn-update", Button)
        
        # Click it
        await pilot.click(update_btn)
        
        # Would check for response in conversation


@pytest.mark.asyncio 
async def test_keyboard_shortcuts():
    """Test keyboard navigation"""
    app = NixForHumanityTUI()
    async with app.run_test() as pilot:
        # Test help
        await pilot.press("f1")
        
        # Test clear
        await pilot.press("ctrl+l")
        
        # Test quit (but don't actually quit in test)
        # await pilot.press("ctrl+c")


def test_conversation_message():
    """Test conversation message widget"""
    msg = ConversationMessage("Hello", is_user=True)
    self.assertEqual(msg.text, "Hello")
    self.assertEqual(msg.is_user, True)
    self.assertIsNotNone(msg.timestamp)


def test_status_indicator():
    """Test status indicator states"""
    indicator = StatusIndicator()
    
    # Test all states
    for state in ["idle", "thinking", "processing", "success", "error"]:
        indicator.state = state
        rendered = indicator.render()
        self.assertTrue(rendered)  # Should produce output
        self.assertIn(indicator.STATES[state][1], rendered)


def test_personality_selector():
    """Test personality selector"""
    selector = PersonalitySelector()
    
    # Default should be friendly
    self.assertEqual(selector.selected, "friendly")
    
    # Test changing selection
    selector.selected = "technical"
    self.assertEqual(selector.selected, "technical")


def test_command_preview():
    """Test command preview widget"""
    commands = [
        {"command": "nix-env -iA nixos.firefox", "description": "Install Firefox"},
        {"command": "sudo nixos-rebuild switch", "description": "Rebuild system"}
    ]
    
    preview = CommandPreview(commands)
    self.assertEqual(len(preview.commands), 2)


def test_educational_panel():
    """Test educational panel"""
    education = {
        "what_happened": "System was updated",
        "why_it_matters": "Ensures reproducibility",
        "next_steps": "You can rollback anytime"
    }
    
    panel = EducationalPanel(education)
    self.assertEqual(panel.education, education)


@pytest.mark.asyncio
async def test_enhanced_app():
    """Test enhanced app features"""
    app = NixForHumanityEnhanced()
    async with app.run_test() as pilot:
        # Check for enhanced widgets
        self.assertTrue(app.query_one("AnimatedLogo"))
        self.assertTrue(app.query_one("StatusIndicator"))
        self.assertTrue(app.query_one("PersonalitySelector"))
        
        # Check personality switching
        await pilot.press("ctrl+p")


# Integration tests would go here
# These would test the full flow with backend integration


if __name__ == "__main__":
    pytest.main([__file__, "-v"])