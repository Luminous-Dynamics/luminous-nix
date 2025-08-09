"""
v1.0 exports - Core functionality only
"""

# v1.0 components
from .preferences import PreferenceManager
from .pattern_learner import PatternRecognizer
from .feedback import FeedbackCollector

__all__ = ['PreferenceManager', 'PatternRecognizer', 'FeedbackCollector']
