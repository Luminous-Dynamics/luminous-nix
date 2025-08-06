#!/usr/bin/env bash
# Migrate to Modern Nix Commands
# Helps users transition from deprecated to modern NixOS practices

set -euo pipefail

echo "🔄 Nix Command Migration Helper"
echo "================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check current status
echo "📊 Checking your current setup..."
echo

# Check for nix-env usage
if command -v nix-env &> /dev/null; then
    echo -e "${YELLOW}⚠️  You have nix-env available (deprecated)${NC}"
    
    # Check installed packages
    if nix-env -q &> /dev/null; then
        PKGS=$(nix-env -q | wc -l)
        if [ "$PKGS" -gt 0 ]; then
            echo -e "${RED}   Found $PKGS packages installed with nix-env${NC}"
            echo "   These should be migrated to nix profile or Home Manager"
            echo
            echo "   Installed packages:"
            nix-env -q | head -10 | sed 's/^/   - /'
            if [ "$PKGS" -gt 10 ]; then
                echo "   ... and $((PKGS - 10)) more"
            fi
        fi
    fi
else
    echo -e "${GREEN}✅ nix-env not in use${NC}"
fi
echo

# Check for nix profile
if command -v nix &> /dev/null && nix profile list &> /dev/null; then
    echo -e "${GREEN}✅ Modern 'nix profile' is available${NC}"
    PROFILE_PKGS=$(nix profile list 2>/dev/null | wc -l)
    if [ "$PROFILE_PKGS" -gt 0 ]; then
        echo "   You have $PROFILE_PKGS packages in your profile"
    fi
else
    echo -e "${YELLOW}⚠️  'nix profile' not available or not set up${NC}"
fi
echo

# Check for Home Manager
if command -v home-manager &> /dev/null; then
    echo -e "${GREEN}✅ Home Manager is installed${NC}"
    echo "   This is the recommended way to manage user packages!"
else
    echo -e "${YELLOW}⚠️  Home Manager not installed${NC}"
    echo "   Home Manager allows package management without sudo"
fi
echo

# Check for flakes
if [ -f /etc/nix/nix.conf ] && grep -q "experimental-features.*flakes" /etc/nix/nix.conf; then
    echo -e "${GREEN}✅ Flakes are enabled${NC}"
else
    echo -e "${BLUE}ℹ️  Flakes are not enabled (optional but recommended)${NC}"
fi
echo

# Migration recommendations
echo "🚀 Migration Recommendations"
echo "============================"
echo

# If using nix-env
if command -v nix-env &> /dev/null && [ "$(nix-env -q 2>/dev/null | wc -l)" -gt 0 ]; then
    echo "📦 To migrate from nix-env to nix profile:"
    echo
    echo "1. List current packages:"
    echo "   ${BLUE}nix-env -q${NC}"
    echo
    echo "2. Install each with nix profile:"
    echo "   ${GREEN}nix profile install nixpkgs#package-name${NC}"
    echo
    echo "3. Remove old nix-env packages:"
    echo "   ${YELLOW}nix-env -e package-name${NC}"
    echo
    echo "Or migrate all at once (advanced):"
    echo "   ${BLUE}for pkg in \$(nix-env -q | cut -d- -f1); do${NC}"
    echo "   ${BLUE}  nix profile install nixpkgs#\$pkg${NC}"
    echo "   ${BLUE}done${NC}"
    echo
fi

# Home Manager setup
if ! command -v home-manager &> /dev/null; then
    echo "🏠 To set up Home Manager (recommended):"
    echo
    echo "1. Add the channel:"
    echo "   ${GREEN}nix-channel --add https://github.com/nix-community/home-manager/archive/master.tar.gz home-manager${NC}"
    echo "   ${GREEN}nix-channel --update${NC}"
    echo
    echo "2. Install Home Manager:"
    echo "   ${GREEN}nix-shell '<home-manager>' -A install${NC}"
    echo
    echo "3. Edit ~/.config/home-manager/home.nix to add packages"
    echo
    echo "4. Apply changes without sudo:"
    echo "   ${GREEN}home-manager switch${NC}"
    echo
fi

# Command reference
echo "📚 Modern Command Reference"
echo "=========================="
echo
echo "Old (deprecated) → New (modern):"
echo
echo "${RED}nix-env -iA nixos.firefox${NC} → ${GREEN}nix profile install nixpkgs#firefox${NC}"
echo "${RED}nix-env -e firefox${NC} → ${GREEN}nix profile remove firefox${NC}"
echo "${RED}nix-env -u${NC} → ${GREEN}nix profile upgrade${NC}"
echo "${RED}nix-env --list-generations${NC} → ${GREEN}nix profile history${NC}"
echo "${RED}nix-env --rollback${NC} → ${GREEN}nix profile rollback${NC}"
echo
echo "${RED}nix-channel --update${NC} → ${GREEN}nix flake update${NC} (with flakes)"
echo "                      → ${GREEN}home-manager switch${NC} (for user packages)"
echo
echo "${RED}sudo nixos-rebuild switch${NC} → ${GREEN}home-manager switch${NC} (for user packages only)"
echo

# Offer interactive migration
echo
read -p "Would you like help migrating a specific package? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    read -p "Enter package name: " PACKAGE
    
    echo
    echo "To install '$PACKAGE' the modern way:"
    echo
    echo "Option 1 - Quick install (no sudo):"
    echo "   ${GREEN}nix profile install nixpkgs#$PACKAGE${NC}"
    echo
    echo "Option 2 - With Home Manager (recommended):"
    echo "   Add to ~/.config/home-manager/home.nix:"
    echo "   ${BLUE}home.packages = with pkgs; [ $PACKAGE ];${NC}"
    echo "   Then run: ${GREEN}home-manager switch${NC}"
    echo
    echo "Option 3 - System-wide (requires sudo):"
    echo "   Add to /etc/nixos/configuration.nix:"
    echo "   ${BLUE}environment.systemPackages = with pkgs; [ $PACKAGE ];${NC}"
    echo "   Then run: ${GREEN}sudo nixos-rebuild switch${NC}"
fi

echo
echo "✨ Happy migrating to modern Nix!"
echo
echo "For more help, try:"
echo "   ${BLUE}ask-nix-modern 'how do I install packages'${NC}"
echo "   ${BLUE}ask-nix-modern 'setup home manager'${NC}"
echo