#!/usr/bin/env python3
"""
Performance Benchmark: XAI Integration Impact Analysis
Tests the performance impact of XAI explanations on Nix for Humanity
"""

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the backend
from luminous_nix.api.schema import Request
from luminous_nix.core.engine import NixForHumanityBackend


class PerformanceBenchmark:
    """Benchmark XAI performance impact"""

    def __init__(self):
        self.results = {"with_xai": {}, "without_xai": {}, "comparison": {}}

    async def benchmark_query(
        self, backend: NixForHumanityBackend, query: str, iterations: int = 100
    ) -> dict[str, float]:
        """Benchmark a single query multiple times"""
        times = []

        for _ in range(iterations):
            request = Request(query=query, context={})

            start = time.perf_counter()
            try:
                response = await backend.process_request(request)
                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
                times.append(elapsed)
            except Exception as e:
                print(f"  ⚠️ Error during benchmark: {e}")
                continue

        if not times:
            return {"mean": 0, "median": 0, "min": 0, "max": 0, "stdev": 0}

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
            "samples": len(times),
        }

    async def run_benchmarks(self):
        """Run comprehensive benchmarks"""
        print("🚀 Nix for Humanity XAI Performance Benchmark")
        print("=" * 60)

        # Test queries covering different intents
        test_queries = [
            ("install firefox", "Simple install command"),
            ("why should I update my system?", "XAI-heavy explanation query"),
            ("search for text editor", "Search operation"),
            ("what are the risks of removing python?", "Risk assessment query"),
            ("help", "Simple help request"),
            ("configure nginx web server", "Complex configuration"),
        ]

        # Warmup
        print("\n⏳ Warming up...")
        backend_warmup = NixForHumanityBackend()
        for query, _ in test_queries[:2]:
            request = Request(query=query, context={})
            try:
                await backend_warmup.process_request(request)
            except:
                pass

        # Benchmark WITH XAI
        print("\n📊 Benchmarking WITH XAI enabled...")
        print("-" * 40)

        backend_with_xai = NixForHumanityBackend()

        for query, description in test_queries:
            print(f"\n Testing: {description}")
            print(f"  Query: '{query}'")

            stats = await self.benchmark_query(backend_with_xai, query, iterations=50)
            self.results["with_xai"][query] = stats

            print(f"  Mean: {stats['mean']:.2f}ms")
            print(f"  Median: {stats['median']:.2f}ms")
            print(f"  Range: {stats['min']:.2f}ms - {stats['max']:.2f}ms")

        # Benchmark WITHOUT XAI
        print("\n📊 Benchmarking WITHOUT XAI...")
        print("-" * 40)

        # Disable XAI by setting the engine to None
        backend_without_xai = NixForHumanityBackend()
        backend_without_xai.xai_engine = None  # Disable XAI

        for query, description in test_queries:
            print(f"\n Testing: {description}")
            print(f"  Query: '{query}'")

            stats = await self.benchmark_query(
                backend_without_xai, query, iterations=50
            )
            self.results["without_xai"][query] = stats

            print(f"  Mean: {stats['mean']:.2f}ms")
            print(f"  Median: {stats['median']:.2f}ms")
            print(f"  Range: {stats['min']:.2f}ms - {stats['max']:.2f}ms")

        # Calculate comparison
        self._calculate_comparison()

        # Print summary
        self._print_summary()

        # Save detailed results
        self._save_results()

    def _calculate_comparison(self):
        """Calculate performance comparison"""
        for query in self.results["with_xai"]:
            if query in self.results["without_xai"]:
                with_xai = self.results["with_xai"][query]
                without_xai = self.results["without_xai"][query]

                # Calculate overhead
                overhead_ms = with_xai["mean"] - without_xai["mean"]
                overhead_percent = (
                    ((with_xai["mean"] / without_xai["mean"]) - 1) * 100
                    if without_xai["mean"] > 0
                    else 0
                )

                self.results["comparison"][query] = {
                    "overhead_ms": overhead_ms,
                    "overhead_percent": overhead_percent,
                    "still_under_100ms": with_xai["mean"] < 100,
                    "still_under_500ms": with_xai["mean"] < 500,
                    "user_noticeable": overhead_ms > 50,  # 50ms is generally noticeable
                }

    def _print_summary(self):
        """Print performance summary"""
        print("\n" + "=" * 60)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 60)

        # Overall stats
        all_with_xai = [v["mean"] for v in self.results["with_xai"].values()]
        all_without_xai = [v["mean"] for v in self.results["without_xai"].values()]

        overall_with = statistics.mean(all_with_xai) if all_with_xai else 0
        overall_without = statistics.mean(all_without_xai) if all_without_xai else 0
        overall_overhead = overall_with - overall_without
        overall_overhead_percent = (
            ((overall_with / overall_without) - 1) * 100 if overall_without > 0 else 0
        )

        print("\n🎯 Overall Performance:")
        print(f"  Without XAI: {overall_without:.2f}ms average")
        print(f"  With XAI:    {overall_with:.2f}ms average")
        print(
            f"  Overhead:    {overall_overhead:.2f}ms ({overall_overhead_percent:+.1f}%)"
        )

        # Check performance goals
        print("\n✅ Performance Goals:")
        goals_met = 0
        goals_total = 4

        if overall_with < 100:
            print(f"  ✅ Average under 100ms: {overall_with:.2f}ms")
            goals_met += 1
        else:
            print(f"  ❌ Average under 100ms: {overall_with:.2f}ms")

        if overall_overhead < 50:
            print(f"  ✅ Overhead under 50ms: {overall_overhead:.2f}ms")
            goals_met += 1
        else:
            print(f"  ❌ Overhead under 50ms: {overall_overhead:.2f}ms")

        if max(all_with_xai) < 500:
            print(f"  ✅ All operations under 500ms: Max {max(all_with_xai):.2f}ms")
            goals_met += 1
        else:
            print(f"  ❌ Some operations over 500ms: Max {max(all_with_xai):.2f}ms")

        if overall_overhead_percent < 100:
            print(f"  ✅ Overhead under 100%: {overall_overhead_percent:+.1f}%")
            goals_met += 1
        else:
            print(f"  ❌ Overhead over 100%: {overall_overhead_percent:+.1f}%")

        print(f"\n📊 Score: {goals_met}/{goals_total} performance goals met")

        # Per-query analysis
        print("\n🔍 Per-Query Impact:")
        print("-" * 40)

        for query, comp in self.results["comparison"].items():
            short_query = query[:40] + "..." if len(query) > 40 else query
            impact = (
                "🟢"
                if comp["overhead_ms"] < 20
                else "🟡"
                if comp["overhead_ms"] < 50
                else "🔴"
            )
            print(f"{impact} '{short_query}'")
            print(
                f"   Overhead: {comp['overhead_ms']:.2f}ms ({comp['overhead_percent']:+.1f}%)"
            )
            if comp["user_noticeable"]:
                print("   ⚠️ User-noticeable delay (>50ms)")

        # Verdict
        print("\n" + "=" * 60)
        print("🏁 VERDICT:")

        if goals_met >= 3:
            print("✅ XAI integration has ACCEPTABLE performance impact")
            print("   Users will not notice significant slowdown")
        elif goals_met >= 2:
            print("🟡 XAI integration has MODERATE performance impact")
            print("   Some optimization may be beneficial")
        else:
            print("🔴 XAI integration has SIGNIFICANT performance impact")
            print("   Optimization recommended before production")

        print("=" * 60)

    def _save_results(self):
        """Save detailed results to JSON"""
        output_file = Path(__file__).parent / "benchmark_results.json"

        # Convert to serializable format
        serializable_results = {}
        for category in self.results:
            serializable_results[category] = {}
            for query, stats in self.results[category].items():
                serializable_results[category][query] = stats

        with open(output_file, "w") as f:
            json.dump(serializable_results, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_file}")


async def main():
    """Run the benchmark"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_benchmarks()


if __name__ == "__main__":
    print("Starting XAI Performance Benchmark...")
    print("This will take 2-3 minutes to complete.\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
