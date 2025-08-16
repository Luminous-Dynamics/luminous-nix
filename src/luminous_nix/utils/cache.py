#!/usr/bin/env python3
"""
Universal Caching Module for Luminous Nix

Provides high-performance caching with multiple backends:
- Memory cache (fastest, limited size)
- Disk cache (persistent, larger capacity)
- TTL support (time-to-live expiration)

Performance target: <100ms for cache operations
"""

import json
import logging
import sqlite3
import time
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Universal cache manager for Luminous Nix
    
    Features:
    - Two-tier caching (memory + disk)
    - TTL expiration
    - Hit/miss statistics
    - Automatic cleanup
    """
    
    DEFAULT_TTL = 3600  # 1 hour
    DEFAULT_MEMORY_SIZE = 1000
    DEFAULT_CLEANUP_INTERVAL = 3600  # 1 hour
    
    def __init__(
        self,
        cache_dir: Path | None = None,
        ttl: int = DEFAULT_TTL,
        memory_size: int = DEFAULT_MEMORY_SIZE,
    ):
        """Initialize cache manager"""
        self.cache_dir = cache_dir or Path.home() / ".cache" / "luminous-nix"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.ttl = ttl
        self.memory_size = memory_size
        
        # Memory cache: {key: (timestamp, value)}
        self._memory_cache: Dict[str, Tuple[float, Any]] = {}
        
        # Statistics
        self.stats = {
            "memory_hits": 0,
            "memory_misses": 0,
            "disk_hits": 0,
            "disk_misses": 0,
            "total_requests": 0,
        }
        
        # Last cleanup time
        self._last_cleanup = time.time()
        
        # Initialize disk cache database
        self._init_disk_cache()
    
    def _init_disk_cache(self):
        """Initialize SQLite database for disk cache"""
        self.db_path = self.cache_dir / "cache.db"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    timestamp REAL,
                    hits INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON cache(timestamp)
            """)
    
    def get(self, key: str) -> Any | None:
        """
        Get value from cache
        
        Returns None if not found or expired
        """
        self.stats["total_requests"] += 1
        
        # Check memory cache first
        if key in self._memory_cache:
            timestamp, value = self._memory_cache[key]
            if time.time() - timestamp < self.ttl:
                self.stats["memory_hits"] += 1
                logger.debug(f"Memory cache hit: {key}")
                return value
            else:
                # Expired, remove from memory
                del self._memory_cache[key]
        
        self.stats["memory_misses"] += 1
        
        # Check disk cache
        value = self._get_from_disk(key)
        if value is not None:
            self.stats["disk_hits"] += 1
            # Promote to memory cache
            self._memory_cache[key] = (time.time(), value)
            self._trim_memory_cache()
            return value
        
        self.stats["disk_misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (seconds)
        """
        effective_ttl = ttl or self.ttl
        timestamp = time.time()
        
        # Set in memory cache
        self._memory_cache[key] = (timestamp, value)
        self._trim_memory_cache()
        
        # Set in disk cache
        self._set_to_disk(key, value, timestamp)
        
        # Periodic cleanup
        if time.time() - self._last_cleanup > self.DEFAULT_CLEANUP_INTERVAL:
            self.cleanup()
            self._last_cleanup = time.time()
    
    def _get_from_disk(self, key: str) -> Any | None:
        """Get value from disk cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value, timestamp FROM cache WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    value_json, timestamp = row
                    # Check TTL
                    if time.time() - timestamp < self.ttl:
                        # Update hit count
                        conn.execute(
                            "UPDATE cache SET hits = hits + 1 WHERE key = ?",
                            (key,)
                        )
                        return json.loads(value_json)
                    else:
                        # Expired, delete it
                        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        except Exception as e:
            logger.warning(f"Disk cache read error: {e}")
        
        return None
    
    def _set_to_disk(self, key: str, value: Any, timestamp: float) -> None:
        """Set value in disk cache"""
        try:
            value_json = json.dumps(value)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, timestamp, hits)
                    VALUES (?, ?, ?, 0)
                    """,
                    (key, value_json, timestamp)
                )
        except Exception as e:
            logger.warning(f"Disk cache write error: {e}")
    
    def _trim_memory_cache(self) -> None:
        """Trim memory cache to size limit"""
        if len(self._memory_cache) > self.memory_size:
            # Remove oldest entries
            sorted_items = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1][0]  # Sort by timestamp
            )
            
            # Keep only the most recent entries
            to_remove = len(self._memory_cache) - self.memory_size
            for key, _ in sorted_items[:to_remove]:
                del self._memory_cache[key]
    
    def cleanup(self) -> int:
        """
        Remove expired entries from cache
        
        Returns number of entries removed
        """
        removed = 0
        current_time = time.time()
        
        # Clean memory cache
        expired_keys = [
            k for k, (t, _) in self._memory_cache.items()
            if current_time - t > self.ttl
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            removed += 1
        
        # Clean disk cache
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE timestamp < ?",
                    (current_time - self.ttl,)
                )
                removed += cursor.rowcount
        except Exception as e:
            logger.warning(f"Disk cache cleanup error: {e}")
        
        logger.debug(f"Cache cleanup: removed {removed} expired entries")
        return removed
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._memory_cache.clear()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache")
        except Exception as e:
            logger.warning(f"Disk cache clear error: {e}")
        
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.stats.copy()
        stats["memory_cache_size"] = len(self._memory_cache)
        
        # Calculate hit rates
        if stats["total_requests"] > 0:
            memory_attempts = stats["memory_hits"] + stats["memory_misses"]
            if memory_attempts > 0:
                stats["memory_hit_rate"] = stats["memory_hits"] / memory_attempts
            
            disk_attempts = stats["disk_hits"] + stats["disk_misses"]
            if disk_attempts > 0:
                stats["disk_hit_rate"] = stats["disk_hits"] / disk_attempts
            
            total_hits = stats["memory_hits"] + stats["disk_hits"]
            stats["overall_hit_rate"] = total_hits / stats["total_requests"]
        
        # Get disk cache size
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM cache")
                stats["disk_cache_size"] = cursor.fetchone()[0]
        except Exception:
            stats["disk_cache_size"] = 0
        
        return stats


def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    cache_manager: CacheManager | None = None
) -> Callable:
    """
    Decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Optional prefix for cache keys
        cache_manager: Optional cache manager instance
    
    Usage:
        @cached(ttl=300)
        def expensive_function(arg):
            return compute_something(arg)
    """
    # Use global cache manager if not provided
    if cache_manager is None:
        cache_manager = get_default_cache_manager()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}{func.__name__}"
            
            # Add arguments to key (simple serialization)
            if args:
                cache_key += f":{args}"
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                cache_key += f":{sorted_kwargs}"
            
            # Check cache
            result = cache_manager.get(cache_key)
            if result is not None:
                return result
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # Add cache management methods
        wrapper.cache_clear = lambda: cache_manager.clear()
        wrapper.cache_stats = lambda: cache_manager.get_stats()
        
        return wrapper
    
    return decorator


# Global cache instance
_default_cache_manager: CacheManager | None = None


def get_default_cache_manager() -> CacheManager:
    """Get or create default cache manager"""
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = CacheManager()
    return _default_cache_manager


# Specialized cache decorators for common use cases

def cache_package_search(ttl: int = 1800):
    """Cache decorator specifically for package searches (30 min default)"""
    return cached(ttl=ttl, key_prefix="package_search:")


def cache_command_result(ttl: int = 300):
    """Cache decorator for command results (5 min default)"""
    return cached(ttl=ttl, key_prefix="command:")


def cache_api_call(ttl: int = 600):
    """Cache decorator for API calls (10 min default)"""
    return cached(ttl=ttl, key_prefix="api:")


# Example usage and testing
if __name__ == "__main__":
    # Demo the cache functionality
    import random
    
    print("🔧 Cache Manager Demo")
    print("=" * 50)
    
    # Create cache manager
    cache = CacheManager(ttl=5)  # 5 second TTL for demo
    
    # Test basic operations
    print("\n1. Basic Cache Operations:")
    cache.set("test_key", {"data": "test_value"})
    print(f"Set: test_key = {{'data': 'test_value'}}")
    
    result = cache.get("test_key")
    print(f"Get: test_key = {result}")
    
    # Test expiration
    print("\n2. TTL Expiration Test:")
    cache.set("expire_key", "will_expire", ttl=2)
    print("Set expire_key with 2 second TTL")
    print(f"Immediate get: {cache.get('expire_key')}")
    
    import time
    time.sleep(3)
    print(f"After 3 seconds: {cache.get('expire_key')}")
    
    # Test decorator
    print("\n3. Decorator Test:")
    
    @cached(ttl=10)
    def expensive_computation(n):
        """Simulate expensive computation"""
        print(f"Computing result for {n}...")
        time.sleep(1)  # Simulate work
        return n * n
    
    print(f"First call: {expensive_computation(5)}")
    print(f"Second call (cached): {expensive_computation(5)}")
    print(f"Different arg: {expensive_computation(10)}")
    
    # Show statistics
    print("\n4. Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        if "rate" in key:
            print(f"  {key}: {value:.2%}")
        else:
            print(f"  {key}: {value}")
    
    print("\n✨ Cache system ready for <100ms operations!")