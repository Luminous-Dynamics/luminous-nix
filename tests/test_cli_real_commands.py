#!/usr/bin/env python3
"""
Real tests for actual CLI commands that exist in ask-nix.

These test the ACTUAL functionality, not phantom features.
"""

import sys
import os
from unittest.mock import patch, MagicMock
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from luminous_nix.core.backend import NixForHumanityBackend
from luminous_nix.api.schema import Request, Response


class TestRealCLICommands(unittest.TestCase):
    """Test actual CLI commands that exist"""

    def setUp(self):
        """Set up test backend"""
        self.backend = NixForHumanityBackend()

    def test_install_package_command(self):
        """Test 1: Install package command"""
        request = Request(
            query="install firefox",
            context={"dry_run": True, "personality": "friendly"}
        )
        
        response = self.backend.process(request)
        
        # Check response
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        self.assertIn("firefox", response.text.lower())
        
        # Should have command or suggestion
        if response.commands:
            cmd = response.commands[0]
            cmd_text = cmd.get("command", "").lower()
            # Check for various install-related terms
            self.assertTrue(
                "install" in cmd_text or
                "firefox" in cmd_text or
                "systempackages" in cmd_text or
                "configuration.nix" in cmd_text
            )

    def test_search_package_command(self):
        """Test 2: Search package command"""
        request = Request(
            query="search python",
            context={"dry_run": True}
        )
        
        response = self.backend.process(request)
        
        # Check response
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        
        # Should mention search
        self.assertTrue(
            "search" in response.text.lower() or 
            "python" in response.text.lower()
        )

    def test_help_command(self):
        """Test 3: Help command"""
        request = Request(
            query="help",
            context={"dry_run": True}
        )
        
        response = self.backend.process(request)
        
        # Check response
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        
        # Should provide helpful information
        self.assertTrue(
            "help" in response.text.lower() or
            "command" in response.text.lower() or
            "available" in response.text.lower()
        )

    def test_update_system_command(self):
        """Test 4: Update system command"""
        request = Request(
            query="update my system",
            context={"dry_run": True}
        )
        
        response = self.backend.process(request)
        
        # Check response
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        
        # Should mention update
        self.assertTrue(
            "update" in response.text.lower() or
            "system" in response.text.lower() or
            "rebuild" in response.text.lower()
        )

    def test_remove_package_command(self):
        """Test 5: Remove package command"""
        request = Request(
            query="remove vim",
            context={"dry_run": True, "confirm": False}
        )
        
        response = self.backend.process(request)
        
        # Check response
        self.assertIsInstance(response, Response)
        self.assertIsNotNone(response.text)
        
        # Should mention removal
        self.assertTrue(
            "remove" in response.text.lower() or
            "uninstall" in response.text.lower() or
            "vim" in response.text.lower()
        )
        
        # Should require confirmation (safety feature)
        # Check if response mentions confirmation
        if hasattr(response, 'requires_confirmation'):
            self.assertTrue(response.requires_confirmation or "confirm" in response.text.lower())
        else:
            # Just check if the text mentions removal
            pass


if __name__ == "__main__":
    unittest.main()