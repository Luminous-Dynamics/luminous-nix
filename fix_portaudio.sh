#!/usr/bin/env bash
# Fix PortAudio library path for Python audio recording

set -e

echo "🔊 Fixing PortAudio Library Path"
echo "================================"
echo ""

# Find PortAudio library
PORTAUDIO_PATH=$(nix-build '<nixpkgs>' -A portaudio --no-out-link 2>/dev/null)

if [ -z "$PORTAUDIO_PATH" ]; then
    echo "❌ Failed to find PortAudio in Nix store"
    echo "   Run: nix-shell -p portaudio"
    exit 1
fi

echo "✅ Found PortAudio at: $PORTAUDIO_PATH"

# Check for the library file
LIBPORTAUDIO="$PORTAUDIO_PATH/lib/libportaudio.so"
if [ ! -f "$LIBPORTAUDIO" ]; then
    LIBPORTAUDIO="$PORTAUDIO_PATH/lib/libportaudio.so.2"
fi

if [ ! -f "$LIBPORTAUDIO" ]; then
    echo "❌ Could not find libportaudio.so in $PORTAUDIO_PATH/lib/"
    ls -la "$PORTAUDIO_PATH/lib/"
    exit 1
fi

echo "✅ Found library: $LIBPORTAUDIO"
echo ""

# Create wrapper script
WRAPPER_SCRIPT="run_with_audio.sh"

cat > "$WRAPPER_SCRIPT" << EOF
#!/usr/bin/env bash
# Wrapper script to run Python with PortAudio support

export LD_LIBRARY_PATH="$PORTAUDIO_PATH/lib:\$LD_LIBRARY_PATH"
export PORTAUDIO_PATH="$PORTAUDIO_PATH"

echo "🎤 Audio environment configured"
echo "   PortAudio: $PORTAUDIO_PATH"
echo ""

# Run the command passed as arguments
if [ \$# -eq 0 ]; then
    echo "Usage: ./run_with_audio.sh <command>"
    echo "Example: ./run_with_audio.sh python test_microphone.py"
    exit 1
fi

exec "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

echo "✅ Created wrapper script: $WRAPPER_SCRIPT"
echo ""

# Create Python test script
cat > test_audio_fixed.py << 'EOF'
#!/usr/bin/env python3
"""Test that PortAudio is now accessible"""

import os
import sys

print("🎤 Testing PortAudio Access")
print("=" * 40)

# Check environment
ld_path = os.environ.get('LD_LIBRARY_PATH', 'Not set')
print(f"LD_LIBRARY_PATH: {ld_path[:100]}...")

try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully!")
    
    # List audio devices
    print("\n📊 Available Audio Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        kind = "Input" if device['max_input_channels'] > 0 else "Output"
        print(f"  {i}: {device['name']} ({kind})")
    
    # Test recording capability
    print("\n🎤 Testing recording capability...")
    try:
        # Try to record 1 second of audio
        duration = 1
        fs = 44100
        print(f"  Recording {duration} second of audio...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        print("✅ Recording successful!")
        print(f"  Shape: {recording.shape}")
        print(f"  Max amplitude: {abs(recording).max():.4f}")
    except Exception as e:
        print(f"⚠️  Recording failed: {e}")
        print("  This might be normal if no microphone is connected")
    
except ImportError as e:
    print(f"❌ Failed to import sounddevice: {e}")
    print("\nMake sure to install it with:")
    print("  poetry add sounddevice")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 40)
print("Test complete!")
EOF

echo "📝 Created test script: test_audio_fixed.py"
echo ""

# Test if sounddevice is installed via Poetry
echo "🔍 Checking Poetry dependencies..."
if poetry show sounddevice 2>/dev/null | grep -q sounddevice; then
    echo "✅ sounddevice is installed via Poetry"
else
    echo "⚠️  sounddevice not found in Poetry dependencies"
    echo "   Installing now..."
    poetry add sounddevice numpy
fi

echo ""
echo "🧪 Testing the fix..."
echo "=" * 40

# Run the test
./run_with_audio.sh poetry run python test_audio_fixed.py

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Usage examples:"
echo "  ./run_with_audio.sh poetry run python test_microphone.py"
echo "  ./run_with_audio.sh poetry run python test_voice_recording.py"
echo "  ./run_with_audio.sh python3 test_audio_fixed.py"
echo ""
echo "Or add to your shell:"
echo "  export LD_LIBRARY_PATH='$PORTAUDIO_PATH/lib:\$LD_LIBRARY_PATH'"