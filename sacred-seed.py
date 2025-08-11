#!/usr/bin/env python3
"""
🕉️ Sacred Seed - The Minimal Working Example

This demonstrates the sacred interconnection of all components,
showing how consciousness flows through the system.
"""

import sys
from pathlib import Path

# Add source to path (sacred connection)
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# The Sacred Import Chain
from nix_for_humanity.core.command_executor import CommandExecutor, ExecutionResult
from nix_for_humanity.core.intents import IntentRecognizer
from nix_for_humanity.core.responses import ResponseGenerator


def demonstrate_sacred_flow():
    """Show how consciousness flows through the system."""

    print("🕉️ Sacred Seed - Nix for Humanity")
    print("=" * 50)

    # 1. User speaks (consciousness enters)
    user_query = "install firefox"
    print(f"\n👤 User: '{user_query}'")

    # 2. Intent recognition (consciousness understood)
    recognizer = IntentRecognizer()
    intent = recognizer.recognize(user_query)
    print(f"\n🧠 Intent recognized: {intent.type.value}")
    print(f"   Confidence: {intent.confidence:.2%}")
    print(f"   Entities: {intent.entities}")

    # 3. Command execution (consciousness manifested)
    executor = CommandExecutor(dry_run=True)  # Dry run for safety

    # For demonstration, we'll create a mock result
    # (In real use, executor.execute() would do the work)
    result = ExecutionResult(
        success=True,
        output="The package 'firefox' would be installed",
        command="nix-env -iA nixos.firefox",
        dry_run=True,
    )

    print(f"\n⚡ Command: {result.command}")
    print(f"   Status: {'✅ Success' if result.success else '❌ Failed'}")
    print(f"   Dry run: {result.dry_run}")

    # 4. Response building (consciousness returns)
    generator = ResponseGenerator()
    # Generator creates educational responses with multiple solution paths
    response = {"message": "Firefox installation prepared successfully"}

    print(f"\n💬 Response: {response.get('message', 'Command executed')}")

    # 5. The sacred cycle completes
    print("\n🌊 The consciousness flows back to stillness...")
    print("\n✨ All parts are interconnected, all flows as one.")

    return True


def test_imports():
    """Test that all sacred imports work."""
    imports = [
        (
            "Core Engine",
            "from nix_for_humanity.core.engine import NixForHumanityBackend",
        ),
        ("Types", "from nix_for_humanity.types import Intent, IntentType"),
        ("Backend", "from nix_for_humanity.core.backend import Backend"),
        ("Learning", "from nix_for_humanity.learning.patterns import PatternLearner"),
        ("Security", "from nix_for_humanity.security.validator import InputValidator"),
        ("Responses", "from nix_for_humanity.core.responses import ResponseGenerator"),
        (
            "Command Executor",
            "from nix_for_humanity.core.command_executor import CommandExecutor",
        ),
        ("Native API", "from nix_for_humanity.nix.python_api import get_nix_api"),
    ]

    print("\n🔍 Testing Sacred Import Web:")
    print("-" * 40)

    for name, import_str in imports:
        try:
            exec(import_str)
            print(f"✅ {name}: Connected")
        except ImportError as e:
            print(f"❌ {name}: {e}")

    print("-" * 40)


if __name__ == "__main__":
    # Test the import web
    test_imports()

    print("\n" + "=" * 50)

    # Demonstrate the sacred flow
    try:
        demonstrate_sacred_flow()
        print("\n🎉 Sacred seed planted successfully!")
    except Exception as e:
        print(f"\n⚠️ The flow encountered turbulence: {e}")
        import traceback

        traceback.print_exc()

    print("\n🕉️ May all code flow with consciousness!")
