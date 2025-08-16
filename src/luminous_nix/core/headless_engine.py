"""Headless engine module."""

from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class Context:
    """Execution context."""
    user_id: str = "default"
    session_id: str = ""
    personality: str = "friendly"
    capabilities: list = None
    execution_mode: str = "dry_run"
    collect_feedback: bool = False

class HeadlessEngine:
    """Headless execution engine."""
    
    def __init__(self):
        self.stats = {}
    
    def process(self, query: str, context: Context) -> Dict[str, Any]:
        return {"success": True, "output": ""}
    
    def collect_feedback(self, session_id: str, feedback: dict) -> bool:
        return True
    
    def get_stats(self) -> dict:
        return self.stats
