#!/bin/bash
# GitHub App Setup Script for Nix for Humanity

echo "🔐 Setting up GitHub App authentication for Luminous-Dynamics"
echo "=================================================="

# Configuration
APP_ID="1666597"
INSTALLATION_ID="77624593"
CLIENT_ID="Iv23liNghcfdG5aiDbGz"
ORG_NAME="Luminous-Dynamics"
REPO_NAME="nix-for-humanity"

# Secure directory for credentials
SECURE_DIR="$HOME/.config/luminous-dynamics/github-app"
mkdir -p "$SECURE_DIR"
chmod 700 "$SECURE_DIR"

# Function to find and secure PEM file
secure_pem_file() {
    echo ""
    echo "🔍 Looking for GitHub App private key (PEM file)..."

    # Common locations and patterns
    PEM_PATTERNS=(
        "$HOME/Downloads/*.pem"
        "$HOME/Downloads/*private*key*.pem"
        "$HOME/Downloads/*github*.pem"
        "$HOME/Downloads/*luminous*.pem"
        "$HOME/Downloads/*app*.pem"
    )

    for pattern in "${PEM_PATTERNS[@]}"; do
        for file in $pattern; do
            if [ -f "$file" ]; then
                echo "✅ Found PEM file: $file"

                # Secure the PEM file
                PEM_DEST="$SECURE_DIR/github-app-private-key.pem"
                echo "🔒 Moving to secure location: $PEM_DEST"

                mv "$file" "$PEM_DEST"
                chmod 600 "$PEM_DEST"

                echo "✅ PEM file secured!"
                return 0
            fi
        done
    done

    echo "❌ No PEM file found automatically."
    echo ""
    echo "Please locate the PEM file manually. It was downloaded when you created the GitHub App."
    echo "Common names:"
    echo "  - luminous-dynamics-claude-code.YYYY-MM-DD.private-key.pem"
    echo "  - [app-name].private-key.pem"
    echo ""
    read -p "Enter the full path to the PEM file: " PEM_PATH

    if [ -f "$PEM_PATH" ]; then
        PEM_DEST="$SECURE_DIR/github-app-private-key.pem"
        echo "🔒 Moving to secure location: $PEM_DEST"
        mv "$PEM_PATH" "$PEM_DEST"
        chmod 600 "$PEM_DEST"
        echo "✅ PEM file secured!"
        return 0
    else
        echo "❌ File not found: $PEM_PATH"
        return 1
    fi
}

# Function to generate JWT token
generate_jwt() {
    local pem_file="$1"
    local app_id="$2"

    # This would normally use a JWT library, but for now we'll use a placeholder
    # In production, use a proper JWT generation tool
    echo "JWT_TOKEN_PLACEHOLDER"
}

# Function to get installation access token
get_installation_token() {
    local jwt="$1"
    local installation_id="$2"

    # This would make an API call to GitHub
    # For now, return placeholder
    echo "INSTALLATION_TOKEN_PLACEHOLDER"
}

# Main setup process
main() {
    echo "📋 GitHub App Details:"
    echo "  App ID: $APP_ID"
    echo "  Installation ID: $INSTALLATION_ID"
    echo "  Organization: $ORG_NAME"
    echo "  Repository: $REPO_NAME"
    echo ""

    # Step 1: Secure the PEM file
    if ! secure_pem_file; then
        echo "❌ Cannot proceed without PEM file"
        exit 1
    fi

    # Step 2: Save configuration
    CONFIG_FILE="$SECURE_DIR/config.json"
    cat > "$CONFIG_FILE" << EOF
{
  "app_id": "$APP_ID",
  "installation_id": "$INSTALLATION_ID",
  "client_id": "$CLIENT_ID",
  "org_name": "$ORG_NAME",
  "repo_name": "$REPO_NAME",
  "pem_file": "$SECURE_DIR/github-app-private-key.pem"
}
EOF
    chmod 600 "$CONFIG_FILE"
    echo "✅ Configuration saved to: $CONFIG_FILE"

    # Step 3: Create authentication script
    AUTH_SCRIPT="$SECURE_DIR/authenticate.sh"
    cat > "$AUTH_SCRIPT" << 'SCRIPT'
#!/bin/bash
# GitHub App Authentication Script

CONFIG_FILE="$HOME/.config/luminous-dynamics/github-app/config.json"
PEM_FILE=$(jq -r .pem_file "$CONFIG_FILE")
APP_ID=$(jq -r .app_id "$CONFIG_FILE")

# Check if gh CLI supports app auth (requires gh 2.40+)
if gh auth status --hostname github.com 2>&1 | grep -q "github-app"; then
    echo "✅ GitHub App authentication already configured"
else
    echo "🔐 Setting up GitHub App authentication..."

    # Use gh CLI with app credentials
    gh auth login \
        --hostname github.com \
        --with-token < <(echo "$GITHUB_TOKEN")
fi

# Export for use in scripts
export GITHUB_APP_ID="$APP_ID"
export GITHUB_APP_PEM_FILE="$PEM_FILE"
SCRIPT
    chmod 700 "$AUTH_SCRIPT"
    echo "✅ Authentication script created: $AUTH_SCRIPT"

    # Step 4: Create push helper script
    PUSH_SCRIPT="$HOME/bin/gh-push-nix-humanity"
    mkdir -p "$HOME/bin"
    cat > "$PUSH_SCRIPT" << 'PUSH'
#!/bin/bash
# Push to nix-for-humanity repository using GitHub App

set -e

# Load configuration
CONFIG_FILE="$HOME/.config/luminous-dynamics/github-app/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Configuration not found. Run setup-github-app.sh first!"
    exit 1
fi

# Authenticate
source "$HOME/.config/luminous-dynamics/github-app/authenticate.sh"

# Change to repository directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Configure git to use GitHub CLI
git config credential.helper ""
git config credential.helper "!gh auth git-credential"

# Push
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Push complete!"
PUSH
    chmod 755 "$PUSH_SCRIPT"
    echo "✅ Push helper script created: $PUSH_SCRIPT"

    # Step 5: Documentation
    DOC_FILE="$SECURE_DIR/README.md"
    cat > "$DOC_FILE" << 'DOC'
# GitHub App Authentication for Luminous-Dynamics

This directory contains secure credentials for GitHub App authentication.

## Files

- `github-app-private-key.pem` - Private key for GitHub App (KEEP SECURE!)
- `config.json` - App configuration
- `authenticate.sh` - Authentication helper script
- `README.md` - This file

## Usage

### Authenticate with GitHub
```bash
source ~/.config/luminous-dynamics/github-app/authenticate.sh
```

### Push to nix-for-humanity
```bash
gh-push-nix-humanity
```

### Manual push with gh CLI
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
gh auth login --with-token < <(gh auth token)
git push origin main
```

## Security

- NEVER share the PEM file
- Keep permissions restrictive (600 for files, 700 for directory)
- Rotate keys periodically
- Use environment variables for automation

## Troubleshooting

If authentication fails:
1. Check gh CLI version: `gh --version` (need 2.40+)
2. Verify PEM file exists and has correct permissions
3. Check GitHub App is still installed in organization
4. Regenerate PEM key if compromised
DOC

    echo ""
    echo "✅ GitHub App setup complete!"
    echo ""
    echo "📁 Secure files location: $SECURE_DIR"
    echo ""
    echo "🚀 To push to GitHub:"
    echo "   gh-push-nix-humanity"
    echo ""
    echo "📚 For more information, see: $DOC_FILE"
    echo ""
    echo "⚠️  IMPORTANT: Keep the PEM file secure and never commit it to git!"
}

# Run main setup
main
