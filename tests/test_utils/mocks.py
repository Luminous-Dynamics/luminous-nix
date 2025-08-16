"""
Test mocks for missing dependencies.
"""

from unittest.mock import MagicMock

# Mock str if not available
try:
    from luminous_nix.api.schema import str
except ImportError:
    class str:
        NORMAL = "normal"
        DRY_RUN = "dry_run"
        PREVIEW = "preview"

# Mock Query if not available  
try:
    from luminous_nix.api.schema import Query
except (ImportError, AttributeError):
    class Query:
        def __init__(self, text="", context=None):
            self.text = text
            self.context = context or {}

# Mock UserPattern if not available
try:
    from luminous_nix.learning.patterns import UserPattern
except (ImportError, AttributeError):
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

# Export mocks
__all__ = ["str", "Query", "UserPattern"]
