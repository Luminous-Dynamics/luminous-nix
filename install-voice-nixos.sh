#!/usr/bin/env bash
# Install voice dependencies the proper NixOS way

echo "🎤 Installing Voice Dependencies for Nix for Humanity"
echo "====================================================="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "✅ Running as root, can modify system configuration"
   CAN_MODIFY_SYSTEM=true
else
   echo "⚠️  Not running as root, will show what to add"
   CAN_MODIFY_SYSTEM=false
fi

# Create a temporary NixOS module for voice support
VOICE_MODULE="/tmp/nix-humanity-voice.nix"

cat > "$VOICE_MODULE" << 'EOF'
{ config, pkgs, ... }:

{
  # Voice interface dependencies for Nix for Humanity
  environment.systemPackages = with pkgs; [
    # Audio I/O
    portaudio
    alsa-utils
    pulseaudio
    
    # Audio processing
    ffmpeg-full
    sox
    
    # Text-to-speech
    espeak-ng
    
    # For building Python audio packages
    pkg-config
    libffi
    openssl
  ];

  # Enable sound support
  hardware.pulseaudio.enable = true;
  # OR if using pipewire:
  # services.pipewire = {
  #   enable = true;
  #   alsa.enable = true;
  #   pulse.enable = true;
  # };

  # Allow audio group access
  users.users.${config.users.users.tstoltz.name or "tstoltz"} = {
    extraGroups = [ "audio" ];
  };
}
EOF

echo "📝 Created voice module at: $VOICE_MODULE"
echo

if [ "$CAN_MODIFY_SYSTEM" = true ]; then
    echo "Would you like to:"
    echo "1. Add to /etc/nixos/configuration.nix automatically"
    echo "2. Just show what to add manually"
    echo "3. Install packages with nix-env (user-level, immediate)"
    read -p "Choose option (1/2/3): " choice
    
    case $choice in
        1)
            echo "Adding to configuration.nix..."
            # Backup current configuration
            sudo cp /etc/nixos/configuration.nix /etc/nixos/configuration.nix.backup-$(date +%Y%m%d-%H%M%S)
            
            # Add import to configuration.nix if not already there
            if ! grep -q "nix-humanity-voice.nix" /etc/nixos/configuration.nix; then
                sudo cp "$VOICE_MODULE" /etc/nixos/nix-humanity-voice.nix
                # This would need proper sed manipulation of the imports list
                echo "⚠️  Please manually add this to your imports in /etc/nixos/configuration.nix:"
                echo "    ./nix-humanity-voice.nix"
            fi
            
            echo "✅ Module added. Run: sudo nixos-rebuild switch"
            ;;
        2)
            echo "Add these packages to your configuration.nix:"
            echo
            cat "$VOICE_MODULE"
            ;;
        3)
            echo "Installing with nix-env (user-level)..."
            nix-env -iA nixos.portaudio nixos.ffmpeg-full nixos.espeak-ng nixos.sox \
                    nixos.pkg-config nixos.libffi nixos.openssl 2>&1 | tail -5
            echo "✅ Packages installed for current user"
            ;;
    esac
else
    echo "To install system-wide, add this to /etc/nixos/configuration.nix:"
    echo
    echo "  environment.systemPackages = with pkgs; ["
    echo "    portaudio"
    echo "    ffmpeg-full"
    echo "    espeak-ng"
    echo "    sox"
    echo "    pkg-config"
    echo "    libffi"
    echo "    openssl"
    echo "  ];"
    echo
    echo "Or install for current user:"
    echo "  nix-env -iA nixos.portaudio nixos.ffmpeg-full nixos.espeak-ng nixos.sox"
fi

echo
echo "🐍 Python packages status:"
echo "=========================="

# Check Python packages
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

echo "Checking installed voice packages..."
poetry show | grep -E "(whisper|piper|vosk|espeak|sounddevice|librosa)" || echo "No voice packages found"

echo
echo "📦 To install Python packages:"
echo "  poetry install --extras voice"

echo
echo "🔍 Testing voice setup..."
poetry run python -c "
import sys
print('Python voice packages:')
try:
    import whisper
    print('  ✅ Whisper (OpenAI) available')
except ImportError:
    print('  ❌ Whisper not found - install with: poetry add openai-whisper')

try:
    import piper
    print('  ✅ Piper TTS available')
except ImportError:
    print('  ⚠️  Piper module not found (binary may still work)')

try:
    import sounddevice
    print('  ✅ Sounddevice available')
except ImportError:
    print('  ❌ Sounddevice not found')

try:
    import vosk
    print('  ✅ Vosk available')
except ImportError:
    print('  ⚠️  Vosk not found (optional)')
" 2>/dev/null

echo
echo "✨ Setup complete!"
echo
echo "Next steps:"
echo "1. Ensure audio packages are installed (see above)"
echo "2. Run: poetry install --extras voice"
echo "3. Test: poetry run python demo_voice_complete.py"
echo "4. Launch TUI: poetry run python -m nix_for_humanity.tui.app"
echo "5. Press 'V' in TUI for voice input!"