#!/usr/bin/env python3
"""
Complexity Budget Tracker for Luminous Nix.

Treats simplicity as a finite resource. Every feature has a complexity cost.
To add complexity, you must remove equivalent complexity elsewhere.

This enforces our philosophy: The best code is no code.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class ComplexityItem:
    """A single source of complexity in the system"""
    name: str
    location: str  # File or module
    lines_of_code: int
    dependencies: List[str] = field(default_factory=list)
    cognitive_load: int = 1  # 1-10 scale
    added_date: datetime = field(default_factory=datetime.now)
    justification: str = ""
    
    @property
    def complexity_score(self) -> int:
        """Calculate total complexity units"""
        # Simple formula: lines + (deps * 10) + (cognitive * 50)
        return (
            self.lines_of_code +
            len(self.dependencies) * 10 +
            self.cognitive_load * 50
        )


@dataclass
class SimplificationCredit:
    """Credit earned by removing complexity"""
    description: str
    lines_removed: int
    dependencies_removed: List[str] = field(default_factory=list)
    cognitive_reduction: int = 0
    date: datetime = field(default_factory=datetime.now)
    celebrated: bool = False  # For deletion ceremonies
    
    @property
    def credit_earned(self) -> int:
        """Calculate simplification credits"""
        return (
            self.lines_removed +
            len(self.dependencies_removed) * 10 +
            self.cognitive_reduction * 50
        )


class ComplexityBudgetManager:
    """
    Manages the complexity budget for the project.
    
    Core principle: You have a fixed budget. To add complexity,
    you must remove equivalent complexity elsewhere.
    """
    
    def __init__(self, budget_limit: int = 10000, storage_path: Optional[Path] = None):
        """
        Initialize complexity budget manager.
        
        Args:
            budget_limit: Maximum allowed complexity units
            storage_path: Where to persist budget data
        """
        self.budget_limit = budget_limit
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "complexity_budget.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.complexity_items: Dict[str, ComplexityItem] = {}
        self.simplification_credits: List[SimplificationCredit] = []
        
        self._load_budget()
    
    @property
    def current_complexity(self) -> int:
        """Total complexity units currently in the system"""
        return sum(item.complexity_score for item in self.complexity_items.values())
    
    @property
    def total_credits(self) -> int:
        """Total simplification credits earned"""
        return sum(credit.credit_earned for credit in self.simplification_credits)
    
    @property
    def available_budget(self) -> int:
        """Remaining complexity budget"""
        return self.budget_limit - self.current_complexity + self.total_credits
    
    def propose_addition(
        self,
        name: str,
        location: str,
        lines: int,
        dependencies: List[str] = None,
        cognitive_load: int = 1,
        justification: str = ""
    ) -> Dict[str, any]:
        """
        Propose adding complexity to the system.
        
        Returns:
            Dict with approval status and required simplification
        """
        item = ComplexityItem(
            name=name,
            location=location,
            lines_of_code=lines,
            dependencies=dependencies or [],
            cognitive_load=cognitive_load,
            justification=justification
        )
        
        cost = item.complexity_score
        available = self.available_budget
        
        if cost <= available:
            return {
                'approved': True,
                'cost': cost,
                'available_budget': available,
                'message': f"✅ Approved! Cost: {cost} units, Budget remaining: {available - cost}"
            }
        else:
            deficit = cost - available
            return {
                'approved': False,
                'cost': cost,
                'available_budget': available,
                'deficit': deficit,
                'message': f"❌ Over budget by {deficit} units! Must simplify first.",
                'suggestion': self._suggest_simplification(deficit)
            }
    
    def add_complexity(
        self,
        name: str,
        location: str,
        lines: int,
        dependencies: List[str] = None,
        cognitive_load: int = 1,
        justification: str = ""
    ) -> bool:
        """
        Add complexity to the system (if budget allows).
        
        Returns:
            True if added, False if over budget
        """
        proposal = self.propose_addition(
            name, location, lines, dependencies, cognitive_load, justification
        )
        
        if not proposal['approved']:
            print(proposal['message'])
            if proposal.get('suggestion'):
                print(proposal['suggestion'])
            return False
        
        self.complexity_items[name] = ComplexityItem(
            name=name,
            location=location,
            lines_of_code=lines,
            dependencies=dependencies or [],
            cognitive_load=cognitive_load,
            justification=justification
        )
        
        self._save_budget()
        print(proposal['message'])
        return True
    
    def remove_complexity(
        self,
        item_name: str,
        description: str = ""
    ) -> Optional[SimplificationCredit]:
        """
        Remove complexity and earn simplification credits.
        
        This is what we celebrate in deletion ceremonies!
        """
        if item_name not in self.complexity_items:
            print(f"⚠️ Item '{item_name}' not found in complexity tracking")
            return None
        
        item = self.complexity_items.pop(item_name)
        
        credit = SimplificationCredit(
            description=description or f"Removed {item_name}",
            lines_removed=item.lines_of_code,
            dependencies_removed=item.dependencies,
            cognitive_reduction=item.cognitive_load
        )
        
        self.simplification_credits.append(credit)
        self._save_budget()
        
        print(f"🎉 Earned {credit.credit_earned} simplification credits!")
        print(f"   Removed {credit.lines_removed} lines")
        if credit.dependencies_removed:
            print(f"   Eliminated {len(credit.dependencies_removed)} dependencies")
        
        return credit
    
    def deletion_ceremony(self) -> str:
        """
        Celebrate recent simplifications!
        
        Returns ceremony report for the team.
        """
        uncelebrated = [c for c in self.simplification_credits if not c.celebrated]
        
        if not uncelebrated:
            return "No new simplifications to celebrate"
        
        total_lines = sum(c.lines_removed for c in uncelebrated)
        total_deps = sum(len(c.dependencies_removed) for c in uncelebrated)
        total_credits = sum(c.credit_earned for c in uncelebrated)
        
        ceremony = f"""
