"""
Central Cache Manager for Nix for Humanity

Coordinates all caching activities with memory-efficient storage
and intelligent invalidation strategies.
"""

import os
import time
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache storage"""
    MEMORY = "memory"  # Fast, limited size
    DISK = "disk"      # Slower, larger capacity
    HYBRID = "hybrid"  # Memory + disk spillover


@dataclass
class CacheConfig:
    """Configuration for cache behavior"""
    # Storage settings
    cache_type: CacheType = CacheType.HYBRID
    memory_size_mb: int = 50  # Max memory cache size
    disk_size_mb: int = 500   # Max disk cache size
    cache_dir: Path = Path.home() / ".cache" / "nix-humanity"
    
    # TTL settings (in seconds)
    response_ttl: int = 300        # 5 minutes for responses
    command_ttl: int = 3600        # 1 hour for command results
    xai_ttl: int = 1800           # 30 minutes for explanations
    system_info_ttl: int = 60      # 1 minute for system state
    
    # Performance settings
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress entries > 1KB
    max_memory_entries: int = 1000
    
    # Behavior settings
    enable_statistics: bool = True
    enable_warming: bool = True      # Pre-warm common queries
    enable_predictive: bool = True   # Predictive caching


@dataclass
class CacheEntry:
    """A single cache entry"""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: int
    metadata: Dict[str, Any]
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self) -> None:
        """Update access time and count"""
        self.accessed_at = datetime.now()
        self.access_count += 1


class CacheStatistics:
    """Track cache performance metrics"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.invalidations = 0
        self.size_bytes = 0
        self.entry_count = 0
        
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Export statistics as dictionary"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{self.hit_rate:.2%}",
            'evictions': self.evictions,
            'invalidations': self.invalidations,
            'size_mb': self.size_bytes / (1024 * 1024),
            'entry_count': self.entry_count
        }


