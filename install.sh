#!/usr/bin/env bash
# 🚀 Luminous Nix Installer
#
# One-command installation for Luminous Nix - Natural Language for NixOS
# 
# Usage:
#   curl -sSL https://luminous-nix.dev/install.sh | bash
#   # or
#   ./install.sh [options]
#
# Options:
#   --dev         Install development dependencies
#   --voice       Install voice interface support
#   --no-color    Disable colored output
#   --prefix DIR  Install to custom directory (default: ~/.local)
#   --help        Show this help message

set -euo pipefail

# Default configuration
INSTALL_PREFIX="${HOME}/.local"
INSTALL_DEV=false
INSTALL_VOICE=false
USE_COLOR=true
REPO_URL="https://github.com/Luminous-Dynamics/luminous-nix.git"
BRANCH="main"

# Colors
if [ -t 1 ] && [ "${USE_COLOR}" = true ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    MAGENTA='\033[0;35m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    MAGENTA=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Logging functions
log() {
    echo -e "${1}"
}

info() {
    log "${BLUE}ℹ${NC}  ${1}"
}

success() {
    log "${GREEN}✅${NC} ${1}"
}

warning() {
    log "${YELLOW}⚠️${NC}  ${1}"
}

error() {
    log "${RED}❌${NC} ${1}" >&2
}

header() {
    echo
    log "${MAGENTA}${BOLD}$1${NC}"
    log "${MAGENTA}$(echo "$1" | sed 's/./=/g')${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        --voice)
            INSTALL_VOICE=true
            shift
            ;;
        --no-color)
            USE_COLOR=false
            shift
            ;;
        --prefix)
            INSTALL_PREFIX="$2"
            shift 2
            ;;
        --help)
            echo "Luminous Nix Installer"
            echo
            echo "Usage: $0 [options]"
            echo
            echo "Options:"
            echo "  --dev         Install development dependencies"
            echo "  --voice       Install voice interface support"
            echo "  --no-color    Disable colored output"
            echo "  --prefix DIR  Install to custom directory (default: ~/.local)"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Banner
clear
cat << "EOF"

    🌟 Luminous Nix Installer 🌟
    ═══════════════════════════════
    Natural Language for NixOS
    Making NixOS accessible to all!

EOF

# Check system requirements
header "System Requirements Check"

check_command() {
    local cmd=$1
    local required=${2:-true}
    
    if command -v "$cmd" &> /dev/null; then
        success "$cmd found: $(command -v "$cmd")"
        return 0
    else
        if [ "$required" = true ]; then
            error "$cmd not found (required)"
            return 1
        else
            warning "$cmd not found (optional)"
            return 0
        fi
    fi
}

REQUIREMENTS_MET=true

# Required commands
check_command python3 || REQUIREMENTS_MET=false
check_command git || REQUIREMENTS_MET=false
check_command curl || REQUIREMENTS_MET=false

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [ "$(echo "$PYTHON_VERSION >= 3.9" | bc)" -eq 1 ]; then
        success "Python $PYTHON_VERSION (>= 3.9 required)"
    else
        error "Python $PYTHON_VERSION found (>= 3.9 required)"
        REQUIREMENTS_MET=false
    fi
fi

# Optional but recommended
check_command nix false
check_command poetry false

# Voice dependencies (if requested)
if [ "$INSTALL_VOICE" = true ]; then
    info "Checking voice dependencies..."
    check_command espeak false
    check_command ffmpeg false
fi

if [ "$REQUIREMENTS_MET" = false ]; then
    echo
    error "System requirements not met. Please install missing dependencies."
    exit 1
fi

# Create installation directory
header "Installation Setup"

INSTALL_DIR="${INSTALL_PREFIX}/share/luminous-nix"
BIN_DIR="${INSTALL_PREFIX}/bin"

info "Installation directory: ${INSTALL_DIR}"
info "Binary directory: ${BIN_DIR}"

mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"

# Clone or update repository
header "Downloading Luminous Nix"

if [ -d "${INSTALL_DIR}/.git" ]; then
    info "Updating existing installation..."
    cd "${INSTALL_DIR}"
    git fetch origin
    git checkout "${BRANCH}"
    git pull origin "${BRANCH}"
    success "Updated to latest version"
else
    info "Cloning repository..."
    git clone --depth 1 --branch "${BRANCH}" "${REPO_URL}" "${INSTALL_DIR}"
    success "Downloaded Luminous Nix"
fi

cd "${INSTALL_DIR}"

# Install Python dependencies
header "Installing Dependencies"

# Check if we have Poetry
if command -v poetry &> /dev/null; then
    info "Installing with Poetry (recommended)..."
    poetry install --no-dev
    
    if [ "$INSTALL_DEV" = true ]; then
        info "Installing development dependencies..."
        poetry install
    fi
    
    if [ "$INSTALL_VOICE" = true ]; then
        info "Installing voice dependencies..."
        poetry install --extras voice
    fi
    
    PYTHON_CMD="poetry run python"
    success "Dependencies installed with Poetry"
else
    info "Installing with pip..."
    
    # Create virtual environment
    python3 -m venv "${INSTALL_DIR}/venv"
    source "${INSTALL_DIR}/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    if [ "$INSTALL_VOICE" = true ]; then
        pip install -r requirements-voice.txt 2>/dev/null || warning "Voice requirements not found"
    fi
    
    PYTHON_CMD="${INSTALL_DIR}/venv/bin/python"
    success "Dependencies installed with pip"
