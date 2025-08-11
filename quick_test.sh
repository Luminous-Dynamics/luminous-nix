#!/bin/bash
# 🚀 Quick Validation Script for Nix for Humanity
# Rapidly tests critical features after changes

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       🚀 Quick Validation - Nix for Humanity v1.0.1           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track results
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name=$1
    local command=$2
    local expected=$3

    echo -n "Testing $test_name... "

    if eval "$command" 2>&1 | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
}

echo "🔒 SECURITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Command injection tests
run_test "Command injection blocking" \
    "./bin/ask-nix 'install firefox; rm -rf /'" \
    "error\|invalid\|Invalid\|dangerous"

run_test "Path traversal blocking" \
    "./bin/ask-nix 'read ../../etc/passwd'" \
    "error\|invalid\|Invalid\|traversal"

echo
echo "📦 FUNCTIONALITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Basic operations
run_test "Install operation" \
    "./bin/ask-nix 'install firefox'" \
    "DRY RUN\|Would execute\|nix"

run_test "Search operation" \
    "./bin/ask-nix 'search for editor'" \
    "search\|editor\|package\|found"

run_test "Config generation" \
    "./bin/ask-nix 'web server with nginx'" \
    "services.nginx\|enable.*true"

echo
echo "🎨 USER EXPERIENCE TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Help system
run_test "Help system" \
    "./bin/ask-nix help" \
    "Nix for Humanity\|USAGE\|EXAMPLES"

run_test "Help flag" \
    "./bin/ask-nix --help" \
    "Natural language\|interface"

# Error handling
echo -n "Testing empty query handling... "
OUTPUT=$(./bin/ask-nix "" 2>&1 || true)
if echo "$OUTPUT" | grep -q "empty\|Empty\|provide"; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAILED++))
fi

echo
echo "🧹 QUALITY TESTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Clean output (no INFO logs)
echo -n "Testing clean output (no log noise)... "
OUTPUT=$(./bin/ask-nix "test query" 2>&1)
if echo "$OUTPUT" | grep -q "INFO\|DEBUG\|WARNING.*import\|Logger"; then
    echo -e "${RED}❌ FAIL (found log noise)${NC}"
    ((FAILED++))
else
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
fi

# Config duplicates
echo -n "Testing config deduplication... "
CONFIG=$(./bin/ask-nix "postgresql postgres database" 2>&1)
POSTGRES_COUNT=$(echo "$CONFIG" | grep -c "services.postgresql.enable = true" || true)
if [ "$POSTGRES_COUNT" -le 1 ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL (found $POSTGRES_COUNT duplicates)${NC}"
    ((FAILED++))
fi

echo
echo "⚡ PERFORMANCE TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Quick performance check
echo -n "Testing response time... "
START=$(date +%s%N)
./bin/ask-nix "test" > /dev/null 2>&1
END=$(date +%s%N)
ELAPSED=$((($END - $START) / 1000000))  # Convert to milliseconds

if [ "$ELAPSED" -lt 2000 ]; then
    echo -e "${GREEN}✅ PASS (${ELAPSED}ms)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  SLOW (${ELAPSED}ms)${NC}"
fi

echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo -e "║  RESULTS: ${GREEN}$PASSED passed${NC} / ${RED}$FAILED failed${NC}                              ║"

if [ "$FAILED" -eq 0 ]; then
    echo -e "║  ${GREEN}✅ ALL CRITICAL TESTS PASSED!${NC}                               ║"
    EXIT_CODE=0
else
    echo -e "║  ${RED}❌ SOME TESTS FAILED - INVESTIGATE!${NC}                         ║"
    EXIT_CODE=1
fi

echo "╚══════════════════════════════════════════════════════════════╝"

# Optional: Run full test suite if requested
if [ "$1" == "--full" ]; then
    echo
    echo "Running full test suite..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./run_tests.sh
fi

exit $EXIT_CODE
