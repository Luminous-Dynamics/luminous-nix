#!/usr/bin/env bash
# Professional Piper model downloader with proper error handling

set -e

echo "🎭 Downloading Piper Voice Model"
echo "================================"

# Configuration
MODEL_DIR="$HOME/.local/share/piper"
MODEL_NAME="en_US-amy-medium"

# Create directory
mkdir -p "$MODEL_DIR"

# Download URLs from Hugging Face (more reliable mirror)
MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx"
CONFIG_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"

echo ""
echo "📥 Downloading model file (this may take a minute)..."
echo "   Source: Hugging Face (reliable mirror)"
echo "   Target: $MODEL_DIR/$MODEL_NAME.onnx"

# Download with progress bar
if curl -L --progress-bar "$MODEL_URL" -o "$MODEL_DIR/$MODEL_NAME.onnx"; then
    echo "✅ Model downloaded successfully"
else
    echo "❌ Failed to download model"
    exit 1
fi

echo ""
echo "📥 Downloading config file..."
if curl -L --progress-bar "$CONFIG_URL" -o "$MODEL_DIR/$MODEL_NAME.onnx.json"; then
    echo "✅ Config downloaded successfully"
else
    echo "❌ Failed to download config"
    exit 1
fi

# Verify file sizes
echo ""
echo "📊 Verifying downloads..."
MODEL_SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME.onnx" | cut -f1)
CONFIG_SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME.onnx.json" | cut -f1)

echo "   Model: $MODEL_SIZE (should be ~60MB)"
echo "   Config: $CONFIG_SIZE (should be ~5KB)"

# Check if model is reasonable size (at least 10MB)
MODEL_BYTES=$(stat -c%s "$MODEL_DIR/$MODEL_NAME.onnx" 2>/dev/null || stat -f%z "$MODEL_DIR/$MODEL_NAME.onnx" 2>/dev/null || echo "0")
if [ "$MODEL_BYTES" -lt 10000000 ]; then
    echo ""
    echo "⚠️  Model file seems too small. Download may have failed."
    echo "   Please check your internet connection and try again."
    exit 1
fi

echo ""
echo "✅ Model downloaded and verified!"
echo ""
echo "🧪 Testing the model..."

# Test the model
TEST_TEXT="Hello from Nix for Humanity. Voice synthesis is now operational."
TEST_FILE="/tmp/piper_test_$(date +%s).wav"

echo "$TEST_TEXT" | piper \
    --model "$MODEL_DIR/$MODEL_NAME.onnx" \
    --output_file "$TEST_FILE" 2>/dev/null

if [ -f "$TEST_FILE" ]; then
    FILE_SIZE=$(du -h "$TEST_FILE" | cut -f1)
    echo "✅ Test successful! Generated $FILE_SIZE audio file"
    echo "   Output: $TEST_FILE"
    
    # Try to play it
    if command -v aplay >/dev/null 2>&1; then
        echo ""
        echo "🔊 Playing test audio..."
        aplay "$TEST_FILE" 2>/dev/null && echo "✅ Playback successful!" || echo "⚠️  Could not play (no audio device?)"
    fi
else
    echo "⚠️  Test failed - but model is downloaded"
    echo "   You can test manually with:"
    echo "   echo 'test' | piper --model $MODEL_DIR/$MODEL_NAME.onnx --output_file test.wav"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Quick test command:"
echo "  echo 'Hello world' | piper --model $MODEL_DIR/$MODEL_NAME.onnx --output_file test.wav"
echo ""
echo "Next steps:"
echo "  1. Run: python3 test_piper_simple.py"
echo "  2. Test voice recording pipeline"
echo "  3. Integrate with TUI"