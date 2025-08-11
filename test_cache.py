#!/usr/bin/env python3
"""
Test caching performance
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core.unified_backend import NixForHumanityBackend


async def test_caching():
    print("Testing caching system...")
    print("=" * 60)

    backend = NixForHumanityBackend({"caching": True})

    # Test 1: First search (will be cached)
    print("\n1. First search query (no cache)")
    start = time.perf_counter()
    result1 = await backend.execute("search markdown editor")
    time1 = time.perf_counter() - start
    print(f"   Time: {time1:.3f}s")
    print(f"   Success: {result1.success}")
    print(f"   Cached: {result1.metadata.get('cached', False)}")

    # Test 2: Same search (should be cached)
    print("\n2. Same search query (should use cache)")
    start = time.perf_counter()
    result2 = await backend.execute("search markdown editor")
    time2 = time.perf_counter() - start
    print(f"   Time: {time2:.3f}s")
    print(f"   Success: {result2.success}")
    print(f"   Cached: {result2.metadata.get('cached', False)}")

    # Test 3: Different search (no cache)
    print("\n3. Different search query (no cache)")
    start = time.perf_counter()
    result3 = await backend.execute("search text editor")
    time3 = time.perf_counter() - start
    print(f"   Time: {time3:.3f}s")
    print(f"   Success: {result3.success}")
    print(f"   Cached: {result3.metadata.get('cached', False)}")

    # Test 4: Config generation (should be cached)
    print("\n4. Config generation (cacheable)")
    start = time.perf_counter()
    result4 = await backend.execute("web server with nginx")
    time4 = time.perf_counter() - start
    print(f"   Time: {time4:.3f}s")

    print("\n5. Same config (should use cache)")
    start = time.perf_counter()
    result5 = await backend.execute("web server with nginx")
    time5 = time.perf_counter() - start
    print(f"   Time: {time5:.3f}s")
    print(f"   Cached: {result5.metadata.get('cached', False)}")

    # Summary
    print("\n" + "=" * 60)
    print("Performance Summary:")
    print("-" * 40)

    if time2 < time1 * 0.1:  # Cached should be 10x faster
        speedup = time1 / time2 if time2 > 0 else float("inf")
        print(f"✅ Cache working! {speedup:.1f}x speedup")
    else:
        print("⚠️  Cache may not be working properly")

    print("\nTiming breakdown:")
    print(f"  First search: {time1:.3f}s")
    print(f"  Cached search: {time2:.3f}s")
    print(f"  Speedup: {time1/time2 if time2 > 0 else 0:.1f}x")

    # Cleanup
    if backend.cache:
        backend.cache.clear()
        print("\n✨ Cache cleared")


if __name__ == "__main__":
    asyncio.run(test_caching())
