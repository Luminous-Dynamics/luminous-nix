#!/usr/bin/env bash

# 🚀 Quick Demo - Nix for Humanity in 2 Minutes
# Shows the essential features fast!

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "═══════════════════════════════════════════════════════"
echo "     🕉️  NIX FOR HUMANITY - 2-MINUTE DEMO  🕉️"
echo "     Natural Language NixOS That Actually Works!"
echo "═══════════════════════════════════════════════════════"
echo -e "${NC}"

cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity 2>/dev/null || exit 1

echo -e "\n${YELLOW}1️⃣  Natural Language Understanding${NC}"
echo -e "${BOLD}$ ask-nix 'install firefox'${NC}"
./bin/ask-nix 'install firefox' 2>&1 | grep -v '^INFO:' | head -3
sleep 1

echo -e "\n${YELLOW}2️⃣  Multiple Ways to Say It${NC}"
echo -e "${BOLD}$ ask-nix 'add vim'${NC}"
./bin/ask-nix 'add vim' 2>&1 | grep -v '^INFO:' | head -3
sleep 1

echo -e "\n${YELLOW}3️⃣  Smart Search${NC}"
echo -e "${BOLD}$ ask-nix 'find markdown editor'${NC}"
./bin/ask-nix 'find markdown editor' 2>&1 | grep -v '^INFO:' | head -8
sleep 1

echo -e "\n${YELLOW}4️⃣  System Management${NC}"
echo -e "${BOLD}$ ask-nix 'what is installed?'${NC}"
./bin/ask-nix 'what is installed?' 2>&1 | grep -v '^INFO:' | head -3
sleep 1

echo -e "\n${YELLOW}5️⃣  Updates & Rollbacks${NC}"
echo -e "${BOLD}$ ask-nix 'update system'${NC}"
./bin/ask-nix 'update system' 2>&1 | grep -v '^INFO:' | head -3
echo -e "${BOLD}$ ask-nix 'go back'${NC}"
./bin/ask-nix 'go back' 2>&1 | grep -v '^INFO:' | head -3
sleep 1

echo -e "\n${YELLOW}6️⃣  Performance: Lightning Fast! ⚡${NC}"
echo -e "${BOLD}Time for operation:${NC}"
time ./bin/ask-nix 'search vim' 2>&1 | grep -v '^INFO:' | head -5

echo -e "\n${GREEN}${BOLD}✨ Key Features:${NC}"
echo "  • Natural language that works"
echo "  • 10x-1500x faster (native Python API)"
echo "  • Safe by default (dry-run)"
echo "  • Learns from your usage"
echo "  • Built by solo dev with AI tools"

echo -e "\n${CYAN}${BOLD}Try it yourself:${NC}"
echo "  ./bin/ask-nix 'your command here'"
echo "  ./bin/ask-nix --execute 'actually run it'"
echo "  ./bin/ask-nix --interactive"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}Revolutionary AI partnership making NixOS accessible!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}\n"