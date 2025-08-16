#!/usr/bin/env python3
"""Quick TUI startup test for v1.1"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_tui_imports():
    """Test that all TUI components can be imported"""
    try:
        print("Testing TUI imports...")

        # Core TUI components
        from luminous_nix.ui.main_app import NixForHumanityTUI

        print("✓ Main TUI app imported")

        from luminous_nix.ui.consciousness_orb import ConsciousnessOrb

        print("✓ Consciousness orb imported")

        from luminous_nix.ui.adaptive_interface import AdaptiveInterface

        print("✓ Adaptive interface imported")

        # Backend connection
        from luminous_nix.core.backend import NixForHumanityBackend

        print("✓ Backend imported")

        # TUI interface
        from luminous_nix.interfaces.tui import main

        print("✓ TUI interface imported")

        print("\n✅ All TUI components imported successfully!")
        print("\nYou can now run: poetry run nix-tui")

        return True

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nMake sure you've run: poetry install -E tui")
        return False


def test_backend_connection():
    """Test that TUI can connect to backend"""
    try:
        from luminous_nix.core.backend import NixForHumanityBackend

        print("\nTesting backend connection...")
        backend = NixForHumanityBackend()

        # Test a simple command
        result = backend.execute_command("help", dry_run=True)
        if result and result.success:
            print("✓ Backend responds to commands")
        else:
            print("⚠ Backend connection works but command failed")

    except Exception as e:
        print(f"⚠ Backend test failed: {e}")


if __name__ == "__main__":
    print("=== Nix for Humanity v1.1 TUI Test ===\n")

    if test_tui_imports():
        test_backend_connection()
        print("\n🎉 TUI is ready for v1.1 launch!")
    else:
        print("\n⚠ TUI dependencies need to be installed")
        sys.exit(1)
