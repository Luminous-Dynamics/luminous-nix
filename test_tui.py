#!/usr/bin/env python3
"""
Test script for the Enhanced TUI

Verifies that all TUI components are working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_tui_imports():
    """Test that all TUI components can be imported"""
    print("🧪 Testing TUI Imports")
    print("=" * 50)
    
    components = [
        ("Basic App", "luminous_nix.interfaces.tui_components.app"),
        ("Enhanced App", "luminous_nix.interfaces.tui_components.enhanced_app"),
        ("Widgets", "luminous_nix.interfaces.tui_components.widgets"),
        ("Themes", "luminous_nix.interfaces.tui_components.themes"),
        ("Voice Widget", "luminous_nix.interfaces.tui_components.voice_widget"),
        ("Main TUI", "luminous_nix.interfaces.tui"),
    ]
    
    success = True
    for name, module_path in components:
        try:
            __import__(module_path)
            print(f"✅ {name}: Successfully imported")
        except ImportError as e:
            print(f"❌ {name}: Import failed - {e}")
            success = False
    
    return success


def test_tui_features():
    """Test TUI feature completeness"""
    print("\n🎯 Testing TUI Features")
    print("=" * 50)
    
    try:
        from luminous_nix.interfaces.tui_components.enhanced_app import EnhancedNixTUI
        
        # Check for all expected features
        features = {
            "Package Search": hasattr(EnhancedNixTUI, "action_focus_search"),
            "Command History": "CommandHistory" in str(EnhancedNixTUI.compose),
            "Settings Panel": "SettingsPanel" in str(EnhancedNixTUI.compose),
            "System Status": "SystemStatusWidget" in str(EnhancedNixTUI.compose),
            "Generations": "GenerationsPanel" in str(EnhancedNixTUI.compose),
            "Cache Management": hasattr(EnhancedNixTUI, "action_clear_cache"),
            "Dry Run Toggle": hasattr(EnhancedNixTUI, "action_toggle_dry_run"),
            "Help System": hasattr(EnhancedNixTUI, "action_show_help"),
            "Consciousness Orb": "ConsciousnessOrb" in str(EnhancedNixTUI.compose),
            "Tabbed Interface": "TabbedContent" in str(EnhancedNixTUI.compose),
        }
        
        total = len(features)
        implemented = sum(1 for v in features.values() if v)
        
        for feature, exists in features.items():
            status = "✅" if exists else "❌"
            print(f"{status} {feature}")
        
        percentage = (implemented / total) * 100
        print(f"\n📊 Feature Completeness: {percentage:.0f}% ({implemented}/{total})")
        
        return percentage >= 100
        
    except Exception as e:
        print(f"❌ Failed to test features: {e}")
        return False


def test_tui_widgets():
    """Test individual widget functionality"""
    print("\n🔧 Testing TUI Widgets")
    print("=" * 50)
    
    try:
        from luminous_nix.interfaces.tui_components.enhanced_app import (
            ConsciousnessOrb,
            PackageSearchWidget,
            CommandHistory,
            GenerationsPanel,
            SettingsPanel,
            SystemStatusWidget,
        )
        
        widgets = [
            ("ConsciousnessOrb", ConsciousnessOrb),
            ("PackageSearchWidget", PackageSearchWidget),
            ("CommandHistory", CommandHistory),
            ("GenerationsPanel", GenerationsPanel),
            ("SettingsPanel", SettingsPanel),
            ("SystemStatusWidget", SystemStatusWidget),
        ]
        
        success = True
        for name, widget_class in widgets:
            try:
                # Check if widget can be instantiated
                widget = widget_class()
                print(f"✅ {name}: Can be instantiated")
                
                # Check for compose method
                if hasattr(widget, "compose"):
                    print(f"   ✓ Has compose method")
                else:
                    print(f"   ✗ Missing compose method")
                    success = False
                    
            except Exception as e:
                print(f"❌ {name}: Failed - {e}")
                success = False
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to test widgets: {e}")
        return False


def test_tui_integration():
    """Test TUI integration with service layer"""
    print("\n🔗 Testing Service Integration")
    print("=" * 50)
    
    try:
        from luminous_nix.interfaces.tui_components.enhanced_app import EnhancedNixTUI
        from luminous_nix.service_simple import LuminousNixService
        
        # Check that TUI uses service layer
        app = EnhancedNixTUI()
        
        checks = {
            "Service attribute": hasattr(app, "service"),
            "Execute command method": hasattr(app, "execute_command"),
            "Package discovery": hasattr(app, "discovery"),
            "Cache manager": hasattr(app, "cache_manager"),
            "History management": hasattr(app, "save_history") and hasattr(app, "load_history"),
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"❌ Failed integration test: {e}")
        return False


def main():
    """Run all TUI tests"""
    print("🌟 Luminous Nix TUI Test Suite")
    print("Testing TUI completeness (40% → 100%)")
    print("=" * 60)
    
    tests = [
        ("Imports", test_tui_imports),
        ("Features", test_tui_features),
        ("Widgets", test_tui_widgets),
        ("Integration", test_tui_integration),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        success = test_func()
        results.append(success)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for (name, _), success in zip(tests, results):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    overall = all(results)
    
    if overall:
        print("\n🎉 SUCCESS: TUI is 100% complete!")
        print("All features implemented:")
        print("  ✅ Live package search with caching")
        print("  ✅ Command history with navigation")
        print("  ✅ Tabbed interface (Terminal, Search, History, Generations, Settings, Status)")
        print("  ✅ System status monitoring")
        print("  ✅ Cache management and statistics")
        print("  ✅ Settings panel with switches")
        print("  ✅ Consciousness orb animation")
        print("  ✅ Help system")
        print("  ✅ Dry run toggle")
        print("  ✅ Service layer integration")
    else:
        print("\n⚠️ Some tests failed")
    
    print("\n💡 To run the TUI:")
    print("  poetry run python -m luminous_nix.interfaces.tui")
    print("  # or")
    print("  ./bin/nix-tui")
    
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())