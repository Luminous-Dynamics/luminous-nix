#!/usr/bin/env bash
# Professional Piper Voice Model Installer
# Downloads and installs voice models for Piper TTS

set -e

# Configuration
PIPER_VERSION="v1.2.0"
MODEL_DIR="$HOME/.local/share/piper"
GITHUB_BASE="https://github.com/rhasspy/piper/releases/download/${PIPER_VERSION}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          🎭 Piper Voice Model Installer 🎭                      ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║     Professional voice model setup for Piper TTS                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Available models with descriptions
declare -A MODELS=(
    ["en_US-amy-medium"]="American English, Female, Medium quality (Recommended)"
    ["en_US-danny-low"]="American English, Male, Low quality (Fast)"
    ["en_US-kathleen-low"]="American English, Female, Low quality (Fast)"
    ["en_US-lessac-high"]="American English, Neutral, High quality (Best)"
    ["en_GB-alan-low"]="British English, Male, Low quality"
    ["en_GB-jenny_dioco-medium"]="British English, Female, Medium quality"
)

# Function to download a model
download_model() {
    local model_name=$1
    local description=$2
    
    echo -e "\n${BLUE}📥 Downloading: ${model_name}${NC}"
    echo -e "   ${description}"
    
    # Check if already exists
    if [ -f "${MODEL_DIR}/${model_name}.onnx" ] && [ -f "${MODEL_DIR}/${model_name}.onnx.json" ]; then
        echo -e "${YELLOW}   ⚠️  Model already exists, skipping${NC}"
        return 0
    fi
    
    # Download model file
    echo -e "   📦 Downloading model file..."
    if curl -L --progress-bar "${GITHUB_BASE}/${model_name}.onnx" -o "${MODEL_DIR}/${model_name}.onnx"; then
        echo -e "${GREEN}   ✅ Model downloaded${NC}"
    else
        echo -e "${RED}   ❌ Failed to download model${NC}"
        return 1
    fi
    
    # Download config file
    echo -e "   📦 Downloading config file..."
    if curl -L --progress-bar "${GITHUB_BASE}/${model_name}.onnx.json" -o "${MODEL_DIR}/${model_name}.onnx.json"; then
        echo -e "${GREEN}   ✅ Config downloaded${NC}"
    else
        echo -e "${RED}   ❌ Failed to download config${NC}"
        return 1
    fi
    
    # Verify files
    local model_size=$(du -h "${MODEL_DIR}/${model_name}.onnx" | cut -f1)
    echo -e "${GREEN}   ✅ Model installed (${model_size})${NC}"
    
    return 0
}

# Create model directory
echo -e "${BLUE}📁 Setting up model directory...${NC}"
mkdir -p "$MODEL_DIR"
echo -e "${GREEN}✅ Directory ready: ${MODEL_DIR}${NC}"

