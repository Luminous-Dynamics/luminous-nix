#!/usr/bin/env bash
# 🚀 Quick Voice Dependencies Installation
# This bypasses the configuration.nix issues and installs directly

echo "🎤 Quick Voice Installation"
echo "=========================="
echo ""
echo "Installing Whisper and Piper for current user..."
echo "(This bypasses configuration issues)"
echo ""

# Install for current user
nix-env -iA nixos.openai-whisper \
            nixos.piper \
            nixos.portaudio \
            nixos.sox \
            nixos.ffmpeg

echo ""
echo "✅ Installation command sent!"
echo ""
echo "This will download and install:"
echo "  • OpenAI Whisper (speech recognition)"
echo "  • Piper (text-to-speech)"
echo "  • Audio processing tools"
echo ""
echo "Installation will continue in the background."
echo "Check progress with: nix-env -q | grep -E 'whisper|piper'"
echo ""
echo "Once complete, test with:"
echo "  whisper --help"
echo "  echo 'Hello' | piper --help"