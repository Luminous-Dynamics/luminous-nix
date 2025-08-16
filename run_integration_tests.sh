#!/usr/bin/env bash
# 🧪 Run Integration Tests for Luminous Nix
#
# Safely runs integration tests that interact with real NixOS.
# Detects environment and runs appropriate test subset.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Luminous Nix Integration Test Runner${NC}"
echo "========================================="
echo

# Check if we're on NixOS
if [ -d "/etc/nixos" ] || [ "${NIXOS_TEST:-0}" = "1" ]; then
    echo -e "${GREEN}✅ Running on NixOS - Full integration tests enabled${NC}"
    IS_NIXOS=true
else
    echo -e "${YELLOW}⚠️  Not on NixOS - Running safe tests only${NC}"
    IS_NIXOS=false
fi

# Check for required commands
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 found"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 not found"
        return 1
    fi
}

echo
echo "Checking dependencies:"
check_command python3
check_command poetry

if [ "$IS_NIXOS" = true ]; then
    echo
    echo "Checking NixOS commands:"
    check_command nix || true
    check_command nix-env || true
    check_command nix-channel || true
    check_command nixos-version || true
fi

echo
echo "Test Configuration:"
echo "  • Python: $(python3 --version)"
echo "  • Poetry: $(poetry --version)"

if [ "$IS_NIXOS" = true ]; then
    echo "  • Nix: $(nix --version 2>/dev/null || echo 'not available')"
    echo "  • NixOS: $(nixos-version 2>/dev/null || echo 'not available')"
fi

# Run tests based on environment
echo
echo "Running tests..."
echo "----------------"

if [ "$IS_NIXOS" = true ]; then
    # Full integration tests on NixOS
    echo -e "${BLUE}Running full integration test suite...${NC}"
    
    # Run with integration marker
    poetry run pytest tests/test_nixos_integration.py \
        -v \
        --tb=short \
        -m integration \
        --color=yes \
        || TEST_FAILED=1
        
    # Also run performance tests with real data
    echo
    echo -e "${BLUE}Running performance tests with real data...${NC}"
    poetry run pytest tests/test_nixos_integration.py::TestPerformanceWithRealData \
        -v \
        --tb=short \
        --color=yes \
        || TEST_FAILED=1
        
else
    # Safe tests only on non-NixOS
    echo -e "${BLUE}Running safe integration tests only...${NC}"
    
    poetry run pytest tests/test_nixos_integration.py::TestSafeOperations \
        -v \
        --tb=short \
        --color=yes \
        || TEST_FAILED=1
        
    poetry run pytest tests/test_nixos_integration.py::TestErrorRecovery \
        -v \
        --tb=short \
        --color=yes \
        || TEST_FAILED=1
fi

# Run service layer tests (always safe)
echo
echo -e "${BLUE}Running service layer tests...${NC}"
poetry run pytest tests/test_service_layer.py \
    -v \
    --tb=short \
    --color=yes \
    || TEST_FAILED=1

# Summary
echo
echo "========================================="
if [ "${TEST_FAILED:-0}" = "1" ]; then
    echo -e "${RED}❌ Some tests failed${NC}"
    echo "Please review the output above for details."
    exit 1
else
    echo -e "${GREEN}✅ All integration tests passed!${NC}"
    
    if [ "$IS_NIXOS" = false ]; then
        echo
        echo -e "${YELLOW}Note: Full integration tests require NixOS.${NC}"
        echo "To run all tests, use a NixOS system or set NIXOS_TEST=1"
    fi
fi

echo
echo "Test Coverage Report:"
echo "--------------------"

# Generate coverage report if all tests passed
if [ "${TEST_FAILED:-0}" = "0" ]; then
    poetry run pytest tests/test_nixos_integration.py tests/test_service_layer.py \
        --cov=luminous_nix \
        --cov-report=term-missing:skip-covered \
        --quiet \
        || true
fi

echo
echo -e "${GREEN}🎉 Integration testing complete!${NC}"