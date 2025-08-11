#!/usr/bin/env bash
# Test script for Nix for Humanity - Exercise all commands
# Run with: bash test-all-commands.sh

set -e  # Exit on error

echo "🧪 Nix for Humanity - Comprehensive Test Suite"
echo "============================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local description="$1"
    local command="$2"
    local expected_behavior="$3"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -e "${YELLOW}Test $TESTS_RUN:${NC} $description"
    echo "Command: $command"
    echo "Expected: $expected_behavior"
    echo

    # Run the command
    if eval "$command"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo
    echo "---"
    echo
}

# 1. Test Search Commands
echo "📦 Testing Search Functionality"
echo "==============================="

run_test "Search with natural language" \
    "./bin/ask-nix-modern --bridge 'search for firefox'" \
    "Should find Firefox browser packages"

run_test "Search with direct term" \
    "./bin/ask-nix-modern --bridge 'search htop'" \
    "Should find htop system monitor"

# 2. Test Install Commands (Dry Run)
echo "📥 Testing Install Commands (Dry Run Mode)"
echo "========================================="

run_test "Install with natural language" \
    "./bin/ask-nix-modern --dry-run 'install firefox'" \
    "Should show what would be installed"

run_test "Install common package" \
    "./bin/ask-nix-modern --dry-run 'i want to install htop'" \
    "Should recognize install intent and show dry run"

run_test "Install with typo" \
    "./bin/ask-nix-modern --dry-run 'install firefx'" \
    "Should show educational error about package not found"

# 3. Test List Commands
echo "📋 Testing List Commands"
echo "========================"

run_test "List installed packages" \
    "./bin/ask-nix-modern 'list my packages'" \
    "Should show currently installed packages"

run_test "Show installed software" \
    "./bin/ask-nix-modern 'what do I have installed?'" \
    "Should recognize list intent"

# 4. Test Update Commands (Dry Run)
echo "🔄 Testing Update Commands (Dry Run)"
echo "===================================="

run_test "Update packages" \
    "./bin/ask-nix-modern --dry-run --bridge 'update my packages'" \
    "Should show package update process"

run_test "Update system" \
    "./bin/ask-nix-modern --dry-run --bridge 'update my system'" \
    "Should show system update process (with sudo)"

# 5. Test Error Handling
echo "❌ Testing Error Handling"
echo "========================="

run_test "Install non-existent package" \
    "./bin/ask-nix-modern --bridge --dry-run 'install totallyfakepackage123'" \
    "Should show educational error message"

run_test "Search with empty term" \
    "./bin/ask-nix-modern --bridge 'search'" \
    "Should handle missing search term gracefully"

# 6. Test Different Personalities
echo "🎭 Testing Personality Modes"
echo "============================"

run_test "Minimal personality" \
    "./bin/ask-nix-modern --minimal 'how to install git'" \
    "Should give brief, factual response"

run_test "Encouraging personality" \
    "./bin/ask-nix-modern --encouraging 'install vim'" \
    "Should be supportive and encouraging"

run_test "Technical personality" \
    "./bin/ask-nix-modern --technical 'install docker'" \
    "Should include technical details"

# 7. Test Execution Bridge
echo "🌉 Testing Execution Bridge"
echo "==========================="

run_test "Direct bridge call - install" \
    "echo '{\"action\": \"install_package\", \"package\": \"tree\"}' | node ./bin/execution-bridge.js /dev/stdin" \
    "Should execute via bridge successfully"

run_test "Direct bridge call - search" \
    "echo '{\"action\": \"search_package\", \"package\": \"python\"}' | node ./bin/execution-bridge.js /dev/stdin" \
    "Should search and format results"

# 8. Test Intent Recognition
echo "🎯 Testing Intent Recognition"
echo "============================="

run_test "Ambiguous intent" \
    "./bin/ask-nix-modern 'firefox'" \
    "Should ask for clarification or suggest actions"

run_test "Complex query" \
    "./bin/ask-nix-modern 'I need a text editor like vscode'" \
    "Should understand and suggest VS Code"

# Summary
echo
echo "📊 Test Summary"
echo "==============="
echo "Total tests run: $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi
