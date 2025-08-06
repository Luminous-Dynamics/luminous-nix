"""
XAI Explanation Cache

Caches AI-generated explanations to avoid recomputation of expensive
causal analysis and confidence calculations.
"""

import hashlib
import json
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from .cache_manager import CacheManager
from ..ai.xai_engine import ExplanationLevel
from ..xai.causal_engine import CausalExplanation


@dataclass
class CachedExplanation:
    """Cached XAI explanation with metadata"""
    explanation: CausalExplanation
    decision_type: str
    decision_value: str
    context_hash: str
    level: ExplanationLevel
    computation_time: float
    confidence_details: Optional[Dict[str, Any]] = None


class XAIExplanationCache:
    """
    Cache for XAI explanations and confidence calculations.
    
    Features:
    - Multi-level explanation caching
    - Context-aware storage
    - Computation time tracking
    - Confidence detail preservation
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize XAI cache"""
        self.cache_manager = cache_manager
        
        # Track computation times for optimization
        self.computation_times: Dict[str, float] = {}
        
    def get(self, decision_type: str, decision_value: str, 
            context: Dict[str, Any], level: ExplanationLevel) -> Optional[CausalExplanation]:
        """
        Get cached explanation if available.
        
        Args:
            decision_type: Type of decision being explained
            decision_value: The decision made
            context: Context of the decision
            level: Explanation detail level
            
        Returns:
            Cached explanation or None
        """
        cache_key = self._generate_cache_key(
            decision_type, decision_value, context, level
        )
        
        cached = self.cache_manager.get(cache_key, cache_type='xai')
        
        if cached:
            # Update access pattern tracking
            self._track_access(decision_type, level)
            return cached.explanation
            
        return None
    
    def set(self, decision_type: str, decision_value: str,
            context: Dict[str, Any], level: ExplanationLevel,
            explanation: CausalExplanation, computation_time: float) -> None:
        """
        Cache an XAI explanation.
        
        Args:
            decision_type: Type of decision explained
            decision_value: The decision made
            context: Context of the decision
            level: Explanation detail level
            explanation: The generated explanation
            computation_time: Time taken to compute
        """
        cache_key = self._generate_cache_key(
            decision_type, decision_value, context, level
        )
        
        cached_explanation = CachedExplanation(
            explanation=explanation,
            decision_type=decision_type,
            decision_value=decision_value,
            context_hash=self._hash_context(context),
            level=level,
            computation_time=computation_time,
            confidence_details=getattr(explanation, 'confidence_details', None)
        )
        
        # Track computation time for optimization
        self._track_computation_time(decision_type, level, computation_time)
        
        # Determine TTL based on decision type
        ttl = self._determine_ttl(decision_type, level)
        
        self.cache_manager.set(
            cache_key,
            cached_explanation,
            ttl=ttl,
            metadata={
                'decision_type': decision_type,
                'level': level.value,
                'computation_time': computation_time,
                'has_confidence': hasattr(explanation, 'confidence_details')
            }
        )
        
    def get_multi_level(self, decision_type: str, decision_value: str,
                       context: Dict[str, Any]) -> Dict[ExplanationLevel, Optional[CausalExplanation]]:
        """Get cached explanations for all levels"""
        results = {}
        
        for level in ExplanationLevel:
            results[level] = self.get(
                decision_type, decision_value, context, level
            )
            
        return results
    
    def set_multi_level(self, decision_type: str, decision_value: str,
                       context: Dict[str, Any], 
                       explanations: Dict[ExplanationLevel, Tuple[CausalExplanation, float]]) -> None:
        """Cache explanations for multiple levels"""
        for level, (explanation, comp_time) in explanations.items():
            self.set(
                decision_type, decision_value, context, level,
                explanation, comp_time
            )
    
    def invalidate_decision_type(self, decision_type: str) -> int:
        """Invalidate all explanations for a decision type"""
        return self.cache_manager.invalidate(f"xai:{decision_type}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get XAI cache statistics"""
        stats = {
            'avg_computation_times': self._calculate_avg_computation_times(),
            'most_explained': self._get_most_explained_types(),
            'cache_efficiency': self._calculate_cache_efficiency()
        }
        
        return stats
    
    # Private helper methods
    
    def _generate_cache_key(self, decision_type: str, decision_value: str,
                           context: Dict[str, Any], level: ExplanationLevel) -> str:
        """Generate cache key for XAI explanation"""
        key_parts = [
            'xai',
            decision_type,
            decision_value,
            self._hash_context(context),
            level.value
        ]
        
        key_string = ':'.join(key_parts)
        return f"xai:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"
    
    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Hash context for cache key"""
        # Only include relevant context fields
        relevant_fields = [
            'user_input', 'session_id', 'persona', 
            'personality', 'factors'
        ]
        
        relevant_context = {
            k: v for k, v in context.items()
            if k in relevant_fields
        }
        
        context_str = json.dumps(relevant_context, sort_keys=True)
        return hashlib.md5(context_str.encode()).hexdigest()[:8]
    
    def _determine_ttl(self, decision_type: str, level: ExplanationLevel) -> int:
        """Determine TTL based on explanation type"""
        # Shorter TTL for simple explanations
        if level == ExplanationLevel.SIMPLE:
            return 600  # 10 minutes
            
        # Longer TTL for detailed/technical (more expensive to compute)
        if level in [ExplanationLevel.DETAILED, ExplanationLevel.TECHNICAL]:
            return 3600  # 1 hour
            
        # Decision-type specific TTLs
        if decision_type == 'error_diagnosis':
            return 300  # 5 minutes (errors change quickly)
        elif decision_type == 'intent_recognition':
            return 1800  # 30 minutes
            
        # Default
        return self.cache_manager.config.xai_ttl
    
    def _track_access(self, decision_type: str, level: ExplanationLevel) -> None:
        """Track access patterns for optimization"""
        # This would be used to identify hot paths for pre-computation
        pass
    
    def _track_computation_time(self, decision_type: str, level: ExplanationLevel,
                               time: float) -> None:
        """Track computation times for performance analysis"""
        key = f"{decision_type}:{level.value}"
        
        if key not in self.computation_times:
            self.computation_times[key] = []
            
        self.computation_times[key].append(time)
        
        # Keep only recent times
        if len(self.computation_times[key]) > 100:
            self.computation_times[key].pop(0)
    
    def _calculate_avg_computation_times(self) -> Dict[str, float]:
        """Calculate average computation times by type and level"""
        avg_times = {}
        
        for key, times in self.computation_times.items():
            if times:
                avg_times[key] = sum(times) / len(times)
                
        return avg_times
    
    def _get_most_explained_types(self) -> List[str]:
        """Get most frequently explained decision types"""
        # This would analyze cache access patterns
        # For now, return mock data
        return ['intent_recognition', 'error_diagnosis', 'command_building']
    
    def _calculate_cache_efficiency(self) -> float:
        """Calculate cache efficiency (time saved)"""
        if not self.computation_times:
            return 0.0
            
        # Estimate time saved by caching
        total_computation_time = sum(
            sum(times) for times in self.computation_times.values()
        )
        
        # Assume each cache hit saves average computation time
        cache_stats = self.cache_manager.get_statistics()
        hits = cache_stats.get('hits', 0)
        
        if hits > 0 and self.computation_times:
            avg_time = total_computation_time / sum(
                len(times) for times in self.computation_times.values()
            )
            time_saved = hits * avg_time
            
            return time_saved / (total_computation_time + time_saved)
            
        return 0.0