#!/usr/bin/env python3
"""
Minimal test script to verify v1.1 components are importable.

This helps verify the TUI build is working correctly.
"""

import importlib.util
import sys


def test_import(module_name, package_path=None):
    """Test if a module can be imported."""
    try:
        if package_path:
            spec = importlib.util.spec_from_file_location(module_name, package_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        else:
            __import__(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - FAILED: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - ERROR: {e}")
        return False


def main():
    """Run minimal import tests."""
    print("🧪 Nix for Humanity v1.1 Import Test")
    print("=" * 40)
    print()

    # Test core imports
    print("📦 Testing Core Imports:")
    core_modules = [
        "src.nix_humanity.core.backend",
        "src.nix_humanity.core.engine",
        "src.nix_humanity.core.native_operations",
        "src.nix_humanity.ai.nlp",
    ]

    core_ok = all(test_import(m) for m in core_modules)
    print()

    # Test CLI imports
    print("💻 Testing CLI Imports:")
    cli_modules = [
        "src.nix_humanity.interfaces.cli",
    ]

    cli_ok = all(test_import(m) for m in cli_modules)
    print()

    # Test TUI imports (if available)
    print("🖥️  Testing TUI Imports:")
    tui_ok = test_import("textual")
    if tui_ok:
        tui_modules = [
            "src.nix_humanity.ui.main_app",
            "src.nix_humanity.ui.consciousness_orb",
            "src.nix_humanity.interfaces.tui",
        ]
        tui_ok = all(test_import(m) for m in tui_modules)
    print()

    # Test Voice imports (if available)
    print("🎤 Testing Voice Imports:")
    voice_ok = True
    voice_deps = ["whisper", "sounddevice", "piper"]

    for dep in voice_deps:
        if not test_import(dep):
            voice_ok = False
            print(f"  Voice dependency {dep} not available")

    if voice_ok:
        voice_modules = [
            "src.nix_humanity.interfaces.voice",
        ]
        voice_ok = all(test_import(m) for m in voice_modules)
    print()

    # Summary
    print("📊 Summary:")
    print(f"  Core: {'✅ Ready' if core_ok else '❌ Failed'}")
    print(f"  CLI: {'✅ Ready' if cli_ok else '❌ Failed'}")
    print(
        f"  TUI: {'✅ Ready' if tui_ok else '⏳ Not installed (run: poetry install -E tui)'}"
    )
    print(
        f"  Voice: {'✅ Ready' if voice_ok else '⏳ Not installed (run: poetry install -E voice)'}"
    )
    print()

    if core_ok and cli_ok:
        print("✨ v1.0 features are ready!")
        if tui_ok and voice_ok:
            print("🎉 v1.1 features are ready!")
        else:
            print("💡 Install optional features for v1.1")
        return 0
    print("❌ Some core components failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
