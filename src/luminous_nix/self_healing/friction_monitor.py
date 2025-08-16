#!/usr/bin/env python3
"""
Simple Friction Monitoring for Luminous Nix.

Tracks user confusion and frustration signals to prevent AI from learning
from confused interactions. Based on research showing UI friction corrupts
training data.

Simple and elegant - just 150 lines instead of complex analytics.
"""

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


@dataclass
class FrictionEvent:
    """Simple friction event tracking"""
    timestamp: float
    event_type: str  # 'error', 'undo', 'help', 'retry'
    context: str     # What user was trying to do
    
    
@dataclass 
class FrictionMetrics:
    """Aggregated friction metrics for a session"""
    score: float = 0.0
    error_rate: float = 0.0
    undo_rate: float = 0.0
    help_frequency: float = 0.0
    retry_rate: float = 0.0
    hesitation_avg: float = 0.0
    

class SimpleFrictionMonitor:
    """
    Monitors user friction to improve system adaptation.
    
    Key principle: High friction means confused user, not lack of knowledge.
    When friction is high, the system should provide more guidance, not
    assume the user doesn't understand.
    """
    
    def __init__(self, window_size: int = 100, threshold: float = 0.3):
        """
        Initialize friction monitor.
        
        Args:
            window_size: Number of recent events to track
            threshold: Friction score above which user is considered confused
        """
        self.events = deque(maxlen=window_size)
        self.threshold = threshold
        self.last_action_time = time.time()
        self.action_times: List[float] = []
        
        # Simple counters
        self.total_actions = 0
        self.error_count = 0
        self.undo_count = 0
        self.help_count = 0
        self.retry_count = 0
        
    def track_action(self, action_type: str, success: bool, context: str = ""):
        """
        Track a user action for friction analysis.
        
        Args:
            action_type: Type of action performed
            success: Whether action succeeded
            context: What user was trying to do
        """
        now = time.time()
        
        # Track hesitation (time between actions)
        if self.last_action_time:
            hesitation = now - self.last_action_time
            self.action_times.append(hesitation)
            
        self.last_action_time = now
        self.total_actions += 1
        
        # Track friction events
        if not success:
            self.error_count += 1
            self.events.append(FrictionEvent(now, 'error', context))
            
        if 'undo' in action_type.lower():
            self.undo_count += 1
            self.events.append(FrictionEvent(now, 'undo', context))
            
        if 'help' in action_type.lower():
            self.help_count += 1
            self.events.append(FrictionEvent(now, 'help', context))
            
        if 'retry' in action_type.lower():
            self.retry_count += 1
            self.events.append(FrictionEvent(now, 'retry', context))
    
    def calculate_friction_score(self) -> float:
        """
        Calculate current friction score (0-1).
        
        Higher score = more user confusion/frustration.
        
        Returns:
            Friction score between 0 and 1
        """
        if self.total_actions == 0:
            return 0.0
            
        # Simple weighted average of friction signals
        weights = {
            'error_rate': 0.3,
            'undo_rate': 0.2,
            'help_rate': 0.2,
            'retry_rate': 0.2,
            'hesitation': 0.1
        }
        
        scores = {
            'error_rate': min(1.0, self.error_count / max(1, self.total_actions)),
            'undo_rate': min(1.0, self.undo_count / max(1, self.total_actions)),
            'help_rate': min(1.0, self.help_count / max(1, self.total_actions)),
            'retry_rate': min(1.0, self.retry_count / max(1, self.total_actions)),
            'hesitation': self._calculate_hesitation_score()
        }
        
        # Weighted sum
        total_score = sum(scores[key] * weights[key] for key in weights)
        
        return min(1.0, total_score)
    
    def _calculate_hesitation_score(self) -> float:
        """Calculate hesitation score from action timing"""
        if not self.action_times:
            return 0.0
            
        avg_time = sum(self.action_times) / len(self.action_times)
        
        # More than 5 seconds average = high hesitation
        if avg_time > 5.0:
            return 1.0
        elif avg_time > 3.0:
            return 0.5
        else:
            return 0.0
    
    def is_user_confused(self) -> bool:
        """Check if user appears confused based on friction score"""
        return self.calculate_friction_score() > self.threshold
    
    def get_metrics(self) -> FrictionMetrics:
        """Get current friction metrics"""
        if self.total_actions == 0:
            return FrictionMetrics()
            
        return FrictionMetrics(
            score=self.calculate_friction_score(),
            error_rate=self.error_count / self.total_actions,
            undo_rate=self.undo_count / self.total_actions,
            help_frequency=self.help_count / self.total_actions,
            retry_rate=self.retry_count / self.total_actions,
            hesitation_avg=sum(self.action_times) / len(self.action_times) if self.action_times else 0
        )
    
    def reset_session(self):
        """Reset metrics for new session"""
        self.events.clear()
        self.action_times.clear()
        self.total_actions = 0
        self.error_count = 0
        self.undo_count = 0
        self.help_count = 0
        self.retry_count = 0
        self.last_action_time = time.time()
    
    def suggest_adaptation(self) -> Dict[str, Any]:
        """
        Suggest system adaptations based on friction patterns.
        
        Returns:
            Dict with adaptation suggestions
        """
        metrics = self.get_metrics()
        suggestions = {
            'verbose_mode': False,
            'show_examples': False,
            'simplify_ui': False,
            'offer_tutorial': False
        }
        
        if metrics.score > 0.5:
            # High friction - user needs help
            suggestions['verbose_mode'] = True
            suggestions['show_examples'] = True
            
        if metrics.error_rate > 0.3:
            # Many errors - simplify interface
            suggestions['simplify_ui'] = True
            
        if metrics.help_frequency > 0.2:
            # Frequent help requests - offer tutorial
            suggestions['offer_tutorial'] = True
            
        return suggestions


# Global instance for easy access
_friction_monitor = SimpleFrictionMonitor()

def get_friction_monitor() -> SimpleFrictionMonitor:
    """Get global friction monitor instance"""
    return _friction_monitor