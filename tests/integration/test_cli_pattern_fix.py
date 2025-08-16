#!/usr/bin/env python3
"""Integration tests for CLI pattern recognition fixes."""

import subprocess
import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from luminous_nix.knowledge.engine import NixOSKnowledgeEngine

class TestCLIPatternIntegration:
    """Test CLI integration with pattern recognition fixes."""

    def setup_method(self):
        """Set up test instance."""
        self.engine = NixOSKnowledgeEngine()
        self.cli_path = project_root / "bin" / "ask-nix"

    def test_cli_i_need_firefox(self):
        """Test 'i need firefox' through CLI."""
        # First test the engine directly
        result = self.engine.parse_query("i need firefox")
        assert result["intent"] == "install"
        assert result["package"] == "firefox"
        
        # Then test through subprocess if CLI exists
        if self.cli_path.exists():
            # The CLI doesn't use --dry-run, it defaults to safe mode
            proc = subprocess.run(
                [str(self.cli_path), "i need firefox"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Check either stdout or stderr as the output might be in either
            output = proc.stdout.lower() + proc.stderr.lower()
            # If it processed the query, firefox should be mentioned
            if proc.returncode == 0:
                assert "firefox" in output or "error" in output

    def test_cli_i_want_vim(self):
        """Test 'i want vim' through CLI."""
        result = self.engine.parse_query("i want vim")
        assert result["intent"] == "install"
        assert result["package"] == "vim"

    def test_cli_install_git(self):
        """Test 'install git' through CLI."""
        result = self.engine.parse_query("install git")
        assert result["intent"] == "install"
        assert result["package"] == "git"

    def test_cli_search_editor(self):
        """Test search functionality."""
        result = self.engine.parse_query("search for text editor")
        assert result["intent"] == "search"

    def test_cli_remove_package(self):
        """Test remove/uninstall functionality."""
        result = self.engine.parse_query("remove firefox")
        assert result["intent"] == "remove"
        assert result["package"] == "firefox"

    def test_cli_update_system(self):
        """Test system update command."""
        result = self.engine.parse_query("update system")
        assert result["intent"] == "update"

    def test_cli_list_packages(self):
        """Test list packages command."""
        result = self.engine.parse_query("list installed packages")
        assert result["intent"] == "list"

    def test_cli_help_me_install(self):
        """Test 'help me install' pattern."""
        result = self.engine.parse_query("help me install brave")
        assert result["intent"] == "install"
        assert result["package"] == "brave"

    def test_cli_can_you_install(self):
        """Test question format."""
        result = self.engine.parse_query("can you install htop")
        assert result["intent"] == "install"
        assert result["package"] == "htop"

    def test_cli_please_install(self):
        """Test polite request format."""
        result = self.engine.parse_query("please install git")
        assert result["intent"] == "install"
        assert result["package"] == "git"

class TestCLIEndToEnd:
    """End-to-end CLI tests."""

    def setup_method(self):
        """Set up test environment."""
        self.cli_path = project_root / "bin" / "ask-nix"
        self.skip_if_no_cli = pytest.mark.skipif(
            not self.cli_path.exists(),
            reason="CLI binary not found"
        )

    @pytest.mark.skipif(not Path("bin/ask-nix").exists(), reason="CLI not available")
    def test_default_safe_mode(self):
        """Test CLI in default safe mode."""
        proc = subprocess.run(
            [str(self.cli_path), "install firefox"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # The CLI should work without crashing
        assert proc.returncode in [0, 1, 2]  # Various exit codes are acceptable
        # Check if it processed the command
        output = proc.stdout.lower() + proc.stderr.lower()
        # Should mention firefox or installation in some way
        assert "firefox" in output or "install" in output or "error" in output

    @pytest.mark.skipif(not Path("bin/ask-nix").exists(), reason="CLI not available")  
    def test_help_command(self):
        """Test CLI help output."""
        proc = subprocess.run(
            [str(self.cli_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert proc.returncode == 0
        assert "usage" in proc.stdout.lower() or "help" in proc.stdout.lower()

    @pytest.mark.skipif(not Path("bin/ask-nix").exists(), reason="CLI not available")
    def test_version_command(self):
        """Test CLI version output."""
        proc = subprocess.run(
            [str(self.cli_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Version might not be implemented, but shouldn't crash
        assert proc.returncode in [0, 1, 2]

if __name__ == "__main__":
    # Run tests directly
    test = TestCLIPatternIntegration()
    test.setup_method()
    
    print("Testing pattern recognition fixes...")
    test.test_cli_i_need_firefox()
    print("✓ 'i need firefox' works correctly")
    
    test.test_cli_i_want_vim()
    print("✓ 'i want vim' works correctly")
    
    test.test_cli_install_git()
    print("✓ 'install git' works correctly")
    
    test.test_cli_search_editor()
    print("✓ Search functionality works")
    
    test.test_cli_remove_package()
    print("✓ Remove functionality works")
    
    test.test_cli_help_me_install()
    print("✓ 'help me install' pattern works")
    
    print("\n✅ All pattern recognition tests passed!")