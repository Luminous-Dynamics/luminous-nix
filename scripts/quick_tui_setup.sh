#!/bin/bash
# Quick setup for TUI without waiting for voice dependencies

echo "🚀 Quick TUI Setup (without voice features)"
echo "=========================================="
echo ""

# Cancel any running builds
echo "⚠️  If a build is running, press Ctrl+C to cancel it"
echo "   Then run this script"
echo ""
read -p "Press Enter when ready to continue..."

# Install just TUI dependencies
echo "📦 Installing TUI dependencies only..."
poetry install -E tui

# Create a voice stub
echo "🔧 Creating voice interface stub..."
cat > src/nix_humanity/interfaces/voice_stub.py << 'EOF'
"""Stub voice interface for when voice deps aren't available."""

class VoiceInterface:
    def __init__(self):
        self.available = False
        
    async def initialize(self):
        print("Voice features not available - dependencies not installed")
        return False
        
    def is_available(self):
        return False
EOF

# Test TUI import
echo "🧪 Testing TUI imports..."
python3 -c "
try:
    from textual import App
    from rich import print
    print('[green]✅ TUI dependencies ready![/green]')
except ImportError as e:
    print(f'[red]❌ Missing dependency: {e}[/red]')
"

echo ""
echo "✨ Quick setup complete!"
echo ""
echo "🎨 Launch TUI with:"
echo "   python3 -m src.nix_humanity.ui.main_app"
echo ""
echo "🎤 Voice features can be added later with:"
echo "   nix-env -iA nixpkgs.whisper-cpp"
echo ""