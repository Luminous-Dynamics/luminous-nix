#!/bin/bash
# Run all v1.1 tests - TUI, Voice, and Performance

set -e

echo "🧪 Nix for Humanity v1.1 Test Suite"
echo "==================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test suite
run_test_suite() {
    local suite_name=$1
    local test_file=$2
    
    echo -e "${YELLOW}Running $suite_name...${NC}"
    
    if python -m pytest "$test_file" -v --tb=short; then
        echo -e "${GREEN}✓ $suite_name passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ $suite_name failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    echo ""
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Must run from project root directory"
    exit 1
fi

# Create test report directory
mkdir -p test_reports

echo "📋 Test Environment"
echo "=================="
python --version
echo "NixOS Version: $(nixos-version 2>/dev/null || echo 'Not on NixOS')"
echo ""

echo "🔧 Setting up test environment..."
export NIX_HUMANITY_PYTHON_BACKEND=true
export TESTING=true
echo ""

# Run TUI Integration Tests
echo "🖥️  TUI Integration Tests"
echo "======================"
run_test_suite "TUI Integration" "tests/integration/test_tui_integration.py"

# Run Voice Interface Tests
echo "🎤 Voice Interface Tests"
echo "======================"
run_test_suite "Voice Interface" "tests/integration/test_voice_interface.py"

# Run Performance Benchmarks
echo "⚡ Performance Benchmarks"
echo "======================="
run_test_suite "Performance" "tests/performance/test_v1_1_benchmarks.py"

# Run existing v1.0 tests to ensure no regression
echo "🔄 Regression Tests (v1.0)"
echo "========================"
run_test_suite "Core Features" "tests/test_core_features.py"
run_test_suite "Native Backend" "tests/test_native_backend.py"

# Generate test report
echo "📊 Test Summary"
echo "=============="
echo "Total test suites: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
echo ""

# Generate JSON report
cat > test_reports/v1_1_test_results.json << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "v1.1.0",
  "test_summary": {
    "total": $TOTAL_TESTS,
    "passed": $PASSED_TESTS,
    "failed": $FAILED_TESTS
  },
  "suites": [
    {"name": "TUI Integration", "status": "pending"},
    {"name": "Voice Interface", "status": "pending"},
    {"name": "Performance", "status": "pending"},
    {"name": "Core Features", "status": "pending"},
    {"name": "Native Backend", "status": "pending"}
  ]
}
EOF

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✨ All tests passed! v1.1 is ready.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi