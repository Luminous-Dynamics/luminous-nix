#!/usr/bin/env python3
"""
Diagnose import errors in the test suite.
"""
import sys
from pathlib import Path

# Add the source directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
test_dir = project_root / "tests"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(test_dir))

# Import conftest to set up mocks
try:
    import conftest

    print("🔧 Test mocks loaded successfully")
except ImportError:
    print("⚠️  Test mocks not available")


def test_import(module_name):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name}: {type(e).__name__}: {e}")
        return False


def main():
    print("🔍 Diagnosing import issues...")
    print(f"Project root: {project_root}")
    print(f"Source directory: {src_dir}")
    print(f"Python path: {sys.path[:3]}...")
    print()

    # Test imports that the test files are trying to use
    imports_to_test = [
        # Core modules
        "nix_for_humanity",
        "luminous_nix.core",
        "luminous_nix.core.types",
        "luminous_nix.core.engine",
        "luminous_nix.core.intent_engine",
        "luminous_nix.core.knowledge_base",
        "luminous_nix.core.execution_engine",
        "luminous_nix.core.learning_system",
        "luminous_nix.core.personality_system",
        # Adapters
        "luminous_nix.adapters",
        "luminous_nix.adapters.cli_adapter",
        # Interfaces
        "luminous_nix.interfaces",
        "luminous_nix.interfaces.backend_interface",
        # Frontend modules that tests are trying to import
        "frontends",
        "frontends.cli",
        "frontends.cli.adapter",
        # TUI
        "luminous_nix.tui",
        "luminous_nix.tui.app",
    ]

    success_count = 0
    total_count = len(imports_to_test)

    for module in imports_to_test:
        if test_import(module):
            success_count += 1

    print(f"\n📊 Results: {success_count}/{total_count} imports successful")

    if success_count < total_count:
        print("\n🔧 Issues found! Let's check what files exist:")

        # Check what files actually exist
        src_nix_humanity = src_dir / "nix_for_humanity"
        if src_nix_humanity.exists():
            print(f"\n📁 Contents of {src_nix_humanity}:")
            for item in sorted(src_nix_humanity.rglob("*.py")):
                rel_path = item.relative_to(src_nix_humanity)
                print(f"   {rel_path}")

        # Check frontends directory
        frontends_dir = project_root / "frontends"
        if frontends_dir.exists():
            print(f"\n📁 Contents of {frontends_dir}:")
            for item in sorted(frontends_dir.rglob("*.py")):
                rel_path = item.relative_to(frontends_dir)
                print(f"   {rel_path}")


if __name__ == "__main__":
    main()
