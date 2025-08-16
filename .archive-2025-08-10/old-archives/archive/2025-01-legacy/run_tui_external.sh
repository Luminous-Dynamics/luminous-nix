#!/bin/bash
# Script to run TUI in external terminal

echo "🚀 Launching Nix for Humanity TUI v1.1..."
echo "This will open in a new terminal window to avoid Claude Code conflicts."
echo ""

# Detect terminal emulator
if command -v gnome-terminal &> /dev/null; then
    echo "Using GNOME Terminal..."
    gnome-terminal -- bash -c "cd $(pwd) && source venv_quick/bin/activate && python simple_tui_demo.py; exec bash"
elif command -v konsole &> /dev/null; then
    echo "Using Konsole..."
    konsole -e bash -c "cd $(pwd) && source venv_quick/bin/activate && python simple_tui_demo.py; exec bash"
elif command -v xterm &> /dev/null; then
    echo "Using XTerm..."
    xterm -e bash -c "cd $(pwd) && source venv_quick/bin/activate && python simple_tui_demo.py; exec bash"
elif command -v alacritty &> /dev/null; then
    echo "Using Alacritty..."
    alacritty -e bash -c "cd $(pwd) && source venv_quick/bin/activate && python simple_tui_demo.py"
else
    echo "❌ No suitable terminal emulator found!"
    echo ""
    echo "Please run manually in a terminal:"
    echo "  cd $(pwd)"
    echo "  source venv_quick/bin/activate"
    echo "  python simple_tui_demo.py"
fi