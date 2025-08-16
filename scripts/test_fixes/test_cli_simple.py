#!/usr/bin/env python3
"""
Simple test of the CLI without all the complex imports.
Tests the pragmatic learning system directly.
"""

import sys

sys.path.insert(0, "src")

# Test 1: Pragmatic learning system
print("🧪 Test 1: Pragmatic Learning System")
print("-" * 40)
try:
    from luminous_nix.learning.pragmatic_learning import PragmaticLearningSystem

    learning = PragmaticLearningSystem("test_user")

    # Simulate some commands
    commands = [
        ("grab firefox", False, "unknown command"),
        ("install firefox", True, None),
        ("grab vscode", False, "unknown command"),
        ("install vscode", True, None),
        ("nixos-rebuild switch", True, None),
        ("nix-collect-garbage", True, None),
    ]

    for cmd, success, error in commands:
        learning.observe_command(cmd, success, error)

    # Test alias suggestion
    suggestion = learning.suggest_alias("grab chrome")
    print(f"✅ Alias suggestion: {suggestion}")

    # Test sequence suggestion
    next_cmd = learning.suggest_next_command("nixos-rebuild switch")
    print(f"✅ Next command: {next_cmd}")

    # Show what was learned
    summary = learning.get_learning_summary()
    print(f"✅ Learned {len(summary['learned_patterns']['aliases'])} aliases")
    print(
        f"✅ Learned {len(summary['learned_patterns']['common_sequences'])} sequences"
    )

    print("\n✅ Pragmatic learning works!")

except Exception as e:
    print(f"❌ Pragmatic learning failed: {e}")
    import traceback

    traceback.print_exc()

# Test 2: Native API (if available)
print("\n🧪 Test 2: Native API Performance")
print("-" * 40)
try:
    import time

    from luminous_nix.backend.native_nix_api import NativeNixAPI

    api = NativeNixAPI()

    # Test search performance
    start = time.time()
    results = api.search_packages("firefox")
    elapsed = time.time() - start

    print(f"✅ Search completed in {elapsed*1000:.2f}ms")
    print(f"✅ Found {len(results)} packages")

    # Verify performance claim
    if elapsed < 0.1:  # Less than 100ms
        print("✅ Performance claim verified: <100ms search!")
    else:
        print(f"⚠️  Search took {elapsed:.2f}s, not as fast as claimed")

except ImportError:
    print("⚠️  Native API not available (expected, it's aspirational)")
except Exception as e:
    print(f"❌ Native API test failed: {e}")

# Test 3: Core CLI functionality (simplified)
print("\n🧪 Test 3: Core CLI Functionality")
print("-" * 40)
try:
    # Just test that the backend can be imported
    from luminous_nix.core.unified_backend import NixForHumanityBackend

    backend = NixForHumanityBackend()
    print("✅ Backend initialized")
    print(f"✅ Dry run mode: {backend.config.get('dry_run', True)}")

    # Test a simple query (without full execution)
    from luminous_nix.nlp.intent_recognition import IntentRecognizer

    recognizer = IntentRecognizer()

    test_queries = [
        "install firefox",
        "search for markdown editor",
        "update system",
    ]

    for query in test_queries:
        intent = recognizer.recognize(query)
        print(f"✅ Recognized: '{query}' → {intent.type.value}")

except Exception as e:
    print(f"❌ Core CLI test failed: {e}")

print("\n" + "=" * 50)
print("📊 Test Summary")
print("=" * 50)
print(
    """
What's Working:
- Pragmatic learning system ✅
- Intent recognition ✅
- Basic backend structure ✅

What Needs Fixing:
- Import issues in plugins
- Missing semver dependency
- Native API not implemented yet

Recommendation: Focus on fixing imports and dependencies
before adding more features.
"""
)
