#!/usr/bin/env python3
"""
TUI Integration Tests for Nix for Humanity v1.1

Tests the complete integration between TUI and backend functionality.
"""

import asyncio

import pytest
from src.nix_humanity.core.backend import NixForHumanityBackend
from src.nix_humanity.ui.main_app import NixForHumanityApp

# REMOVED MOCK IMPORT: Mock, patch, AsyncMock
from textual.widgets import Button, Input


class TestTUIIntegration:
    """Test TUI integration with backend."""

    @pytest.fixture
    def mock_backend(self):
        """Create a mock backend for testing."""
        backend = Mock(spec=NixForHumanityBackend)
        backend.process_natural_language = AsyncMock(
            return_value={
                "success": True,
                "intent": "install",
                "response": "Installing firefox...",
                "confidence": 0.95,
            }
        )
        backend.get_system_info = AsyncMock(
            return_value={
                "nixos_version": "24.05",
                "system": "x86_64-linux",
                "packages_installed": 1234,
            }
        )
        return backend

    @pytest.mark.asyncio
    async def test_tui_launches_successfully(self):
        """Test that TUI launches without errors."""
        app = NixForHumanityApp()
        async with app.run_test() as pilot:
            # Check that app started
            assert app.is_running

            # Check title is displayed
            assert app.title == "Nix for Humanity v1.1"

    @pytest.mark.asyncio
    async def test_command_input_processing(self, mock_backend):
        """Test processing commands through TUI."""
        app = NixForHumanityApp()
        app.backend = mock_backend

        async with app.run_test() as pilot:
            # Find command input
            command_input = app.query_one("#command-input", Input)

            # Type a command
            await pilot.click(command_input)
            await pilot.type("install firefox")
            await pilot.press("enter")

            # Verify backend was called
            mock_backend.process_natural_language.assert_called_once()
            call_args = mock_backend.process_natural_language.call_args[0][0]
            assert call_args == "install firefox"

    @pytest.mark.asyncio
    async def test_response_display(self, mock_backend):
        """Test that responses are displayed correctly."""
        app = NixForHumanityApp()
        app.backend = mock_backend

        async with app.run_test() as pilot:
            # Submit a command
            command_input = app.query_one("#command-input", Input)
            await pilot.click(command_input)
            await pilot.type("install firefox")
            await pilot.press("enter")

            # Wait for response
            await pilot.pause(0.5)

            # Check response is displayed
            output = app.query_one("#output-display")
            assert "Installing firefox..." in output.renderable

    @pytest.mark.asyncio
    async def test_consciousness_orb_animation(self):
        """Test consciousness orb responds to activity."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            orb = app.query_one("#consciousness-orb")
            initial_state = orb.state

            # Trigger activity
            command_input = app.query_one("#command-input", Input)
            await pilot.click(command_input)
            await pilot.type("test command")

            # Check orb state changed
            await pilot.pause(0.1)
            assert orb.state != initial_state

    @pytest.mark.asyncio
    async def test_settings_panel_toggle(self):
        """Test settings panel can be toggled."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Settings should be hidden initially
            settings = app.query_one("#settings-panel")
            assert not settings.visible

            # Click settings button
            settings_btn = app.query_one("#settings-button", Button)
            await pilot.click(settings_btn)

            # Settings should now be visible
            assert settings.visible

            # Click again to hide
            await pilot.click(settings_btn)
            assert not settings.visible

    @pytest.mark.asyncio
    async def test_persona_switching(self):
        """Test switching between personas."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Open settings
            settings_btn = app.query_one("#settings-button", Button)
            await pilot.click(settings_btn)

            # Select Maya persona
            maya_btn = app.query_one("#persona-maya", Button)
            await pilot.click(maya_btn)

            # Check theme changed
            assert app.theme == "maya-adhd"
            assert app.current_persona == "maya"

    @pytest.mark.asyncio
    async def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts work correctly."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Test Ctrl+Q to quit
            with pytest.raises(SystemExit):
                await pilot.press("ctrl+q")

            # Test Ctrl+S for settings
            await pilot.press("ctrl+s")
            settings = app.query_one("#settings-panel")
            assert settings.visible

            # Test Ctrl+H for help
            await pilot.press("ctrl+h")
            help_modal = app.query_one("#help-modal")
            assert help_modal.visible

    @pytest.mark.asyncio
    async def test_error_handling_display(self, mock_backend):
        """Test error messages are displayed properly."""
        app = NixForHumanityApp()

        # Mock an error response
        mock_backend.process_natural_language = AsyncMock(
            return_value={
                "success": False,
                "error": "Command not recognized",
                "suggestions": ["Did you mean 'install'?"],
            }
        )
        app.backend = mock_backend

        async with app.run_test() as pilot:
            # Submit invalid command
            command_input = app.query_one("#command-input", Input)
            await pilot.click(command_input)
            await pilot.type("installl firefox")
            await pilot.press("enter")

            # Wait for response
            await pilot.pause(0.5)

            # Check error is displayed
            output = app.query_one("#output-display")
            assert "Command not recognized" in output.renderable
            assert "Did you mean 'install'?" in output.renderable

    @pytest.mark.asyncio
    async def test_loading_states(self, mock_backend):
        """Test loading indicators during operations."""
        app = NixForHumanityApp()

        # Mock slow response
        async def slow_response(*args):
            await asyncio.sleep(1)
            return {"success": True, "response": "Done"}

        mock_backend.process_natural_language = slow_response
        app.backend = mock_backend

        async with app.run_test() as pilot:
            # Submit command
            command_input = app.query_one("#command-input", Input)
            await pilot.click(command_input)
            await pilot.type("update system")
            await pilot.press("enter")

            # Check loading indicator appears
            await pilot.pause(0.1)
            loading = app.query_one("#loading-indicator")
            assert loading.visible

            # Wait for completion
            await pilot.pause(1.2)
            assert not loading.visible

    @pytest.mark.asyncio
    async def test_history_navigation(self):
        """Test command history navigation."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            command_input = app.query_one("#command-input", Input)

            # Submit multiple commands
            for cmd in ["install firefox", "update system", "search neovim"]:
                await pilot.click(command_input)
                await pilot.type(cmd)
                await pilot.press("enter")
                await pilot.pause(0.1)

            # Navigate history with up arrow
            await pilot.click(command_input)
            await pilot.press("up")  # Should show "search neovim"
            assert command_input.value == "search neovim"

            await pilot.press("up")  # Should show "update system"
            assert command_input.value == "update system"

            await pilot.press("down")  # Back to "search neovim"
            assert command_input.value == "search neovim"


