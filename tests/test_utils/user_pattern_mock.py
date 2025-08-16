"""Mock UserPattern class for tests."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class UserPattern:
    """Mock user pattern for testing."""
    
    pattern_key: str
    input_template: str
    success_count: int = 0
    failure_count: int = 0
    total_count: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}