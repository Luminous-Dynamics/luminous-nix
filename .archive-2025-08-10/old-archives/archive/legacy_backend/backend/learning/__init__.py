"""
v1.0 exports - Core functionality only
"""

# v1.0 components
from .feedback import FeedbackCollector
from .pattern_learner import PatternRecognizer
from .preferences import PreferenceManager

__all__ = ["PreferenceManager", "PatternRecognizer", "FeedbackCollector"]
