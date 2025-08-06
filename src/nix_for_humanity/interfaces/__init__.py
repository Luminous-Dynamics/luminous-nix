"""
Sacred Interfaces for Nix for Humanity

This module provides the contract interfaces that all implementations must honor.
These interfaces define the sacred boundaries between components, ensuring clean
separation of concerns and enabling multiple implementations.
"""

from .backend_interface import BackendInterface
from .intent_interface import IntentRecognizerInterface
from .executor_interface import ExecutorInterface
from .knowledge_interface import KnowledgeInterface
from .learning_interface import LearningInterface
from .personality_interface import PersonalityInterface

__all__ = [
    'BackendInterface',
    'IntentRecognizerInterface',
    'ExecutorInterface',
    'KnowledgeInterface',
    'LearningInterface',
    'PersonalityInterface',
]