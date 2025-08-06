"""
Intent Recognizer Interface - Understanding User Needs

This interface defines how we understand what users want from their
natural language input. It's the bridge between human expression and
machine comprehension.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..core.types import Intent, IntentType


class IntentRecognizerInterface(ABC):
    """
    Contract for understanding user intent from natural language.
    
    Implementations can range from simple pattern matching to
    sophisticated NLP models, but all must honor this interface.
    """
    
    @abstractmethod
    def recognize(self, query: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """
        Recognize intent from a natural language query.
        
        Args:
            query: The user's natural language input
            context: Optional context that might help with recognition:
                - previous_intents: List of recent intents
                - user_preferences: Known user preferences
                - session_context: Current session information
                
        Returns:
            Intent: The recognized intent with confidence score
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[IntentType]:
        """
        Get the list of intent types this recognizer supports.
        
        Returns:
            List of IntentType enums that can be recognized
        """
        pass
    
    @abstractmethod
    def get_confidence_threshold(self) -> float:
        """
        Get the minimum confidence threshold for accepting an intent.
        
        Intents with confidence below this threshold should be
        treated as UNKNOWN.
        
        Returns:
            float: Confidence threshold (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the minimum confidence threshold.
        
        Args:
            threshold: New threshold (0.0 to 1.0)
            
        Raises:
            ValueError: If threshold is not in valid range
        """
        pass
    
    @abstractmethod
    def get_entity_extractors(self) -> Dict[str, Any]:
        """
        Get information about entity extraction capabilities.
        
        Returns:
            Dictionary mapping entity types to their extractors:
                - package: Package name extractor
                - version: Version extractor
                - service: Service name extractor
                - config: Configuration option extractor
        """
        pass
    
    @abstractmethod
    def train_on_correction(self, query: str, correct_intent: Intent) -> None:
        """
        Learn from a correction to improve future recognition.
        
        This enables the recognizer to learn from mistakes and
        improve over time.
        
        Args:
            query: The original query
            correct_intent: The correct intent that should have been recognized
        """
        pass
    
    @abstractmethod
    def get_debug_info(self, query: str) -> Dict[str, Any]:
        """
        Get detailed debug information about intent recognition.
        
        Useful for understanding why a particular intent was chosen.
        
        Args:
            query: The query to analyze
            
        Returns:
            Dictionary containing:
                - matched_patterns: List of patterns that matched
                - confidence_scores: Scores for each intent type
                - extracted_entities: Entities found in the query
                - processing_steps: Steps taken during recognition
        """
        pass