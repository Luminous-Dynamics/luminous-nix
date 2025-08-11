#!/usr/bin/env python3
"""
Fix dependency management for Nix for Humanity.
Unifies all dependencies through Poetry as single source of truth.
"""

import subprocess
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command and return output."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=check
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    return result


def main():
    """Fix dependency issues by setting up proper Poetry environment."""

    print("🎯 Fixing Nix for Humanity Dependencies")
    print("=" * 50)

    # Step 1: Check current environment
    print("\n1️⃣ Checking current environment...")
    run_command("which python", check=False)
    run_command("python --version", check=False)

    # Step 2: Install Poetry if needed
    print("\n2️⃣ Ensuring Poetry is available...")
    poetry_check = run_command("which poetry", check=False)
    if poetry_check.returncode != 0:
        print("📦 Installing Poetry...")
        run_command("curl -sSL https://install.python-poetry.org | python3 -")
        print("⚠️  Please add Poetry to PATH and re-run this script")
        return

    # Step 3: Install all dependencies with Poetry
    print("\n3️⃣ Installing all dependencies via Poetry...")
    print("This includes: core, tui, voice, ml features")

    # First, try to install without heavy ML deps
    print("\n🚀 Quick install (without ML dependencies):")
    run_command("poetry install -E tui -E voice", check=False)

    # Step 4: Verify installations
    print("\n4️⃣ Verifying installations...")
    test_imports = [
        ("Core", "from nix_for_humanity.core.nlp_engine import NLPEngine"),
        ("CLI", "from nix_for_humanity.interfaces.cli import main"),
        (
            "TUI",
            "import textual; from nix_for_humanity.ui.main_app import NixForHumanityApp",
        ),
        ("Voice", "import whisper, sounddevice, piper"),
    ]

    for name, import_str in test_imports:
        print(f"\n🧪 Testing {name}...")
        result = run_command(
            f"poetry run python -c \"{import_str}; print('✅ {name} imports working!')\"",
            check=False,
        )
        if result.returncode != 0:
            print(f"⚠️  {name} not fully installed")

    # Step 5: Create unified launcher
    print("\n5️⃣ Creating unified launcher script...")
    launcher_content = """#!/bin/bash
# Unified launcher for Nix for Humanity v1.1

echo "🌟 Nix for Humanity v1.1 Launcher"
echo "================================"

# Ensure we're using Poetry environment
export POETRY_VIRTUALENVS_IN_PROJECT=true

case "$1" in
    "cli")
        echo "🖥️  Launching CLI..."
        poetry run ask-nix "${@:2}"
        ;;
    "tui")
        echo "🎨 Launching TUI..."
        poetry run nix-tui "${@:2}"
        ;;
    "voice")
        echo "🎤 Launching Voice Interface..."
        poetry run python -m nix_humanity.interfaces.voice "${@:2}"
        ;;
    "test")
        echo "🧪 Running tests..."
        poetry run pytest "${@:2}"
        ;;
    *)
        echo "Usage: $0 {cli|tui|voice|test} [args...]"
        echo ""
        echo "Examples:"
        echo "  $0 cli 'install firefox'"
        echo "  $0 tui"
        echo "  $0 voice"
        echo "  $0 test tests/integration/"
        exit 1
        ;;
esac
"""

    launcher_path = Path("nix-humanity")
    launcher_path.write_text(launcher_content)
    launcher_path.chmod(0o755)
    print("✅ Created launcher: ./nix-humanity")

    # Step 6: Create development setup script
    print("\n6️⃣ Creating development setup script...")
    dev_setup = """#!/bin/bash
# Development environment setup

echo "🔧 Setting up Nix for Humanity development environment"

# Use project-local virtualenv
export POETRY_VIRTUALENVS_IN_PROJECT=true

# Install with all dev dependencies
echo "📦 Installing all dependencies..."
poetry install --with dev -E tui -E voice

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
poetry run pre-commit install 2>/dev/null || true

# Run initial tests
echo "🧪 Running quick tests..."
poetry run python -c "
from nix_for_humanity.core.nlp_engine import NLPEngine
print('✅ Core imports working!')
try:
    from nix_for_humanity.ui.main_app import NixForHumanityApp
    print('✅ TUI imports working!')
except ImportError:
    print('⚠️  TUI not available')
"

echo ""
echo "✨ Development environment ready!"
echo ""
echo "🚀 Quick start:"
echo "  ./nix-humanity cli 'help'      # Test CLI"
echo "  ./nix-humanity tui             # Launch TUI"
echo "  ./nix-humanity test            # Run tests"
"""

    dev_path = Path("setup-dev.sh")
    dev_path.write_text(dev_setup)
    dev_path.chmod(0o755)
    print("✅ Created dev setup: ./setup-dev.sh")

    print("\n✅ Dependency fix complete!")
    print("\n📋 Next steps:")
    print("1. Run: ./setup-dev.sh")
    print("2. Test: ./nix-humanity tui")
    print("3. Commit the fixed configuration")


if __name__ == "__main__":
    main()
