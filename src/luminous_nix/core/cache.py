"""
Simple caching system for Nix for Humanity

Caches common queries and results to improve performance.
"""

import hashlib
import json
import logging
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple file-based cache for query results

    This provides:
    - Fast lookup for repeated queries
    - TTL-based expiration
    - Memory-efficient operation
    """

    def __init__(self, cache_dir: Path | None = None, ttl_seconds: int = 3600):
        """
        Initialize cache

        Args:
            cache_dir: Directory for cache files (default: ~/.cache/luminous-nix)
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache_dir = cache_dir or (
            Path.home() / ".cache" / "nix-humanity" / "queries"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(seconds=ttl_seconds)

        # In-memory cache for this session (even faster)
        self._memory_cache: dict[str, tuple[Any, float]] = {}

    def _get_cache_key(self, query: str, context: dict | None = None) -> str:
        """Generate a cache key from query and context"""
        # Create a unique key from query and relevant context
        key_data = {
            "query": query.lower().strip(),
            "dry_run": context.get("dry_run", True) if context else True,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def get(self, query: str, context: dict | None = None) -> Any | None:
        """
        Get cached result if available and not expired

        Args:
            query: The query to look up
            context: Optional context dict

        Returns:
            Cached result or None if not found/expired
        """
        cache_key = self._get_cache_key(query, context)

        # Check memory cache first (fastest)
        if cache_key in self._memory_cache:
            result, timestamp = self._memory_cache[cache_key]
            if time.time() - timestamp < self.ttl.total_seconds():
                logger.debug(f"Cache hit (memory): {query[:50]}...")
                return result
            # Expired, remove from memory
            del self._memory_cache[cache_key]

        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
                timestamp = data.get("timestamp", 0)

                # Check if expired
                if time.time() - timestamp < self.ttl.total_seconds():
                    result = data.get("result")
                    # Store in memory for next time
                    self._memory_cache[cache_key] = (result, timestamp)
                    logger.debug(f"Cache hit (file): {query[:50]}...")
                    return result
                # Expired, delete file
                cache_file.unlink()
                logger.debug(f"Cache expired: {query[:50]}...")

            except (json.JSONDecodeError, KeyError) as e:
                logger.debug(f"Cache read error: {e}")
                cache_file.unlink()  # Remove corrupted cache

        logger.debug(f"Cache miss: {query[:50]}...")
        return None

    def set(self, query: str, result: Any, context: dict | None = None) -> None:
        """
        Store result in cache

        Args:
            query: The query that was executed
            result: The result to cache
            context: Optional context dict
        """
        cache_key = self._get_cache_key(query, context)
        timestamp = time.time()

        # Store in memory cache
        self._memory_cache[cache_key] = (result, timestamp)

        # Store in file cache
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            cache_data = {
                "query": query,
                "result": result,
                "timestamp": timestamp,
                "context": context,
            }
            cache_file.write_text(json.dumps(cache_data, indent=2))
            logger.debug(f"Cached result: {query[:50]}...")
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")

    def clear(self) -> None:
        """Clear all cache entries"""
        # Clear memory cache
        self._memory_cache.clear()

        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file: {e}")

        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries

        Returns:
            Number of entries removed
        """
        removed = 0
        current_time = time.time()

        # Clean memory cache
        expired_keys = [
            key
            for key, (_, timestamp) in self._memory_cache.items()
            if current_time - timestamp > self.ttl.total_seconds()
        ]
        for key in expired_keys:
            del self._memory_cache[key]
            removed += 1

        # Clean file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                data = json.loads(cache_file.read_text())
                timestamp = data.get("timestamp", 0)
                if current_time - timestamp > self.ttl.total_seconds():
                    cache_file.unlink()
                    removed += 1
            except Exception:
                # Remove corrupted cache files
                cache_file.unlink()
                removed += 1

        if removed > 0:
            logger.debug(f"Cleaned up {removed} expired cache entries")

        return removed


class SmartCache(SimpleCache):
    """
    Smarter caching with selective caching based on query type
    """

    # Queries that should always be cached
    CACHEABLE_INTENTS = {
        "search",  # Package searches rarely change
        "generate_config",  # Config generation is deterministic
        "query",  # Information queries don't change
        "translate_error",  # Error translations are stable
    }

    # Queries that should never be cached
    NON_CACHEABLE_INTENTS = {
        "install",  # System state changes
        "remove",  # System state changes
        "update",  # System state changes
        "rollback",  # System state changes
    }

    def should_cache(self, intent_type: str) -> bool:
        """
        Determine if a query result should be cached

        Args:
            intent_type: The type of intent

        Returns:
            True if should cache, False otherwise
        """
        # Explicitly cacheable
        if intent_type in self.CACHEABLE_INTENTS:
            return True

        # Explicitly non-cacheable
        if intent_type in self.NON_CACHEABLE_INTENTS:
            return False

        # Default: cache read-only operations
        return True

    def get_ttl_for_intent(self, intent_type: str) -> int:
        """
        Get appropriate TTL for different intent types

        Args:
            intent_type: The type of intent

        Returns:
            TTL in seconds
        """
        ttl_map = {
            "search": 7200,  # 2 hours - package list changes slowly
            "generate_config": 86400,  # 24 hours - configs are stable
            "query": 3600,  # 1 hour - general info
            "translate_error": 86400,  # 24 hours - errors don't change
        }

        return ttl_map.get(intent_type, 3600)  # Default 1 hour


# Global cache instance
_cache: SmartCache | None = None


def get_cache() -> SmartCache:
    """Get the global cache instance"""
    global _cache
    if _cache is None:
        _cache = SmartCache()
    return _cache
