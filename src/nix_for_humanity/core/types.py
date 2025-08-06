"""
Core type definitions for Nix for Humanity backend

These types establish the contract between frontend adapters and the backend engine.
All communication flows through these well-defined structures.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum


class PersonalityStyle(Enum):
    """Available personality styles"""
    MINIMAL = "minimal"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    TECHNICAL = "technical"
    SYMBIOTIC = "symbiotic"
    ADAPTIVE = "adaptive"


class ExecutionMode(Enum):
    """How commands should be executed"""
    DRY_RUN = "dry_run"
    EXECUTE = "execute"
    EXPLAIN = "explain"


class IntentType(Enum):
    """Types of intents the system can recognize"""
    INSTALL = "install"
    REMOVE = "remove" 
    UPDATE = "update"
    SEARCH = "search"
    INFO = "info"
    CONFIG = "config"
    ROLLBACK = "rollback"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Recognized intent from user input"""
    type: IntentType
    entities: Dict[str, Any] = field(default_factory=dict)
    target: str = ''
    confidence: float = 1.0
    raw_input: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Context:
    """Request context carrying session and preference information"""
    execute: bool = False                    # Whether to actually execute commands
    dry_run: bool = False                    # Show what would happen without doing it
    personality: str = "friendly"            # Response personality style
    frontend: str = "cli"                    # Which frontend sent the request
    session_id: str = ""                     # Unique session identifier
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            "execute": self.execute,
            "dry_run": self.dry_run,
            "personality": self.personality,
            "frontend": self.frontend,
            "session_id": self.session_id,
            "user_preferences": self.user_preferences
        }


@dataclass
class Request:
    """
    Incoming request from any frontend adapter
    
    This is the primary input structure that all frontends use to communicate
    with the backend engine.
    """
    query: str                               # Natural language query from user
    context: Context = field(default_factory=Context)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary for serialization"""
        return {
            "query": self.query,
            "context": self.context.to_dict(),
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Request":
        """Create request from dictionary"""
        context_data = data.get("context", {})
        context = Context(**context_data) if isinstance(context_data, dict) else Context()
        
        return cls(
            query=data.get("query", ""),
            context=context,
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
        )


@dataclass
class ExecutionResult:
    """Result of executing a command"""
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    duration: float = 0.0  # Execution time in seconds


@dataclass
class Plan:
    """Execution plan for an intent"""
    steps: List[str] = field(default_factory=list)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    requires_sudo: bool = False
    is_destructive: bool = False
    estimated_duration: float = 0.0


@dataclass
class Response:
    """
    Response from backend to frontend
    
    This is the primary output structure that the backend uses to communicate
    results back to any frontend adapter.
    """
    # Core response data
    success: bool = True
    text: str = ""                           # Human-readable response text
    
    # Structured data
    intent: Optional[Intent] = None          # What we understood
    plan: Optional[Plan] = None              # What we plan to do
    result: Optional[ExecutionResult] = None # What happened (if executed)
    
    # Additional information
    commands: List[Dict[str, Any]] = field(default_factory=list)  # Specific commands
    suggestions: List[str] = field(default_factory=list)          # Helpful suggestions
    explanation: str = ""                                          # Why we did what we did
    
    # Metadata
    data: Dict[str, Any] = field(default_factory=dict)           # Additional data
    error: Optional[str] = None                                   # Error message if failed
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization"""
        result = {
            "success": self.success,
            "text": self.text,
            "commands": self.commands,
            "suggestions": self.suggestions,
            "explanation": self.explanation,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }
        
        # Add optional structured data
        if self.intent:
            result["intent"] = {
                "type": self.intent.type.value,
                "entities": self.intent.entities,
                "confidence": self.intent.confidence
            }
        
        if self.plan:
            result["plan"] = {
                "steps": self.plan.steps,
                "commands": self.plan.commands,
                "requires_sudo": self.plan.requires_sudo,
                "is_destructive": self.plan.is_destructive,
                "estimated_duration": self.plan.estimated_duration
            }
        
        if self.result:
            result["result"] = {
                "success": self.result.success,
                "output": self.result.output,
                "error": self.result.error,
                "exit_code": self.result.exit_code,
                "duration": self.result.duration
            }
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Response":
        """Create response from dictionary"""
        # Parse intent if present
        intent = None
        if "intent" in data and data["intent"]:
            intent_data = data["intent"]
            intent = Intent(
                type=IntentType(intent_data["type"]),
                entities=intent_data.get("entities", {}),
                confidence=intent_data.get("confidence", 1.0)
            )
        
        # Parse plan if present
        plan = None
        if "plan" in data and data["plan"]:
            plan_data = data["plan"]
            plan = Plan(**plan_data)
        
        # Parse result if present  
        result = None
        if "result" in data and data["result"]:
            result_data = data["result"]
            result = ExecutionResult(**result_data)
        
        return cls(
            success=data.get("success", True),
            text=data.get("text", ""),
            intent=intent,
            plan=plan,
            result=result,
            commands=data.get("commands", []),
            suggestions=data.get("suggestions", []),
            explanation=data.get("explanation", ""),
            data=data.get("data", {}),
            error=data.get("error"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now()
        )


# Additional helper types

@dataclass
class Command:
    """A single command to execute"""
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    requires_sudo: bool = False
    description: str = ""


@dataclass
class Package:
    """Information about a Nix package"""
    name: str
    attribute: str
    version: str = ""
    description: str = ""
    installed: bool = False


@dataclass
class FeedbackItem:
    """User feedback on a response"""
    response_id: str
    helpful: bool
    comment: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


# Type aliases for common patterns
CommandList = List[Command]
PackageList = List[Package]
ErrorMessage = Optional[str]


@dataclass
class ConversationContext:
    """Context for a conversation session, used by voice interface"""
    persona: str
    interface_type: str
    conversation_id: str