# Check existing models
echo -e "\n${BLUE}🔍 Checking existing models...${NC}"
existing_count=$(find "$MODEL_DIR" -name "*.onnx" 2>/dev/null | wc -l)
if [ "$existing_count" -gt 0 ]; then
    echo -e "${GREEN}✅ Found ${existing_count} existing model(s)${NC}"
    ls -lh "$MODEL_DIR"/*.onnx 2>/dev/null | awk '{print "   • " $9 " (" $5 ")"}'
else
    echo -e "${YELLOW}⚠️  No existing models found${NC}"
fi

# Model selection
echo -e "\n${BLUE}📋 Available Models:${NC}"
echo ""
echo "  1) en_US-amy-medium - ${MODELS[en_US-amy-medium]} [RECOMMENDED]"
echo "  2) en_US-danny-low - ${MODELS[en_US-danny-low]}"
echo "  3) en_US-kathleen-low - ${MODELS[en_US-kathleen-low]}"
echo "  4) en_US-lessac-high - ${MODELS[en_US-lessac-high]}"
echo "  5) en_GB-alan-low - ${MODELS[en_GB-alan-low]}"
echo "  6) en_GB-jenny_dioco-medium - ${MODELS[en_GB-jenny_dioco-medium]}"
echo "  7) All American English models"
echo "  8) All models"
echo ""

read -p "Select model(s) to download (1-8, default: 1): " choice
choice=${choice:-1}

# Process selection
case $choice in
    1)
        download_model "en_US-amy-medium" "${MODELS[en_US-amy-medium]}"
        ;;
    2)
        download_model "en_US-danny-low" "${MODELS[en_US-danny-low]}"
        ;;
    3)
        download_model "en_US-kathleen-low" "${MODELS[en_US-kathleen-low]}"
        ;;
    4)
        download_model "en_US-lessac-high" "${MODELS[en_US-lessac-high]}"
        ;;
    5)
        download_model "en_GB-alan-low" "${MODELS[en_GB-alan-low]}"
        ;;
    6)
        download_model "en_GB-jenny_dioco-medium" "${MODELS[en_GB-jenny_dioco-medium]}"
        ;;
    7)
        echo -e "${BLUE}📦 Downloading all American English models...${NC}"
        download_model "en_US-amy-medium" "${MODELS[en_US-amy-medium]}"
        download_model "en_US-danny-low" "${MODELS[en_US-danny-low]}"
        download_model "en_US-kathleen-low" "${MODELS[en_US-kathleen-low]}"
        download_model "en_US-lessac-high" "${MODELS[en_US-lessac-high]}"
        ;;
    8)
        echo -e "${BLUE}📦 Downloading all models...${NC}"
        for model in "${!MODELS[@]}"; do
            download_model "$model" "${MODELS[$model]}"
        done
        ;;
    *)
        echo -e "${YELLOW}Invalid choice, downloading recommended model...${NC}"
        download_model "en_US-amy-medium" "${MODELS[en_US-amy-medium]}"
        ;;
esac

# Test the installation
echo -e "\n${BLUE}🧪 Testing Piper with installed models...${NC}"

# Find a model to test
TEST_MODEL=$(find "$MODEL_DIR" -name "*.onnx" | head -1)

if [ -n "$TEST_MODEL" ]; then
    MODEL_NAME=$(basename "$TEST_MODEL" .onnx)
    echo -e "Testing with model: ${MODEL_NAME}"
    
    # Create test audio
    TEST_TEXT="Hello from Nix for Humanity. Voice synthesis is now operational."
    TEST_OUTPUT="/tmp/piper_test_$(date +%s).wav"
    
    echo "$TEST_TEXT" | piper --model "$TEST_MODEL" --output_file "$TEST_OUTPUT" 2>/dev/null
    
    if [ -f "$TEST_OUTPUT" ]; then
        echo -e "${GREEN}✅ Test successful! Audio generated: $TEST_OUTPUT${NC}"
        
        # Try to play it
        if command -v aplay >/dev/null 2>&1; then
            echo -e "${BLUE}🔊 Playing test audio...${NC}"
            aplay "$TEST_OUTPUT" 2>/dev/null && echo -e "${GREEN}✅ Audio playback successful${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Test audio generation failed${NC}"
    fi
else
    echo -e "${RED}❌ No models found for testing${NC}"
fi

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Installation Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

FINAL_COUNT=$(find "$MODEL_DIR" -name "*.onnx" 2>/dev/null | wc -l)
echo -e "\n${GREEN}✅ Models installed: ${FINAL_COUNT}${NC}"
echo -e "📁 Location: ${MODEL_DIR}"

if [ "$FINAL_COUNT" -gt 0 ]; then
    echo -e "\n${GREEN}🎉 Piper TTS is ready for use!${NC}"
    echo -e "\n${BLUE}Quick test command:${NC}"
    echo "echo 'Hello world' | piper --model ${MODEL_DIR}/$(ls $MODEL_DIR/*.onnx | head -1 | xargs basename) --output_file test.wav"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Run the voice recording test: poetry run python test_voice_recording.py"
    echo "  2. Test the complete pipeline: ./test_voice_simple.sh"
    echo "  3. Integrate with TUI"
else
    echo -e "\n${RED}❌ No models installed. Please run this script again.${NC}"
fi