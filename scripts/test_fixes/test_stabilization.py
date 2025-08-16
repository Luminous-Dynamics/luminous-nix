#!/usr/bin/env python3
"""
Comprehensive stabilization test suite.
Tests what actually works and identifies what needs fixing.
"""

import sys
import time

sys.path.insert(0, "src")

print("=" * 60)
print("🧪 NIX FOR HUMANITY STABILIZATION TEST SUITE")
print("=" * 60)

# Track results
results = {"passed": [], "failed": [], "warnings": []}


def test(name, func):
    """Run a test and track results."""
    print(f"\n📋 Testing: {name}")
    print("-" * 40)
    try:
        result = func()
        if result:
            results["passed"].append(name)
            print(f"✅ PASSED: {name}")
        else:
            results["failed"].append(name)
            print(f"❌ FAILED: {name}")
        return result
    except Exception as e:
        results["failed"].append(name)
        print(f"❌ FAILED: {name} - {e}")
        return False


# TEST 1: Core Imports
def test_core_imports():
    """Test that core modules can be imported."""
    try:
        from luminous_nix.backend.native_nix_api import NativeNixAPI
        from luminous_nix.core.unified_backend import NixForHumanityBackend
        from luminous_nix.learning.pragmatic_learning import PragmaticLearningSystem

        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False


# TEST 2: Pragmatic Learning with Kairos
def test_pragmatic_learning():
    """Test the pragmatic learning system with kairos improvements."""
    from luminous_nix.learning.pragmatic_learning import PragmaticLearningSystem

    learning = PragmaticLearningSystem("test_user")

    # Kairos: Adaptive thresholds
    learning.ALIAS_THRESHOLD = 2  # Learn faster for testing

    # Test error → success learning
    learning.observe_command("grab firefox", False, "unknown command")
    learning.observe_command("install firefox", True, None)
    learning.observe_command("grab vscode", False, "unknown command")
    learning.observe_command("install vscode", True, None)

    # Should have learned the alias now
    suggestion = learning.suggest_alias("grab chrome")
    if suggestion and "install" in suggestion:
        print("  ✓ Learned alias: grab → install")
        return True
    print(f"  ✗ Failed to learn alias (got: {suggestion})")
    return False


# TEST 3: Native API Performance
def test_native_api_performance():
    """Test the native API performance claims."""
    from luminous_nix.backend.native_nix_api import NativeNixAPI

    api = NativeNixAPI()

    # Test search performance
    start = time.time()
    results = api.search_packages("firefox")
    elapsed = time.time() - start

    print(f"  Search time: {elapsed*1000:.2f}ms")
    print(f"  Results: {len(results)} packages")

    # Performance should be under 100ms
    if elapsed < 0.1:
        print(f"  ✓ Performance verified: {elapsed*1000:.0f}ms < 100ms")
        return True
    print(f"  ✗ Too slow: {elapsed*1000:.0f}ms > 100ms")
    results["warnings"].append(f"Search took {elapsed*1000:.0f}ms")
    return False


# TEST 4: Backend Initialization
def test_backend_init():
    """Test that the backend initializes properly."""
    from luminous_nix.core.unified_backend import NixForHumanityBackend

    backend = NixForHumanityBackend()

    # Check default configuration
    if backend.config.get("dry_run", True):
        print("  ✓ Dry run mode enabled by default (safe)")
    else:
        print("  ⚠️  Dry run disabled by default (unsafe)")
        results["warnings"].append("Dry run should be enabled by default")

    return True


# TEST 5: CLI Entry Point
def test_cli_entry():
    """Test that the CLI can at least show help."""
    import subprocess

    result = subprocess.run(
        ["python3", "bin/ask-nix", "--help"], capture_output=True, text=True, timeout=5
    )

    # Should not crash
    if result.returncode != 0:
        print(f"  ✗ CLI crashed: {result.stderr[:200]}")
        return False

    # Should show help text
    if "Nix for Humanity" in result.stdout or "Usage" in result.stdout.lower():
        print("  ✓ CLI help works")
        return True
    print("  ✗ No help text shown")
    return False


# TEST 6: Learning Persistence
def test_learning_persistence():
    """Test that learning data persists."""
    from luminous_nix.learning.pragmatic_learning import PragmaticLearningSystem

    # Create and save
    learning1 = PragmaticLearningSystem("persist_test")
    learning1.preferences.aliases["test"] = "works"
    learning1.save_preferences()

    # Load in new instance
    learning2 = PragmaticLearningSystem("persist_test")

    if learning2.preferences.aliases.get("test") == "works":
        print("  ✓ Learning data persists")
        # Clean up
        learning2.delete_all_data()
        return True
    print("  ✗ Learning data lost")
    return False


# TEST 7: Intent Recognition
def test_intent_recognition():
    """Test basic intent recognition."""
    try:
        # Try multiple possible locations
        try:
            from luminous_nix.nlp.intent_recognition import IntentRecognizer
        except ImportError:
            from luminous_nix.core.intents import IntentRecognizer

        recognizer = IntentRecognizer()

        tests = [
            ("install firefox", "INSTALL"),
            ("search for editor", "SEARCH"),
            ("update system", "UPDATE"),
            ("remove package", "REMOVE"),
        ]

        for query, expected_type in tests:
            intent = recognizer.recognize(query)
            if expected_type in str(intent.type):
                print(f"  ✓ '{query}' → {intent.type}")
            else:
                print(f"  ✗ '{query}' → {intent.type} (expected {expected_type})")
                return False

        return True
    except Exception as e:
        print(f"  ⚠️  Intent recognition not available: {e}")
        results["warnings"].append("Intent recognition module missing")
        return False


# Run all tests
test("Core Imports", test_core_imports)
test("Pragmatic Learning", test_pragmatic_learning)
test("Native API Performance", test_native_api_performance)
test("Backend Initialization", test_backend_init)
test("CLI Entry Point", test_cli_entry)
test("Learning Persistence", test_learning_persistence)
test("Intent Recognition", test_intent_recognition)

# Summary
print("\n" + "=" * 60)
print("📊 TEST RESULTS SUMMARY")
print("=" * 60)

print(f"\n✅ PASSED: {len(results['passed'])}")
for name in results["passed"]:
    print(f"   • {name}")

if results["warnings"]:
    print(f"\n⚠️  WARNINGS: {len(results['warnings'])}")
    for warning in results["warnings"]:
        print(f"   • {warning}")

if results["failed"]:
    print(f"\n❌ FAILED: {len(results['failed'])}")
    for name in results["failed"]:
        print(f"   • {name}")

# Overall status
print("\n" + "=" * 60)
if not results["failed"]:
    print("🎉 ALL CRITICAL TESTS PASSED!")
    print("The system is stable enough for v1.1.0 release.")
elif len(results["failed"]) <= 2:
    print("⚠️  MOSTLY STABLE")
    print("Fix the remaining issues before release.")
else:
    print("🚨 NEEDS WORK")
    print("Multiple critical failures need attention.")

# Recommendations
print("\n📝 RECOMMENDATIONS:")
print("-" * 40)

if "CLI Entry Point" in results["failed"]:
    print("1. Fix import issues in CLI (semver, Intent)")

if "Intent Recognition" in results["failed"]:
    print("2. Intent recognition module needs to be implemented")

if results["warnings"]:
    print("3. Address warnings for better stability")

if not results["failed"]:
    print("1. Add more comprehensive tests")
    print("2. Test with real NixOS commands")
    print("3. Get user feedback on learning system")
    print("4. Tag and release v1.1.0!")

print("\n🌊 Kairos: The right improvements at the right time.")
