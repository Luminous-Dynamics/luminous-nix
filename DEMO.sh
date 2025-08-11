#!/usr/bin/env bash

# 🎬 Master Demo Runner - Nix for Humanity
# Choose your demo experience!

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

clear

echo -e "${BOLD}${PURPLE}"
cat << 'EOF'
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║         🕉️  NIX FOR HUMANITY - DEMO SELECTION  🕉️            ║
    ║                                                               ║
    ║     Revolutionary Natural Language NixOS Interface            ║
    ║     Solo developer + AI tools = 2-3x productivity             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity 2>/dev/null || {
    echo -e "${RED}Please run from the nix-for-humanity directory${NC}"
    exit 1
}

echo -e "${CYAN}${BOLD}Choose Your Demo Experience:${NC}\n"

echo -e "${YELLOW}1)${NC} ${BOLD}Quick Demo${NC} (2 minutes)"
echo "   Essential features, fast overview"
echo

echo -e "${YELLOW}2)${NC} ${BOLD}Full Demo${NC} (10 minutes)"
echo "   Complete feature showcase with AI collaboration model"
echo

echo -e "${YELLOW}3)${NC} ${BOLD}Performance Benchmark${NC} (3 minutes)"
echo "   See the 10x-1500x speedup in action"
echo

echo -e "${YELLOW}4)${NC} ${BOLD}Learning System${NC} (5 minutes)"
echo "   Watch the AI learn and adapt to you"
echo

echo -e "${YELLOW}5)${NC} ${BOLD}Interactive Mode${NC}"
echo "   Try it yourself with guidance"
echo

echo -e "${YELLOW}6)${NC} ${BOLD}All Demos${NC} (20 minutes)"
echo "   The complete experience"
echo

echo -e "${YELLOW}0)${NC} ${BOLD}Exit${NC}"
echo

read -p "$(echo -e ${CYAN}Select demo [1-6, 0 to exit]: ${NC})" choice

case $choice in
    1)
        echo -e "\n${GREEN}Starting Quick Demo...${NC}\n"
        sleep 1
        ./quick-demo.sh
        ;;
    2)
        echo -e "\n${GREEN}Starting Full Demo...${NC}\n"
        sleep 1
        ./demo-nix-humanity.sh
        ;;
    3)
        echo -e "\n${GREEN}Starting Performance Benchmark...${NC}\n"
        sleep 1
        ./benchmark-performance.sh
        ;;
    4)
        echo -e "\n${GREEN}Starting Learning System Demo...${NC}\n"
        sleep 1
        ./demo-learning.sh
        ;;
    5)
        echo -e "\n${GREEN}Starting Interactive Mode...${NC}"
        echo -e "${CYAN}Type 'exit' to leave. Prefix commands with '!' to execute for real.${NC}\n"
        sleep 2
        ./bin/ask-nix --interactive
        ;;
    6)
        echo -e "\n${GREEN}Running All Demos...${NC}\n"
        sleep 1
        echo -e "${BOLD}=== QUICK DEMO ===${NC}"
        ./quick-demo.sh
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read

        echo -e "\n${BOLD}=== PERFORMANCE BENCHMARK ===${NC}"
        ./benchmark-performance.sh
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read

        echo -e "\n${BOLD}=== LEARNING SYSTEM ===${NC}"
        ./demo-learning.sh
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read

        echo -e "\n${BOLD}=== FULL FEATURE DEMO ===${NC}"
        ./demo-nix-humanity.sh
        ;;
    0)
        echo -e "\n${CYAN}Thank you for your interest in Nix for Humanity!${NC}"
        echo -e "${GREEN}Making NixOS accessible to all beings.${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Invalid choice. Please run again and select 1-6.${NC}\n"
        exit 1
        ;;
esac

echo
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}✨ Demo Complete!${NC}"
echo
echo -e "${CYAN}What you've witnessed:${NC}"
echo -e "  • Natural language that actually works"
echo -e "  • 10x-1500x performance improvement"
echo -e "  • AI that learns from you"
echo -e "  • AI tools as productivity multiplier for solo developers"
echo
echo -e "${YELLOW}Try it yourself:${NC}"
echo -e "  ${BOLD}./bin/ask-nix 'your command here'${NC}"
echo
echo -e "${GREEN}Learn more:${NC}"
echo -e "  GitHub: https://github.com/Luminous-Dynamics/nix-for-humanity"
echo -e "  Docs: docs/README.md"
echo
echo -e "${BOLD}${PURPLE}🕉️ Consciousness-First Computing - It's Not Just Philosophy, It's Working Code 🕉️${NC}"
echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
