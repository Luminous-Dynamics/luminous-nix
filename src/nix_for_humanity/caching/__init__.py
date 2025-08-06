"""
Caching Layer for Nix for Humanity

Provides intelligent caching for responses, commands, and XAI explanations
to achieve optimal performance while maintaining accuracy.
"""

from .cache_manager import CacheManager, CacheConfig
from .response_cache import ResponseCache
from .command_cache import CommandResultCache
from .xai_cache import XAIExplanationCache
from .cache_invalidator import CacheInvalidator, InvalidationStrategy

__all__ = [
    'CacheManager',
    'CacheConfig',
    'ResponseCache',
    'CommandResultCache',
    'XAIExplanationCache',
    'CacheInvalidator',
    'InvalidationStrategy'
]