"""Caching system for Nix for Humanity"""

class CacheManager:
    """Manages caching for package searches and system queries"""
    
    def __init__(self):
        self.cache = {}
    
    def get(self, key: str):
        """Get value from cache"""
        return self.cache.get(key)
    
    def set(self, key: str, value, ttl: int = 3600):
        """Set value in cache with TTL"""
        self.cache[key] = value
        
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        keys_to_remove = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]
