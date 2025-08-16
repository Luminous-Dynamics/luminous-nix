#!/usr/bin/env python3
"""
Unified test runner for Nix for Humanity.

This replaces multiple test runners and provides a single
entry point for all testing needs.

Usage:
    python run_all_tests.py           # Run all tests
    python run_all_tests.py --unit    # Run unit tests only
    python run_all_tests.py --fast    # Skip slow tests
    python run_all_tests.py --cov     # With coverage report
"""

import sys
import subprocess
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(message):
    """Print a colored header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{message}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def run_tests(test_type="all", coverage=False, verbose=False):
    """Run the test suite."""
    
    # Base pytest command
    cmd = ["poetry", "run", "pytest"]
    
    # Add test directory based on type
    if test_type == "unit":
        cmd.append("tests_consolidated/unit")
        print_header("Running Unit Tests")
    elif test_type == "integration":
        cmd.append("tests_consolidated/integration")
        print_header("Running Integration Tests")
    elif test_type == "e2e":
        cmd.append("tests_consolidated/e2e")
        print_header("Running End-to-End Tests")
    elif test_type == "fast":
        cmd.extend(["tests_consolidated", "-m", "not slow"])
        print_header("Running Fast Tests (excluding slow)")
    else:
        cmd.append("tests_consolidated")
        print_header("Running All Tests")
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            "--cov=nix_for_humanity",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_report",
            "--cov-fail-under=80"  # Fail if coverage < 80%
        ])
    
    # Add verbosity
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Fail on unknown markers
        "--color=yes",  # Colored output
        "-x",  # Stop on first failure
    ])
    
    # Run the tests
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    return result.returncode


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified test runner for Nix for Humanity")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--cov", "--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmarks")
    
    args = parser.parse_args()
    
    # Determine test type
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.e2e:
        test_type = "e2e"
    elif args.fast:
        test_type = "fast"
    elif args.benchmark:
        print_header("Running Performance Benchmarks")
        # Run performance tests separately
        cmd = [
            "poetry", "run", "pytest",
            "tests_consolidated",
            "-m", "performance",
            "-v",
            "--benchmark-only"
        ]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    else:
        test_type = "all"
    
    # Run tests
    exit_code = run_tests(test_type, args.cov, args.verbose)
    
    # Print summary
    if exit_code == 0:
        print(f"\n{GREEN}✅ All tests passed!{RESET}")
        if args.cov:
            print(f"{GREEN}📊 Coverage report generated in coverage_report/index.html{RESET}")
    else:
        print(f"\n{RED}❌ Tests failed!{RESET}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()