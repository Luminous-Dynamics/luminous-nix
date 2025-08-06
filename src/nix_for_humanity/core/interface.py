# Core Interface Definitions
"""
Defines the interface between the headless core and frontend adapters
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime


class ExecutionMode(Enum):
    """How commands should be executed"""
    DRY_RUN = "dry_run"
    EXECUTE = "execute"
    EXPLAIN = "explain"


# IntentType, Intent, Command, and Response moved to types.py to avoid duplicates
# Import them from types if needed in this module
from .types import IntentType, Intent, Command, Response


@dataclass
class Query:
    """Input query from any frontend"""
    text: str
    context: Optional[Dict[str, Any]] = None
    personality: str = "adaptive"
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    mode: ExecutionMode = ExecutionMode.DRY_RUN
    timestamp: datetime = field(default_factory=datetime.now)


# Command and Response classes moved to types.py to avoid conflicts