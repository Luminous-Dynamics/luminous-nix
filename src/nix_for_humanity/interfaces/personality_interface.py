"""
Personality Interface - Adaptive Communication

This interface defines how the system adapts its communication style
to best serve each user. One size does not fit all.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.types import Intent, Response


class PersonalityInterface(ABC):
    """
    Contract for personality and communication style management.
    
    Implementations enable the system to communicate in ways that
    resonate with different users - from minimal technical responses
    to warm, encouraging guidance.
    """
    
    @abstractmethod
    def get_available_personalities(self) -> List[str]:
        """
        Get list of available personality styles.
        
        Returns:
            List of personality names (e.g., ["minimal", "friendly", "technical"])
        """
        pass
    
    @abstractmethod
    def get_personality_description(self, personality: str) -> str:
        """
        Get a description of a personality style.
        
        Args:
            personality: The personality name
            
        Returns:
            Human-readable description of the personality
            
        Raises:
            ValueError: If personality doesn't exist
        """
        pass
    
    @abstractmethod
    def format_response(self, 
                       base_response: str, 
                       personality: str,
                       intent: Optional[Intent] = None,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """
        Format a response according to a personality style.
        
        Args:
            base_response: The core response content
            personality: The personality style to use
            intent: Optional intent for context-aware formatting
            context: Optional additional context
            
        Returns:
            The formatted response text
            
        Raises:
            ValueError: If personality doesn't exist
        """
        pass
    
    @abstractmethod
    def adapt_response(self, response: Response, personality: str) -> Response:
        """
        Adapt an entire Response object to a personality style.
        
        This goes beyond just text formatting to adjust suggestions,
        explanations, and other response elements.
        
        Args:
            response: The response to adapt
            personality: The personality style to use
            
        Returns:
            New Response object adapted to the personality
        """
        pass
    
    @abstractmethod
    def suggest_personality(self, user_profile: Dict[str, Any]) -> str:
        """
        Suggest the best personality based on user profile.
        
        Args:
            user_profile: Dictionary containing:
                - skill_level: User's technical skill level
                - preferences: Known preferences
                - interaction_history: Past interactions
                
        Returns:
            Suggested personality name
        """
        pass
    
    @abstractmethod
    def get_personality_traits(self, personality: str) -> Dict[str, Any]:
        """
        Get detailed traits of a personality.
        
        Args:
            personality: The personality name
            
        Returns:
            Dictionary containing:
                - formality: Level of formality (0.0-1.0)
                - verbosity: How verbose responses are (0.0-1.0)
                - technical_depth: Technical detail level (0.0-1.0)
                - encouragement: How encouraging (0.0-1.0)
                - emoji_usage: Whether to use emojis
                - example_style: How to present examples
        """
        pass
    
    @abstractmethod
    def create_custom_personality(self, name: str, traits: Dict[str, Any]) -> None:
        """
        Create a custom personality style.
        
        Args:
            name: Name for the new personality
            traits: Personality traits (see get_personality_traits)
            
        Raises:
            ValueError: If name already exists or traits are invalid
        """
        pass
    
    @abstractmethod
    def get_response_variations(self, base_response: str) -> Dict[str, str]:
        """
        Get the same response in all available personalities.
        
        Useful for testing and comparison.
        
        Args:
            base_response: The core response content
            
        Returns:
            Dictionary mapping personality names to formatted responses
        """
        pass