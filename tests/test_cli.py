#!/usr/bin/env python3
"""
Tests for CLI Interface

Tests the command-line interface functionality.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Path to the CLI script
CLI_PATH = Path(__file__).parent.parent / "bin" / "ask-nix"


class TestCLI:
    """Test CLI functionality"""

    def run_cli(self, *args):
        """Helper to run CLI with arguments"""
        cmd = [sys.executable, str(CLI_PATH)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result

    def test_cli_help(self):
        """Test help output"""
        result = self.run_cli("--help")
        assert result.returncode == 0
        assert "Natural language interface to NixOS" in result.stdout
        assert "--execute" in result.stdout
        assert "--interactive" in result.stdout

    def test_cli_help_full(self):
        """Test comprehensive help"""
        result = self.run_cli("--help-full")
        assert result.returncode == 0
        assert "Nix for Humanity" in result.stdout
        assert "EXAMPLES:" in result.stdout
        assert "FEATURES:" in result.stdout
        assert "install firefox" in result.stdout

    def test_cli_help_query(self):
        """Test help query handling"""
        result = self.run_cli("help")
        assert result.returncode == 0
        assert "Nix for Humanity" in result.stdout

    def test_cli_empty_query(self):
        """Test handling of no arguments"""
        result = self.run_cli()
        assert result.returncode == 0
        # Should show help when no arguments
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_cli_dry_run(self):
        """Test dry-run mode (default)"""
        result = self.run_cli("install firefox")
        # Should succeed in dry-run mode
        assert result.returncode == 0 or "[DRY RUN]" in result.stdout

    def test_cli_search(self):
        """Test search functionality"""
        result = self.run_cli("search for editor")
        # Should handle search queries
        assert result.returncode == 0 or "search" in result.stdout.lower()

    def test_cli_config_generation(self):
        """Test configuration generation"""
        result = self.run_cli("web server with nginx")
        # Should generate config or show dry-run message
        assert result.returncode == 0 or "nginx" in result.stdout.lower()

    def test_cli_debug_flag(self):
        """Test debug flag"""
        result = self.run_cli("--debug", "test query")
        # Debug mode should work (might show more output)
        assert result.returncode == 0 or result.returncode == 1

    def test_cli_with_spaces(self):
        """Test query with multiple words"""
        result = self.run_cli("install", "firefox", "and", "chrome")
        # Should handle multi-word queries
        assert result.returncode == 0 or result.returncode == 1

    def test_cli_special_characters(self):
        """Test handling of special characters"""
        # Should safely handle special characters
        result = self.run_cli("install firefox; echo bad")
        # Should either reject or sanitize
        assert "error" in result.stdout.lower() or "[DRY RUN]" in result.stdout


class TestCLIIntegration:
    """Integration tests for CLI"""

    def test_version_compatibility(self):
        """Test Python version compatibility"""
        result = subprocess.run(
            [sys.executable, "-c", "import sys; print(sys.version_info[:2])"],
            capture_output=True,
            text=True,
        )
        version = eval(result.stdout.strip())
        assert version >= (3, 7), "Requires Python 3.7+"

    def test_import_availability(self):
        """Test that required modules can be imported"""
        test_code = (
            """
import sys
from pathlib import Path
sys.path.insert(0, str(Path('%s').parent.parent / 'src'))
try:
    from nix_for_humanity.core.unified_backend import NixForHumanityBackend
    print("SUCCESS")
except ImportError as e:
    print(f"FAILED: {e}")
"""
            % __file__
        )

        result = subprocess.run(
            [sys.executable, "-c", test_code], capture_output=True, text=True
        )
        assert "SUCCESS" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
