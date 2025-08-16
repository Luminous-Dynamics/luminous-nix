#!/usr/bin/env python3
"""Basic tests for the Nix for Humanity MVP."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from luminous_nix.core import CommandExecutor, CommandTranslator
from luminous_nix.core.config import Config


def test_translator():
    """Test the command translator."""
    translator = CommandTranslator()

    # Test basic commands and new patterns
    test_cases = [
        # Original patterns
        ("install firefox", "install", True),
        ("search python", "search", True),
        ("list installed", "query", True),
        ("update system", "system", True),
        ("gibberish", "unknown", False),
        # New patterns
        ("clean up", "maintenance", True),
        ("garbage collect", "maintenance", True),
        ("where is vim", "query", True),
        ("test configuration", "system", True),
        ("rollback", "system", True),
        ("show channels", "query", True),
        ("optimize store", "maintenance", True),
        ("dev shell", "development", True),
        ("update flake", "flake", True),
        # Alternative phrasings
        ("add docker", "install", True),
        ("delete firefox", "remove", True),
        ("look for editor", "search", True),
    ]

    print("Testing CommandTranslator:")
    for user_input, expected_category, should_succeed in test_cases:
        command, category, explanation = translator.translate(user_input)
        success = command is not None

        if success == should_succeed and (
            not should_succeed or category == expected_category
        ):
            print(f"  ✅ '{user_input}' -> {category}")
        else:
            print(
                f"  ❌ '{user_input}' failed (expected {expected_category}, got {category})"
            )

    # Test suggestions
    suggestions = translator.get_suggestions("install something")
    print(f"\n  Suggestions for 'install something': {len(suggestions)} items")


def test_executor():
    """Test the command executor in dry-run mode."""
    executor = CommandExecutor(dry_run=True, auto_confirm=True)

    print("\nTesting CommandExecutor (dry-run):")

    # Test safe command
    success, output = executor.execute("nixos-version", "Show system version")
    print(f"  {'✅' if success else '❌'} nixos-version: {output[:50]}...")

    # Test dangerous pattern detection
    success, output = executor.execute("rm -rf /", "Dangerous!")
    print(
        f"  {'✅' if not success else '❌'} Blocked dangerous command: {output[:50]}..."
    )


def test_integration():
    """Test the full pipeline."""
    translator = CommandTranslator()
    executor = CommandExecutor(dry_run=True, auto_confirm=True)

    print("\nTesting Integration:")

    test_queries = [
        "install firefox",
        "search text editor",
        "list installed",
        "system info",
    ]

    for query in test_queries:
        command, category, explanation = translator.translate(query)
        if command:
            success, output = executor.execute(command, explanation)
            print(f"  {'✅' if success else '❌'} '{query}' -> {command[:40]}...")
        else:
            print(f"  ❌ '{query}' -> Translation failed")


def test_config():
    """Test configuration system."""
    print("\nTesting Config System:")

    # Create temp config file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_config = {
            "version": "0.2.0",
            "preferences": {
                "use_nix_profile": True,
            },
            "aliases": {
                "testpkg": "real-package-name",
            },
            "custom_commands": {
                "test command": "echo 'test works'",
            },
        }
        json.dump(test_config, f)
        config_path = f.name

    try:
        # Test loading config
        config = Config(config_path)
        print(f"  ✅ Config loaded from {config_path}")

        # Test getting values
        use_profile = config.get("preferences.use_nix_profile")
        print(f"  ✅ Config get: use_nix_profile = {use_profile}")

        # Test translator with config
        translator = CommandTranslator(config)

        # Test alias resolution
        command, category, _ = translator.translate("install testpkg")
        if "real-package-name" in command:
            print("  ✅ Alias resolution: testpkg -> real-package-name")
        else:
            print("  ❌ Alias resolution failed")

        # Test custom command
        command, category, _ = translator.translate("test command")
        if command == "echo 'test works'":
            print("  ✅ Custom command: 'test command' -> echo 'test works'")
        else:
            print("  ❌ Custom command failed")

        # Test adding alias
        config.add_alias("newalias", "newpackage")
        if config.get("aliases.newalias") == "newpackage":
            print("  ✅ Add alias: newalias -> newpackage")
        else:
            print("  ❌ Add alias failed")

    finally:
        # Clean up
        os.unlink(config_path)


if __name__ == "__main__":
    print("=== Nix for Humanity MVP Test Suite ===\n")

    test_translator()
    test_executor()
    test_integration()
    test_config()

    print("\n=== Test Suite Complete ===")
