#!/usr/bin/env python3
"""
Performance Visualization for Nix for Humanity

Generates charts and graphs from benchmark results.
"""

import json
import statistics
import sys
from pathlib import Path
from typing import Any

# Try to import plotting library
try:
    import matplotlib

    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Note: Install matplotlib for visual charts (pip install matplotlib)")


def load_benchmark_data(filepath: Path) -> dict[str, Any]:
    """Load benchmark results from JSON file"""
    with open(filepath) as f:
        return json.load(f)


def generate_text_chart(data: dict[str, Any]):
    """Generate ASCII text charts for terminal display"""
    print("\n" + "=" * 60)
    print("📈 Performance Comparison Chart (Text Version)")
    print("=" * 60)

    benchmarks = data.get("benchmarks", [])

    if not benchmarks:
        print("No benchmark data available")
        return

    # Find max values for scaling
    max_native = max(b["native_avg_ms"] for b in benchmarks)
    max_subprocess = max(b["subprocess_avg_ms"] for b in benchmarks)
    max_value = max(max_native, max_subprocess)

    # Create bar chart
    for bench in benchmarks:
        name = bench["name"]
        native_ms = bench["native_avg_ms"]
        subprocess_ms = bench["subprocess_avg_ms"]
        speedup = bench["speedup"]

        # Calculate bar lengths (max 40 chars)
        native_bar_len = int((native_ms / max_value) * 40) if max_value > 0 else 0
        subprocess_bar_len = (
            int((subprocess_ms / max_value) * 40) if max_value > 0 else 0
        )

        print(f"\n{name}:")
        print(f"  Native API: {'█' * max(1, native_bar_len)} {native_ms:.2f}ms")
        print(f"  Subprocess: {'█' * max(1, subprocess_bar_len)} {subprocess_ms:.2f}ms")
        print(f"  🚀 Speedup: {speedup:.1f}x")

    # Summary statistics
    print("\n" + "-" * 60)
    print("🏆 Overall Performance Summary")
    print("-" * 60)

    summary = data.get("summary", {})
    print(f"  Average speedup: {summary.get('average_speedup', 0):.1f}x")
    print(f"  Median speedup:  {summary.get('median_speedup', 0):.1f}x")
    print(f"  Maximum speedup: {summary.get('max_speedup', 0):.1f}x")
    print(f"  Minimum speedup: {summary.get('min_speedup', 0):.1f}x")
    print(f"  Time saved:      {summary.get('total_time_saved_ms', 0):.2f}ms")


def generate_comparison_table(data: dict[str, Any]):
    """Generate a comparison table"""
    print("\n" + "=" * 80)
    print("📊 Performance Comparison Table")
    print("=" * 80)

    # Header
    print(
        f"{'Operation':<25} {'Native (ms)':<12} {'Subprocess (ms)':<15} {'Speedup':<10}"
    )
    print("-" * 80)

    benchmarks = data.get("benchmarks", [])
    for bench in benchmarks:
        name = bench["name"][:24]  # Truncate if too long
        native = bench["native_avg_ms"]
        subprocess = bench["subprocess_avg_ms"]
        speedup = bench["speedup"]

        # Color code based on speedup
        speedup_str = f"{speedup:.1f}x"
        if speedup >= 100:
            speedup_str = f"🚀 {speedup_str}"
        elif speedup >= 10:
            speedup_str = f"⚡ {speedup_str}"
        elif speedup >= 2:
            speedup_str = f"✅ {speedup_str}"

        print(f"{name:<25} {native:<12.2f} {subprocess:<15.2f} {speedup_str:<10}")

    print("=" * 80)


