"""
Backend Interface - The Core Contract

This interface defines the sacred contract that all backends must honor.
It is the bridge between frontends and the intelligent engine that powers
Nix for Humanity.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Dict, Any
from ..core.types import Request, Response, Intent


class BackendInterface(ABC):
    """
    The sacred contract for all Nix for Humanity backends.
    
    This interface ensures that any backend implementation can serve
    the needs of all frontends (CLI, TUI, API, Voice) while maintaining
    the flexibility to evolve and improve.
    """
    
    @abstractmethod
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the backend with optional configuration.
        
        Args:
            config: Optional configuration dictionary containing:
                - progress_callback: Function to report progress
                - knowledge_path: Path to knowledge base
                - learning_enabled: Whether to enable learning
                - personality: Default personality style
                - native_api: Whether to use native Python-Nix API
        """
        pass
    
    @abstractmethod
    def process(self, request: Request) -> Response:
        """
        Process a request and return a response.
        
        This is the primary method - the sacred dialogue between
        frontend and backend. It must:
        
        1. Understand the user's intent from the request
        2. Plan appropriate actions
        3. Execute if requested (respecting dry_run)
        4. Return a well-formed Response
        
        Args:
            request: The user's request with context
            
        Returns:
            Response: A complete response with all necessary data
            
        Raises:
            Should not raise exceptions - errors go in Response.error
        """
        pass
    
    @abstractmethod
    async def process_async(self, request: Request) -> Response:
        """
        Asynchronous version of process for async frontends.
        
        This enables better performance and non-blocking operations
        for frontends that support async operations (API, Voice).
        
        Args:
            request: The user's request with context
            
        Returns:
            Response: A complete response with all necessary data
        """
        pass
    
    @abstractmethod
    def get_intent(self, query: str) -> Intent:
        """
        Extract intent from natural language.
        
        This is pure understanding - no execution, just comprehension.
        
        Args:
            query: Natural language input
            
        Returns:
            Intent: The recognized intent with confidence
        """
        pass
    
    @abstractmethod
    def explain(self, intent: Intent) -> str:
        """
        Generate a human-friendly explanation of an intent.
        
        This helps users understand what the system thinks they want.
        
        Args:
            intent: The recognized intent
            
        Returns:
            str: Human-readable explanation
        """
        pass
    
    @abstractmethod
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """
        Set a callback for progress updates.
        
        This enables frontends to show real-time progress during
        long-running operations.
        
        Args:
            callback: Function that takes (message: str, progress: float)
                     where progress is 0.0-1.0
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of this backend.
        
        This allows frontends to adapt their behavior based on
        what the backend supports.
        
        Returns:
            Dictionary containing:
                - native_api: bool - Whether native Python-Nix API is available
                - learning_enabled: bool - Whether learning is enabled
                - personalities: List[str] - Available personality styles
                - features: List[str] - Supported features
                - version: str - Backend version
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """
        Gracefully shutdown the backend.
        
        This should clean up resources, save state, and prepare
        for termination.
        """
        pass