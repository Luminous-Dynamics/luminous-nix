#!/usr/bin/env bash
# Fix modelfile syntax for coder and quick models

echo "🔧 Creating fixed modelfiles for coder and quick models..."

# Create coder modelfile
cat > /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/training-data/coder_fixed.modelfile << 'EOF'
FROM qwen2.5:3b

SYSTEM You are a NixOS expert specializing in generating Nix configurations and scripts. You are part of the Sacred Trinity workflow. Always provide complete, working code examples with clear explanations.

PARAMETER temperature 0.5
EOF

# Create quick modelfile
cat > /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/training-data/quick_fixed.modelfile << 'EOF'
FROM tinyllama:1.1b

SYSTEM You are a NixOS expert providing quick answers to simple questions. You are part of the Sacred Trinity workflow. Be concise and direct in your responses.

PARAMETER temperature 0.6
EOF

# Create the models
echo "Creating nix-coder model..."
ollama create nix-coder -f /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/training-data/coder_fixed.modelfile

echo "Creating nix-quick model..."
ollama create nix-quick -f /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/training-data/quick_fixed.modelfile

# Update current model files
echo "nix-coder" > /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/models/current_coder.txt
echo "nix-quick" > /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/models/current_quick.txt

echo "✅ Models fixed and created!"