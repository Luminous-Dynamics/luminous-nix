#!/usr/bin/env bash
# Setup Ollama for Sacred Trinity

echo "🔮 Setting up Ollama for Sacred Trinity..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install it first:"
    echo "   In your configuration.nix, add: pkgs.ollama"
    exit 1
fi

# Create systemd user service
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/ollama.service << 'EOF'
[Unit]
Description=Ollama Model Server
After=network.target

[Service]
Type=simple
ExecStart=/run/current-system/sw/bin/ollama serve
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=%h/.ollama/models"

[Install]
WantedBy=default.target
EOF

echo "✅ Created systemd service"

# Enable and start the service
systemctl --user daemon-reload
systemctl --user enable ollama.service
systemctl --user start ollama.service

echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if running
if systemctl --user is-active ollama.service >/dev/null 2>&1; then
    echo "✅ Ollama service is running!"

    # Pull base models if not present
    echo ""
    echo "📥 Checking base models..."

    for model in mistral:7b phi-2; do
        if ! ollama list | grep -q "$model"; then
            echo "Pulling $model..."
            ollama pull $model
        else
            echo "✓ $model already available"
        fi
    done

    # Optional: Pull better models if RAM available
    echo ""
    echo "📊 System memory: $(free -h | grep Mem | awk '{print $2}')"
    echo ""
    echo "🤔 Would you like to pull additional models?"
    echo "1. gemma:7b (Better conversations, needs 8GB)"
    echo "2. deepseek-coder:6.7b (Better code, needs 8GB)"
    echo "3. mixtral:8x7b (Best reasoning, needs 48GB)"
    echo "4. Skip additional models"
    echo ""
    read -p "Select (1-4) [4]: " choice

    case $choice in
        1) ollama pull gemma:7b ;;
        2) ollama pull deepseek-coder:6.7b ;;
        3) ollama pull mixtral:8x7b ;;
        *) echo "Skipping additional models" ;;
    esac

else
    echo "❌ Failed to start Ollama service"
    echo "Try starting manually: ollama serve"
    exit 1
fi

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "📝 Next: Run the Sacred Trinity trainer"
echo "   cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts"
echo "   python3 sacred-trinity-trainer-v2.py"
