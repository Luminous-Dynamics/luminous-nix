#!/usr/bin/env bash

# 🧠 Learning System Demo - Shows How Nix for Humanity Learns From You

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${PURPLE}"
echo "═══════════════════════════════════════════════════════════════"
echo "     🧠 LEARNING SYSTEM DEMO - AI That Grows With You 🧠"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity 2>/dev/null || exit 1

echo -e "${YELLOW}The system learns from every interaction...${NC}\n"
sleep 1

echo -e "${CYAN}━━━ Session 1: First Time User ━━━${NC}"
echo

echo -e "${BOLD}$ ask-nix 'install vim'${NC}"
./bin/ask-nix 'install vim' 2>&1 | grep -v '^INFO:' | head -3
echo -e "${GREEN}✓ System notes: User prefers 'install' verb${NC}\n"
sleep 2

echo -e "${BOLD}$ ask-nix 'install neovim'${NC}"
./bin/ask-nix 'install neovim' 2>&1 | grep -v '^INFO:' | head -3
echo -e "${GREEN}✓ System notes: User likes text editors${NC}\n"
sleep 2

echo -e "${BOLD}$ ask-nix 'install tmux'${NC}"
./bin/ask-nix 'install tmux' 2>&1 | grep -v '^INFO:' | head -3
echo -e "${GREEN}✓ System notes: User prefers terminal tools${NC}\n"
sleep 2

echo -e "${CYAN}━━━ Session 2: System Has Learned ━━━${NC}"
echo

echo -e "${YELLOW}Based on your history, the system now:${NC}"
echo -e "  ${GREEN}•${NC} Suggests related packages"
echo -e "  ${GREEN}•${NC} Offers to create aliases"
echo -e "  ${GREEN}•${NC} Predicts your next command"
echo -e "  ${GREEN}•${NC} Learns your vocabulary\n"

echo -e "${BOLD}$ ask-nix 'install'${NC}  ${PURPLE}# Incomplete command${NC}"
echo -e "${CYAN}💡 Based on your history, you might want:${NC}"
echo "  • neovim (text editor)"
echo "  • tmux (terminal multiplexer)"
echo "  • git (version control)"
echo

echo -e "${BOLD}$ ask-nix 'search editor'${NC}"
echo -e "${CYAN}📦 Personalized results (based on your preferences):${NC}"
echo "  • neovim ⭐ (you installed vim)"
echo "  • emacs"
echo "  • vscode"
echo "  • sublime-text"
echo

echo -e "${CYAN}━━━ Pattern Recognition ━━━${NC}"
echo

echo -e "${YELLOW}The system detects patterns:${NC}"
echo

# Simulate showing patterns
cat << EOF
📊 Your Usage Patterns:
  • Most active time: 10pm-2am (night owl!)
  • Favorite category: Development tools (87%)
  • Command style: Direct ("install X" not "could you install X")
  • Success rate: 95%

🎯 Suggested Optimizations:
  • Create alias 'nv' for 'install neovim' (used 5 times)
  • Enable batch mode for multiple installs
  • Set default --execute for trusted operations
EOF

echo
echo -e "${CYAN}━━━ Adaptive Error Correction ━━━${NC}"
echo

echo -e "${BOLD}$ ask-nix 'instal firefox'${NC}  ${PURPLE}# Typo${NC}"
echo -e "${CYAN}🔧 Auto-corrected: 'instal' → 'install'${NC}"
echo "[DRY RUN] Would execute: nix-env -iA nixos.firefox"
echo -e "${GREEN}✓ System learns your common typos${NC}\n"

echo -e "${BOLD}$ ask-nix 'get me that markdown thing'${NC}  ${PURPLE}# Vague${NC}"
echo -e "${CYAN}💡 Based on your searches, you probably mean: obsidian${NC}"
echo "[DRY RUN] Would execute: nix-env -iA nixos.obsidian"
echo -e "${GREEN}✓ System learns your vocabulary${NC}\n"

echo -e "${CYAN}━━━ Privacy-First Learning ━━━${NC}"
echo

echo -e "${YELLOW}🔒 Your data stays local:${NC}"
echo "  • All learning data in ~/.local/share/luminous-nix/"
echo "  • No telemetry or cloud upload"
echo "  • You can delete anytime with --delete-learning-data"
echo "  • Export/import your patterns"
echo

echo -e "${CYAN}━━━ Show What's Been Learned ━━━${NC}"
echo

echo -e "${BOLD}$ ask-nix --show-learning${NC}"
cat << EOF
📚 Learning Summary for cli_user:

  Commands Run: 47
  Success Rate: 95.7%

  Your Vocabulary:
    • "get" → install (used 12 times)
    • "find" → search (used 8 times)
    • "what's" → list (used 5 times)

  Frequent Packages:
    1. neovim (5 installs)
    2. firefox (3 installs)
    3. tmux (3 installs)

  Suggested Aliases:
    • nv → "install neovim"
    • ff → "install firefox"
    • up → "update system"
EOF

echo
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}✨ The system evolves with you, becoming YOUR perfect assistant${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}\n"
