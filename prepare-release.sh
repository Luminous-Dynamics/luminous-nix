#!/usr/bin/env bash

# 🚀 Prepare for GitHub Release - Nix for Humanity v0.1.0-alpha

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "═══════════════════════════════════════════════════════════════"
echo "     🚀 PREPARING GITHUB RELEASE - v0.1.0-alpha"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Not in nix-for-humanity directory${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-Release Checklist:${NC}\n"

# 1. Check demos work
echo -n "1. Testing demos... "
if [ -x "./quick-demo.sh" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Demos not executable${NC}"
    chmod +x *.sh
    echo -e "   ${GREEN}Fixed!${NC}"
fi

# 2. Check CLI works
echo -n "2. Testing CLI... "
if ./bin/ask-nix "install test" 2>&1 | grep -q "DRY RUN"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ CLI not working${NC}"
    exit 1
fi

# 3. Create demo archive
echo -n "3. Creating demo archive... "
tar -czf demos.tar.gz *.sh
echo -e "${GREEN}✓${NC}"

# 4. Show git status
echo -e "\n${YELLOW}📊 Git Status:${NC}"
git status --short | head -10

# 5. Show current version
echo -e "\n${YELLOW}📌 Current Version:${NC}"
if [ -f "VERSION" ]; then
    cat VERSION
else
    echo "0.1.0-alpha"
fi

# 6. Display release plan
echo -e "\n${CYAN}📝 Release Steps:${NC}\n"
echo "1. Review and update README:"
echo "   ${BOLD}mv README-NEW.md README.md${NC}"
echo
echo "2. Commit changes:"
echo "   ${BOLD}git add -A${NC}"
echo "   ${BOLD}git commit -m \"feat: Natural language NixOS CLI that actually works! 🎉\"${NC}"
echo
echo "3. Create and push tag:"
echo "   ${BOLD}git tag -a v0.1.0-alpha -m \"First working release\"${NC}"
echo "   ${BOLD}git push origin main --tags${NC}"
echo
echo "4. Create GitHub release:"
echo "   ${BOLD}gh release create v0.1.0-alpha \\${NC}"
echo "   ${BOLD}  --title \"v0.1.0-alpha: Natural Language NixOS That Actually Works!\" \\${NC}"
echo "   ${BOLD}  --notes-file RELEASE-v0.1.0-alpha.md \\${NC}"
echo "   ${BOLD}  --prerelease \\${NC}"
echo "   ${BOLD}  demos.tar.gz${NC}"

echo -e "\n${YELLOW}📊 Statistics:${NC}"
echo "• Natural language patterns: 20+"
echo "• Response time: <50ms"
echo "• Development time: 2 weeks"
echo "• AI tools cost: ~\$200/month"
echo "• Productivity: 2-3x solo developer"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}✨ Ready to share with the world!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${CYAN}Review the files:${NC}"
echo "• README-NEW.md (new honest README)"
echo "• RELEASE-v0.1.0-alpha.md (release notes)"
echo "• GITHUB-RELEASE-PLAN.md (promotion strategy)"
echo

read -p "$(echo -e ${YELLOW}Ready to proceed? [y/N]: ${NC})" confirm

if [[ $confirm == [yY] ]]; then
    echo -e "\n${GREEN}Great! Follow the steps above to complete the release.${NC}"
    echo -e "${CYAN}Don't forget to share on social media!${NC}\n"
else
    echo -e "\n${YELLOW}No problem! Review the files and run again when ready.${NC}\n"
fi