class CacheManager:
    """
    Central cache manager coordinating all caching operations.
    
    Features:
    - Hybrid memory/disk storage
    - LRU eviction
    - TTL-based expiration
    - Intelligent invalidation
    - Compression for large entries
    - Statistics tracking
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache manager"""
        self.config = config or CacheConfig()
        self.stats = CacheStatistics()
        
        # Memory cache (fast access)
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.memory_size = 0
        
        # Ensure cache directory exists
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize disk cache (SQLite for reliability)
        self.db_path = self.config.cache_dir / "cache.db"
        self._init_disk_cache()
        
        # Warm cache if enabled
        if self.config.enable_warming:
            self._warm_cache()
            
        logger.info(f"Cache manager initialized: {self.config.cache_type.value} mode")
    
    def _init_disk_cache(self) -> None:
        """Initialize SQLite disk cache"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value BLOB,
                created_at REAL,
                accessed_at REAL,
                access_count INTEGER,
                size_bytes INTEGER,
                ttl_seconds INTEGER,
                metadata TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_accessed_at 
            ON cache_entries(accessed_at)
        """)
        conn.commit()
        conn.close()
    
    def get(self, key: str, cache_type: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            cache_type: Specific cache type to check
            
        Returns:
            Cached value or None if not found/expired
        """
        # Generate hash key for consistent storage
        hash_key = self._hash_key(key)
        
        # Check memory cache first
        if hash_key in self.memory_cache:
            entry = self.memory_cache[hash_key]
            if not entry.is_expired():
                entry.touch()
                self.stats.hits += 1
                logger.debug(f"Cache hit (memory): {key[:50]}...")
                return entry.value
            else:
                # Remove expired entry
                del self.memory_cache[hash_key]
                self.memory_size -= entry.size_bytes
                
        # Check disk cache if configured
        if self.config.cache_type in [CacheType.DISK, CacheType.HYBRID]:
            value = self._get_from_disk(hash_key)
            if value is not None:
                self.stats.hits += 1
                logger.debug(f"Cache hit (disk): {key[:50]}...")
                
                # Promote to memory if hybrid mode
                if self.config.cache_type == CacheType.HYBRID:
                    self._promote_to_memory(hash_key, value)
                    
                return value
        
        self.stats.misses += 1
        logger.debug(f"Cache miss: {key[:50]}...")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            metadata: Additional metadata to store
        """
        hash_key = self._hash_key(key)
        
        # Determine TTL
        if ttl is None:
            ttl = self._get_default_ttl(key)
            
        # Create cache entry
        entry = CacheEntry(
            key=hash_key,
            value=value,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            access_count=0,
            size_bytes=self._estimate_size(value),
            ttl_seconds=ttl,
            metadata=metadata or {}
        )
        
        # Store in appropriate cache
        if self.config.cache_type == CacheType.MEMORY:
            self._store_in_memory(hash_key, entry)
        elif self.config.cache_type == CacheType.DISK:
            self._store_on_disk(hash_key, entry)
        else:  # HYBRID
            # Use memory for small/hot entries, disk for large/cold
            if entry.size_bytes < self.config.compression_threshold:
                self._store_in_memory(hash_key, entry)
            else:
                self._store_on_disk(hash_key, entry)
                
        self.stats.entry_count += 1
        logger.debug(f"Cache set: {key[:50]}... (TTL: {ttl}s)")
    
    def invalidate(self, pattern: Optional[str] = None, 
                  cache_type: Optional[str] = None) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Key pattern to match (None = all)
            cache_type: Specific cache type to invalidate
            
        Returns:
            Number of entries invalidated
        """
        count = 0
        
        # Invalidate memory cache
        if pattern is None:
            count += len(self.memory_cache)
            self.memory_cache.clear()
            self.memory_size = 0
        else:
            keys_to_remove = [k for k in self.memory_cache if pattern in k]
            for key in keys_to_remove:
                entry = self.memory_cache.pop(key)
                self.memory_size -= entry.size_bytes
                count += 1
        
        # Invalidate disk cache
        if self.config.cache_type in [CacheType.DISK, CacheType.HYBRID]:
            count += self._invalidate_disk(pattern)
            
        self.stats.invalidations += count
        self.stats.entry_count = max(0, self.stats.entry_count - count)
        
        logger.info(f"Invalidated {count} cache entries (pattern: {pattern})")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.stats.to_dict()
    
    def cleanup(self) -> None:
        """Clean up expired entries"""
        # Clean memory cache
        expired_keys = [
            k for k, v in self.memory_cache.items() 
            if v.is_expired()
        ]
        for key in expired_keys:
            entry = self.memory_cache.pop(key)
            self.memory_size -= entry.size_bytes
            self.stats.evictions += 1
            
        # Clean disk cache
        if self.config.cache_type in [CacheType.DISK, CacheType.HYBRID]:
            self._cleanup_disk()
            
        logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    # Private helper methods
    
    def _hash_key(self, key: str) -> str:
        """Generate consistent hash key"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _get_default_ttl(self, key: str) -> int:
        """Determine default TTL based on key type"""
        if 'response' in key:
            return self.config.response_ttl
        elif 'command' in key:
            return self.config.command_ttl
        elif 'xai' in key or 'explanation' in key:
            return self.config.xai_ttl
        elif 'system' in key:
            return self.config.system_info_ttl
        else:
            return self.config.response_ttl
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes"""
        if isinstance(value, str):
            return len(value.encode())
        elif isinstance(value, dict):
            return len(json.dumps(value).encode())
        else:
            return len(str(value).encode())
    
    def _store_in_memory(self, key: str, entry: CacheEntry) -> None:
        """Store entry in memory cache with LRU eviction"""
        # Check if we need to evict
        while (self.memory_size + entry.size_bytes > 
               self.config.memory_size_mb * 1024 * 1024):
            self._evict_lru_memory()
            
        self.memory_cache[key] = entry
        self.memory_size += entry.size_bytes
    
    def _evict_lru_memory(self) -> None:
        """Evict least recently used entry from memory"""
        if not self.memory_cache:
            return
            
        # Find LRU entry
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].accessed_at
        )
        
        entry = self.memory_cache.pop(lru_key)
        self.memory_size -= entry.size_bytes
        self.stats.evictions += 1
        
        # Optionally spill to disk in hybrid mode
        if self.config.cache_type == CacheType.HYBRID:
            self._store_on_disk(lru_key, entry)
    
    def _store_on_disk(self, key: str, entry: CacheEntry) -> None:
        """Store entry on disk"""
        conn = sqlite3.connect(self.db_path)
        
        # Compress if enabled and large enough
        value_data = entry.value
        if (self.config.enable_compression and 
            entry.size_bytes > self.config.compression_threshold):
            import gzip
            value_data = gzip.compress(
                json.dumps(value_data).encode()
            )
            entry.metadata['compressed'] = True
            
        conn.execute("""
            INSERT OR REPLACE INTO cache_entries 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            key,
            value_data if isinstance(value_data, bytes) else json.dumps(value_data),
            entry.created_at.timestamp(),
            entry.accessed_at.timestamp(),
            entry.access_count,
            entry.size_bytes,
            entry.ttl_seconds,
            json.dumps(entry.metadata)
        ))
        conn.commit()
        conn.close()
    
    def _get_from_disk(self, key: str) -> Optional[Any]:
        """Retrieve entry from disk"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, created_at, ttl_seconds, metadata
            FROM cache_entries
            WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        value, created_at, ttl_seconds, metadata_str = row
        metadata = json.loads(metadata_str)
        
        # Check expiration
        age = time.time() - created_at
        if age > ttl_seconds:
            self._invalidate_disk(key)
            return None
            
        # Decompress if needed
        if metadata.get('compressed'):
            import gzip
            value = json.loads(gzip.decompress(value).decode())
        elif isinstance(value, str):
            try:
                value = json.loads(value)
            except:
                pass  # Keep as string
                
        # Update access time
        self._update_disk_access(key)
        
        return value
    
    def _update_disk_access(self, key: str) -> None:
        """Update access time and count for disk entry"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE cache_entries
            SET accessed_at = ?, access_count = access_count + 1
            WHERE key = ?
        """, (time.time(), key))
        conn.commit()
        conn.close()
    
    def _invalidate_disk(self, pattern: Optional[str] = None) -> int:
        """Invalidate disk cache entries"""
        conn = sqlite3.connect(self.db_path)
        
        if pattern is None:
            cursor = conn.execute("DELETE FROM cache_entries")
        else:
            cursor = conn.execute(
                "DELETE FROM cache_entries WHERE key LIKE ?",
                (f"%{pattern}%",)
            )
            
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def _cleanup_disk(self) -> None:
        """Clean up expired disk entries"""
        conn = sqlite3.connect(self.db_path)
        current_time = time.time()
        
        cursor = conn.execute("""
            DELETE FROM cache_entries
            WHERE (? - created_at) > ttl_seconds
        """, (current_time,))
        
        self.stats.evictions += cursor.rowcount
        conn.commit()
        conn.close()
    
    def _promote_to_memory(self, key: str, value: Any) -> None:
        """Promote disk entry to memory cache"""
        # Estimate size and create entry
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            access_count=1,
            size_bytes=self._estimate_size(value),
            ttl_seconds=self.config.response_ttl,
            metadata={}
        )
        
        self._store_in_memory(key, entry)
    
    def _warm_cache(self) -> None:
        """Pre-warm cache with common queries"""
        common_queries = [
            "help",
            "install firefox",
            "update system",
            "search package",
            "list installed"
        ]
        
        logger.info("Warming cache with common queries...")
        # This would be implemented based on actual usage patterns