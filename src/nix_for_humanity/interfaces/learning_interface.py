"""
Learning Interface - Continuous Improvement

This interface defines how the system learns and improves from
interactions. It's the path to true symbiotic intelligence.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..core.types import Request, Response, FeedbackItem


class LearningInterface(ABC):
    """
    Contract for system learning and improvement.
    
    Implementations enable the system to learn from every interaction,
    building a personalized understanding of each user while respecting
    privacy.
    """
    
    @abstractmethod
    def record_interaction(self, request: Request, response: Response) -> str:
        """
        Record an interaction for learning purposes.
        
        Args:
            request: The user's request
            response: The system's response
            
        Returns:
            str: Unique interaction ID for future reference
        """
        pass
    
    @abstractmethod
    def record_feedback(self, feedback: FeedbackItem) -> None:
        """
        Record user feedback on a response.
        
        Args:
            feedback: The feedback item containing response_id and rating
        """
        pass
    
    @abstractmethod
    def get_user_preferences(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get learned preferences for a user.
        
        Args:
            user_id: Optional user identifier (uses default if not provided)
            
        Returns:
            Dictionary containing:
                - preferred_personality: Their preferred response style
                - common_tasks: Tasks they frequently perform
                - skill_level: Estimated NixOS skill level
                - preferences: Specific preferences learned
        """
        pass
    
    @abstractmethod
    def update_user_preference(self, preference: str, value: Any, user_id: Optional[str] = None) -> None:
        """
        Update a specific user preference.
        
        Args:
            preference: The preference to update
            value: The new value
            user_id: Optional user identifier
        """
        pass
    
    @abstractmethod
    def get_pattern_insights(self) -> Dict[str, Any]:
        """
        Get insights from usage patterns.
        
        Returns:
            Dictionary containing:
                - common_intents: Most frequently used intents
                - common_errors: Frequently encountered errors
                - success_patterns: Patterns that lead to success
                - improvement_areas: Areas where users struggle
        """
        pass
    
    @abstractmethod
    def suggest_improvements(self, intent_type: str) -> List[str]:
        """
        Suggest improvements based on learning.
        
        Args:
            intent_type: The type of intent to get suggestions for
            
        Returns:
            List of improvement suggestions
        """
        pass
    
    @abstractmethod
    def export_learning_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export learning data for a user (privacy feature).
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            All learning data associated with the user
        """
        pass
    
    @abstractmethod
    def reset_learning_data(self, user_id: Optional[str] = None) -> None:
        """
        Reset all learning data for a user (privacy feature).
        
        Args:
            user_id: Optional user identifier
        """
        pass
    
    @abstractmethod
    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the learning system.
        
        Returns:
            Dictionary containing:
                - total_interactions: Number of interactions recorded
                - total_feedback: Amount of feedback received
                - positive_feedback_rate: Percentage of positive feedback
                - learning_improvements: Measurable improvements
                - active_users: Number of active users
        """
        pass
    
    @abstractmethod
    def enable_federated_learning(self, consent: bool) -> None:
        """
        Enable or disable federated learning.
        
        When enabled, anonymized patterns can be shared to improve
        the system for everyone while preserving privacy.
        
        Args:
            consent: Whether the user consents to federated learning
        """
        pass