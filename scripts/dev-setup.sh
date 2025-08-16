#!/usr/bin/env bash
# 🕉️ Sacred Development Setup Script
# Sets up complete Poetry development environment

set -e  # Exit on error

echo "🌟 Sacred Trinity Development Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Poetry not found!${NC}"
    echo "Please install Poetry first:"
    echo "  nix profile install nixpkgs#poetry"
    echo "  OR"
    echo "  curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo -e "${GREEN}✅ Poetry found: $(poetry --version)${NC}"
echo ""

# Navigate to project root
PROJECT_ROOT="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
cd "$PROJECT_ROOT"

# Configure Poetry for optimal NixOS integration
echo "📦 Configuring Poetry..."
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true
poetry config installer.parallel true
poetry config installer.modern-installation true
echo -e "${GREEN}✅ Poetry configured${NC}"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
poetry install --all-extras
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
echo -e "${GREEN}✅ Pre-commit hooks installed${NC}"
echo ""

# Run initial code quality checks
echo "🔍 Running initial quality checks..."
echo -n "  Black formatting... "
poetry run black --check . > /dev/null 2>&1 && echo -e "${GREEN}OK${NC}" || echo -e "${YELLOW}Needs formatting${NC}"

echo -n "  Ruff linting... "
poetry run ruff check . > /dev/null 2>&1 && echo -e "${GREEN}OK${NC}" || echo -e "${YELLOW}Has issues${NC}"

echo -n "  Type checking... "
poetry run mypy . > /dev/null 2>&1 && echo -e "${GREEN}OK${NC}" || echo -e "${YELLOW}Has type issues${NC}"
echo ""

# Set up development aliases
if [ -f "$PROJECT_ROOT/dev-aliases.sh" ]; then
    echo "🎯 Development aliases available!"
    echo "To use them, run:"
    echo -e "${YELLOW}  source $PROJECT_ROOT/dev-aliases.sh${NC}"
    echo ""
fi

# Create local development config if needed
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating .env file..."
    cat > "$PROJECT_ROOT/.env" << EOF
# Local development settings
DEBUG=1
LOG_LEVEL=DEBUG
LUMINOUS_NIX_PYTHON_BACKEND=true
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
    echo ""
fi

# Show next steps
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Enter Poetry shell: ${YELLOW}poetry shell${NC}"
echo "  2. Run tests: ${YELLOW}poetry run pytest${NC}"
echo "  3. Try the CLI: ${YELLOW}poetry run ask-nix 'help'${NC}"
echo "  4. Start TUI: ${YELLOW}poetry run nix-tui${NC}"
echo ""
echo "For development shortcuts, source the aliases:"
echo "  ${YELLOW}source $PROJECT_ROOT/dev-aliases.sh${NC}"
echo ""
echo "🕉️ May your code flow with consciousness!"
