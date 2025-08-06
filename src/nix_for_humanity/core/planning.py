# Planning Types
"""
Types for the plan/execute separation in the core engine
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from .types import Intent, Command, ExecutionResult
import uuid  # For plan_id generation


@dataclass
class Plan:
    """
    A planned action that can be shown to the user before execution.
    This separates "thinking" from "doing".
    """
    # What we'll show the user
    text: str
    intent: Intent
    
    # What we'll do if approved
    command: Optional[Command] = None
    
    # Additional context
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 1.0
    requires_confirmation: bool = False
    
    # Metadata
    planned_at: datetime = field(default_factory=datetime.now)
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


# ExecutionResult is now imported from types.py to avoid duplication