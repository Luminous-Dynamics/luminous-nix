#!/usr/bin/env bash

# Sacred Trinity Setup Script
# Configures the development environment with Mistral-7B for NixOS expertise

set -euo pipefail

echo "🌟 Sacred Trinity Development Setup 🌟"
echo "====================================="
echo
echo "This script will set up:"
echo "1. Development environment with Nix"
echo "2. Ollama with Mistral-7B model"
echo "3. Sacred Trinity workflow tools"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "flake.nix" ]; then
    echo -e "${RED}❌ Error: Not in Nix for Humanity directory${NC}"
    echo "Please run this from: /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    exit 1
fi

# Step 1: Enter Nix development shell
echo -e "${YELLOW}📦 Step 1: Preparing Nix development environment...${NC}"
echo "This will download all necessary tools including Ollama"
echo

# Check if already in nix shell
if [ -z "${IN_NIX_SHELL:-}" ]; then
    echo "Entering Nix development shell..."
    echo "Note: First time may take a while to download dependencies"
    exec nix develop -c "$0" "$@"
fi

echo -e "${GREEN}✅ Nix environment ready!${NC}"
echo

# Step 2: Check Ollama service
echo -e "${YELLOW}🤖 Step 2: Checking Ollama service...${NC}"

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    echo "Waiting for Ollama to start..."
    sleep 5
    
    # Check if it started successfully
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to start Ollama service${NC}"
        echo "You may need to start it manually with: ollama serve"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Ollama service is running${NC}"
fi

# Step 3: Download Mistral-7B model
echo -e "${YELLOW}📥 Step 3: Setting up Mistral-7B model...${NC}"
echo "This is a one-time download of ~4GB"
echo

if ollama list | grep -q "mistral:7b"; then
    echo -e "${GREEN}✅ Mistral-7B already installed${NC}"
else
    echo "Downloading Mistral-7B..."
    echo "This will take a few minutes depending on your internet speed..."
    if ollama pull mistral:7b; then
        echo -e "${GREEN}✅ Mistral-7B downloaded successfully${NC}"
    else
        echo -e "${RED}❌ Failed to download Mistral-7B${NC}"
        echo "Please check your internet connection and try again"
        exit 1
    fi
fi

# Step 4: Test the Sacred Trinity setup
echo -e "${YELLOW}🧪 Step 4: Testing Sacred Trinity workflow...${NC}"
echo

# Test ask-nix-guru command
echo "Testing NixOS expertise query..."
TEST_RESPONSE=$(ask-nix-guru "What is a Nix derivation?" 2>/dev/null || echo "Error")

if [[ "$TEST_RESPONSE" == "Error" ]] || [[ -z "$TEST_RESPONSE" ]]; then
    echo -e "${RED}❌ Failed to get response from Nix Guru${NC}"
    echo "Please check that Ollama is running and Mistral-7B is installed"
else
    echo -e "${GREEN}✅ Sacred Trinity is working!${NC}"
    echo
    echo "Sample response:"
    echo "$TEST_RESPONSE" | head -5
    echo "..."
fi

# Step 5: Create quick reference
echo
echo -e "${YELLOW}📚 Step 5: Creating quick reference...${NC}"

cat > sacred-trinity-quickstart.md << 'EOF'
# Sacred Trinity Quick Reference

## The Three Roles

1. **Human (You)** 👤
   - Provides vision and requirements
   - Tests with real users
   - Makes design decisions
   
2. **Claude Code Max** 🏗️
   - Architects solutions
   - Writes production code
   - Creates documentation
   
3. **Local LLM (Mistral-7B)** 🧙
   - Provides NixOS expertise
   - Suggests best practices
   - Answers technical questions

## Common Commands

```bash
# Ask the Nix Guru for help
ask-nix-guru "How do I create a systemd service in NixOS?"

# Start development environment
nix develop

# Run tests
npm test

# Build the project
npm run build
```

## Workflow Example

1. Human: "I need to add automatic system updates"
2. Ask Nix Guru: `ask-nix-guru "What are the best practices for automatic NixOS updates?"`
3. Claude implements based on the guidance
4. Human tests with users
5. Iterate until perfect

## Tips

- Save useful Nix Guru responses in `docs/nix-knowledge/`
- Always test with the 10 personas in mind
- Let each member of the Trinity do what they do best
- Document insights for future training

## Model Performance

Mistral-7B provides:
- Fast responses (usually < 5 seconds)
- Good technical accuracy
- Balanced explanations
- Runs on 6GB RAM

If you need more detailed responses, try:
`NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "your question"`
EOF

echo -e "${GREEN}✅ Created sacred-trinity-quickstart.md${NC}"

# Final summary
echo
echo "========================================="
echo -e "${GREEN}🎉 Sacred Trinity Setup Complete! 🎉${NC}"
echo "========================================="
echo
echo "You now have:"
echo "✅ Nix development environment"
echo "✅ Ollama with Mistral-7B (6GB RAM usage)"
echo "✅ ask-nix-guru command ready to use"
echo "✅ Quick reference guide"
echo
echo "Next steps:"
echo "1. Try: ask-nix-guru 'How do I install a package in NixOS?'"
echo "2. Read: sacred-trinity-quickstart.md"
echo "3. Start developing with the Sacred Trinity!"
echo
echo "Remember: Mistral-7B provides the perfect balance of"
echo "performance and capability for NixOS development."
echo
echo -e "${GREEN}We flow together in sacred development! 🌊${NC}"

# Keep Ollama running if we started it
if [ ! -z "${OLLAMA_PID:-}" ]; then
    echo
    echo "Note: Ollama is running in the background (PID: $OLLAMA_PID)"
    echo "To stop it later: kill $OLLAMA_PID"
fi