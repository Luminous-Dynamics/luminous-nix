#!/usr/bin/env python3
"""
Comprehensive performance analysis
"""

import os
import subprocess
import time
from statistics import mean, stdev


def measure_execution(command, runs=5):
    """Measure execution time of a command"""
    times = []

    for i in range(runs):
        start = time.perf_counter()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        "mean": mean(times),
        "stdev": stdev(times) if len(times) > 1 else 0,
        "min": min(times),
        "max": max(times),
        "times": times,
    }


def main():
    print("🚀 Performance Analysis - Nix for Humanity")
    print("=" * 60)

    os.chdir("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")

    # Test 1: Full CLI execution
    print("\n1. Full CLI Execution (5 runs)")
    print("-" * 40)

    full_cli = measure_execution(
        "python3 bin/ask-nix 'install firefox' > /dev/null 2>&1"
    )
    print(f"Average: {full_cli['mean']:.3f}s ± {full_cli['stdev']:.3f}s")
    print(f"Min: {full_cli['min']:.3f}s, Max: {full_cli['max']:.3f}s")

    # Test 2: Just imports
    print("\n2. Import Time Only")
    print("-" * 40)

    import_only = measure_execution(
        "python3 -c 'import sys; sys.path.insert(0, \"src\"); from luminous_nix.core.unified_backend import NixForHumanityBackend'",
        runs=5,
    )
    print(f"Average: {import_only['mean']:.3f}s ± {import_only['stdev']:.3f}s")

    # Test 3: Python startup
    print("\n3. Python Startup Overhead")
    print("-" * 40)

    python_startup = measure_execution("python3 -c 'pass'", runs=10)
    print(f"Average: {python_startup['mean']:.3f}s")

    # Test 4: Different operations
    print("\n4. Operation Breakdown")
    print("-" * 40)

    operations = [
        ("Help", "python3 bin/ask-nix --help > /dev/null 2>&1"),
        ("Simple query", "python3 bin/ask-nix 'test' 2>&1 | head -1 > /dev/null"),
        ("Config generation", "python3 bin/ask-nix 'web server' > /dev/null 2>&1"),
    ]

    for name, cmd in operations:
        result = measure_execution(cmd, runs=3)
        print(f"{name}: {result['mean']:.3f}s")

    # Analysis
    print("\n" + "=" * 60)
    print("Performance Breakdown:")
    print("-" * 40)

    actual_work = full_cli["mean"] - import_only["mean"]
    import_overhead = import_only["mean"] - python_startup["mean"]

    print(f"Total time: {full_cli['mean']:.3f}s")
    print(
        f"  Python startup: {python_startup['mean']:.3f}s ({python_startup['mean']/full_cli['mean']*100:.1f}%)"
    )
    print(
        f"  Import overhead: {import_overhead:.3f}s ({import_overhead/full_cli['mean']*100:.1f}%)"
    )
    print(
        f"  Actual work: {actual_work:.3f}s ({actual_work/full_cli['mean']*100:.1f}%)"
    )

    # Bottleneck identification
    print("\n" + "=" * 60)
    print("Bottleneck Analysis:")
    print("-" * 40)

    if import_overhead > 0.5:
        print("❗ Major bottleneck: Import overhead")
        print("   Solution: Implement lazy imports")

    if python_startup["mean"] > 0.1:
        print("⚠️  Python startup is slow")
        print("   Consider: Compiled executable or daemon mode")

    if actual_work > 1.0:
        print("⚠️  Processing is slow")
        print("   Solution: Optimize algorithms, add caching")

    # Recommendations
    print("\n" + "=" * 60)
    print("Optimization Recommendations:")
    print("-" * 40)

    target_time = 1.0
    current_time = full_cli["mean"]

    if current_time > target_time:
        reduction_needed = current_time - target_time
        print(f"Need to reduce time by {reduction_needed:.3f}s to meet <1s target")
        print("\nPriority optimizations:")
        print("1. Lazy load nixos-rebuild module (saves ~0.5s)")
        print("2. Defer asyncio import until needed (saves ~0.05s)")
        print("3. Cache initialized backend between calls")
        print("4. Use --skip-imports flag for common operations")
    else:
        print(f"✅ Already meeting <1s target! ({current_time:.3f}s)")


if __name__ == "__main__":
    main()
