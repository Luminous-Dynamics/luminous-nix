#!/usr/bin/env bash
# Add essential NixOS knowledge to the training data

echo "📚 Adding NixOS-specific knowledge..."

KNOWLEDGE_DIR="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/docs/nix-knowledge"
mkdir -p "$KNOWLEDGE_DIR"/{questions,answers,examples}

# Helper function to add Q&A pair
add_qa() {
    local question="$1"
    local answer="$2"
    local timestamp=$(date +%s.%N)
    
    echo "$question" > "$KNOWLEDGE_DIR/questions/q_$timestamp.txt"
    echo "$answer" > "$KNOWLEDGE_DIR/answers/a_$timestamp.txt"
    sleep 0.1  # Ensure unique timestamps
}

# Add essential NixOS knowledge
add_qa "How do I install Firefox on NixOS?" "There are several ways to install Firefox on NixOS:

1. **Temporarily (for current session)**:
   \`\`\`bash
   nix-shell -p firefox
   \`\`\`

2. **For current user (imperative)**:
   \`\`\`bash
   nix-env -iA nixos.firefox
   \`\`\`

3. **System-wide (declarative - recommended)**:
   Edit /etc/nixos/configuration.nix and add firefox to environment.systemPackages:
   \`\`\`nix
   environment.systemPackages = with pkgs; [
     firefox
     # other packages...
   ];
   \`\`\`
   Then apply:
   \`\`\`bash
   sudo nixos-rebuild switch
   \`\`\`

4. **Using Home Manager (declarative for user)**:
   Add to home.nix:
   \`\`\`nix
   home.packages = with pkgs; [
     firefox
   ];
   \`\`\`"

add_qa "How do I update my NixOS system?" "To update NixOS:

1. **Update channel** (get latest package definitions):
   \`\`\`bash
   sudo nix-channel --update
   \`\`\`

2. **Rebuild system** with updates:
   \`\`\`bash
   sudo nixos-rebuild switch
   \`\`\`

3. **Or do both in one command**:
   \`\`\`bash
   sudo nixos-rebuild switch --upgrade
   \`\`\`

4. **Check what would change** (dry run):
   \`\`\`bash
   sudo nixos-rebuild dry-build
   \`\`\`"

add_qa "What is a Nix flake?" "A Nix flake is a new way to manage Nix projects with these benefits:

- **Reproducible**: Locks all dependencies
- **Hermetic**: Pure evaluation, no impurities
- **Composable**: Easy to use other flakes

Basic flake structure:
\`\`\`nix
{
  description = \"My project\";
  
  inputs = {
    nixpkgs.url = \"github:NixOS/nixpkgs/nixos-unstable\";
  };
  
  outputs = { self, nixpkgs }: {
    # Your outputs here
  };
}
\`\`\`

Enable flakes by adding to configuration.nix:
\`\`\`nix
nix.settings.experimental-features = [ \"nix-command\" \"flakes\" ];
\`\`\`"

add_qa "How do I rollback my NixOS system?" "NixOS makes rollbacks easy:

1. **List generations**:
   \`\`\`bash
   sudo nix-env --list-generations --profile /nix/var/nix/profiles/system
   \`\`\`

2. **Rollback to previous**:
   \`\`\`bash
   sudo nixos-rebuild switch --rollback
   \`\`\`

3. **Switch to specific generation**:
   \`\`\`bash
   sudo nix-env --switch-generation 42 --profile /nix/var/nix/profiles/system
   sudo /nix/var/nix/profiles/system/bin/switch-to-configuration switch
   \`\`\`

4. **Boot menu**: You can also select older generations from the boot menu!"

echo "✅ Added $(ls -1 $KNOWLEDGE_DIR/questions/q_*.txt | wc -l) Q&A pairs"
echo ""
echo "To retrain models with this knowledge:"
echo "  cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts"
echo "  python3 sacred-trinity-trainer-v2.py --force"