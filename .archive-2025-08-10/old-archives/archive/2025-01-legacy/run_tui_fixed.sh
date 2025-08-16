#!/bin/bash
# Run the Nix for Humanity TUI with proper environment

echo "🌟 Launching Nix for Humanity TUI..."
echo ""
echo "✨ Tips:"
echo "  - Type 'help' to see available commands"
echo "  - Press Ctrl+C to quit"
echo "  - Press Ctrl+Z for Zen Mode"
echo "  - Press F1 for help"
echo ""

# Activate the TUI virtual environment
source venv_tui/bin/activate

# Set Python path
export PYTHONPATH="${PWD}/src:$PYTHONPATH"

# Run the TUI
python launch_tui_quick.py