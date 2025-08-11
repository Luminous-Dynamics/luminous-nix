#!/usr/bin/env bash
# Test all 5 core commands for Nix for Humanity

echo "🧪 Testing All 5 Core Commands for Nix for Humanity"
echo "=================================================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local command="$2"

    echo -e "${YELLOW}Test:${NC} $test_name"
    echo "Command: $command"
    echo "---"

    if $command; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo
    echo "=================================="
    echo
    sleep 1
}

# Make sure we're in the right directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity || exit 1

echo "📍 Testing from: $(pwd)"
echo

# Test 1: Search for a package
echo "=== TEST 1: SEARCH COMMAND ==="
run_test "Search for neovim" "./bin/ask-nix 'search neovim'"

# Test 2: Install a package (dry-run to avoid actually installing)
echo "=== TEST 2: INSTALL COMMAND (DRY RUN) ==="
run_test "Install neovim (dry-run)" "./bin/ask-nix --dry-run 'install neovim'"

# Test 3: List installed packages
echo "=== TEST 3: LIST PACKAGES COMMAND ==="
run_test "List installed packages" "./bin/ask-nix 'list installed packages'"

# Test 4: Remove a package (dry-run)
echo "=== TEST 4: REMOVE COMMAND (DRY RUN) ==="
run_test "Remove neovim (dry-run)" "./bin/ask-nix --dry-run 'remove neovim'"

# Test 5: Update system
echo "=== TEST 5: UPDATE COMMAND (DRY RUN) ==="
run_test "Update my packages (dry-run)" "./bin/ask-nix --dry-run 'update my packages'"

# Summary
echo
echo "📊 TEST SUMMARY"
echo "=============="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
