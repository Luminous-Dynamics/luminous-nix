#!/usr/bin/env bash
# 🌊 Sacred Development Flow Helper
# Prevents dependency issues and maintains flow state

set -e

PROJECT_DIR="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌊 Sacred Development Flow Manager${NC}"
echo "===================================="
echo ""

# Function to check if we're in nix-shell
check_nix_shell() {
    if [ -z "$IN_NIX_SHELL" ]; then
        echo -e "${YELLOW}⚠️  Not in nix-shell. Entering now...${NC}"
        exec nix-shell shell-complete.nix --run "$0 $@"
    else
        echo -e "${GREEN}✅ Nix shell active${NC}"
    fi
}

# Function to setup direnv
setup_direnv() {
    echo -e "${BLUE}Setting up direnv for automatic environment...${NC}"
    
    if ! command -v direnv &> /dev/null; then
        echo -e "${YELLOW}Installing direnv...${NC}"
        nix-env -iA nixos.direnv
    fi
    
    direnv allow .
    echo -e "${GREEN}✅ Direnv configured - environment will auto-activate!${NC}"
}

# Function to install all dependencies
install_deps() {
    echo -e "${BLUE}Installing all dependencies...${NC}"
    
    # Python dependencies via Poetry
    echo "📦 Python dependencies..."
    poetry install --all-extras
    
    # Check voice tools
    echo "🎤 Checking voice tools..."
    which whisper &>/dev/null && echo "  ✅ Whisper installed" || echo "  ⚠️  Whisper missing"
    which piper &>/dev/null && echo "  ✅ Piper installed" || echo "  ⚠️  Piper missing"
    
    echo -e "${GREEN}✅ All dependencies ready${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}Running tests...${NC}"
    poetry run pytest -v
}

# Function to format code
format_code() {
    echo -e "${BLUE}Formatting code...${NC}"
    poetry run black .
    poetry run ruff check --fix .
    echo -e "${GREEN}✅ Code formatted${NC}"
}

# Function to check code quality
check_quality() {
    echo -e "${BLUE}Checking code quality...${NC}"
    poetry run mypy .
    poetry run ruff check .
    echo -e "${GREEN}✅ Code quality check complete${NC}"
}

# Function to start development session
start_session() {
    echo -e "${BLUE}🧘 Starting sacred development session...${NC}"
    echo ""
    echo "Setting intention: Consciousness-first development"
    sleep 1
    
    check_nix_shell
    install_deps
    
    echo ""
    echo -e "${GREEN}✨ Environment ready for flow state!${NC}"
    echo ""
    echo "Available commands:"
    echo "  ./dev-flow.sh test     - Run tests"
    echo "  ./dev-flow.sh format   - Format code"
    echo "  ./dev-flow.sh check    - Check code quality"
    echo "  ./dev-flow.sh direnv   - Setup auto-activation"
    echo "  ./dev-flow.sh shell    - Enter complete nix-shell"
    echo "  ./dev-flow.sh voice    - Test voice setup"
    echo ""
}

# Function to test voice setup
test_voice() {
    echo -e "${BLUE}Testing voice setup...${NC}"
    
    echo "🎤 Whisper (Speech Recognition):"
    if which whisper &>/dev/null; then
        whisper --help | head -5
    else
        echo "  Not installed. Run: nix-env -iA nixos.openai-whisper"
    fi
    
    echo ""
    echo "🔊 Piper (Text-to-Speech):"
    if which piper &>/dev/null; then
        echo "Hello from Nix for Humanity" | piper --help | head -5
    else
        echo "  Not installed. Run: nix-env -iA nixos.piper"
    fi
    
    echo ""
    echo "🐍 Python voice packages:"
    poetry run python -c "
import pkg_resources
packages = ['openai-whisper', 'pyttsx3', 'sounddevice']
for pkg in packages:
    try:
        version = pkg_resources.get_distribution(pkg).version
        print(f'  ✅ {pkg} v{version}')
    except:
        print(f'  ❌ {pkg} not installed')
"
}

# Main command dispatcher
case "${1:-start}" in
    test)
        check_nix_shell
        run_tests
        ;;
    format)
        check_nix_shell
        format_code
        ;;
    check)
        check_nix_shell
        check_quality
        ;;
    direnv)
        setup_direnv
        ;;
    shell)
        echo "Entering complete nix-shell..."
        exec nix-shell shell-complete.nix
        ;;
    voice)
        check_nix_shell
        test_voice
        ;;
    start|*)
        start_session
        ;;
esac

echo ""
echo -e "${BLUE}🌊 Flow preserved${NC}"