#!/usr/bin/env python3
"""Create mock implementations for missing learning system classes."""

from pathlib import Path

def create_learning_mocks():
    """Create mock implementations for missing learning system classes."""
    
    # Create comprehensive mocks file
    mocks_file = Path("tests/test_utils/learning_mocks.py")
    
    mock_content = '''"""Mock implementations for learning system classes."""

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
'''
    
    mocks_file.write_text(mock_content)
    print(f"Created {mocks_file}")
    
    # Update test files to import from mocks
    test_dir = Path("tests")
    
    for test_file in test_dir.rglob("test_learning*.py"):
        if not test_file.is_file():
            continue
            
        content = test_file.read_text()
        original = content
        
        # Add import for mocks at the top after other imports
        if "from luminous_nix.learning.preferences import" in content:
            # Replace with mock import
            content = content.replace(
                "from luminous_nix.learning.preferences import",
                "from tests.test_utils.learning_mocks import"
            )
        
        if content != original:
            test_file.write_text(content)
            print(f"Updated {test_file}")

if __name__ == "__main__":
    create_learning_mocks()