def generate_matplotlib_charts(data: dict[str, Any], output_dir: Path):
    """Generate matplotlib charts if available"""
    if not HAS_MATPLOTLIB:
        return

    benchmarks = data.get("benchmarks", [])
    if not benchmarks:
        return

    # Prepare data
    names = [b["name"] for b in benchmarks]
    native_times = [b["native_avg_ms"] for b in benchmarks]
    subprocess_times = [b["subprocess_avg_ms"] for b in benchmarks]
    speedups = [b["speedup"] for b in benchmarks]

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(
        "Nix for Humanity Performance Benchmarks", fontsize=16, fontweight="bold"
    )

    # 1. Bar comparison
    ax1 = axes[0, 0]
    x = range(len(names))
    width = 0.35
    ax1.bar(
        [i - width / 2 for i in x],
        native_times,
        width,
        label="Native API",
        color="#2ecc71",
    )
    ax1.bar(
        [i + width / 2 for i in x],
        subprocess_times,
        width,
        label="Subprocess",
        color="#e74c3c",
    )
    ax1.set_xlabel("Operation")
    ax1.set_ylabel("Time (ms)")
    ax1.set_title("Execution Time Comparison")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=45, ha="right")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Speedup chart
    ax2 = axes[0, 1]
    colors = [
        "#2ecc71" if s >= 10 else "#3498db" if s >= 2 else "#95a5a6" for s in speedups
    ]
    ax2.bar(names, speedups, color=colors)
    ax2.set_xlabel("Operation")
    ax2.set_ylabel("Speedup Factor")
    ax2.set_title("Performance Speedup (x times faster)")
    ax2.set_xticklabels(names, rotation=45, ha="right")
    ax2.axhline(y=1, color="r", linestyle="--", alpha=0.5, label="No speedup")
    ax2.axhline(y=10, color="g", linestyle="--", alpha=0.5, label="10x speedup")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Log scale comparison
    ax3 = axes[1, 0]
    ax3.semilogy(
        names, native_times, "o-", label="Native API", color="#2ecc71", linewidth=2
    )
    ax3.semilogy(
        names, subprocess_times, "s-", label="Subprocess", color="#e74c3c", linewidth=2
    )
    ax3.set_xlabel("Operation")
    ax3.set_ylabel("Time (ms, log scale)")
    ax3.set_title("Performance Comparison (Log Scale)")
    ax3.set_xticklabels(names, rotation=45, ha="right")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # 4. Summary pie chart
    ax4 = axes[1, 1]
    summary = data.get("summary", {})
    speedup_categories = {
        "Ultra Fast (>100x)": sum(1 for s in speedups if s > 100),
        "Very Fast (10-100x)": sum(1 for s in speedups if 10 <= s <= 100),
        "Fast (2-10x)": sum(1 for s in speedups if 2 <= s < 10),
        "Similar (<2x)": sum(1 for s in speedups if s < 2),
    }

    # Only show categories with values
    categories = {k: v for k, v in speedup_categories.items() if v > 0}
    if categories:
        colors_pie = ["#2ecc71", "#3498db", "#f39c12", "#95a5a6"]
        ax4.pie(
            categories.values(),
            labels=categories.keys(),
            colors=colors_pie[: len(categories)],
            autopct="%1.0f%%",
            startangle=90,
        )
        ax4.set_title("Speedup Distribution")

    plt.tight_layout()

    # Save figure
    output_path = output_dir / "performance_charts.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\n🎨 Charts saved to: {output_path}")

    # Also save individual charts
    for i, (ax, title) in enumerate(
        zip([ax1, ax2, ax3], ["comparison", "speedup", "logscale"], strict=False)
    ):
        fig_single = plt.figure(figsize=(8, 6))
        ax_single = fig_single.add_subplot(111)

        # Copy the plot
        for line in ax.get_lines():
            ax_single.plot(
                line.get_xdata(),
                line.get_ydata(),
                label=line.get_label(),
                color=line.get_color(),
                marker=line.get_marker(),
                linestyle=line.get_linestyle(),
                linewidth=line.get_linewidth(),
            )

        ax_single.set_xlabel(ax.get_xlabel())
        ax_single.set_ylabel(ax.get_ylabel())
        ax_single.set_title(ax.get_title())
        ax_single.legend()
        ax_single.grid(True, alpha=0.3)

        output_path = output_dir / f"performance_{title}.png"
        fig_single.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig_single)


def analyze_performance_trends(data: dict[str, Any]):
    """Analyze and report performance trends"""
    print("\n" + "=" * 60)
    print("🔍 Performance Analysis & Insights")
    print("=" * 60)

    benchmarks = data.get("benchmarks", [])
    if not benchmarks:
        return

    speedups = [b["speedup"] for b in benchmarks]

    # Categorize performance
    ultra_fast = [b for b in benchmarks if b["speedup"] > 100]
    very_fast = [b for b in benchmarks if 10 <= b["speedup"] <= 100]
    fast = [b for b in benchmarks if 2 <= b["speedup"] < 10]
    similar = [b for b in benchmarks if b["speedup"] < 2]

    print("\n🎯 Performance Categories:")
    if ultra_fast:
        print("\n  🚀 Ultra Fast (>100x speedup):")
        for b in ultra_fast:
            print(f"    - {b['name']}: {b['speedup']:.1f}x faster")

    if very_fast:
        print("\n  ⚡ Very Fast (10-100x speedup):")
        for b in very_fast:
            print(f"    - {b['name']}: {b['speedup']:.1f}x faster")

    if fast:
        print("\n  ✅ Fast (2-10x speedup):")
        for b in fast:
            print(f"    - {b['name']}: {b['speedup']:.1f}x faster")

    if similar:
        print("\n  🔄 Similar performance (<2x):")
        for b in similar:
            print(f"    - {b['name']}: {b['speedup']:.1f}x")

    # Key insights
    print("\n💡 Key Insights:")

    avg_speedup = statistics.mean(speedups)
    if avg_speedup > 50:
        print(f"  🎆 Exceptional performance with {avg_speedup:.1f}x average speedup!")
    elif avg_speedup > 10:
        print(f"  🎉 Excellent performance with {avg_speedup:.1f}x average speedup!")
    elif avg_speedup > 2:
        print(f"  ✨ Good performance with {avg_speedup:.1f}x average speedup!")

    # Find bottlenecks
    slowest = min(benchmarks, key=lambda x: x["speedup"])
    if slowest["speedup"] < 2:
        print(
            f"  ⚠️  Optimization opportunity: {slowest['name']} ({slowest['speedup']:.1f}x)"
        )

    # Best performer
    fastest = max(benchmarks, key=lambda x: x["speedup"])
    print(
        f"  🏆 Best performer: {fastest['name']} with {fastest['speedup']:.1f}x speedup!"
    )

    # Total time saved
    total_saved = data.get("summary", {}).get("total_time_saved_ms", 0)
    if total_saved > 0:
        print(f"  ⏱️  Total time saved per operation set: {total_saved:.2f}ms")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize Nix for Humanity performance benchmarks"
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        default="benchmark_results.json",
        help="Input JSON file with benchmark results",
    )
    parser.add_argument(
        "--output-dir", type=str, default=".", help="Output directory for charts"
    )
    parser.add_argument(
        "--no-charts", action="store_true", help="Skip chart generation"
    )

    args = parser.parse_args()

    # Load data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found")
        print("Run benchmark_suite.py first to generate results")
        return 1

    data = load_benchmark_data(input_path)

    # Generate visualizations
    generate_text_chart(data)
    generate_comparison_table(data)
    analyze_performance_trends(data)

    # Generate matplotlib charts if available
    if not args.no_charts:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        generate_matplotlib_charts(data, output_dir)

    print("\n✅ Visualization complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
