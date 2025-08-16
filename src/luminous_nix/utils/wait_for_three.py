#!/usr/bin/env python3
"""
The "Wait for Three" Rule Implementation.

Prevents premature abstraction by tracking patterns and only suggesting
generalization after seeing three distinct examples.

Based on the principle: "Don't generalize from one example. Wait for three."
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

@dataclass
class PatternExample:
    """A single example of a pattern"""
    code_snippet: str
    file_path: str
    timestamp: datetime
    context: str = ""
    
@dataclass 
class Pattern:
    """A pattern being tracked"""
    name: str
    description: str
    examples: List[PatternExample] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def count(self) -> int:
        """Number of examples seen"""
        return len(self.examples)
    
    @property
    def is_ready(self) -> bool:
        """Ready for generalization (3+ examples)"""
        return self.count >= 3


class WaitForThreeTracker:
    """
    Tracks patterns and prevents premature abstraction.
    
    Simple rule: Don't create abstractions until you see the pattern THREE times.
    This prevents over-engineering and ensures we only generalize real patterns.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize pattern tracker.
        
        Args:
            storage_path: Where to persist patterns (optional)
        """
        self.patterns: Dict[str, Pattern] = {}
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "patterns.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_patterns()
    
    def track_pattern(
        self, 
        pattern_name: str, 
        code_snippet: str,
        file_path: str,
        context: str = "",
        description: str = ""
    ) -> Pattern:
        """
        Track an instance of a pattern.
        
        Args:
            pattern_name: Name of the pattern (e.g., "error_handling")
            code_snippet: The code exhibiting the pattern
            file_path: Where this pattern was seen
            context: Additional context
            description: Pattern description (used on first occurrence)
            
        Returns:
            The updated pattern
        """
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = Pattern(
                name=pattern_name,
                description=description or f"Pattern: {pattern_name}"
            )
        
        pattern = self.patterns[pattern_name]
        
        # Check if this is a duplicate
        for example in pattern.examples:
            if example.code_snippet == code_snippet and example.file_path == file_path:
                return pattern  # Don't add duplicates
        
        # Add new example
        pattern.examples.append(PatternExample(
            code_snippet=code_snippet,
            file_path=file_path,
            timestamp=datetime.now(),
            context=context
        ))
        
        self._save_patterns()
        return pattern
    
    def check_pattern(self, pattern_name: str) -> Optional[Pattern]:
        """
        Check if a pattern is ready for abstraction.
        
        Returns None if pattern doesn't exist or has < 3 examples.
        """
        pattern = self.patterns.get(pattern_name)
        if pattern and pattern.is_ready:
            return pattern
        return None
    
    def get_ready_patterns(self) -> List[Pattern]:
        """Get all patterns ready for abstraction (3+ examples)"""
        return [p for p in self.patterns.values() if p.is_ready]
    
    def get_waiting_patterns(self) -> List[Pattern]:
        """Get patterns still waiting for more examples"""
        return [p for p in self.patterns.values() if not p.is_ready]
    
    def suggest_abstraction(self, pattern_name: str) -> Optional[str]:
        """
        Suggest an abstraction if pattern is ready.
        
        Returns:
            Suggestion string or None if not ready
        """
        pattern = self.check_pattern(pattern_name)
        if not pattern:
            remaining = 3 - (self.patterns.get(pattern_name, Pattern("", "")).count)
            return f"⏳ Need {remaining} more examples before abstracting '{pattern_name}'"
        
        suggestion = f"""
✅ Pattern '{pattern_name}' is ready for abstraction!

Found {pattern.count} examples:
"""
        for i, example in enumerate(pattern.examples[:3], 1):
            suggestion += f"\n{i}. {example.file_path} ({example.timestamp.strftime('%Y-%m-%d')})"
        
        suggestion += f"""

Consider creating a shared abstraction that:
1. Captures the common pattern
2. Remains simple and composable  
3. Has a clear, single responsibility

Remember: The abstraction should make the code simpler, not just shorter.
"""
        return suggestion
    
    def report(self) -> str:
        """Generate a status report of all tracked patterns"""
        ready = self.get_ready_patterns()
        waiting = self.get_waiting_patterns()
        
        report = "📊 Pattern Tracking Report\n"
        report += "=" * 40 + "\n\n"
        
        if ready:
            report += f"✅ Ready for Abstraction ({len(ready)} patterns):\n"
            for pattern in ready:
                report += f"  • {pattern.name}: {pattern.count} examples\n"
            report += "\n"
        
        if waiting:
            report += f"⏳ Waiting for More Examples ({len(waiting)} patterns):\n"
            for pattern in waiting:
                report += f"  • {pattern.name}: {pattern.count}/3 examples\n"
        
        if not ready and not waiting:
            report += "No patterns tracked yet.\n"
        
        report += "\n" + "=" * 40
        report += "\nRemember: Wait for THREE before abstracting!"
        
        return report
    
    def _save_patterns(self):
        """Persist patterns to disk"""
        data = {}
        for name, pattern in self.patterns.items():
            data[name] = {
                'description': pattern.description,
                'created_at': pattern.created_at.isoformat(),
                'examples': [
                    {
                        'code_snippet': ex.code_snippet,
                        'file_path': ex.file_path,
                        'timestamp': ex.timestamp.isoformat(),
                        'context': ex.context
                    }
                    for ex in pattern.examples
                ]
            }
        
        self.storage_path.write_text(json.dumps(data, indent=2))
    
    def _load_patterns(self):
        """Load patterns from disk"""
        if not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            for name, pattern_data in data.items():
                pattern = Pattern(
                    name=name,
                    description=pattern_data['description'],
                    created_at=datetime.fromisoformat(pattern_data['created_at'])
                )
                
                for ex_data in pattern_data['examples']:
                    pattern.examples.append(PatternExample(
                        code_snippet=ex_data['code_snippet'],
                        file_path=ex_data['file_path'],
                        timestamp=datetime.fromisoformat(ex_data['timestamp']),
                        context=ex_data.get('context', '')
                    ))
                
                self.patterns[name] = pattern
        except Exception as e:
            print(f"Warning: Could not load patterns: {e}")


# Global instance for easy access
_tracker = WaitForThreeTracker()

def track(pattern_name: str, code: str, file: str, context: str = "") -> str:
    """
    Quick function to track a pattern.
    
    Returns a message about the pattern status.
    """
    pattern = _tracker.track_pattern(pattern_name, code, file, context)
    
    if pattern.is_ready:
        return f"✅ Pattern '{pattern_name}' has {pattern.count} examples - ready for abstraction!"
    else:
        remaining = 3 - pattern.count
        return f"📝 Pattern '{pattern_name}' tracked ({pattern.count}/3). Need {remaining} more examples."


# Example usage
if __name__ == "__main__":
    # Track some patterns
    print(track("error_formatting", 
                "f'Error: {e}'", 
                "module1.py",
                "Formatting user-facing errors"))
    
    print(track("error_formatting",
                "f'Failed: {error}'",
                "module2.py", 
                "Another error format"))
    
    print(track("error_formatting",
                "f'Oops: {msg}'",
                "module3.py",
                "Third error format"))
    
    # Check if ready
    suggestion = _tracker.suggest_abstraction("error_formatting")
    if suggestion:
        print(suggestion)
    
    # Generate report
    print("\n" + _tracker.report())