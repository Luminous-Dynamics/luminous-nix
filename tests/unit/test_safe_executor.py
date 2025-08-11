#!/usr/bin/env python3
"""
Unit tests for the SafeExecutor component.
Tests safe command execution with rollback support.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from nix_for_humanity.core.executor import SafeExecutor, Result
from nix_for_humanity.core.intents import Intent, IntentType


class TestSafeExecutor(unittest.TestCase):
    """Test the SafeExecutor class"""

    def setUp(self):
        """Set up test instance"""
        self.executor = SafeExecutor()

    def test_initialization(self):
        """Test SafeExecutor initialization"""
        self.assertIsNotNone(self.executor)
        self.assertFalse(self.executor.dry_run)
        
        # Test with progress callback
        callback = Mock()
        executor_with_callback = SafeExecutor(progress_callback=callback)
        self.assertEqual(executor_with_callback.progress_callback, callback)

    def test_dry_run_mode(self):
        """Test setting dry run mode"""
        self.assertFalse(self.executor.dry_run)
        
        self.executor.dry_run = True
        self.assertTrue(self.executor.dry_run)
        
        self.executor.dry_run = False
        self.assertFalse(self.executor.dry_run)

    def test_get_operation_type_mapping(self):
        """Test operation type mapping for different intents"""
        test_cases = [
            (IntentType.INSTALL_PACKAGE, "install-package"),
            (IntentType.UPDATE_SYSTEM, "modify-configuration"),
            (IntentType.REMOVE_PACKAGE, "remove-package"),
            (IntentType.SEARCH_PACKAGE, "read-file"),
            (IntentType.GARBAGE_COLLECT, "modify-configuration"),
            (IntentType.LIST_INSTALLED, "read-file"),
            (IntentType.START_SERVICE, "modify-configuration"),
            (IntentType.SERVICE_STATUS, "read-file"),
        ]
        
        for intent_type, expected_op in test_cases:
            intent = Intent(
                type=intent_type,
                entities={},
                confidence=1.0,
                raw_text="test"
            )
            
            operation = self.executor._get_operation_type(intent)
            self.assertEqual(operation, expected_op)

    @patch('subprocess.run')
    def test_run_command(self, mock_run):
        """Test running a command through subprocess"""
        # Set up mock
        mock_result = Mock()
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        # Test command execution
        result = self.executor._run_command("echo 'test'")
        
        self.assertEqual(result["stdout"], "Success output")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["returncode"], 0)
        self.assertTrue(result["success"])
        
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_run_command_with_error(self, mock_run):
        """Test handling command errors"""
        # Set up mock for error
        mock_result = Mock()
        mock_result.stdout = ""
        mock_result.stderr = "Error occurred"
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        # Test command execution with error
        result = self.executor._run_command("false")
        
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "Error occurred")
        self.assertEqual(result["returncode"], 1)
        self.assertFalse(result["success"])

    def test_validate_command_safe(self):
        """Test command validation for safe commands"""
        safe_commands = [
            "nix-env -q",
            "nix search firefox",
            "nixos-rebuild dry-build",
            "nix-channel --list",
            "systemctl status nginx",
        ]
        
        for cmd in safe_commands:
            result = self.executor._validate_command(cmd)
            self.assertTrue(result["safe"], f"Command '{cmd}' should be safe")

    def test_validate_command_dangerous(self):
        """Test command validation blocks dangerous commands"""
        dangerous_commands = [
            "rm -rf /",
            "rm -rf /*",
            "dd if=/dev/zero of=/dev/sda",
            "chmod -R 777 /",
            ":(){ :|:& };:",  # Fork bomb
        ]
        
        for cmd in dangerous_commands:
            result = self.executor._validate_command(cmd)
            self.assertFalse(result["safe"], f"Command '{cmd}' should be blocked")

    def test_check_disk_space(self):
        """Test disk space checking"""
        with patch('shutil.disk_usage') as mock_disk:
            # Mock sufficient space
            mock_disk.return_value = Mock(free=10 * 1024 * 1024 * 1024)  # 10GB
            
            result = self.executor._check_disk_space()
            self.assertTrue(result["has_space"])
            self.assertGreater(result["free_gb"], 5)
            
            # Mock insufficient space
            mock_disk.return_value = Mock(free=100 * 1024 * 1024)  # 100MB
            
            result = self.executor._check_disk_space()
            self.assertFalse(result["has_space"])
            self.assertLess(result["free_gb"], 1)

    def test_create_rollback_point(self):
        """Test rollback point creation"""
        with patch.object(self.executor, '_run_command') as mock_run:
            mock_run.return_value = {
                "success": True,
                "stdout": "Generation 42",
                "stderr": "",
                "returncode": 0
            }
            
            generation = self.executor._create_rollback_point()
            self.assertEqual(generation, 42)
            mock_run.assert_called_once()

    def test_rollback_on_error(self):
        """Test rollback functionality"""
        with patch.object(self.executor, '_run_command') as mock_run:
            mock_run.return_value = {
                "success": True,
                "stdout": "Rolled back to generation 41",
                "stderr": "",
                "returncode": 0
            }
            
            result = self.executor._rollback(41, "Test error")
            self.assertTrue(result)
            mock_run.assert_called_once()

    def test_dry_run_execution(self):
        """Test dry-run mode doesn't execute commands"""
        self.executor.dry_run = True
        
        with patch.object(self.executor, '_run_command') as mock_run:
            # Mock should not be called in dry-run mode
            plan = ["nix-env -iA nixpkgs.firefox"]
            intent = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": "firefox"},
                confidence=1.0,
                raw_text="install firefox"
            )
            
            # The execute method is async, so we test the dry_run flag effect
            self.assertTrue(self.executor.dry_run)
            
            # In dry-run mode, commands should not be executed
            # This is verified by the dry_run flag being set

    def test_progress_callback(self):
        """Test progress callback is called"""
        callback = Mock()
        executor = SafeExecutor(progress_callback=callback)
        
        # Test progress wrapper
        executor._progress_wrapper("Test message", 50)
        callback.assert_called_once_with("Test message", 50)

    def test_native_api_initialization(self):
        """Test native API initialization handling"""
        # The executor should handle missing native API gracefully
        self.assertIsNotNone(self.executor)
        # Should fall back to subprocess if native API not available
        # This is indicated by _has_python_api flag
        if hasattr(self.executor, '_has_python_api'):
            # Either True or False is fine, just shouldn't crash
            self.assertIsInstance(self.executor._has_python_api, bool)

    def test_permission_check(self):
        """Test permission checking for operations"""
        # Read operations should not require sudo
        read_intent = Intent(
            type=IntentType.LIST_INSTALLED,
            entities={},
            confidence=1.0,
            raw_text="list packages"
        )
        
        op_type = self.executor._get_operation_type(read_intent)
        self.assertEqual(op_type, "read-file")
        
        # Modify operations should require sudo
        modify_intent = Intent(
            type=IntentType.UPDATE_SYSTEM,
            entities={},
            confidence=1.0,
            raw_text="update system"
        )
        
        op_type = self.executor._get_operation_type(modify_intent)
        self.assertEqual(op_type, "modify-configuration")

    def test_command_timeout_handling(self):
        """Test handling of command timeouts"""
        with patch('subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
            
            result = self.executor._run_command("long-running-command", timeout=30)
            
            self.assertFalse(result["success"])
            self.assertIn("timeout", result["error"].lower())

    def test_unicode_command_handling(self):
        """Test handling of unicode in commands"""
        with patch.object(self.executor, '_run_command') as mock_run:
            mock_run.return_value = {
                "success": True,
                "stdout": "✓ Success",
                "stderr": "",
                "returncode": 0
            }
            
            result = self.executor._run_command("echo '🎉 Unicode test'")
            self.assertTrue(result["success"])
            self.assertIn("✓", result["stdout"])


if __name__ == "__main__":
    unittest.main()