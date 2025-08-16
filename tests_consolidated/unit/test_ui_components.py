"""
Tests for UI components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from luminous_nix.ui.consolidated_ui import (
    ConsolidatedUI, UIConfig, SimpleUI
)


class TestUIComponents:
    """Test UI components."""
    
    def test_ui_config_defaults(self):
        """Test default UI configuration."""
        config = UIConfig()
        
        assert config.theme == "default"
        assert config.show_hints is True
        assert config.enable_animations is True
        assert config.max_history == 100
    
    def test_simple_ui_init(self):
        """Test simple UI initialization."""
        ui = SimpleUI()
        
        assert ui is not None
        assert hasattr(ui, 'prompt')
        assert hasattr(ui, 'display')
    
    def test_simple_ui_prompt(self, monkeypatch):
        """Test simple UI prompting."""
        ui = SimpleUI()
        
        # Mock input
        monkeypatch.setattr('builtins.input', lambda _: "test command")
        
        result = ui.prompt()
        assert result == "test command"
    
    def test_simple_ui_display(self, capsys):
        """Test simple UI display."""
        ui = SimpleUI()
        
        ui.display("Test message")
        
        captured = capsys.readouterr()
        assert "Test message" in captured.out
    
    @patch('luminous_nix.ui.consolidated_ui.TEXTUAL_AVAILABLE', True)
    def test_consolidated_ui_with_textual(self):
        """Test ConsolidatedUI when Textual is available."""
        config = UIConfig(theme="dark")
        ui = ConsolidatedUI(config)
        
        assert ui.config.theme == "dark"
    
    @patch('luminous_nix.ui.consolidated_ui.TEXTUAL_AVAILABLE', False) 
    def test_consolidated_ui_fallback(self):
        """Test ConsolidatedUI fallback when Textual not available."""
        ui = ConsolidatedUI()
        
        # Should fallback to SimpleUI behavior
        assert hasattr(ui, 'prompt')
        assert hasattr(ui, 'display')
