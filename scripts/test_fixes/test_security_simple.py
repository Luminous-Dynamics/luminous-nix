#!/usr/bin/env python3
"""
Simple security test without pytest
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.security.validator import InputValidator


def test_security():
    """Test security validation"""
    validator = InputValidator()

    print("Testing Security Validation")
    print("-" * 40)

    # Test command injection
    dangerous_inputs = [
        ("firefox; rm -rf /", "package"),
        ("package`echo bad`", "package"),
        ("../../etc/passwd", "path"),
    ]

    passed = 0
    failed = 0

    for dangerous_input, input_type in dangerous_inputs:
        result = validator.validate_input(dangerous_input, input_type)
        if not result["valid"]:
            print(f"✅ Blocked: {dangerous_input[:30]}...")
            passed += 1
        else:
            print(f"❌ ALLOWED: {dangerous_input} - SECURITY ISSUE!")
            failed += 1

    # Test valid inputs
    valid_inputs = [
        ("firefox", "package"),
        ("python3", "package"),
        ("/etc/nixos/configuration.nix", "path"),
    ]

    for valid_input, input_type in valid_inputs:
        result = validator.validate_input(valid_input, input_type)
        if result["valid"]:
            print(f"✅ Allowed: {valid_input}")
            passed += 1
        else:
            print(f"❌ Blocked valid input: {valid_input}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = test_security()
    sys.exit(0 if success else 1)
