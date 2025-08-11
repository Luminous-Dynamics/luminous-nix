#!/usr/bin/env bash
# Install voice interface dependencies with proper system libraries

echo "🎤 Installing Voice Interface Dependencies..."

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Not in nix-shell. Run 'nix-shell' first for system dependencies!"
    echo "   This provides PortAudio, FFmpeg, and other audio libraries."
    exit 1
fi

echo "✅ Nix shell detected - system libraries available"

# Install PyAudio with proper build flags
echo "📦 Installing PyAudio with PortAudio support..."
PORTAUDIO_PATH=$(nix-build '<nixpkgs>' -A portaudio --no-out-link)
export CFLAGS="-I${PORTAUDIO_PATH}/include"
export LDFLAGS="-L${PORTAUDIO_PATH}/lib"

# Use pip directly since Poetry has issues with PyAudio
poetry run pip install --force-reinstall pyaudio

# Verify installation
echo "🔍 Verifying voice dependencies..."
poetry run python -c "
import sys
print('Testing voice interface dependencies...')
try:
    import speech_recognition as sr
    print('✅ SpeechRecognition installed')
except ImportError as e:
    print(f'❌ SpeechRecognition error: {e}')
    sys.exit(1)

try:
    import pyaudio
    print('✅ PyAudio installed')
except ImportError as e:
    print(f'❌ PyAudio error: {e}')
    sys.exit(1)

try:
    import pyttsx3
    print('✅ pyttsx3 (TTS) installed')
except ImportError as e:
    print(f'❌ pyttsx3 error: {e}')
    sys.exit(1)

try:
    import sounddevice as sd
    print('✅ Sounddevice installed')
except ImportError as e:
    print(f'❌ Sounddevice error: {e}')
    sys.exit(1)

print()
print('🎉 All voice dependencies installed successfully!')
print('You can now run: poetry run python demo_voice.py')
"

echo ""
echo "🚀 Voice interface dependencies ready!"
echo "   Run: poetry run python demo_voice.py"
echo "   Or:  poetry run python bin/nix-voice"