🎊 DELETION CEREMONY 🎊
{'=' * 40}

We gather to celebrate the code that is no more!

📊 Achievements:
  • Lines deleted: {total_lines}
  • Dependencies removed: {total_deps}
  • Complexity credits earned: {total_credits}
  
🏆 Simplifications:
"""
        
        for credit in uncelebrated:
            ceremony += f"\n  ✨ {credit.description}"
            ceremony += f"\n     -{credit.lines_removed} lines"
            credit.celebrated = True
        
        ceremony += f"""

💡 Remember: "The best code is no code."

New Available Budget: {self.available_budget} units
{'=' * 40}
"""
        
        self._save_budget()
        return ceremony
    
    def report(self) -> str:
        """Generate complexity budget report"""
        report = f"""
📊 Complexity Budget Report
{'=' * 40}

Budget Limit: {self.budget_limit} units
Current Usage: {self.current_complexity} units
Credits Earned: {self.total_credits} units
Available: {self.available_budget} units

Progress Bar:
[{'█' * (self.current_complexity // 500)}{'░' * ((self.budget_limit - self.current_complexity) // 500)}]
{self.current_complexity}/{self.budget_limit}

Top Complexity Sources:
"""
        
        # Sort by complexity score
        sorted_items = sorted(
            self.complexity_items.values(),
            key=lambda x: x.complexity_score,
            reverse=True
        )[:5]
        
        for item in sorted_items:
            report += f"\n  • {item.name}: {item.complexity_score} units"
            report += f"\n    {item.location} ({item.lines_of_code} lines)"
        
        if self.available_budget < 1000:
            report += "\n\n⚠️ WARNING: Budget running low! Time for a Simplicity Sprint!"
        
        return report
    
    def _suggest_simplification(self, deficit: int) -> str:
        """Suggest what could be simplified to make room"""
        candidates = sorted(
            self.complexity_items.values(),
            key=lambda x: x.complexity_score,
            reverse=True
        )
        
        suggestion = "\n💡 Simplification opportunities:\n"
        running_total = 0
        
        for item in candidates:
            if running_total >= deficit:
                break
            suggestion += f"  • Simplify {item.name} ({item.complexity_score} units)\n"
            running_total += item.complexity_score
        
        return suggestion
    
    def _save_budget(self):
        """Persist budget to disk"""
        data = {
            'budget_limit': self.budget_limit,
            'items': {
                name: {
                    'location': item.location,
                    'lines': item.lines_of_code,
                    'dependencies': item.dependencies,
                    'cognitive_load': item.cognitive_load,
                    'added_date': item.added_date.isoformat(),
                    'justification': item.justification
                }
                for name, item in self.complexity_items.items()
            },
            'credits': [
                {
                    'description': c.description,
                    'lines_removed': c.lines_removed,
                    'dependencies_removed': c.dependencies_removed,
                    'cognitive_reduction': c.cognitive_reduction,
                    'date': c.date.isoformat(),
                    'celebrated': c.celebrated
                }
                for c in self.simplification_credits
            ]
        }
        
        self.storage_path.write_text(json.dumps(data, indent=2))
    
    def _load_budget(self):
        """Load budget from disk"""
        if not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            self.budget_limit = data.get('budget_limit', self.budget_limit)
            
            # Load complexity items
            for name, item_data in data.get('items', {}).items():
                self.complexity_items[name] = ComplexityItem(
                    name=name,
                    location=item_data['location'],
                    lines_of_code=item_data['lines'],
                    dependencies=item_data.get('dependencies', []),
                    cognitive_load=item_data.get('cognitive_load', 1),
                    added_date=datetime.fromisoformat(item_data['added_date']),
                    justification=item_data.get('justification', '')
                )
            
            # Load credits
            for credit_data in data.get('credits', []):
                self.simplification_credits.append(SimplificationCredit(
                    description=credit_data['description'],
                    lines_removed=credit_data['lines_removed'],
                    dependencies_removed=credit_data.get('dependencies_removed', []),
                    cognitive_reduction=credit_data.get('cognitive_reduction', 0),
                    date=datetime.fromisoformat(credit_data['date']),
                    celebrated=credit_data.get('celebrated', False)
                ))
        except Exception as e:
            print(f"Warning: Could not load budget: {e}")


# Global instance
_budget_manager = ComplexityBudgetManager()

def check_budget(name: str, lines: int, deps: List[str] = None) -> bool:
    """Quick function to check if we have budget for a feature"""
    proposal = _budget_manager.propose_addition(name, "unknown", lines, deps)
    print(proposal['message'])
    return proposal['approved']


# Example usage
if __name__ == "__main__":
    manager = ComplexityBudgetManager(budget_limit=5000)
    
    # Try to add complexity
    manager.add_complexity(
        "fancy_ml_system",
        "ml/predictor.py",
        lines=1500,
        dependencies=["tensorflow", "numpy", "pandas"],
        cognitive_load=8,
        justification="Predicts user intent"
    )
    
    # Check budget
    print(manager.report())
    
    # Remove something
    manager.remove_complexity("fancy_ml_system", "Replaced with simple pattern matching")
    
    # Celebrate!
    print(manager.deletion_ceremony())