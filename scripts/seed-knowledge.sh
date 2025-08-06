#!/usr/bin/env bash
# Seed initial knowledge for Sacred Trinity training

KNOWLEDGE_DIR="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/nix-knowledge"
mkdir -p "$KNOWLEDGE_DIR"/{questions,answers,meta}

echo "🌱 Seeding Sacred Trinity knowledge base..."

# Helper function to save Q&A
save_qa() {
    local question="$1"
    local answer="$2"
    local category="$3"
    local timestamp=$(date +%s)
    
    echo "$question" > "$KNOWLEDGE_DIR/questions/q_${timestamp}.txt"
    echo "$answer" > "$KNOWLEDGE_DIR/answers/a_${timestamp}.txt"
    echo "category:$category,source:seed,rating:5" > "$KNOWLEDGE_DIR/meta/m_${timestamp}.txt"
    
    sleep 0.1  # Ensure unique timestamps
}

# Seed empathy-focused Q&As
save_qa "How do I install Firefox?" \
"I'll help you install Firefox! The best way in NixOS is to add it to your system configuration:

1. Open your configuration file: sudo nano /etc/nixos/configuration.nix
2. Find the line with 'environment.systemPackages'
3. Add 'firefox' to the list
4. Save and exit (Ctrl+X, then Y)
5. Apply changes: sudo nixos-rebuild switch

Firefox will then appear in your applications menu!" \
"empathy"

save_qa "My WiFi isn't working" \
"Let's fix your WiFi connection together! First, let me check what's happening:

1. Is your WiFi adapter enabled? Run: nmcli radio wifi
   - If it says 'disabled', enable it with: nmcli radio wifi on

2. Can you see available networks? Run: nmcli device wifi list
   - If you see networks, connect with: nmcli device wifi connect 'YourNetworkName' password 'YourPassword'

3. If nothing works, let's restart the network service:
   sudo systemctl restart NetworkManager

Don't worry, we'll get it working!" \
"empathy"

# Seed expert-focused Q&As
save_qa "Explain how Nix derivations work" \
"Nix derivations are the fundamental building blocks of the Nix package manager. A derivation is a precise description of how to build a package:

1. **Input Specification**: Derivations declare all inputs (source code, dependencies, build tools) with cryptographic hashes
2. **Build Instructions**: Contains the exact steps to transform inputs into outputs
3. **Output Paths**: Specifies where results will be stored in /nix/store
4. **Purity**: Build environment is isolated - same inputs always produce same outputs
5. **Content Addressing**: Output path includes hash of all inputs, ensuring uniqueness

The .drv files in /nix/store are ATerm-formatted descriptions that Nix reads to perform builds. This deterministic model enables reproducibility, rollbacks, and multiple versions coexisting." \
"expert"

# Seed coder-focused Q&As
save_qa "Create a flake.nix for a Python project" \
"Here's a complete flake.nix for a Python development environment:

\`\`\`nix
{
  description = \"Python development environment\";
  
  inputs = {
    nixpkgs.url = \"github:NixOS/nixpkgs/nixos-unstable\";
    flake-utils.url = \"github:numtide/flake-utils\";
  };
  
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.\${system};
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pip
          numpy
          pandas
          requests
          pytest
          black
          ipython
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            ruff
            poetry
          ];
          
          shellHook = ''
            echo \"🐍 Python \$(python --version)\"
            echo \"📦 Packages: numpy, pandas, requests, pytest\"
            echo \"🛠️  Tools: black, ruff, poetry, ipython\"
          '';
        };
      });
}
\`\`\`

Usage: \`nix develop\` to enter the environment." \
"coder"

# Seed quick-focused Q&As
save_qa "Update system" \
"sudo nixos-rebuild switch" \
"quick"

save_qa "List installed packages" \
"nix-env -q" \
"quick"

save_qa "Check disk space" \
"df -h" \
"quick"

# Trinity-specific patterns
save_qa "What's the Sacred Trinity workflow?" \
"The Sacred Trinity workflow combines three perspectives for complete solutions:

1. **Human (You)**: Provides vision, identifies user needs, ensures solutions work for real people
2. **Claude**: Designs architecture, implements features, ensures code quality
3. **Local LLM (Me)**: Provides NixOS expertise, best practices, and technical guidance

Together, we create solutions that are both technically excellent and user-friendly. Each member contributes their unique strengths to serve users with wisdom and compassion." \
"expert"

echo "✅ Seeded $(ls -1 $KNOWLEDGE_DIR/questions | wc -l) initial Q&A pairs"
echo ""
echo "📊 Categories:"
for cat in empathy expert coder quick; do
    count=$(grep -l "category:$cat" $KNOWLEDGE_DIR/meta/*.txt 2>/dev/null | wc -l)
    echo "   $cat: $count examples"
done