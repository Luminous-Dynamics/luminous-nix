"""Redis caching layer for Nix for Humanity."""

import hashlib
import json
import logging
import os
import pickle
from contextlib import contextmanager
from datetime import timedelta
from functools import wraps
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, Union

import redis
from redis.exceptions import ConnectionError, RedisError

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default cache TTLs (in seconds)
PACKAGE_CACHE_TTL = 3600 * 24  # 24 hours
COMMAND_CACHE_TTL = 3600  # 1 hour
LEARNING_CACHE_TTL = 3600 * 24 * 7  # 7 days
DEFAULT_TTL = 3600  # 1 hour


class RedisCache:
    """Redis cache manager for Nix for Humanity."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        socket_timeout: int = 5,
        max_connections: int = 50,
    ):
        """Initialize Redis cache connection.
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password if required
            socket_timeout: Socket timeout in seconds
            max_connections: Maximum number of connections in pool
        """
        self.redis_url = os.getenv("REDIS_URL", f"redis://{host}:{port}/{db}")
        
        try:
            self.pool = redis.ConnectionPool.from_url(
                self.redis_url,
                password=password,
                socket_timeout=socket_timeout,
                max_connections=max_connections,
                decode_responses=False,  # We'll handle encoding/decoding
            )
            self.client = redis.Redis(connection_pool=self.pool)
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info(f"Redis cache connected: {self.redis_url}")
        except (ConnectionError, RedisError) as e:
            logger.warning(f"Redis cache unavailable: {e}. Running without cache.")
            self.client = None
            self.enabled = False

    @contextmanager
    def _get_client(self) -> Generator[Optional[redis.Redis], None, None]:
        """Context manager for Redis client with error handling."""
        if not self.enabled:
            yield None
            return
            
        try:
            yield self.client
        except (ConnectionError, RedisError) as e:
            logger.error(f"Redis error: {e}")
            self.enabled = False
            yield None

    def _make_key(self, namespace: str, key: str) -> str:
        """Create a namespaced cache key.
        
        Args:
            namespace: Cache namespace (e.g., 'packages', 'commands')
            key: Unique key within namespace
            
        Returns:
            Formatted cache key
        """
        return f"nix_humanity:{namespace}:{key}"

    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized bytes
        """
        try:
            # Try JSON first (more portable)
            return json.dumps(value).encode("utf-8")
        except (TypeError, ValueError):
            # Fall back to pickle for complex objects
            return pickle.dumps(value)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage.
        
        Args:
            data: Serialized bytes
            
        Returns:
            Deserialized value
        """
        if not data:
            return None
            
        try:
            # Try JSON first
            return json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        with self._get_client() as client:
            if not client:
                return None
                
            cache_key = self._make_key(namespace, key)
            try:
                data = client.get(cache_key)
                if data:
                    return self._deserialize(data)
            except Exception as e:
                logger.error(f"Cache get error: {e}")
        return None

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for no expiration)
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_client() as client:
            if not client:
                return False
                
            cache_key = self._make_key(namespace, key)
            try:
                data = self._serialize(value)
                if ttl:
                    client.setex(cache_key, ttl, data)
                else:
                    client.set(cache_key, data)
                return True
            except Exception as e:
                logger.error(f"Cache set error: {e}")
        return False

    def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        with self._get_client() as client:
            if not client:
                return False
                
            cache_key = self._make_key(namespace, key)
            try:
                return bool(client.delete(cache_key))
            except Exception as e:
                logger.error(f"Cache delete error: {e}")
        return False

    def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in a namespace.
        
        Args:
            namespace: Cache namespace to clear
            
        Returns:
            Number of keys deleted
        """
        with self._get_client() as client:
            if not client:
                return 0
                
            pattern = self._make_key(namespace, "*")
            try:
                keys = client.keys(pattern)
                if keys:
                    return client.delete(*keys)
            except Exception as e:
                logger.error(f"Cache clear error: {e}")
        return 0

    def get_or_set(
        self,
        namespace: str,
        key: str,
        factory: Callable[[], T],
        ttl: Optional[int] = None,
    ) -> T:
        """Get value from cache or compute and cache it.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            factory: Function to compute value if not cached
            ttl: Time to live in seconds
            
        Returns:
            Cached or computed value
        """
        # Try to get from cache
        value = self.get(namespace, key)
        if value is not None:
            return value
            
        # Compute value
        value = factory()
        
        # Cache it
        self.set(namespace, key, value, ttl)
        
        return value

    def increment(self, namespace: str, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache.
        
        Args:
            namespace: Cache namespace
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if failed
        """
        with self._get_client() as client:
            if not client:
                return None
                
            cache_key = self._make_key(namespace, key)
            try:
                return client.incr(cache_key, amount)
            except Exception as e:
                logger.error(f"Cache increment error: {e}")
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary of cache statistics
        """
        stats = {
            "enabled": self.enabled,
            "connected": False,
            "keys": 0,
            "memory_used": 0,
        }
        
        with self._get_client() as client:
            if client:
                try:
                    info = client.info()
                    stats.update({
                        "connected": True,
                        "keys": client.dbsize(),
                        "memory_used": info.get("used_memory", 0),
                        "hits": info.get("keyspace_hits", 0),
                        "misses": info.get("keyspace_misses", 0),
                    })
                except Exception as e:
                    logger.error(f"Error getting cache stats: {e}")
                    
        return stats


def cached(
    namespace: str,
    ttl: Optional[int] = DEFAULT_TTL,
    key_func: Optional[Callable[..., str]] = None,
) -> Callable:
    """Decorator for caching function results.
    
    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        key_func: Function to generate cache key from arguments
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Create key from function name and arguments
                key_parts = [func.__name__]
                if args:
                    key_parts.append(str(args))
                if kwargs:
                    key_parts.append(str(sorted(kwargs.items())))
                cache_key = hashlib.md5(
                    ":".join(key_parts).encode()
                ).hexdigest()
            
            # Get cache instance (assuming it's available globally or via import)
            from nix_for_humanity.cache import cache_instance
            
            if cache_instance and cache_instance.enabled:
                # Try to get from cache
                result = cache_instance.get(namespace, cache_key)
                if result is not None:
                    logger.debug(f"Cache hit: {namespace}:{cache_key}")
                    return result
                
                # Compute result
                result = func(*args, **kwargs)
                
                # Cache it
                cache_instance.set(namespace, cache_key, result, ttl)
                logger.debug(f"Cache set: {namespace}:{cache_key}")
                
                return result
            else:
                # No cache, just run function
                return func(*args, **kwargs)
                
        return wrapper
    return decorator


# Global cache instance (initialized on first import)
cache_instance: Optional[RedisCache] = None


def initialize_cache(**kwargs) -> RedisCache:
    """Initialize global cache instance.
    
    Args:
        **kwargs: Arguments to pass to RedisCache constructor
        
    Returns:
        Initialized cache instance
    """
    global cache_instance
    cache_instance = RedisCache(**kwargs)
    return cache_instance