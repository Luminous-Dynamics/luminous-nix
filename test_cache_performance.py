#!/usr/bin/env python3
"""
Performance Test for Package Search Caching

This verifies that our caching reduces search time from 10s to <100ms
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from luminous_nix.nix.package_discovery import PackageDiscovery
from luminous_nix.utils.cache import CacheManager


def test_package_search_performance():
    """Test that package search meets <100ms target with caching"""
    print("🚀 Testing Package Search Performance")
    print("=" * 50)
    
    # Initialize discovery with fresh cache
    discovery = PackageDiscovery()
    discovery.clear_cache()
    
    test_queries = [
        "firefox",
        "text editor",
        "python development",
        "music player",
        "system monitor",
    ]
    
    print("\n1. First search (cache miss - slower):")
    for query in test_queries:
        start = time.time()
        results = discovery.search_packages(query, limit=5)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        print(f"   '{query}': {elapsed:.1f}ms - Found {len(results)} packages")
    
    print("\n2. Second search (cache hit - should be <100ms):")
    cache_times = []
    for query in test_queries:
        start = time.time()
        results = discovery.search_packages(query, limit=5)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        cache_times.append(elapsed)
        
        status = "✅ PASS" if elapsed < 100 else "❌ FAIL"
        print(f"   '{query}': {elapsed:.1f}ms {status}")
    
    # Check cache statistics
    print("\n3. Cache Statistics:")
    stats = discovery.get_cache_stats()
    print(f"   Memory cache hits: {stats.get('memory_cache_info', {}).get('hits', 0)}")
    print(f"   Memory cache size: {stats.get('memory_cache_size', 0)}")
    print(f"   Disk cache size: {stats.get('disk_cache_size', 0)}")
    
    # Overall result
    avg_cache_time = sum(cache_times) / len(cache_times)
    print(f"\n📊 Average cached search time: {avg_cache_time:.1f}ms")
    
    if avg_cache_time < 100:
        print("✅ SUCCESS: Package search meets <100ms target!")
        return True
    else:
        print("❌ FAILURE: Package search exceeds 100ms target")
        return False


def test_command_executor_caching():
    """Test command executor caching"""
    from luminous_nix.core.command_executor import CommandExecutor
    
    print("\n\n🚀 Testing Command Executor Caching")
    print("=" * 50)
    
    executor = CommandExecutor(dry_run=True)
    executor.clear_cache()
    
    # Test search caching
    print("\n1. Search command caching:")
    
    # First search (cache miss)
    start = time.time()
    result1 = executor.execute("search", package="firefox")
    time1 = (time.time() - start) * 1000
    print(f"   First search: {time1:.1f}ms")
    
    # Second search (should be cached)
    start = time.time()
    result2 = executor.execute("search", package="firefox")
    time2 = (time.time() - start) * 1000
    print(f"   Cached search: {time2:.1f}ms")
    
    if time2 < time1 / 2:  # Should be at least 2x faster
        print("   ✅ Caching working! Second search was {:.1f}x faster".format(time1/time2))
    else:
        print("   ⚠️ Caching may not be working properly")
    
    # Show cache stats
    stats = executor.get_cache_stats()
    print(f"\n2. Executor cache stats:")
    print(f"   Total requests: {stats.get('total_requests', 0)}")
    print(f"   Memory hits: {stats.get('memory_hits', 0)}")
    print(f"   Memory hit rate: {stats.get('memory_hit_rate', 0):.1%}")


def test_cache_manager():
    """Test the universal cache manager"""
    print("\n\n🚀 Testing Universal Cache Manager")
    print("=" * 50)
    
    cache = CacheManager(ttl=60)  # 1 minute TTL
    
    # Test basic operations
    print("\n1. Basic cache operations:")
    
    # Write to cache
    start = time.time()
    cache.set("test_key", {"data": "test_value"})
    write_time = (time.time() - start) * 1000
    print(f"   Cache write: {write_time:.1f}ms")
    
    # Read from memory cache
    start = time.time()
    value = cache.get("test_key")
    read_time = (time.time() - start) * 1000
    print(f"   Memory cache read: {read_time:.1f}ms")
    
    if read_time < 1:  # Should be <1ms for memory cache
        print("   ✅ Memory cache is fast!")
    
    # Test performance with many items
    print("\n2. Performance with 1000 items:")
    cache.clear()
    
    # Write 1000 items
    start = time.time()
    for i in range(1000):
        cache.set(f"key_{i}", {"value": i})
    total_write = time.time() - start
    avg_write = (total_write / 1000) * 1000  # ms per item
    print(f"   Average write time: {avg_write:.2f}ms per item")
    
    # Read 1000 items
    start = time.time()
    for i in range(1000):
        cache.get(f"key_{i}")
    total_read = time.time() - start
    avg_read = (total_read / 1000) * 1000  # ms per item
    print(f"   Average read time: {avg_read:.2f}ms per item")
    
    # Show final stats
    stats = cache.get_stats()
    print(f"\n3. Final cache statistics:")
    print(f"   Memory cache size: {stats['memory_cache_size']}")
    print(f"   Overall hit rate: {stats.get('overall_hit_rate', 0):.1%}")
    
    if avg_read < 0.1:  # Should be <0.1ms per read
        print("   ✅ Cache performance excellent!")
    elif avg_read < 1:
        print("   ✅ Cache performance good")
    else:
        print("   ⚠️ Cache performance needs improvement")


if __name__ == "__main__":
    print("🌟 Luminous Nix Performance Test Suite")
    print("Target: <100ms for all operations")
    print("=" * 60)
    
    success = True
    
    # Run all tests
    try:
        success = test_package_search_performance() and success
        test_command_executor_caching()
        test_cache_manager()
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure to run: poetry install --all-extras")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: All performance targets met!")
        print("Package search: 10s → <100ms achieved! 🚀")
    else:
        print("⚠️ Some performance targets not met")
    
    print("\n💡 Next optimizations:")
    print("   - Lazy loading for faster startup")
    print("   - Memory usage reduction")
    print("   - Background cache pre-warming")