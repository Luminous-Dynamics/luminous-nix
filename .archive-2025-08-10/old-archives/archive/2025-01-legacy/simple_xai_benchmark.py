#!/usr/bin/env python3
"""
Simple XAI Performance Benchmark
Tests the actual performance impact of XAI explanations
"""

import statistics
import sys
import time
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "features" / "v3.0" / "xai"))


def benchmark_xai_operations():
    """Benchmark XAI operations directly"""

    print("🚀 Direct XAI Performance Benchmark")
    print("=" * 60)

    # Try to import XAI
    try:
        from causal_xai_engine import CausalXAIEngine, ExplanationDepth

        print("✅ XAI engine loaded successfully")
    except ImportError as e:
        print(f"❌ Could not load XAI engine: {e}")
        return

    # Create XAI instance
    xai = CausalXAIEngine()

    # Test queries
    test_cases = [
        {
            "intent": {"action": "install_package", "package": "firefox"},
            "context": {"result_success": True},
            "description": "Install package",
        },
        {
            "intent": {"action": "update_system", "package": ""},
            "context": {"result_success": True, "security_updates_available": True},
            "description": "System update",
        },
        {
            "intent": {"action": "search_package", "package": "editor"},
            "context": {"result_success": True},
            "description": "Package search",
        },
        {
            "intent": {"action": "remove_package", "package": "python"},
            "context": {"result_success": True},
            "description": "Package removal",
        },
    ]

    # Benchmark each operation
    results = {}

    for test in test_cases:
        print(f"\n📊 Testing: {test['description']}")
        print("-" * 40)

        times = []

        # Test with different explanation depths
        for depth in [
            ExplanationDepth.SIMPLE,
            ExplanationDepth.STANDARD,
            ExplanationDepth.DETAILED,
        ]:
            depth_times = []

            # Run multiple iterations
            for _ in range(100):
                start = time.perf_counter()

                explanation = xai.explain_intent(test["intent"], test["context"], depth)

                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                depth_times.append(elapsed)

            avg_time = statistics.mean(depth_times)
            print(
                f"  {depth.value:10s}: {avg_time:.2f}ms (min: {min(depth_times):.2f}ms, max: {max(depth_times):.2f}ms)"
            )
            times.extend(depth_times)

        results[test["description"]] = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
        }

    # Test error explanation
    print("\n📊 Testing: Error explanation")
    print("-" * 40)

    error_times = []
    for _ in range(100):
        start = time.perf_counter()

        error_result = xai.explain_error(
            "attribute 'firefox' not found",
            {"operation": "install", "user_input": "install firefox"},
        )

        elapsed = (time.perf_counter() - start) * 1000
        error_times.append(elapsed)

    print(f"  Error handling: {statistics.mean(error_times):.2f}ms")

    # Test quick explanation
    print("\n📊 Testing: Quick explanation")
    print("-" * 40)

    quick_times = []
    for action in ["install_package", "update_system", "search_package"]:
        for _ in range(100):
            start = time.perf_counter()

            quick = xai.get_quick_explanation(action, "test-package")

            elapsed = (time.perf_counter() - start) * 1000
            quick_times.append(elapsed)

    print(f"  Quick explanation: {statistics.mean(quick_times):.2f}ms")

    # Summary
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 60)

    all_times = []
    for desc, stats in results.items():
        all_times.append(stats["mean"])
        print(f"  {desc:20s}: {stats['mean']:.2f}ms avg")

    overall_avg = statistics.mean(all_times)
    print(f"\n  Overall average: {overall_avg:.2f}ms")

    # Performance verdict
    print("\n🏁 VERDICT:")
    if overall_avg < 5:
        print("✅ EXCELLENT - XAI adds <5ms overhead (imperceptible)")
    elif overall_avg < 20:
        print("✅ GOOD - XAI adds <20ms overhead (not noticeable)")
    elif overall_avg < 50:
        print("🟡 ACCEPTABLE - XAI adds <50ms overhead (barely noticeable)")
    else:
        print("🔴 NEEDS OPTIMIZATION - XAI adds >50ms overhead (noticeable)")

    print("\n💡 Note: These are pure XAI operation times, not including")
    print("   the rest of the Nix for Humanity pipeline.")


if __name__ == "__main__":
    benchmark_xai_operations()
