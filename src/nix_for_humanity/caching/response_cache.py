"""
Response Cache for Natural Language Queries

Caches responses to user queries with intelligent similarity matching
to handle variations in phrasing.
"""

import json
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
# Note: Numpy import is optional for basic functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create mock numpy for basic operations (not used in this file but imported for compatibility)
    class MockNumpy:
        def array(self, data):
            return data
        def mean(self, data):
            return sum(data) / len(data) if data else 0
    np = MockNumpy()
    import logging
    logging.warning("Numpy not available. Using simplified numerical operations.")
from dataclasses import dataclass

from .cache_manager import CacheManager, CacheConfig
from ..core.types import Request, Response


@dataclass
class CachedResponse:
    """Cached response with metadata"""
    response: Response
    query: str
    context_hash: str
    confidence: float
    variations: List[str]  # Alternative phrasings that map to this


class ResponseCache:
    """
    Intelligent response caching with fuzzy matching.
    
    Features:
    - Exact match caching
    - Similarity-based retrieval
    - Context-aware caching
    - Query normalization
    - Variation learning
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize response cache"""
        self.cache_manager = cache_manager
        self.similarity_threshold = 0.85
        
        # Track query variations for better matching
        self.query_variations: Dict[str, List[str]] = {}
        
    def get(self, request: Request) -> Optional[Response]:
        """
        Retrieve cached response for request.
        
        Checks for:
        1. Exact match
        2. Normalized match
        3. Similar queries (fuzzy match)
        4. Context-compatible matches
        """
        # Try exact match first
        cache_key = self._generate_cache_key(request)
        cached = self.cache_manager.get(cache_key, cache_type='response')
        
        if cached and self._is_context_compatible(cached, request):
            return cached.response
            
        # Try normalized query
        normalized_query = self._normalize_query(request.query)
        normalized_key = self._generate_normalized_key(normalized_query, request)
        cached = self.cache_manager.get(normalized_key, cache_type='response')
        
        if cached and self._is_context_compatible(cached, request):
            # Learn this variation
            self._learn_variation(normalized_query, request.query)
            return cached.response
            
        # Try similarity matching
        similar_response = self._find_similar_cached(request)
        if similar_response:
            return similar_response
            
        return None
    
    def set(self, request: Request, response: Response) -> None:
        """Cache a response with intelligent keying"""
        # Cache exact query
        cache_key = self._generate_cache_key(request)
        cached_response = CachedResponse(
            response=response,
            query=request.query,
            context_hash=self._hash_context(request.context),
            confidence=1.0,
            variations=[request.query]
        )
        
        self.cache_manager.set(
            cache_key,
            cached_response,
            ttl=self._determine_ttl(response),
            metadata={
                'query_type': self._classify_query(request.query),
                'success': response.success,
                'has_plan': response.plan is not None
            }
        )
        
        # Also cache normalized version
        normalized_query = self._normalize_query(request.query)
        if normalized_query != request.query:
            normalized_key = self._generate_normalized_key(normalized_query, request)
            self.cache_manager.set(normalized_key, cached_response)
            
        # Update variations mapping
        self._learn_variation(normalized_query, request.query)
    
    def invalidate_query_type(self, query_type: str) -> int:
        """Invalidate all cached responses of a specific type"""
        # This would need more sophisticated implementation
        # to track query types efficiently
        return self.cache_manager.invalidate(f"response:{query_type}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache_manager.get_statistics()
        stats['variations_learned'] = sum(len(v) for v in self.query_variations.values())
        return stats
    
    # Private helper methods
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request"""
        # Include query and relevant context
        key_parts = [
            'response',
            request.query,
            str(request.dry_run),
            str(request.execute),
            self._hash_context(request.context)
        ]
        
        key_string = ':'.join(key_parts)
        return f"response:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"
    
    def _generate_normalized_key(self, normalized_query: str, request: Request) -> str:
        """Generate cache key for normalized query"""
        key_parts = [
            'response_norm',
            normalized_query,
            str(request.dry_run),
            str(request.execute),
            self._hash_context(request.context)
        ]
        
        key_string = ':'.join(key_parts)
        return f"response_norm:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better matching"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove common variations
        replacements = {
            "please ": "",
            "can you ": "",
            "could you ": "",
            "i want to ": "",
            "i need to ": "",
            "how do i ": "",
            "how to ": "",
            " for me": "",
            "?": "",
            "!": "",
            ".": ""
        }
        
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
            
        # Normalize whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _hash_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Hash context for cache key"""
        if not context:
            return "no_context"
            
        # Only include relevant context fields
        relevant_fields = ['persona', 'personality', 'session_id']
        relevant_context = {
            k: v for k, v in context.items() 
            if k in relevant_fields
        }
        
        context_str = json.dumps(relevant_context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    def _is_context_compatible(self, cached: CachedResponse, request: Request) -> bool:
        """Check if cached response is compatible with request context"""
        # If contexts match exactly, it's compatible
        request_hash = self._hash_context(request.context)
        if cached.context_hash == request_hash:
            return True
            
        # Check if only non-critical fields differ
        # This would be more sophisticated in production
        return False
    
    def _determine_ttl(self, response: Response) -> int:
        """Determine TTL based on response type"""
        # Shorter TTL for errors
        if not response.success:
            return 60  # 1 minute
            
        # Longer TTL for system info queries
        if response.intent and response.intent.type.value in ['info', 'status']:
            return 30  # 30 seconds for rapidly changing info
            
        # Default TTL from config
        return self.cache_manager.config.response_ttl
    
    def _classify_query(self, query: str) -> str:
        """Classify query type for cache management"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['install', 'remove', 'uninstall']):
            return 'package_management'
        elif any(word in query_lower for word in ['update', 'upgrade']):
            return 'system_update'
        elif any(word in query_lower for word in ['search', 'find', 'list']):
            return 'search'
        elif any(word in query_lower for word in ['help', 'how', 'what']):
            return 'help'
        else:
            return 'general'
    
    def _find_similar_cached(self, request: Request) -> Optional[Response]:
        """Find similar cached queries using fuzzy matching"""
        # This is a simplified version
        # In production, would use embedding-based similarity
        
        normalized_query = self._normalize_query(request.query)
        
        # Check learned variations
        for base_query, variations in self.query_variations.items():
            if normalized_query in variations:
                # Try to get the cached response for base query
                # This would need more sophisticated implementation
                pass
                
        return None
    
    def _learn_variation(self, base_query: str, variation: str) -> None:
        """Learn query variation for better future matching"""
        if base_query not in self.query_variations:
            self.query_variations[base_query] = []
            
        if variation not in self.query_variations[base_query]:
            self.query_variations[base_query].append(variation)
            
            # Limit variations to prevent memory bloat
            if len(self.query_variations[base_query]) > 10:
                self.query_variations[base_query].pop(0)
    
    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate similarity between two queries"""
        # Simple character-based similarity
        # In production, would use embeddings
        
        set1 = set(query1.lower().split())
        set2 = set(query2.lower().split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0