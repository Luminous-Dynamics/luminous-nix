#!/usr/bin/env python3
"""
The Simplicity Score - Our North Star Metric.

Simplicity Score = (User Value Delivered) / (Codebase Complexity)

This beautifully resolves the User Simplicity Paradox by balancing
both sides of the equation. We win by simultaneously increasing 
user value while decreasing complexity.
"""

import subprocess
from pathlib import Path
from typing import Dict, Optional
from .teachability_tracker import TeachabilityTracker
from ..utils.complexity_budget import ComplexityBudgetManager
from ..cli.friction_dashboard_simple import show_session_summary
import json

class SimplicityScoreCalculator:
    """
    Calculate the ultimate metric for Luminous Nix.
    
    This score captures our entire philosophy in a single number:
    - High user value (low friction, high teachability, satisfaction)
    - Low codebase complexity (fewer lines, dependencies, cognitive load)
    """
    
    def __init__(self):
        """Initialize calculators for all components"""
        self.teachability = TeachabilityTracker()
        self.complexity = ComplexityBudgetManager()
        self.session_file = Path.home() / ".luminous-nix" / "current_session.json"
    
    def calculate_user_value(self) -> Dict[str, float]:
        """
        Calculate composite user value delivered.
        
        Components:
        - Friction Score (inverted) - Lower friction = higher value
        - Autonomous Success Rate - Higher ASR = higher value
        - User Satisfaction - Would need user surveys (placeholder)
        """
        components = {}
        
        # 1. Friction Score (inverted to become value)
        friction = self._get_friction_score()
        components['friction_value'] = (1.0 - friction) * 100
        
        # 2. Autonomous Success Rate (teachability)
        components['teachability'] = self.teachability.calculate_simplicity_score()
        
        # 3. User Satisfaction (placeholder - would come from surveys)
        components['satisfaction'] = 85.0  # Placeholder
        
        # Weighted average
        weights = {
            'friction_value': 0.4,
            'teachability': 0.4,
            'satisfaction': 0.2
        }
        
        components['total'] = sum(
            components[key] * weights.get(key, 0)
            for key in ['friction_value', 'teachability', 'satisfaction']
        )
        
        return components
    
    def calculate_codebase_complexity(self) -> Dict[str, float]:
        """
        Calculate normalized codebase complexity.
        
        Components:
        - Lines of Code (via cloc)
        - Dependencies count
        - Cognitive complexity from budget tracker
        """
        components = {}
        
        # 1. Lines of Code (normalized to 0-100 scale)
        loc = self._count_lines_of_code()
        # Assume 10,000 lines = complexity score of 100
        components['lines_complexity'] = min(100, (loc / 10000) * 100)
        
        # 2. Dependencies (normalized)
        deps = self._count_dependencies()
        # Assume 50 deps = complexity score of 100
        components['deps_complexity'] = min(100, (deps / 50) * 100)
        
        # 3. Cognitive complexity from budget
        budget_usage = (self.complexity.current_complexity / self.complexity.budget_limit) * 100
        components['cognitive_complexity'] = budget_usage
        
        # Weighted average
        weights = {
            'lines_complexity': 0.4,
            'deps_complexity': 0.3,
            'cognitive_complexity': 0.3
        }
        
        components['total'] = sum(
            components[key] * weights.get(key, 0)
            for key in ['lines_complexity', 'deps_complexity', 'cognitive_complexity']
        )
        
        return components
    
    def calculate_simplicity_score(self) -> Dict[str, any]:
        """
        Calculate the final Simplicity Score.
        
        Higher is better - means more value with less complexity.
        """
        user_value = self.calculate_user_value()
        complexity = self.calculate_codebase_complexity()
        
        # Avoid division by zero
        complexity_total = max(1, complexity['total'])
        
        # The magic formula
        simplicity_score = (user_value['total'] / complexity_total) * 100
        
        return {
            'score': simplicity_score,
            'user_value': user_value,
            'complexity': complexity,
            'interpretation': self._interpret_score(simplicity_score)
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret what the score means"""
        if score < 50:
            return "⚠️ Complexity exceeds value - time for Simplicity Sprint!"
        elif score < 75:
            return "📊 Balanced - room for improvement"
        elif score < 100:
            return "✨ Good - delivering value efficiently"
        elif score < 150:
            return "🌟 Excellent - high value, low complexity"
        else:
            return "🚀 Transcendent - achieving sophisticated simplicity!"
    
    def _get_friction_score(self) -> float:
        """Get current friction score from session"""
        if not self.session_file.exists():
            return 0.0
        
        try:
            with open(self.session_file) as f:
                data = json.load(f)
            
            total = data.get('total_actions', 0)
            if total == 0:
                return 0.0
            
            errors = data.get('error_count', 0)
            helps = data.get('help_count', 0)
            undos = data.get('undo_count', 0)
            
            return (errors + helps * 0.5 + undos * 0.3) / max(1, total)
        except:
            return 0.0
    
    def _count_lines_of_code(self) -> int:
        """Count lines of Python code (simple version)"""
        try:
            # Use cloc if available, otherwise simple count
            result = subprocess.run(
                ['cloc', '--json', 'src/'],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent.parent  # Project root
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                return data.get('Python', {}).get('code', 0)
        except:
            pass
        
        # Fallback: simple line count
        try:
            src_dir = Path(__file__).parent.parent
            total = 0
            for py_file in src_dir.rglob('*.py'):
                total += len(py_file.read_text().splitlines())
            return total
        except:
            return 5000  # Reasonable estimate
    
    def _count_dependencies(self) -> int:
        """Count Python dependencies"""
        try:
            pyproject = Path(__file__).parent.parent.parent / 'pyproject.toml'
            if pyproject.exists():
                content = pyproject.read_text()
                # Simple count of dependencies (not perfect but good enough)
                import re
                deps = re.findall(r'^[a-zA-Z0-9-_]+\s*=', content, re.MULTILINE)
                return len(deps)
        except:
            pass
        
        return 10  # Reasonable estimate
    
    def report(self) -> str:
        """Generate comprehensive Simplicity Score report"""
        result = self.calculate_simplicity_score()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║           🌟 SIMPLICITY SCORE REPORT 🌟                  ║
╚══════════════════════════════════════════════════════════╝

Overall Score: {result['score']:.1f}
Status: {result['interpretation']}

┌─────────────────────────────────────────────────────────┐
│ USER VALUE DELIVERED: {result['user_value']['total']:.1f}%                       │
├─────────────────────────────────────────────────────────┤
│ • Friction Reduction:  {result['user_value']['friction_value']:.1f}%             │
│ • Teachability (ASR):  {result['user_value']['teachability']:.1f}%               │
│ • User Satisfaction:   {result['user_value']['satisfaction']:.1f}%               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ CODEBASE COMPLEXITY: {result['complexity']['total']:.1f}%                        │
├─────────────────────────────────────────────────────────┤
│ • Lines of Code:       {result['complexity']['lines_complexity']:.1f}%           │
│ • Dependencies:        {result['complexity']['deps_complexity']:.1f}%            │
│ • Cognitive Load:      {result['complexity']['cognitive_complexity']:.1f}%       │
└─────────────────────────────────────────────────────────┘

Formula: Simplicity Score = User Value / Complexity × 100

📈 Progress Bar:
[{'=' * int(result['score'] / 10)}{'·' * (20 - int(result['score'] / 10))}]

💡 Recommendations:
"""
        
        if result['complexity']['total'] > 70:
            report += "• Schedule a Simplicity Sprint - complexity is high\n"
        
        if result['user_value']['friction_value'] < 60:
            report += "• Focus on reducing friction in common workflows\n"
        
        if result['user_value']['teachability'] < 70:
            report += "• Improve feature teachability to increase ASR\n"
        
        if result['score'] > 150:
            report += "• 🎉 Celebrate! You're achieving sophisticated simplicity!\n"
        
        report += """
═══════════════════════════════════════════════════════════
Goal: Maximize value while minimizing complexity
Target: Simplicity Score > 150 (Transcendent)
═══════════════════════════════════════════════════════════
"""
        
        return report
    
    def dashboard(self) -> str:
        """Quick dashboard view"""
        result = self.calculate_simplicity_score()
        
        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  SIMPLICITY SCORE: {result['score']:3.0f} ┃
┃  {result['interpretation'][:20]:<20} ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
User Value: {result['user_value']['total']:.0f}% | Complexity: {result['complexity']['total']:.0f}%
"""


# Global instance
_calculator = SimplicityScoreCalculator()

def get_score() -> float:
    """Quick function to get current simplicity score"""
    return _calculator.calculate_simplicity_score()['score']

def show_dashboard():
    """Display quick dashboard"""
    print(_calculator.dashboard())

def show_report():
    """Display full report"""
    print(_calculator.report())


# Example usage
if __name__ == "__main__":
    calculator = SimplicityScoreCalculator()
    print(calculator.report())