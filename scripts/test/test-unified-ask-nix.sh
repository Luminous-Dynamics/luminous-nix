#!/usr/bin/env bash

# Test script for unified ask-nix command
# Tests all major functionality to ensure consolidation worked correctly

echo "🧪 Testing Unified ask-nix Command"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_pattern="$3"
    
    echo -e "\n📋 Testing: $test_name"
    echo "Command: $command"
    
    # Run the command and capture output
    output=$(eval "$command" 2>&1)
    exit_code=$?
    
    # Check if output contains expected pattern
    if [[ "$output" =~ $expected_pattern ]] || [[ $exit_code -eq 0 && -z "$expected_pattern" ]]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Got output: $output"
        ((TESTS_FAILED++))
    fi
}

# Navigate to the project directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

echo -e "\n${YELLOW}1. Basic Functionality Tests${NC}"
echo "=============================="

# Test help/usage
run_test "Help display" \
    "bin/ask-nix --help" \
    "Nix for Humanity"

# Test intent detection
run_test "Intent detection display" \
    "bin/ask-nix --show-intent 'install firefox'" \
    "Intent detected: install_package"

# Test dry-run mode
run_test "Dry-run mode" \
    "bin/ask-nix --dry-run 'install tree'" \
    "Running in dry-run mode"

echo -e "\n${YELLOW}2. Personality System Tests${NC}"
echo "============================="

# Test personality styles
run_test "Minimal personality" \
    "bin/ask-nix --minimal 'how to install vim?'" \
    "install"

run_test "Friendly personality" \
    "bin/ask-nix --friendly 'how to install vim?'" \
    "Hi there!"

run_test "Encouraging personality" \
    "bin/ask-nix --encouraging 'how to install vim?'" \
    "Great question!"

run_test "Technical personality" \
    "bin/ask-nix --technical 'how to install vim?'" \
    "declarative configuration paradigm"

echo -e "\n${YELLOW}3. Knowledge Engine Tests${NC}"
echo "=========================="

# Test various intents
run_test "Install intent" \
    "bin/ask-nix 'I want to install firefox'" \
    "install firefox"

run_test "Search intent" \
    "bin/ask-nix 'search for python packages'" \
    "search"

run_test "Update intent" \
    "bin/ask-nix 'update my system'" \
    "update"

run_test "WiFi help" \
    "bin/ask-nix 'my wifi is not working'" \
    "NetworkManager"

run_test "List packages" \
    "bin/ask-nix 'list installed packages'" \
    "list"

echo -e "\n${YELLOW}4. Cache System Tests${NC}"
echo "====================="

# Test cache functionality
run_test "Clear cache" \
    "bin/ask-nix --clear-cache 'test'" \
    "Cache clearing not implemented"

run_test "No cache mode" \
    "bin/ask-nix --no-cache 'search python'" \
    "search"

echo -e "\n${YELLOW}5. Visual Options Tests${NC}"
echo "======================="

# Test visual options
run_test "No progress mode" \
    "bin/ask-nix --no-progress 'install git'" \
    "install"

run_test "No visual mode" \
    "bin/ask-nix --no-visual 'search rust'" \
    "search"

echo -e "\n${YELLOW}6. Feature Integration Tests${NC}"
echo "============================"

# Test combined features
run_test "Dry-run with personality" \
    "bin/ask-nix --dry-run --encouraging 'install emacs'" \
    "Running in dry-run mode"

run_test "Intent with minimal style" \
    "bin/ask-nix --show-intent --minimal 'remove firefox'" \
    "Intent detected: remove_package"

echo -e "\n${YELLOW}Test Summary${NC}"
echo "============"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! The unified command is working correctly.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed. Please review the output above.${NC}"
    exit 1
fi