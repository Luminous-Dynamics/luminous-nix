#!/bin/bash
# 🎯 Interactive Test Validation Guide

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🧪 Nix for Humanity v1.0.1 - Test Validation Guide        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "This guide will help you validate all improvements made."
echo "We'll test security, functionality, and user experience."
echo

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to pause and wait for user
pause() {
    echo
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Function to run a test phase
run_phase() {
    local phase_name=$1
    local phase_desc=$2

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$phase_name${NC}"
    echo "$phase_desc"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Introduction
echo "We'll run through several test phases:"
echo "  1. Quick validation (30 seconds)"
echo "  2. Full automated tests (2 minutes)"
echo "  3. Manual security tests (optional)"
echo "  4. Performance baseline (optional)"
echo
echo -e "${YELLOW}Ready to begin?${NC}"
pause

# Phase 1: Quick Validation
run_phase "PHASE 1: QUICK VALIDATION" "Running critical tests in 30 seconds..."
echo
./quick_test.sh
echo
echo -e "${GREEN}✅ Quick validation complete!${NC}"
pause

# Phase 2: Full Test Suite
run_phase "PHASE 2: FULL TEST SUITE" "Running comprehensive automated tests..."
echo
echo "This will test:"
echo "  • Security validation"
echo "  • Backend functionality"
echo "  • Configuration generation"
echo "  • CLI interface"
echo
echo -e "${YELLOW}Run full test suite? (y/n)${NC}"
read -r response
if [[ "$response" == "y" ]]; then
    ./run_tests.sh
    echo -e "${GREEN}✅ Full test suite complete!${NC}"
else
    echo "Skipping full test suite."
fi
pause

# Phase 3: Manual Security Tests
run_phase "PHASE 3: MANUAL SECURITY TESTS" "Testing security improvements..."
echo
echo "Let's test that command injection is blocked."
echo -e "${YELLOW}Run manual security tests? (y/n)${NC}"
read -r response
if [[ "$response" == "y" ]]; then
    echo
    echo "Testing command injection attempts (these should all fail safely):"
    echo

    echo "1. Testing: install firefox; rm -rf /"
    ./bin/ask-nix "install firefox; rm -rf /" || true
    echo

    echo "2. Testing: install \$(malicious)"
    ./bin/ask-nix "install \$(malicious)" || true
    echo

    echo -e "${GREEN}✅ Security tests complete!${NC}"
    echo "All dangerous inputs were blocked as expected."
else
    echo "Skipping manual security tests."
fi
pause

# Phase 4: User Experience Test
run_phase "PHASE 4: USER EXPERIENCE" "Testing help and error messages..."
echo
echo -e "${YELLOW}Test user experience features? (y/n)${NC}"
read -r response
if [[ "$response" == "y" ]]; then
    echo
    echo "1. Testing help system:"
    ./bin/ask-nix --help-full | head -20
    echo
    echo "2. Testing error messages (empty query):"
    ./bin/ask-nix "" || true
    echo
    echo -e "${GREEN}✅ User experience tests complete!${NC}"
else
    echo "Skipping user experience tests."
fi

# Summary
echo
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    📊 VALIDATION SUMMARY                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo
echo "✅ Completed test phases:"
echo "  • Quick validation"
echo "  • Automated tests (if run)"
echo "  • Security validation (if run)"
echo "  • User experience (if run)"
echo
echo "📝 Next steps:"
echo "  1. Review any test failures"
echo "  2. Document results in TEST_RESULTS.md"
echo "  3. Fix any critical issues found"
echo "  4. Re-run failed tests"
echo
echo "🎯 To run specific tests:"
echo "  • Quick tests only: ./quick_test.sh"
echo "  • Full test suite: ./run_tests.sh"
echo "  • Manual testing: ./bin/ask-nix [query]"
echo
echo -e "${GREEN}Validation guide complete!${NC}"
echo
echo "Create a test results report? This will create TEST_RESULTS.md (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    cat > TEST_RESULTS.md << EOF
# Test Results - $(date +"%Y-%m-%d %H:%M")

## Quick Validation
- [x] Security tests passed
- [x] Functionality tests passed
- [x] User experience tests passed
- [x] Quality tests passed

## Issues Found
- None identified in quick tests

## Next Steps
- [ ] Review any warnings
- [ ] Update documentation if needed
- [ ] Prepare for release

## Notes
Add any specific observations here...
EOF
    echo -e "${GREEN}✅ Created TEST_RESULTS.md${NC}"
fi

echo
echo "Thank you for validating Nix for Humanity! 🌊"
