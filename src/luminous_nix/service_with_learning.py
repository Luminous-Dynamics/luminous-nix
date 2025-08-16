"""
Enhanced Service Layer with Learning System Integration.

This builds on the simple service layer to add learning capabilities
that improve over time based on user patterns.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .service_simple import LuminousNixService, ServiceOptions
from .api.schema import Request, Response
from .learning.pragmatic_learning import PragmaticLearningSystem, UserPreferences

logger = logging.getLogger(__name__)


@dataclass
class LearningServiceOptions(ServiceOptions):
    """Extended options with learning configuration."""
    enable_learning: bool = True
    learning_path: Optional[Path] = None
    privacy_mode: bool = False  # Don't track when True


class LuminousNixServiceWithLearning(LuminousNixService):
    """
    Service layer with integrated learning system.
    
    This enhances the basic service with:
    - Command pattern recognition
    - User preference learning
    - Personalized suggestions
    - Error recovery patterns
    """
    
    def __init__(self, options: Optional[LearningServiceOptions] = None):
        """Initialize service with learning."""
        super().__init__(options or LearningServiceOptions())
        
        # Initialize learning system if enabled
        self.learning_system = None
        if isinstance(self.options, LearningServiceOptions) and self.options.enable_learning:
            if not self.options.privacy_mode:
                user_id = self.options.user_id or "default"
                self.learning_system = PragmaticLearningSystem(
                    user_id=user_id,
                    storage_path=self.options.learning_path
                )
                self._load_preferences()
    
    def _load_preferences(self):
        """Load user preferences from learning system."""
        if self.learning_system:
            try:
                self.learning_system.load_preferences()
                logger.info(f"Loaded preferences for user {self.learning_system.user_id}")
            except Exception as e:
                logger.warning(f"Could not load preferences: {e}")
    
    async def execute_command(
        self, 
        query: str, 
        execute: Optional[bool] = None,
        **kwargs
    ) -> Response:
        """
        Execute command with learning enhancements.
        
        This adds:
        - Alias expansion from learned patterns
        - Command tracking for pattern recognition
        - Error recovery suggestions
        - Personalized responses
        """
        # Apply learned aliases if available
        enhanced_query = self._apply_learned_aliases(query)
        
        # Execute the command
        response = await super().execute_command(enhanced_query, execute, **kwargs)
        
        # Track for learning (if enabled and not in privacy mode)
        if self.learning_system and not self.options.privacy_mode:
            self._track_command(query, response)
            
            # Add personalized suggestions if applicable
            response = self._enhance_with_suggestions(query, response)
        
        return response
    
    def _apply_learned_aliases(self, query: str) -> str:
        """Apply user's learned command aliases."""
        if not self.learning_system:
            return query
        
        # Check if query matches any learned aliases
        preferences = self.learning_system.preferences
        for alias, replacement in preferences.aliases.items():
            if query.startswith(alias):
                enhanced = query.replace(alias, replacement, 1)
                logger.info(f"Applied learned alias: '{alias}' → '{replacement}'")
                return enhanced
        
        return query
    
    def _track_command(self, query: str, response: Response):
        """Track command for learning patterns."""
        if not self.learning_system:
            return
        
        try:
            # Track command execution using observe_command method
            error_text = response.text if not response.success else None
            self.learning_system.observe_command(query, response.success, error_text)
            
            # Periodically save preferences
            if len(self.learning_system.recent_commands) % 10 == 0:
                self.learning_system.save_preferences()
                
        except Exception as e:
            logger.warning(f"Could not track command for learning: {e}")
    
    def _enhance_with_suggestions(self, query: str, response: Response) -> Response:
        """Add personalized suggestions based on learned patterns."""
        if not self.learning_system or not response.success:
            return response
        
        try:
            suggestions = []
            
            # Try to get alias suggestion
            alias_suggestion = self.learning_system.suggest_alias(query)
            if alias_suggestion:
                suggestions.append(f"Try: {alias_suggestion}")
            
            # Try to get next command suggestion
            next_cmd = self.learning_system.suggest_next_command(query)
            if next_cmd:
                suggestions.append(f"Next: {next_cmd}")
            
            if suggestions:
                # Add to response data
                if not response.data:
                    response.data = {}
                response.data["personalized_suggestions"] = suggestions
                
                # Optionally add to text response
                if suggestions and self.options.verbose:
                    suggestion_text = "\n💡 Based on your patterns: " + ", ".join(suggestions[:3])
                    response.text = (response.text or "") + suggestion_text
        
        except Exception as e:
            logger.warning(f"Could not add suggestions: {e}")
        
        return response
    
    def get_user_preferences(self) -> Optional[UserPreferences]:
        """Get current user preferences."""
        if self.learning_system:
            return self.learning_system.preferences
        return None
    
    def teach_alias(self, alias: str, command: str) -> bool:
        """Explicitly teach the system an alias."""
        if not self.learning_system:
            return False
        
        try:
            self.learning_system.preferences.aliases[alias] = command
            self.learning_system.save_preferences()
            logger.info(f"Learned alias: '{alias}' → '{command}'")
            return True
        except Exception as e:
            logger.error(f"Failed to learn alias: {e}")
            return False
    
    def forget_user_data(self) -> bool:
        """Clear all learned user data (privacy feature)."""
        if not self.learning_system:
            return True
        
        try:
            self.learning_system.delete_all_data()
            logger.info(f"Cleared all data for user {self.learning_system.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear user data: {e}")
            return False
    
    async def cleanup(self):
        """Clean up and save preferences."""
        if self.learning_system:
            try:
                self.learning_system.save_preferences()
                logger.info("Saved learning preferences on cleanup")
            except Exception as e:
                logger.warning(f"Could not save preferences: {e}")
        
        await super().cleanup()


# Factory functions with learning support

async def create_cli_service_with_learning(**kwargs) -> LuminousNixServiceWithLearning:
    """Create CLI service with learning enabled."""
    options = LearningServiceOptions(interface="cli", **kwargs)
    service = LuminousNixServiceWithLearning(options)
    await service.initialize()
    return service


async def create_tui_service_with_learning(**kwargs) -> LuminousNixServiceWithLearning:
    """Create TUI service with learning enabled."""
    options = LearningServiceOptions(interface="tui", **kwargs)
    service = LuminousNixServiceWithLearning(options)
    await service.initialize()
    return service


async def create_voice_service_with_learning(**kwargs) -> LuminousNixServiceWithLearning:
    """Create Voice service with learning enabled."""
    options = LearningServiceOptions(interface="voice", **kwargs)
    service = LuminousNixServiceWithLearning(options)
    await service.initialize()
    return service


async def create_api_service_with_learning(**kwargs) -> LuminousNixServiceWithLearning:
    """Create API service with learning enabled."""
    if 'json_output' not in kwargs:
        kwargs['json_output'] = True
    options = LearningServiceOptions(interface="api", **kwargs)
    service = LuminousNixServiceWithLearning(options)
    await service.initialize()
    return service


# Privacy-respecting mode for sensitive environments

async def create_private_service(**kwargs) -> LuminousNixServiceWithLearning:
    """Create service with learning disabled for privacy."""
    options = LearningServiceOptions(
        privacy_mode=True,
        enable_learning=False,
        **kwargs
    )
    service = LuminousNixServiceWithLearning(options)
    await service.initialize()
    return service