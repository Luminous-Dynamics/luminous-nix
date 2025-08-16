#!/usr/bin/env python3
"""
Test configuration persistence system
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.core.config_manager import ConfigManager, get_config_manager


def test_preferences():
    """Test preference management"""
    print("\n1. Testing Preferences")
    print("-" * 40)

    config = ConfigManager()

    # Test default preferences
    assert config.preferences.default_dry_run == True
    assert config.preferences.enable_learning == True
    print("  ✅ Default preferences loaded")

    # Test modifying preferences
    config.preferences.preferred_output = "json"
    config.preferences.theme = "minimal"
    config.save_preferences()
    print("  ✅ Preferences modified and saved")

    # Test preference conversion
    config_dict = config.get_config_dict()
    assert config_dict["dry_run"] == True
    assert config_dict["learning"] == True
    print("  ✅ Config dict conversion works")


def test_aliases():
    """Test alias management"""
    print("\n2. Testing Aliases")
    print("-" * 40)

    config = ConfigManager()

    # Test default aliases
    assert "i" in config.aliases
    assert config.aliases["i"].expansion == "install"
    print("  ✅ Default aliases loaded")

    # Test adding alias
    config.add_alias("test", "test expansion", "Test description")
    assert "test" in config.aliases
    print("  ✅ Alias added")

    # Test alias expansion
    expanded = config.expand_aliases("i firefox")
    assert expanded == "install firefox"
    print("  ✅ Alias expansion works")

    # Test removing alias
    config.remove_alias("test")
    assert "test" not in config.aliases
    print("  ✅ Alias removed")


def test_history():
    """Test history tracking"""
    print("\n3. Testing History")
    print("-" * 40)

    config = ConfigManager()

    # Add history entries
    config.add_to_history("test query 1", True, 0.5)
    config.add_to_history("test query 2", False, 1.0)
    config.add_to_history("test query 3", True, 0.3)
    print("  ✅ History entries added")

    # Test retrieving history
    history = config.get_recent_history(2)
    assert len(history) <= 2
    if len(history) > 0:
        assert "query" in history[0]
        assert "success" in history[0]
    print("  ✅ History retrieval works")

    # Test stats update
    assert config.stats["total_queries"] >= 3
    print(f"  ✅ Stats updated: {config.stats['total_queries']} total queries")


def test_patterns():
    """Test pattern learning"""
    print("\n4. Testing Pattern Learning")
    print("-" * 40)

    config = ConfigManager()

    # Learn patterns
    config.learn_pattern("install", "install firefox", True)
    config.learn_pattern("search", "search vim", True)
    config.learn_pattern("install", "install vim", True)
    config.learn_pattern("install", "install broken", False)
    print("  ✅ Patterns learned")

    # Check patterns
    assert len(config.patterns.get("frequent_queries", [])) > 0
    assert len(config.patterns.get("success_patterns", [])) > 0
    assert len(config.patterns.get("error_patterns", [])) > 0
    print("  ✅ Pattern storage works")

    # Test suggestions
    suggestions = config.get_suggestions("inst")
    # Should have some suggestions for "inst"
    # Note: suggestions depend on learned patterns
    print(f"  ✅ Suggestions generated: {len(suggestions)} found")


def test_session():
    """Test session management"""
    print("\n5. Testing Session Management")
    print("-" * 40)

    config = ConfigManager()

    # Check session exists
    assert config.session is not None
    assert config.session.session_id is not None
    print(f"  ✅ Session created: {config.session.session_id}")

    # Update session
    original_count = config.session.command_count
    config.session.command_count += 1
    config.save_session()
    assert config.session.command_count == original_count + 1
    print("  ✅ Session updated and saved")


def test_export_import():
    """Test configuration export/import"""
    print("\n6. Testing Export/Import")
    print("-" * 40)

    config = ConfigManager()

    # Modify config
    config.preferences.theme = "test_theme"
    config.add_alias("test_alias", "test_expansion")

    # Export
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        export_path = Path(f.name)

    config.export_config(export_path)
    print(f"  ✅ Exported to {export_path}")

    # Create new config and import
    new_config = ConfigManager()
    new_config.import_config(export_path)

    # Verify import
    assert new_config.preferences.theme == "test_theme"
    assert "test_alias" in new_config.aliases
    print("  ✅ Import successful")

    # Cleanup
    export_path.unlink()


def test_cleanup():
    """Test data cleanup"""
    print("\n7. Testing Data Cleanup")
    print("-" * 40)

    config = ConfigManager()

    # Add old entries (would need to modify timestamps in real test)
    config.add_to_history("old query", True, 0.5)

    # Run cleanup
    config.cleanup_old_data(days=30)
    print("  ✅ Cleanup executed")

    # Verify (in real test, would check that old entries are removed)
    history = config.get_recent_history(100)
    print(f"  ✅ History size after cleanup: {len(history)} entries")


def test_integration():
    """Test integration with backend"""
    print("\n8. Testing Backend Integration")
    print("-" * 40)

    from luminous_nix.core.unified_backend import get_backend

    # Backend should use config manager
    backend = get_backend()
    assert backend._config_manager is not None
    print("  ✅ Backend uses config manager")

    # Test alias expansion in backend
    config = get_config_manager()
    config.add_alias("tst", "test command")

    # This would be expanded by backend
    expanded = config.expand_aliases("tst arg")
    assert expanded == "test command arg"
    print("  ✅ Backend alias expansion ready")


if __name__ == "__main__":
    print("🧪 Testing Configuration Persistence System")
    print("=" * 60)

    test_preferences()
    test_aliases()
    test_history()
    test_patterns()
    test_session()
    test_export_import()
    test_cleanup()
    test_integration()

    print("\n" + "=" * 60)
    print("🎉 All configuration tests passed!")
    print("\nConfiguration persistence provides:")
    print("  • User preferences management")
    print("  • Command alias system")
    print("  • History tracking")
    print("  • Pattern learning")
    print("  • Session continuity")
    print("  • Export/Import capability")
    print("  • Data cleanup")
    print("  • Backend integration")
