#!/usr/bin/env bash
# Script to integrate the trained NixOS expert model with ask-nix-guru

set -e

echo "🔗 Integrating Trained Model with ask-nix-guru"
echo "============================================="
echo ""

# Check if model exists
if ! ollama list | grep -q "nixos-expert"; then
    echo "❌ Error: nixos-expert model not found!"
    echo "Please run the training pipeline first:"
    echo "  python3 train-nixos-expert.py"
    exit 1
fi

# Update ask-nix-guru to use the trained model
ASK_NIX_GURU_PATH="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-nix-guru"

if [[ -f "$ASK_NIX_GURU_PATH" ]]; then
    echo "✅ Found ask-nix-guru at: $ASK_NIX_GURU_PATH"
    
    # Create updated version that uses trained model
    cat > "${ASK_NIX_GURU_PATH}.trained" << 'EOF'
#!/usr/bin/env bash
# ask-nix-guru with trained NixOS expert model

# Use the trained model by default
MODEL="${NIX_GURU_MODEL:-nixos-expert}"

# Fallback models if trained model not available
FALLBACK_MODELS=("codellama:7b" "mistral:7b" "llama2:7b")

# Check if model exists
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    echo "🔄 Trained model '$MODEL' not found. Using fallback..."
    for fallback in "${FALLBACK_MODELS[@]}"; do
        if ollama list 2>/dev/null | grep -q "$fallback"; then
            MODEL="$fallback"
            echo "📚 Using fallback model: $MODEL"
            break
        fi
    done
fi

# Function to ensure Ollama is running
ensure_ollama() {
    if ! pgrep -x "ollama" > /dev/null; then
        echo "🚀 Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
}

# Function to ask the guru
ask_guru() {
    local question="$*"
    
    # Add NixOS context to improve responses
    local prompt="You are a NixOS expert trained on official documentation. Answer this question concisely and accurately: $question"
    
    # Save Q&A for future training
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local knowledge_dir="${NIXOS_KNOWLEDGE_DIR:-$HOME/.nix-for-humanity/knowledge}"
    mkdir -p "$knowledge_dir/questions" "$knowledge_dir/answers"
    
    echo "$question" > "$knowledge_dir/questions/q_$timestamp.txt"
    
    # Get response
    local response=$(ollama run "$MODEL" "$prompt" 2>/dev/null)
    
    # Save response
    echo "$response" > "$knowledge_dir/answers/a_$timestamp.txt"
    
    # Display response
    echo "$response"
}

# Main execution
ensure_ollama

if [ $# -eq 0 ]; then
    echo "🤖 NixOS Guru (Trained Model: $MODEL)"
    echo "Usage: ask-nix-guru <your question>"
    echo ""
    echo "Examples:"
    echo "  ask-nix-guru How do I install Firefox?"
    echo "  ask-nix-guru What is a NixOS generation?"
    echo "  ask-nix-guru How do I rollback my system?"
    echo ""
    echo "Set NIX_GURU_MODEL environment variable to use a different model."
    exit 0
fi

ask_guru "$@"
EOF

    # Make executable
    chmod +x "${ASK_NIX_GURU_PATH}.trained"
    
    echo "✅ Created enhanced ask-nix-guru with trained model support"
    echo ""
    echo "To use the trained version:"
    echo "  1. Replace the original: mv ${ASK_NIX_GURU_PATH}.trained ${ASK_NIX_GURU_PATH}"
    echo "  2. Or test it directly: ${ASK_NIX_GURU_PATH}.trained 'your question'"
    echo ""
else
    echo "⚠️  ask-nix-guru not found at expected location"
    echo "Creating a new one..."
    
    mkdir -p "$(dirname "$ASK_NIX_GURU_PATH")"
    cat > "$ASK_NIX_GURU_PATH" << 'EOF'
#!/usr/bin/env bash
# ask-nix-guru - Query the trained NixOS expert model

MODEL="${NIX_GURU_MODEL:-nixos-expert}"

if ! command -v ollama &> /dev/null; then
    echo "❌ Error: Ollama not installed. Please install it first."
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "🤖 NixOS Guru (Model: $MODEL)"
    echo "Usage: ask-nix-guru <your question>"
    exit 0
fi

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Ask the trained model
ollama run "$MODEL" "You are a NixOS expert. Answer concisely: $*"
EOF
    
    chmod +x "$ASK_NIX_GURU_PATH"
    echo "✅ Created new ask-nix-guru script"
fi

echo "🧪 Testing the trained model..."
echo ""
echo "Example query: 'What is the difference between nix-env and configuration.nix?'"
echo ""

if command -v ask-nix-guru &> /dev/null; then
    ask-nix-guru "What is the difference between nix-env and configuration.nix?" || {
        echo "⚠️  Test failed. Make sure the model is trained and Ollama is running."
    }
else
    echo "ℹ️  Add $(dirname "$ASK_NIX_GURU_PATH") to your PATH to use ask-nix-guru from anywhere"
    echo "  export PATH=\"\$PATH:$(dirname "$ASK_NIX_GURU_PATH")\""
fi

echo ""
echo "✅ Integration complete!"
echo ""
echo "📚 Next steps:"
echo "  1. Train more specific models for different domains"
echo "  2. Collect user questions to improve training data"
echo "  3. Set up automatic retraining with new documentation"