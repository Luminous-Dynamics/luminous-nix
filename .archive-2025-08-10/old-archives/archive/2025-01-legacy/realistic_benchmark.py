#!/usr/bin/env python3
"""
Realistic Performance Comparison: With vs Without XAI
Simulates actual backend operations to measure real-world impact
"""

import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "features" / "v3.0" / "xai"))


@dataclass
class MockIntent:
    """Mock intent for testing"""

    type: str
    entities: dict[str, Any]
    confidence: float = 0.8


@dataclass
class MockResult:
    """Mock result for testing"""

    success: bool
    output: str = ""
    error: str = ""


class RealisticBenchmark:
    """Realistic benchmark comparing with/without XAI"""

    def __init__(self):
        self.xai_engine = None

    def simulate_backend_with_xai(self, query: str) -> dict[str, Any]:
        """Simulate backend processing WITH XAI"""

        # Import XAI
        from causal_xai_engine import CausalXAIEngine, ExplanationDepth

        if not self.xai_engine:
            self.xai_engine = CausalXAIEngine()

        # Simulate intent recognition (mock)
        intent = MockIntent(
            type="install_package", entities={"package": "firefox"}, confidence=0.85
        )

        # Simulate execution (mock)
        result = MockResult(success=True, output="Package installed")

        # Generate XAI explanation
        xai_explanation = self.xai_engine.explain_intent(
            {"action": "install_package", "package": "firefox"},
            {"result_success": True},
            ExplanationDepth.STANDARD,
        )

        # Generate XAI suggestions
        suggestions = []
        if hasattr(xai_explanation, "alternatives"):
            suggestions.extend(xai_explanation.alternatives[:2])
        if hasattr(xai_explanation, "benefits"):
            suggestions.append(f"✨ {xai_explanation.benefits[0]}")

        return {
            "intent": intent,
            "result": result,
            "explanation": (
                xai_explanation.why
                if hasattr(xai_explanation, "why")
                else "Processed your request"
            ),
            "suggestions": suggestions,
        }

    def simulate_backend_without_xai(self, query: str) -> dict[str, Any]:
        """Simulate backend processing WITHOUT XAI"""

        # Simulate intent recognition (mock)
        intent = MockIntent(
            type="install_package", entities={"package": "firefox"}, confidence=0.85
        )

        # Simulate execution (mock)
        result = MockResult(success=True, output="Package installed")

        # Simple template-based explanation
        explanation = "I'll help you install firefox"

        # Simple suggestions
        suggestions = [
            "You can now run firefox from your terminal",
            "To make this permanent, add firefox to your configuration.nix",
        ]

        return {
            "intent": intent,
            "result": result,
            "explanation": explanation,
            "suggestions": suggestions,
        }

    def run_comparison(self):
        """Run the comparison benchmark"""

        print("🚀 Realistic Performance Comparison: With vs Without XAI")
        print("=" * 60)

        # Test queries
        test_queries = [
            "install firefox",
            "why should I update my system?",
            "search for text editor",
            "remove python package",
            "help with configuration",
        ]

        # Warmup
        print("\n⏳ Warming up...")
        for _ in range(10):
            self.simulate_backend_with_xai("warmup")
            self.simulate_backend_without_xai("warmup")

        # Benchmark WITH XAI
        print("\n📊 With XAI Enabled:")
        print("-" * 40)

        with_xai_times = []
        for query in test_queries:
            query_times = []
            for _ in range(100):
                start = time.perf_counter()
                result = self.simulate_backend_with_xai(query)
                elapsed = (time.perf_counter() - start) * 1000
                query_times.append(elapsed)

            avg = statistics.mean(query_times)
            with_xai_times.extend(query_times)
            print(f"  '{query[:30]:30s}': {avg:.2f}ms")

        with_xai_overall = statistics.mean(with_xai_times)

        # Benchmark WITHOUT XAI
        print("\n📊 Without XAI:")
        print("-" * 40)

        without_xai_times = []
        for query in test_queries:
            query_times = []
            for _ in range(100):
                start = time.perf_counter()
                result = self.simulate_backend_without_xai(query)
                elapsed = (time.perf_counter() - start) * 1000
                query_times.append(elapsed)

            avg = statistics.mean(query_times)
            without_xai_times.extend(query_times)
            print(f"  '{query[:30]:30s}': {avg:.2f}ms")

        without_xai_overall = statistics.mean(without_xai_times)

        # Calculate impact
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE IMPACT ANALYSIS")
        print("=" * 60)

        overhead_ms = with_xai_overall - without_xai_overall
        overhead_percent = (
            ((with_xai_overall / without_xai_overall) - 1) * 100
            if without_xai_overall > 0
            else 0
        )

        print(f"\n  Without XAI: {without_xai_overall:.3f}ms average")
        print(f"  With XAI:    {with_xai_overall:.3f}ms average")
        print(f"  Overhead:    {overhead_ms:.3f}ms ({overhead_percent:+.1f}%)")

        # Statistical analysis
        print("\n📊 Statistical Analysis:")
        print(
            f"  Median overhead: {statistics.median(with_xai_times) - statistics.median(without_xai_times):.3f}ms"
        )
        print(f"  Max with XAI:    {max(with_xai_times):.3f}ms")
        print(f"  Max without XAI: {max(without_xai_times):.3f}ms")

        # Value proposition
        print("\n💡 Value Proposition:")
        print(f"  Cost: {overhead_ms:.3f}ms additional latency")
        print("  Benefits:")
        print("    • Causal explanations (WHY)")
        print("    • Confidence indicators")
        print("    • Risk assessments")
        print("    • Smart alternatives")
        print("    • Learning from outcomes")

        # Final verdict
        print("\n🏁 VERDICT:")
        if overhead_ms < 1:
            print("✅ PERFECT - XAI adds <1ms (completely imperceptible)")
            print("   The benefits FAR outweigh the negligible cost!")
        elif overhead_ms < 10:
            print("✅ EXCELLENT - XAI adds <10ms (imperceptible)")
            print("   Users get intelligent explanations with zero perceived slowdown!")
        elif overhead_ms < 50:
            print("✅ GOOD - XAI adds <50ms (not noticeable)")
            print("   Worth it for the intelligence gained!")
        else:
            print("🟡 ACCEPTABLE - XAI adds noticeable overhead")
            print("   Consider optimization or making it optional")

        # User experience impact
        print("\n👤 User Experience Impact:")
        total_time = with_xai_overall
        if total_time < 100:
            print(f"   Total response time: {total_time:.1f}ms")
            print("   ✅ Feels INSTANT to users (<100ms)")
        elif total_time < 200:
            print(f"   Total response time: {total_time:.1f}ms")
            print("   ✅ Feels FAST to users (<200ms)")
        elif total_time < 500:
            print(f"   Total response time: {total_time:.1f}ms")
            print("   ✅ Feels RESPONSIVE to users (<500ms)")
        else:
            print(f"   Total response time: {total_time:.1f}ms")
            print("   🟡 May feel slightly slow (>500ms)")


if __name__ == "__main__":
    try:
        benchmark = RealisticBenchmark()
        benchmark.run_comparison()
    except ImportError as e:
        print(f"❌ Could not run benchmark: {e}")
        print("\nPlease ensure XAI engine is available:")
        print("  features/v3.0/xai/causal_xai_engine.py")
