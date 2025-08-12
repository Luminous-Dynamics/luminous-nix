#!/usr/bin/env bash
# Simple voice test without complex dependencies

echo "🎤 Simple Voice Pipeline Test"
echo "=============================="
echo ""

# Test 1: Check if voice tools are available
echo "1️⃣ Checking voice tools..."
which whisper && echo "✅ Whisper found" || echo "❌ Whisper not found"
which piper && echo "✅ Piper found" || echo "❌ Piper not found"
which ffmpeg && echo "✅ FFmpeg found" || echo "❌ FFmpeg not found"
echo ""

# Test 2: Test Whisper with a sample file
echo "2️⃣ Testing Whisper..."
if which whisper >/dev/null; then
    # Create a simple test audio file with ffmpeg
    TEST_DIR=$(mktemp -d)
    TEST_AUDIO="$TEST_DIR/test.wav"
    
    # Generate a sine wave (beep) as test audio
    ffmpeg -f lavfi -i "sine=frequency=1000:duration=1" -ac 1 -ar 16000 "$TEST_AUDIO" -y 2>/dev/null
    
    if [ -f "$TEST_AUDIO" ]; then
        echo "  Created test audio: $TEST_AUDIO"
        
        # Try to transcribe it
        echo "  Attempting transcription..."
        whisper "$TEST_AUDIO" --model tiny --output_dir "$TEST_DIR" --language en 2>&1 | grep -E "(Detected|text)" | head -5
        
        # Check for output
        if [ -f "$TEST_DIR/test.txt" ]; then
            echo "  Transcription result: $(cat $TEST_DIR/test.txt)"
        fi
    else
        echo "  Could not create test audio"
    fi
else
    echo "  Skipping - Whisper not available"
fi
echo ""

# Test 3: Test Piper TTS
echo "3️⃣ Testing Piper..."
if which piper >/dev/null; then
    TEST_TEXT="Hello from Nix for Humanity voice interface"
    OUTPUT_FILE="$TEST_DIR/speech.wav"
    
    echo "  Input text: '$TEST_TEXT'"
    echo "$TEST_TEXT" | piper --output_file "$OUTPUT_FILE" 2>&1 | grep -v "^$" | head -5
    
    if [ -f "$OUTPUT_FILE" ]; then
        echo "✅ Speech generated: $OUTPUT_FILE"
        # Try to play it
        if which aplay >/dev/null; then
            echo "  Playing audio..."
            aplay "$OUTPUT_FILE" 2>/dev/null && echo "✅ Audio played" || echo "⚠️  Could not play audio"
        fi
    else
        echo "⚠️  No speech file generated"
        echo "  Piper may need to download voice models on first use"
    fi
else
    echo "  Skipping - Piper not available"
fi
echo ""

# Test 4: Check Python audio support
echo "4️⃣ Testing Python audio packages..."
python3 -c "
import sys
packages = ['whisper', 'sounddevice', 'numpy', 'pyttsx3']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg} available')
    except ImportError:
        print(f'  ❌ {pkg} not found')
" 2>/dev/null || echo "  ⚠️  Python packages need to be installed via Poetry"

echo ""
echo "📊 Summary"
echo "=========="
echo "Voice tools are installed at the system level."
echo "Python packages need to be installed via Poetry."
echo ""
echo "Next steps:"
echo "1. Download Whisper models: whisper --model base --help"
echo "2. Download Piper voices: echo 'test' | piper --list-models"
echo "3. Fix Poetry dependencies and run full test"
echo ""
echo "Test files saved in: ${TEST_DIR:-/tmp}"