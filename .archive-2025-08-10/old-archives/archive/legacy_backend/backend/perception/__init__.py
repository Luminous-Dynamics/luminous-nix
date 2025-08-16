"""
Perception System - Privacy-first behavioral awareness

Integrates with ActivityWatch for understanding user context while
preserving complete privacy and user control.
"""

from .activity_monitor import ActivityMonitor
from .behavioral_insights import BehavioralInsights
from .context_awareness import ContextAwareness
from .privacy_guard import PrivacyGuard

__all__ = ["ActivityMonitor", "ContextAwareness", "PrivacyGuard", "BehavioralInsights"]
