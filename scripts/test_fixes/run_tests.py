#!/usr/bin/env python3
"""
Test runner for Nix for Humanity

Runs all tests with coverage reporting.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run test suite with coverage"""

    print("🧪 Running Nix for Humanity Test Suite")
    print("=" * 60)

    # Change to project directory
    project_dir = Path(__file__).parent

    # Run pytest with coverage
    cmd = ["python3", "-m", "pytest", "tests/", "-v", "--tb=short", "--color=yes"]

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
