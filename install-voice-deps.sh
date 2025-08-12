#!/usr/bin/env bash
# 🎤 Install Voice Dependencies for Nix for Humanity

set -e

echo "🎤 Installing Voice Dependencies"
echo "================================"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Please don't run this as root. We'll use sudo where needed."
   exit 1
fi

# Function to check if package is installed
check_installed() {
    if command -v "$1" &> /dev/null; then
        echo "✅ $1 is already installed"
        return 0
    else
        echo "❌ $1 not found"
        return 1
    fi
}

# Function to install via nix-env
install_user() {
    echo "📦 Installing for current user..."
    nix-env -iA nixos.openai-whisper nixos.piper nixos.portaudio
}

# Function to add to configuration.nix
install_system() {
    echo "📝 Generating system configuration addition..."
    
    cat > /tmp/voice-packages.nix << 'EOF'
# Voice interface packages for Nix for Humanity
environment.systemPackages = with pkgs; [
  # Speech recognition
  openai-whisper
  openai-whisper-cpp
  
  # Text-to-speech
  piper
  piper-phonemize
  
  # Audio processing
  portaudio
  sox
  ffmpeg
];
EOF

    echo ""
    echo "To add system-wide, append this to /etc/nixos/configuration.nix:"
    echo "----------------------------------------"
    cat /tmp/voice-packages.nix
    echo "----------------------------------------"
    echo ""
    echo "Then rebuild: nohup sudo nixos-rebuild switch > /tmp/rebuild.log 2>&1 &"
}

# Main menu
echo "How would you like to install voice dependencies?"
echo ""
echo "1) User install (quick, no sudo needed)"
echo "2) System-wide (requires edit to configuration.nix)"
echo "3) Check status only"
echo ""
read -p "Choose [1-3]: " choice

case $choice in
    1)
        echo ""
        install_user
        echo ""
        echo "✅ Installation started. This may take a few minutes..."
        echo "   Packages will be available after installation completes."
        ;;
    2)
        echo ""
        install_system
        ;;
    3)
        echo ""
        echo "Current status:"
        check_installed whisper
        check_installed piper
        check_installed ffmpeg
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎯 Next steps:"
echo "  1. Test whisper: whisper --help"
echo "  2. Test piper: echo 'Hello' | piper --help"
echo "  3. Run voice demo: poetry run python demo_voice_with_nix.py"
echo ""
echo "🌊 Voice setup assistance complete!"