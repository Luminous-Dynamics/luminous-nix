#!/usr/bin/env bash
# Migrate from requirements.txt to pyproject.toml

set -e

echo "🔄 Migrating to pyproject.toml..."
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Are you in the project root?${NC}"
    exit 1
fi

# Archive old requirements files
echo -e "${YELLOW}📦 Archiving old requirements files...${NC}"
mkdir -p archive/old-requirements

# Move requirements files if they exist
for file in requirements*.txt scripts/requirements.txt; do
    if [ -f "$file" ]; then
        echo "  Moving $file to archive/"
        mv "$file" archive/old-requirements/ 2>/dev/null || true
    fi
done

# Check for existing virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}🗑️  Removing old virtual environment...${NC}"
    rm -rf venv
fi

# Create new virtual environment
echo -e "${GREEN}🐍 Creating fresh virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${GREEN}✨ Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${GREEN}📦 Upgrading pip...${NC}"
pip install --upgrade pip

# Install with all features for development
echo -e "${GREEN}📥 Installing nix-for-humanity with all features...${NC}"
pip install -e ".[all]"

echo
echo -e "${GREEN}✅ Migration complete!${NC}"
echo
echo "Next steps:"
echo "1. Test the installation:"
echo "   ask-nix --version"
echo "   nix-tui  # if you installed with [tui]"
echo
echo "2. Run tests:"
echo "   pytest"
echo
echo "3. Check code quality:"
echo "   black src tests"
echo "   ruff src tests"
echo "   mypy src"
echo
echo "4. Old requirements files have been moved to archive/old-requirements/"
echo
echo -e "${YELLOW}📝 Note: Remember to activate the virtual environment in new terminals:${NC}"
echo "   source venv/bin/activate"
