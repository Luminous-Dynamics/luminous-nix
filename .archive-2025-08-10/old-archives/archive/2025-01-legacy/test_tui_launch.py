#!/usr/bin/env python3
"""
Quick TUI test script to verify the interface works
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_tui():
    """Test TUI launch"""
    print("🎯 Testing TUI components...")

    try:
        # Test imports
        print("  1. Testing imports...")
        from luminous_nix.ui.adaptive_interface import AdaptiveInterface
        from luminous_nix.ui.consciousness_orb import (
            AIState,
            ConsciousnessOrb,
            EmotionalState,
        )
        from luminous_nix.ui.visual_state_controller import VisualStateController

        print("     ✅ UI components import successfully")

        # Test backend import
        from luminous_nix.core.backend import NixForHumanityBackend

        print("     ✅ Backend imports successfully")

        # Test main app import
        from luminous_nix.ui.main_app import NixForHumanityTUI

        print("     ✅ Main app imports successfully")

        print("\n✨ All imports successful! TUI is ready to launch.")
        print("\nTo run the full TUI:")
        print("  nix develop --command python3 src/nix_for_humanity/interfaces/tui.py")

        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nThis usually means dependencies are missing.")
        print("Run: nix develop")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_tui()
    sys.exit(0 if success else 1)
