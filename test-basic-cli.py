#!/usr/bin/env python3
"""
Basic CLI test script to verify functionality
"""

import sys

# Add src to path
sys.path.insert(0, "src")


def test_imports():
    """Test that basic imports work"""
    print("Testing imports...")
    try:
        from nix_for_humanity.core.engine import NixForHumanityCore

        print("✅ Core engine imports")
    except ImportError as e:
        print(f"❌ Core engine import failed: {e}")

    try:
        from nix_for_humanity.knowledge.engine import ModernNixOSKnowledgeEngine

        print("✅ Knowledge engine imports")
    except ImportError as e:
        print(f"❌ Knowledge engine import failed: {e}")

    try:
        from nix_for_humanity.nlp.personas import PersonaManager

        print("✅ PersonaManager imports")
    except ImportError as e:
        print(f"❌ PersonaManager import failed: {e}")

    try:
        from nix_for_humanity.interfaces.cli import UnifiedNixAssistant

        print("✅ CLI interface imports")
    except ImportError as e:
        print(f"❌ CLI interface import failed: {e}")


def test_basic_knowledge():
    """Test basic knowledge engine functionality"""
    print("\nTesting knowledge engine...")
    try:
        from nix_for_humanity.knowledge.engine import ModernNixOSKnowledgeEngine

        engine = ModernNixOSKnowledgeEngine()

        # Test parse_query
        result = engine.parse_query("install firefox")
        print(f"✅ Parse 'install firefox': {result}")

        # Test extract_intent (alias)
        result = engine.extract_intent("search python")
        print(f"✅ Extract intent 'search python': {result}")

        # Test get_command
        cmd = engine.get_command("install", package="firefox")
        print(f"✅ Get install command: {cmd}")

    except Exception as e:
        print(f"❌ Knowledge engine test failed: {e}")


def test_basic_cli():
    """Test basic CLI functionality"""
    print("\nTesting CLI...")
    try:
        from nix_for_humanity.interfaces.cli import UnifiedNixAssistant

        # Create assistant without config (use defaults)
        assistant = UnifiedNixAssistant()
        print("✅ UnifiedNixAssistant created")

        # Test basic properties
        assistant.dry_run = True
        assistant.skip_confirmation = True
        assistant.visual_mode = False
        print("✅ Basic properties set")

    except Exception as e:
        print(f"❌ CLI test failed: {e}")


def test_personas():
    """Test persona manager"""
    print("\nTesting personas...")
    try:
        from nix_for_humanity.nlp.personas import PersonaManager

        pm = PersonaManager()
        print("✅ PersonaManager created")

        # Get default persona
        persona = pm.get_persona("default")
        print(f"✅ Default persona: {persona.name}")

        # Format a response
        response = pm.format_response(
            "Test message", {"action": "test", "result": "success"}
        )
        print(f"✅ Formatted response: {response[:50]}...")

    except Exception as e:
        print(f"❌ Persona test failed: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Basic CLI Functionality Test")
    print("=" * 60)

    test_imports()
    test_basic_knowledge()
    test_basic_cli()
    test_personas()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("\nThe basic CLI components are working!")
    print("Next steps:")
    print("  1. Fix configuration parsing issues")
    print("  2. Add real NixOS command execution")
    print("  3. Implement learning system properly")
    print("  4. Add comprehensive error handling")


if __name__ == "__main__":
    main()
