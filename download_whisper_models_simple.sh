#!/usr/bin/env bash
# Download Whisper models for offline speech recognition

set -e

echo "🎙️ Downloading Whisper Models"
echo "=============================="
echo ""

# Model to download (base.en is a good balance of speed/accuracy)
MODEL="base.en"
MODEL_URL="https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/${MODEL}.pt"
MODEL_DIR="$HOME/.cache/whisper"

echo "📦 Model: $MODEL (140MB)"
echo "📁 Target: $MODEL_DIR"
echo ""

# Create directory
mkdir -p "$MODEL_DIR"

# Check if already downloaded
if [ -f "$MODEL_DIR/${MODEL}.pt" ]; then
    SIZE=$(du -h "$MODEL_DIR/${MODEL}.pt" | cut -f1)
    echo "✅ Model already downloaded ($SIZE)"
    echo "   Location: $MODEL_DIR/${MODEL}.pt"
else
    echo "📥 Downloading model..."
    echo "   This may take a few minutes..."
    
    # Download with curl (show progress)
    if curl -L --progress-bar "$MODEL_URL" -o "$MODEL_DIR/${MODEL}.pt"; then
        SIZE=$(du -h "$MODEL_DIR/${MODEL}.pt" | cut -f1)
        echo "✅ Model downloaded successfully ($SIZE)"
    else
        echo "❌ Download failed"
        echo "   You can also download by running:"
        echo "   whisper --model base.en --language en audio.wav"
        exit 1
    fi
fi

echo ""
echo "🧪 Testing Whisper with downloaded model..."

# Create a test audio file with ffmpeg
TEST_DIR=$(mktemp -d)
TEST_AUDIO="$TEST_DIR/test.wav"

# Generate 2 seconds of sine wave
ffmpeg -f lavfi -i "sine=frequency=440:duration=2" -ac 1 -ar 16000 "$TEST_AUDIO" -y 2>/dev/null

if [ -f "$TEST_AUDIO" ]; then
    echo "📝 Testing transcription..."
    
    # Test whisper
    if whisper "$TEST_AUDIO" --model base.en --language en --output_dir "$TEST_DIR" 2>&1 | grep -q "Detected"; then
        echo "✅ Whisper is working with the model!"
    else
        echo "⚠️  Whisper test had issues (this may be normal for sine wave audio)"
    fi
    
    # Clean up
    rm -rf "$TEST_DIR"
else
    echo "⚠️  Could not create test audio"
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "Available models:"
ls -lh "$MODEL_DIR"/*.pt 2>/dev/null || echo "No models found"
echo ""
echo "Usage:"
echo "  whisper audio.wav --model base.en --language en"
echo "  whisper audio.mp3 --model base.en --task transcribe"
echo ""
echo "Next steps:"
echo "  1. Test with real audio: whisper recording.wav --model base.en"
echo "  2. Integrate with voice pipeline"
echo "  3. Test with different accents/voices"