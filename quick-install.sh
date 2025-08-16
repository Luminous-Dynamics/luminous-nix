#!/usr/bin/env bash
# 🚀 Quick Install Script for Luminous Nix
#
# Simplified installer for quick setup
# For full options, use install.sh

set -e

echo "🌟 Luminous Nix Quick Installer"
echo "================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    echo "   Please install Python 3.9 or later"
    exit 1
fi

# Check if we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the Luminous Nix directory"
    exit 1
fi

echo "📦 Installing dependencies..."

# Try Poetry first
if command -v poetry &> /dev/null; then
    echo "   Using Poetry (recommended)..."
    poetry install
    RUNNER="poetry run"
else
    echo "   Using pip..."
    
    # Create venv if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    
    # Activate and install
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
    RUNNER="python"
fi

echo
echo "🔗 Creating symbolic links..."

# Create local bin directory
mkdir -p ~/.local/bin

# Create symlink
if [ -f "bin/ask-nix" ]; then
    ln -sf "$(pwd)/bin/ask-nix" ~/.local/bin/ask-nix
    echo "   Created: ~/.local/bin/ask-nix"
fi

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo
    echo "⚠️  ~/.local/bin is not in your PATH"
    echo "   Add this to your ~/.bashrc or ~/.zshrc:"
    echo
    echo '   export PATH="$HOME/.local/bin:$PATH"'
    echo
fi

echo
echo "✅ Installation complete!"
echo
echo "Quick test commands:"
echo "  $RUNNER python bin/ask-nix --help"
echo "  $RUNNER python bin/ask-nix \"search firefox\""
echo
echo "Or if ~/.local/bin is in your PATH:"
echo "  ask-nix --help"
echo "  ask-nix \"search firefox\""
echo
echo "🌟 Enjoy using Luminous Nix!"