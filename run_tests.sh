#!/bin/bash
# 🧪 Test Runner for Nix for Humanity

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🧪 Running Nix for Humanity Test Suite                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests for a module
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo -e "${YELLOW}Testing $test_name...${NC}"
    
    if python3 "$test_file" -v 2>&1 | tee /tmp/test_output.txt; then
        echo -e "${GREEN}✅ $test_name passed${NC}\n"
        return 0
    else
        echo -e "${RED}❌ $test_name failed${NC}\n"
        return 1
    fi
}

# Track overall success
FAILED=0

# Run individual test modules
echo "🔒 Security Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_test tests/test_security.py "Security Validation" || FAILED=1

echo "🏗️ Backend Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_test tests/test_unified_backend.py "Unified Backend" || FAILED=1

echo "⚙️ Config Generation Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_test tests/test_config_generator.py "Config Generator" || FAILED=1

echo "💻 CLI Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
run_test tests/test_cli.py "CLI Interface" || FAILED=1

# Summary
echo
echo "╔══════════════════════════════════════════════════════════════╗"
if [ $FAILED -eq 0 ]; then
    echo -e "║        ${GREEN}✅ All Tests Passed Successfully!${NC}                     ║"
else
    echo -e "║        ${RED}❌ Some Tests Failed${NC}                                  ║"
fi
echo "╚══════════════════════════════════════════════════════════════╝"

# Run with pytest if available for better reporting
if command -v pytest &> /dev/null; then
    echo
    echo "📊 Running with pytest for detailed coverage..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    pytest tests/ -v --tb=short || true
fi

exit $FAILED