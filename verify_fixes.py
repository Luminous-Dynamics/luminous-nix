#!/usr/bin/env python3
"""
Verify all critical fixes are working
"""

import os
import subprocess
import sys

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_test(name, command, check_for=None, should_fail=False):
    """Run a test and check the output"""
    print(f"Testing {name}... ", end="")

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=5
        )

        output = result.stdout + result.stderr

        # Check if it should fail
        if should_fail:
            if result.returncode != 0:
                print(f"{GREEN}✅ PASS{RESET} (correctly failed)")
                return True
            print(f"{RED}❌ FAIL{RESET} (should have failed)")
            return False

        # Check for expected output
        if check_for:
            if check_for in output:
                print(f"{GREEN}✅ PASS{RESET}")
                return True
            print(f"{RED}❌ FAIL{RESET}")
            print(f"  Expected: {check_for}")
            print(f"  Got: {output[:100]}...")
            return False

        # Just check if it ran
        if result.returncode == 0:
            print(f"{GREEN}✅ PASS{RESET}")
            return True
        print(f"{RED}❌ FAIL{RESET}")
        print(f"  Error: {output[:100]}...")
        return False

    except subprocess.TimeoutExpired:
        print(f"{YELLOW}⚠️  TIMEOUT{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ ERROR: {e}{RESET}")
        return False


def main():
    print("=" * 60)
    print("🧪 Verifying Nix for Humanity Fixes")
    print("=" * 60)
    print()

    os.chdir("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")

    passed = 0
    failed = 0

    # Test 1: Basic functionality
    print("📦 BASIC FUNCTIONALITY")
    print("-" * 40)
    if run_test("Basic CLI", "python3 bin/ask-nix 'install firefox'", "DRY RUN"):
        passed += 1
    else:
        failed += 1
    print()

    # Test 2: Security - Command Injection
    print("🔒 SECURITY FIXES")
    print("-" * 40)
    if run_test(
        "Command injection blocked",
        "python3 bin/ask-nix 'install firefox; rm -rf /'",
        "Invalid",
    ):
        passed += 1
    else:
        failed += 1

    if run_test(
        "Path traversal blocked",
        "python3 bin/ask-nix 'read ../../etc/passwd'",
        "Invalid",
    ):
        passed += 1
    else:
        failed += 1
    print()

    # Test 3: Config Generation
    print("⚙️ BUG FIXES")
    print("-" * 40)
    result = subprocess.run(
        "python3 bin/ask-nix 'postgresql postgres database'",
        shell=True,
        capture_output=True,
        text=True,
    )
    postgres_count = result.stdout.count("services.postgresql.enable = true")
    if postgres_count <= 1:
        print(f"Config deduplication... {GREEN}✅ PASS{RESET}")
        passed += 1
    else:
        print(
            f"Config deduplication... {RED}❌ FAIL{RESET} ({postgres_count} duplicates)"
        )
        failed += 1
    print()

    # Test 4: Logging
    print("🧹 QUALITY IMPROVEMENTS")
    print("-" * 40)
    result = subprocess.run(
        "python3 bin/ask-nix 'test' 2>&1", shell=True, capture_output=True, text=True
    )
    if "INFO" not in result.stdout and "WARNING - XAI" not in result.stdout:
        print(f"Clean logging... {GREEN}✅ PASS{RESET}")
        passed += 1
    else:
        print(f"Clean logging... {RED}❌ FAIL{RESET} (found log noise)")
        failed += 1
    print()

    # Test 5: Help System
    print("📚 HELP SYSTEM")
    print("-" * 40)
    if run_test("Help flag", "python3 bin/ask-nix --help", "Natural language"):
        passed += 1
    else:
        failed += 1

    if run_test("Help query", "python3 bin/ask-nix help", "Nix for Humanity"):
        passed += 1
    else:
        failed += 1
    print()

    # Test 6: Error Handling
    print("⚠️ ERROR HANDLING")
    print("-" * 40)
    result = subprocess.run(
        "python3 bin/ask-nix ''", shell=True, capture_output=True, text=True
    )
    if "Empty" in result.stdout or "empty" in result.stdout:
        print(f"Empty query handling... {GREEN}✅ PASS{RESET}")
        passed += 1
    else:
        print(f"Empty query handling... {RED}❌ FAIL{RESET}")
        failed += 1
    print()

    # Summary
    print("=" * 60)
    print(f"📊 RESULTS: {GREEN}{passed} passed{RESET} / {RED}{failed} failed{RESET}")

    if failed == 0:
        print(f"{GREEN}✅ ALL CRITICAL FIXES VERIFIED!{RESET}")
        return 0
    print(f"{RED}❌ SOME FIXES NEED ATTENTION{RESET}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
