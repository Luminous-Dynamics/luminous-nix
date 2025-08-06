"""
Sacred Contracts for Nix for Humanity

This module defines the authoritative data structures and interfaces that govern
all communication within our system. These are the contracts that bind our
components together in harmonious collaboration.

"Contracts First, Then Concrete" - This is our architectural principle.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum


# ============================================================================
# Core Data Structures - The Language of Our System
# ============================================================================

@dataclass
class Request:
    """
    The sacred input structure - how all frontends speak to the backend.
    
    This represents a user's intention, wrapped with context about their
    environment and preferences.
    """
    query: str                          # The user's natural language input
    frontend: str = "cli"               # Which interface sent this request
    context: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    def __post_init__(self):
        """Ensure context has default values"""
        self.context.setdefault('personality', 'friendly')
        self.context.setdefault('execute', False)
        self.context.setdefault('dry_run', False)
        self.context.setdefault('collect_feedback', True)


@dataclass
class Response:
    """
    The sacred output structure - how the backend speaks to all frontends.
    
    This carries not just the answer, but the understanding, the plan,
    and the wisdom to help the user on their journey.
    """
    # Core response
    text: str                           # Human-readable response
    success: bool = True                # Did we handle the request successfully?
    
    # Structured data for different frontends
    commands: List[Dict[str, Any]] = field(default_factory=list)  # Executable commands
    data: Dict[str, Any] = field(default_factory=dict)           # Additional data
    
    # Learning and improvement
    collect_feedback: bool = True       # Should we ask for feedback?
    suggestions: List[str] = field(default_factory=list)          # Related suggestions
    
    # Error handling
    error: Optional[str] = None         # Error message if something went wrong
    
    # Metadata
    response_id: str = field(default_factory=lambda: f"resp_{datetime.now().timestamp()}")
    timestamp: datetime = field(default_factory=datetime.now)


class IntentType(Enum):
    """Types of user intentions we can recognize"""
    INSTALL = "install"
    REMOVE = "remove"
    UPDATE = "update"
    SEARCH = "search"
    INFO = "info"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """The backend's understanding of what the user wants"""
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of executing a command or action"""
    success: bool
    output: str = ""
    error: Optional[str] = None
    exit_code: int = 0


# ============================================================================
# The Backend Interface - The Grammar of Our System
# ============================================================================

class BackendInterface(ABC):
    """
    The sacred contract that all backends must honor.
    
    This defines the one true way to interact with our AI's "brain".
    Any class that implements this interface can serve as the intelligence
    behind Nix for Humanity.
    """
    
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


# ============================================================================
# Helper Types - Supporting Structures
# ============================================================================

@dataclass
class Package:
    """Information about a Nix package"""
    name: str
    attribute: str
    version: Optional[str] = None
    description: Optional[str] = None
    installed: bool = False


@dataclass
class SystemInfo:
    """Current system state information"""
    nixos_version: str
    channel: str
    last_updated: Optional[datetime] = None
    generation: int = 0


@dataclass
class Feedback:
    """User feedback on a response"""
    response_id: str
    helpful: bool
    comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Type Aliases - For Clarity
# ============================================================================

CommandList = List[Dict[str, Any]]
PackageList = List[Package]
ErrorMessage = Optional[str]


# ============================================================================
# Contract Validators - Ensuring Integrity
# ============================================================================

def validate_request(request: Request) -> bool:
    """
    Validate that a request is well-formed.
    
    Returns:
        bool: True if valid, raises ValueError if not
    """
    if not isinstance(request, Request):
        raise ValueError("Request must be a Request instance")
    
    if not request.query or not request.query.strip():
        raise ValueError("Request query cannot be empty")
    
    if not request.frontend:
        raise ValueError("Request must specify a frontend")
    
    return True


def validate_response(response: Response) -> bool:
    """
    Validate that a response is well-formed.
    
    Returns:
        bool: True if valid, raises ValueError if not
    """
    if not isinstance(response, Response):
        raise ValueError("Response must be a Response instance")
    
    if not response.text and not response.error:
        raise ValueError("Response must have either text or error")
    
    if response.error and response.success:
        raise ValueError("Response cannot be successful with an error")
    
    return True


# ============================================================================
# Documentation - Making the Contracts Clear
# ============================================================================

"""
Usage Example:

    # Frontend creates a request
    request = Request(
        query="install firefox",
        frontend="cli",
        context={
            'personality': 'minimal',
            'execute': True,
            'dry_run': False
        }
    )
    
    # Backend processes it
    backend = NixForHumanityBackend()  # implements BackendInterface
    response = backend.process(request)
    
    # Frontend uses the response
    print(response.text)
    for cmd in response.commands:
        print(f"$ {cmd['command']}")
    
    if response.collect_feedback:
        feedback = collect_user_feedback(response)
        backend.learn(feedback)

This is the way. All components speak this language. All tests verify
these contracts. This is our architectural foundation.
"""