class TestTUIAccessibility:
    """Test TUI accessibility features."""

    @pytest.mark.asyncio
    async def test_screen_reader_support(self):
        """Test screen reader announcements."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Check ARIA labels are present
            command_input = app.query_one("#command-input", Input)
            assert command_input.aria_label == "Natural language command input"

            # Check role attributes
            output = app.query_one("#output-display")
            assert output.aria_role == "log"

    @pytest.mark.asyncio
    async def test_high_contrast_mode(self):
        """Test high contrast mode for visibility."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Enable high contrast
            await pilot.press("ctrl+h")
            await pilot.press("c")  # Toggle contrast

            # Check theme changed
            assert app.theme == "high-contrast"

    @pytest.mark.asyncio
    async def test_keyboard_only_navigation(self):
        """Test complete keyboard navigation without mouse."""
        app = NixForHumanityApp()

        async with app.run_test() as pilot:
            # Tab through interface
            await pilot.press("tab")  # Focus command input
            await pilot.press("tab")  # Focus settings button
            await pilot.press("enter")  # Open settings

            # Navigate settings with keyboard
            await pilot.press("tab")  # Focus first setting
            await pilot.press("space")  # Toggle setting

            # Close with Escape
            await pilot.press("escape")
            settings = app.query_one("#settings-panel")
            assert not settings.visible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
