#!/bin/bash
# 🎬 Luminous Nix Self-Healing Demo Launcher

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🎬 Luminous Nix Self-Healing System Demo${NC}"
echo "=========================================="
echo

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/pyproject.toml" ]; then
    echo -e "${RED}❌ Error: Not in Luminous Nix project directory${NC}"
    exit 1
fi

cd "$PROJECT_ROOT"

# Check Poetry installation
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}❌ Error: Poetry not installed${NC}"
    echo "Please install Poetry first: https://python-poetry.org/docs/"
    exit 1
fi

# Install dependencies if needed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"
poetry install --quiet 2>/dev/null || poetry install

echo

# Show options
echo "Demo Options:"
echo "============="
echo "1. Interactive Demo (manual advance)"
echo "2. Auto-Play Demo (automatic advance)"
echo "3. Quick Test (specific scene)"
echo "4. Recording Mode (optimized for video)"
echo

read -p "Select option (1-4): " option

case $option in
    1)
        echo -e "\n${GREEN}▶️  Starting Interactive Demo...${NC}"
        echo "Press Enter to advance through scenes"
        echo
        sleep 2
        poetry run python demo/run_demo.py
        ;;
    2)
        read -p "Auto-advance delay in seconds (default 3): " delay
        delay=${delay:-3}
        echo -e "\n${GREEN}▶️  Starting Auto-Play Demo (${delay}s delay)...${NC}"
        echo
        sleep 2
        poetry run python demo/run_demo.py --auto --delay "$delay"
        ;;
    3)
        echo
        echo "Available Scenes:"
        echo "1. Introduction"
        echo "2. Create Problems"
        echo "3. Detection"
        echo "4. Healing"
        echo "5. Verification"
        echo "6. Performance"
        echo "7. Predictive"
        echo "8. Simplicity"
        echo "9. Conclusion"
        echo
        read -p "Select scene (1-9): " scene
        echo -e "\n${GREEN}▶️  Running Scene $scene...${NC}"
        echo
        sleep 1
        poetry run python demo/run_demo.py --scene "$scene"
        ;;
    4)
        echo -e "\n${GREEN}🎥 Recording Mode${NC}"
        echo "Optimized for screen recording:"
        echo "- Auto-advance with 5s delays"
        echo "- Clear screen between scenes"
        echo "- High contrast output"
        echo
        read -p "Press Enter to start recording mode..."
        poetry run python demo/run_demo.py --auto --delay 5
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}✅ Demo Complete!${NC}"
echo
echo "Learn more:"
echo "- Documentation: docs/SELF_HEALING_SYSTEM_DOCUMENTATION.md"
echo "- Benchmarks: benchmarks/test_healing_performance.py"
echo "- GitHub: https://github.com/Luminous-Dynamics/luminous-nix"