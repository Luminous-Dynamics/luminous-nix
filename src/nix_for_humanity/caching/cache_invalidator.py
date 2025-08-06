"""
Intelligent Cache Invalidation

Manages cache invalidation strategies to ensure cached data remains accurate
while maximizing cache efficiency.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Callable
from datetime import datetime, timedelta
import re

from .cache_manager import CacheManager


class InvalidationStrategy(Enum):
    """Cache invalidation strategies"""
    TIME_BASED = "time_based"      # TTL expiration
    EVENT_BASED = "event_based"    # System events trigger invalidation
    PATTERN_BASED = "pattern_based" # Invalidate by key patterns
    DEPENDENCY_BASED = "dependency_based"  # Cascade invalidation
    MANUAL = "manual"              # Explicit invalidation


class InvalidationRule:
    """Rule for cache invalidation"""
    
    def __init__(self, name: str, strategy: InvalidationStrategy,
                 condition: Callable[[Dict], bool],
                 patterns: List[str],
                 dependencies: Optional[List[str]] = None):
        self.name = name
        self.strategy = strategy
        self.condition = condition
        self.patterns = patterns
        self.dependencies = dependencies or []
        self.last_triggered = None
        self.trigger_count = 0


class CacheInvalidator:
    """
    Intelligent cache invalidation manager.
    
    Features:
    - Multiple invalidation strategies
    - Event-driven invalidation
    - Dependency tracking
    - Pattern matching
    - Invalidation logging
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize cache invalidator"""
        self.cache_manager = cache_manager
        self.rules: Dict[str, InvalidationRule] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        
        # Initialize default rules
        self._setup_default_rules()
        
        # Track invalidation history
        self.invalidation_history: List[Dict] = []
        
    def _setup_default_rules(self) -> None:
        """Set up default invalidation rules"""
        
        # System update invalidates most caches
        self.add_rule(InvalidationRule(
            name="system_update",
            strategy=InvalidationStrategy.EVENT_BASED,
            condition=lambda e: e.get('type') == 'system_update',
            patterns=['response:*', 'command:*', 'xai:*'],
            dependencies=[]
        ))
        
        # Package installation invalidates package lists
        self.add_rule(InvalidationRule(
            name="package_change",
            strategy=InvalidationStrategy.EVENT_BASED,
            condition=lambda e: e.get('type') in ['package_install', 'package_remove'],
            patterns=['command:nix-env -q*', 'response:*list*', 'response:*installed*'],
            dependencies=['package_search']
        ))
        
        # Configuration change invalidates option queries
        self.add_rule(InvalidationRule(
            name="config_change",
            strategy=InvalidationStrategy.EVENT_BASED,
            condition=lambda e: e.get('type') == 'config_change',
            patterns=['command:nixos-option*', 'response:*config*'],
            dependencies=['system_info']
        ))
        
        # Error patterns change invalidates error caches
        self.add_rule(InvalidationRule(
            name="error_pattern_update",
            strategy=InvalidationStrategy.EVENT_BASED,
            condition=lambda e: e.get('type') == 'error_pattern_update',
            patterns=['xai:error_*', 'response:*error*', 'response:*fail*'],
            dependencies=[]
        ))
        
        # Time-based invalidation for system info
        self.add_rule(InvalidationRule(
            name="system_info_refresh",
            strategy=InvalidationStrategy.TIME_BASED,
            condition=lambda e: self._is_stale('system_info', minutes=5),
            patterns=['response:*status*', 'response:*info*', 'command:*df*'],
            dependencies=[]
        ))
    
    def add_rule(self, rule: InvalidationRule) -> None:
        """Add invalidation rule"""
        self.rules[rule.name] = rule
        
        # Track dependencies
        for pattern in rule.patterns:
            if pattern not in self.dependencies:
                self.dependencies[pattern] = set()
            self.dependencies[pattern].update(rule.dependencies)
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register handler for cache invalidation events"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def trigger_event(self, event: Dict[str, Any]) -> int:
        """
        Trigger cache invalidation based on event.
        
        Args:
            event: Event dictionary with 'type' and other fields
            
        Returns:
            Number of entries invalidated
        """
        total_invalidated = 0
        triggered_rules = []
        
        # Check each rule
        for rule_name, rule in self.rules.items():
            if rule.strategy == InvalidationStrategy.EVENT_BASED:
                if rule.condition(event):
                    count = self._apply_rule(rule)
                    total_invalidated += count
                    triggered_rules.append(rule_name)
                    
        # Log invalidation
        self._log_invalidation(event, triggered_rules, total_invalidated)
        
        # Notify handlers
        self._notify_handlers(event.get('type', 'unknown'), total_invalidated)
        
        return total_invalidated
    
    def invalidate_pattern(self, pattern: str, cascade: bool = True) -> int:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            cascade: Whether to invalidate dependencies
            
        Returns:
            Number of entries invalidated
        """
        count = self.cache_manager.invalidate(pattern)
        
        if cascade and pattern in self.dependencies:
            for dep_pattern in self.dependencies[pattern]:
                count += self.cache_manager.invalidate(dep_pattern)
                
        return count
    
    def invalidate_by_age(self, max_age_seconds: int) -> int:
        """Invalidate entries older than specified age"""
        # This would require cache manager support for age-based queries
        # For now, trigger cleanup
        self.cache_manager.cleanup()
        return 0
    
    def check_time_based_rules(self) -> int:
        """Check and apply time-based invalidation rules"""
        total_invalidated = 0
        
        for rule in self.rules.values():
            if rule.strategy == InvalidationStrategy.TIME_BASED:
                if rule.condition({}):  # Time-based conditions don't need events
                    count = self._apply_rule(rule)
                    total_invalidated += count
                    
        return total_invalidated
    
    def get_invalidation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent invalidation history"""
        return self.invalidation_history[-limit:]
    
    def suggest_invalidation(self, query: str) -> List[str]:
        """
        Suggest what might need invalidation based on query.
        
        Useful for proactive cache management.
        """
        suggestions = []
        
        # Analyze query for potential stale data
        if 'install' in query or 'remove' in query:
            suggestions.append('package_lists')
        if 'update' in query or 'upgrade' in query:
            suggestions.append('system_info')
        if 'config' in query or 'option' in query:
            suggestions.append('configuration')
            
        return suggestions
    
    # Private helper methods
    
    def _apply_rule(self, rule: InvalidationRule) -> int:
        """Apply invalidation rule"""
        total = 0
        
        for pattern in rule.patterns:
            count = self.cache_manager.invalidate(pattern)
            total += count
            
        # Update rule stats
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        return total
    
    def _is_stale(self, cache_type: str, minutes: int) -> bool:
        """Check if cache type is stale"""
        # This would check actual cache timestamps
        # For now, simple time-based check
        return True  # Always trigger for demo
    
    def _log_invalidation(self, event: Dict, rules: List[str], count: int) -> None:
        """Log invalidation event"""
        entry = {
            'timestamp': datetime.now(),
            'event': event,
            'triggered_rules': rules,
            'entries_invalidated': count
        }
        
        self.invalidation_history.append(entry)
        
        # Limit history size
        if len(self.invalidation_history) > 1000:
            self.invalidation_history.pop(0)
    
    def _notify_handlers(self, event_type: str, count: int) -> None:
        """Notify registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_type, count)
                except Exception as e:
                    # Log but don't crash on handler errors
                    pass
    
    def _compile_pattern(self, pattern: str) -> re.Pattern:
        """Compile wildcard pattern to regex"""
        # Convert simple wildcards to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return re.compile(f"^{regex_pattern}$")