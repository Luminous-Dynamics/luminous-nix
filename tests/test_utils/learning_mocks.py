"""Mock implementations for learning system classes."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class InteractionResult(Enum):
    """Result of an interaction."""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


@dataclass
class Preference:
    """Mock preference class for testing."""
    key: str
    value: Any
    confidence: float = 1.0
    
@dataclass
class PreferenceManager:
    """Mock preference manager for testing."""
    def __init__(self):
        self.preferences = {}
    
    def add_preference(self, key: str, value: Any, confidence: float = 1.0):
        self.preferences[key] = Preference(key, value, confidence)
    
    def get_preference(self, key: str) -> Optional[Preference]:
        return self.preferences.get(key)

@dataclass
class Interaction:
    """Mock interaction class for testing."""
    user_id: str
    query: str
    response: str
    timestamp: datetime
    successful: bool
    feedback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class UserPreference:
    """Mock user preference class."""
    user_id: str
    preference_key: str
    preference_value: Any
    confidence: float = 0.5
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class FeedbackEntry:
    """Mock feedback entry class."""
    interaction_id: str
    user_id: str
    helpful: bool
    comment: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LearningPattern:
    """Mock learning pattern class."""
    def __init__(self, pattern_type: str, pattern_data: Dict[str, Any]):
        self.pattern_type = pattern_type
        self.pattern_data = pattern_data
        self.confidence = 0.5
        self.occurrences = 1


@dataclass
class PreferencePair:
    """Mock preference pair class."""
    key: str
    value: Any
    confidence: float = 0.5
    source: str = "user"


@dataclass
class UserModel:
    """Mock user model class."""
    user_id: str
    skill_level: str = "beginner"
    preferences: Dict[str, Any] = None
    interaction_count: int = 0
    success_rate: float = 0.5
    interests: List[str] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}
        if self.interests is None:
            self.interests = []


class PreferenceManager:
    """Mock preference manager class."""
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.preferences = {}
        self.interactions = []
        self.feedback = []
    
    def record_interaction(self, interaction: Interaction):
        """Record an interaction."""
        self.interactions.append(interaction)
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences."""
        return self.preferences.get(user_id, {})
    
    def update_preference(self, user_id: str, key: str, value: Any):
        """Update a user preference."""
        if user_id not in self.preferences:
            self.preferences[user_id] = {}
        self.preferences[user_id][key] = value
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get feedback summary."""
        total = len(self.feedback)
        positive = sum(1 for f in self.feedback if f.helpful)
        return {
            "total_feedback": total,
            "positive_feedback": positive,
            "negative_feedback": total - positive,
        }
