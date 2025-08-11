#!/usr/bin/env bash

# Test script to document which commands work with --execute
# Tests in dry-run mode first to be safe

echo "🧪 Testing ask-nix --execute Command Support"
echo "==========================================="
echo "Testing in DRY-RUN mode for safety"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Change to project directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Function to test a command
test_command() {
    local test_name="$1"
    local query="$2"
    local expected_pattern="$3"
    local needs_sudo="$4"

    echo -e "\n📋 Testing: $test_name"
    echo "Query: $query"
    if [ "$needs_sudo" = "yes" ]; then
        echo -e "${YELLOW}⚠️  Requires sudo${NC}"
    fi

    # Run with --execute in dry-run mode (default)
    output=$(bin/ask-nix --execute "$query" 2>&1)
    exit_code=$?

    # Check if output indicates it would execute
    if [[ "$output" =~ "DRY RUN" ]] || [[ "$output" =~ "Would execute" ]] || [[ "$output" =~ "dry-run mode" ]]; then
        echo -e "${GREEN}✅ SUPPORTED${NC} - Command recognized and would execute"
        echo "Pattern found: Dry run mode active"
        ((TESTS_PASSED++))

        # Extract the actual command that would run
        if [[ "$output" =~ "Would execute: "(.*) ]] || [[ "$output" =~ "DRY RUN - Would execute: "(.*) ]]; then
            echo "Command: ${BASH_REMATCH[1]}"
        fi
    elif [[ "$output" =~ $expected_pattern ]]; then
        echo -e "${GREEN}✅ SUPPORTED${NC} - Command recognized"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ NOT SUPPORTED${NC} - Command not recognized for execution"
        echo "Output: $output" | head -5
        ((TESTS_FAILED++))
    fi
}

echo -e "${YELLOW}=== Package Installation Commands ===${NC}"
test_command "Install Firefox" "install firefox" "firefox|install" "no"
test_command "Install VS Code" "install vscode" "vscode|install" "no"
test_command "Install Python" "I need python" "python|install" "no"
test_command "Install Git" "set up git" "git|install" "no"
test_command "Install Docker" "install docker" "docker|install" "no"

echo -e "\n${YELLOW}=== Package Search Commands ===${NC}"
test_command "Search Python" "search for python packages" "search|python" "no"
test_command "Find Editors" "find text editors" "search|editor" "no"
test_command "Look for Games" "look for games" "search|game" "no"

echo -e "\n${YELLOW}=== Package Removal Commands ===${NC}"
test_command "Remove Package" "remove firefox" "remove|uninstall" "no"
test_command "Uninstall Package" "uninstall vscode" "remove|uninstall" "no"

echo -e "\n${YELLOW}=== System Update Commands ===${NC}"
test_command "Update System" "update my system" "update|upgrade" "yes"
test_command "Upgrade System" "upgrade nixos" "update|upgrade" "yes"
test_command "Update Channels" "update channels" "channel.*update" "yes"

echo -e "\n${YELLOW}=== System Management Commands ===${NC}"
test_command "List Generations" "list generations" "generation|list" "yes"
test_command "Rollback System" "rollback to previous" "rollback" "yes"
test_command "Switch Generation" "switch to generation 5" "switch|generation" "yes"

echo -e "\n${YELLOW}=== Package Listing Commands ===${NC}"
test_command "List Installed" "list installed packages" "list|installed" "no"
test_command "Show Packages" "show my packages" "list|show" "no"
test_command "What's Installed" "what packages do I have" "list|installed" "no"

echo -e "\n${YELLOW}=== Configuration Commands ===${NC}"
test_command "Edit Config" "edit configuration" "edit|configuration" "yes"
test_command "Rebuild Config" "rebuild configuration" "rebuild|switch" "yes"

echo -e "\n${YELLOW}=== Network Commands ===${NC}"
test_command "Fix WiFi" "my wifi isn't working" "wifi|network" "yes"
test_command "Enable Network" "enable networking" "network|enable" "yes"

echo -e "\n${YELLOW}Test Summary${NC}"
echo "============"
echo -e "Commands Supported: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Commands Not Supported: ${RED}$TESTS_FAILED${NC}"

echo -e "\n${YELLOW}Safety Analysis${NC}"
echo "==============="
echo "Commands that DON'T need sudo (safe by default):"
echo "- Package installation (nix profile install)"
echo "- Package search (nix search)"
echo "- Package removal (nix profile remove)"
echo "- Listing packages (nix profile list)"
echo
echo "Commands that NEED sudo (require admin privileges):"
echo "- System updates (nixos-rebuild switch)"
echo "- Channel updates (nix-channel --update)"
echo "- Generation management (nixos-rebuild switch --rollback)"
echo "- Configuration changes (editing /etc/nixos/)"
echo "- Network configuration changes"
echo
echo "⚠️  Note: This test used dry-run mode. Actual execution would require:"
echo "   - No --dry-run flag for the commands to actually run"
echo "   - Proper sudo setup for system-level commands"
echo "   - User confirmation for destructive operations"