fi

# Create executable wrapper
header "Creating Command Line Interface"

cat > "${BIN_DIR}/ask-nix" << EOF
#!/usr/bin/env bash
# Luminous Nix CLI wrapper
# Auto-generated by installer

export LUMINOUS_NIX_HOME="${INSTALL_DIR}"

if [ -f "${INSTALL_DIR}/venv/bin/python" ]; then
    # pip installation
    exec "${INSTALL_DIR}/venv/bin/python" "${INSTALL_DIR}/bin/ask-nix" "\$@"
elif command -v poetry &> /dev/null; then
    # Poetry installation
    cd "${INSTALL_DIR}"
    exec poetry run python bin/ask-nix "\$@"
else
    # Direct Python
    exec python3 "${INSTALL_DIR}/bin/ask-nix" "\$@"
fi
EOF

chmod +x "${BIN_DIR}/ask-nix"
success "Created ask-nix command"

# Create additional commands
for cmd in nix-tui nix-voice; do
    if [ -f "${INSTALL_DIR}/bin/${cmd}" ]; then
        ln -sf "${BIN_DIR}/ask-nix" "${BIN_DIR}/${cmd}"
        success "Created ${cmd} command"
    fi
done

# Setup configuration
header "Configuration"

CONFIG_DIR="${HOME}/.config/luminous-nix"
mkdir -p "${CONFIG_DIR}"

if [ ! -f "${CONFIG_DIR}/config.yaml" ]; then
    info "Creating default configuration..."
    cat > "${CONFIG_DIR}/config.yaml" << EOF
# Luminous Nix Configuration
# Generated by installer

# Default settings
defaults:
  dry_run: true  # Safe by default
  verbose: false
  interface: cli

# Cache settings
cache:
  enabled: true
  ttl: 3600  # 1 hour
  max_size: 1000

# Voice settings (if installed)
voice:
  enabled: ${INSTALL_VOICE}
  language: en-US
  
# Personas (adaptive user profiles)
personas:
  enabled: true
  default: developer
EOF
    success "Created configuration file"
else
    info "Configuration already exists"
fi

# Test installation
header "Testing Installation"

if "${BIN_DIR}/ask-nix" --version &> /dev/null; then
    success "Installation test passed"
    VERSION=$("${BIN_DIR}/ask-nix" --version 2>/dev/null || echo "unknown")
    info "Version: ${VERSION}"
else
    warning "Could not verify installation"
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    header "PATH Configuration"
    
    info "Adding ${BIN_DIR} to PATH..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case "$SHELL_NAME" in
        bash)
            RC_FILE="${HOME}/.bashrc"
            ;;
        zsh)
            RC_FILE="${HOME}/.zshrc"
            ;;
        fish)
            RC_FILE="${HOME}/.config/fish/config.fish"
            ;;
        *)
            RC_FILE="${HOME}/.profile"
            ;;
    esac
    
    if [ -f "$RC_FILE" ]; then
        echo "" >> "$RC_FILE"
        echo "# Luminous Nix" >> "$RC_FILE"
        echo "export PATH=\"${BIN_DIR}:\$PATH\"" >> "$RC_FILE"
        success "Added to ${RC_FILE}"
        info "Run: source ${RC_FILE}"
    else
        warning "Could not update PATH automatically"
        info "Add this to your shell configuration:"
        echo "  export PATH=\"${BIN_DIR}:\$PATH\""
    fi
fi

# Show next steps
header "Installation Complete! 🎉"

echo
log "${GREEN}Luminous Nix has been successfully installed!${NC}"
echo
log "📍 Installation location: ${CYAN}${INSTALL_DIR}${NC}"
log "🔧 Configuration: ${CYAN}${CONFIG_DIR}/config.yaml${NC}"
log "📚 Documentation: ${CYAN}${INSTALL_DIR}/docs/${NC}"
echo

header "Quick Start"

echo "1. Reload your shell configuration:"
log "   ${CYAN}source ~/.bashrc${NC}  # or ~/.zshrc"
echo
echo "2. Test the installation:"
log "   ${CYAN}ask-nix --help${NC}"
echo
echo "3. Try natural language commands:"
log "   ${CYAN}ask-nix \"search for text editors\"${NC}"
log "   ${CYAN}ask-nix \"install firefox\"${NC}"
log "   ${CYAN}ask-nix \"update system\"${NC}"
echo

if [ "$INSTALL_VOICE" = true ]; then
    echo "4. Try voice interface:"
    log "   ${CYAN}nix-voice${NC}"
    echo
fi

echo "5. Launch the TUI:"
log "   ${CYAN}nix-tui${NC}"
echo

header "Resources"

log "📖 Documentation: ${CYAN}https://luminous-nix.dev/docs${NC}"
log "🐛 Report issues: ${CYAN}https://github.com/Luminous-Dynamics/luminous-nix/issues${NC}"
log "💬 Community: ${CYAN}https://discord.gg/luminous-nix${NC}"
echo

log "${MAGENTA}${BOLD}Thank you for installing Luminous Nix!${NC}"
log "${MAGENTA}Making NixOS accessible through natural language 🌟${NC}"
echo

# Optional: Run first-time setup
if [ -t 0 ]; then  # Check if interactive
    echo
    read -p "Would you like to run the interactive setup wizard? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        "${BIN_DIR}/ask-nix" --setup
    fi
fi

exit 0