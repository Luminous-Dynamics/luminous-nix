"""Mock caching module."""

class CacheLayer:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        self.cache[key] = value
        return True
    
    def clear(self):
        self.cache.clear()

class RedisCache(CacheLayer):
    pass

class CacheManager:
    def __init__(self):
        self.cache = CacheLayer()
    
    def get_cache(self, cache_type=None):
        return self.cache
