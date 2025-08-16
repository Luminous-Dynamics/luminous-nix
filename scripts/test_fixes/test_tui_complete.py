#!/usr/bin/env python3
"""
Complete TUI validation test - ensures all components are working
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_tui_imports():
    """Test that all TUI components can be imported"""
    try:
        from luminous_nix.tui.app import (
            NixForHumanityTUI,
            ConsciousnessOrb,
            CommandHistory,
            run_tui
        )
        print("✅ Core TUI components import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_tui_creation():
    """Test that TUI instance can be created"""
    try:
        from luminous_nix.tui.app import NixForHumanityTUI
        
        app = NixForHumanityTUI()
        
        # Check attributes
        assert hasattr(app, 'CSS'), "Missing CSS attribute"
        assert hasattr(app, 'BINDINGS'), "Missing BINDINGS attribute"
        assert hasattr(app, 'compose'), "Missing compose method"
        assert hasattr(app, 'backend'), "Missing backend attribute"
        assert hasattr(app, 'context'), "Missing context attribute"
        assert hasattr(app, 'dry_run'), "Missing dry_run attribute"
        
        # Check initial state
        assert app.dry_run == True, "dry_run should be True by default"
        assert app.backend is None, "backend should be None before mount"
        
        print("✅ TUI instance created with all required attributes")
        return True
    except Exception as e:
        print(f"❌ Failed to create TUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consciousness_orb():
    """Test the consciousness orb component"""
    try:
        from luminous_nix.tui.app import ConsciousnessOrb
        
        orb = ConsciousnessOrb()
        
        # Check states
        assert hasattr(orb, 'RENDER_STATES'), "Missing RENDER_STATES"
        assert 'idle' in orb.RENDER_STATES, "Missing idle state"
        assert 'thinking' in orb.RENDER_STATES, "Missing thinking state"
        assert 'executing' in orb.RENDER_STATES, "Missing executing state"
        
        # Check methods
        assert hasattr(orb, 'set_activity'), "Missing set_activity method"
        assert hasattr(orb, 'animate'), "Missing animate method"
        assert hasattr(orb, 'render'), "Missing render method"
        
        # Test state changes
        orb.set_activity("thinking")
        assert orb.activity == "thinking", "Failed to set activity"
        
        # Test render output
        output = orb.render()
        assert "Consciousness" in output, "Render output missing text"
        assert "[yellow]" in output or "cyan" in output, "Render output missing color"
        
        print("✅ ConsciousnessOrb component working correctly")
        return True
    except Exception as e:
        print(f"❌ ConsciousnessOrb test failed: {e}")
        return False

def test_command_history():
    """Test the command history component"""
    try:
        from luminous_nix.tui.app import CommandHistory
        
        history = CommandHistory()
        
        # Check methods
        assert hasattr(history, 'add_command'), "Missing add_command method"
        assert hasattr(history, 'add_result'), "Missing add_result method"
        assert hasattr(history, 'write'), "Missing write method (inherited)"
        
        print("✅ CommandHistory component working correctly")
        return True
    except Exception as e:
        print(f"❌ CommandHistory test failed: {e}")
        return False

def test_backend_integration():
    """Test that TUI can integrate with backend"""
    try:
        from luminous_nix.tui.app import NixForHumanityTUI
        from luminous_nix.core.unified_backend import Context
        
        app = NixForHumanityTUI()
        
        # Check context initialization
        assert app.context.user_id == "tui_user", "Context not initialized correctly"
        
        # Check that backend can be configured
        app.dry_run = False
        assert app.dry_run == False, "Failed to change dry_run setting"
        
        print("✅ Backend integration configured correctly")
        return True
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

def test_tui_methods():
    """Test TUI methods and actions"""
    try:
        from luminous_nix.tui.app import NixForHumanityTUI
        
        app = NixForHumanityTUI()
        
        # Check action methods
        assert hasattr(app, 'action_clear_history'), "Missing clear_history action"
        assert hasattr(app, 'action_toggle_dry_run'), "Missing toggle_dry_run action"
        assert hasattr(app, 'action_show_help'), "Missing show_help action"
        
        # Check command execution
        assert hasattr(app, 'execute_command'), "Missing execute_command method"
        assert hasattr(app, 'update_status'), "Missing update_status method"
        
        # Test dry run toggle
        initial_state = app.dry_run
        app.action_toggle_dry_run()
        assert app.dry_run != initial_state, "Failed to toggle dry_run"
        
        print("✅ TUI methods and actions working correctly")
        return True
    except Exception as e:
        print(f"❌ TUI methods test failed: {e}")
        return False

def main():
    """Run all TUI tests"""
    print("🧪 Testing Nix for Humanity TUI Components")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_tui_imports),
        ("Creation Test", test_tui_creation),
        ("ConsciousnessOrb Test", test_consciousness_orb),
        ("CommandHistory Test", test_command_history),
        ("Backend Integration Test", test_backend_integration),
        ("Methods Test", test_tui_methods),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📝 Running {name}...")
        success = test_func()
        results.append(success)
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"  Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All TUI tests passed! The TUI is ready for use.")
        print("\nTo run the TUI:")
        print("  poetry run python bin/nix-tui")
        print("\nOr directly:")
        print("  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        print("  poetry run python -c 'from luminous_nix.tui.app import run; run()'")
    else:
        print(f"\n⚠️ {total - passed} tests failed. TUI needs fixes.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())