"""
Package Cache Manager stub
This will be replaced with the full implementation
"""


class PackageCacheManager:
    def __init__(self):
        self.is_enabled = True
        self.cache = {}

    def search_cached(self, query):
        """Search in cache first"""
        return self.cache.get(query)

    def cache_search(self, query, results):
        """Cache search results"""
        self.cache[query] = results
