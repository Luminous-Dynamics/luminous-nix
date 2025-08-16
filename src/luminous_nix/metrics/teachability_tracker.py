#!/usr/bin/env python3
"""
Teachability Tracker - Quantifying the Disappearing Path.

Tracks the Autonomous Success Rate (ASR) for each feature to measure
how well we're teaching users to not need us.

When ASR approaches 100%, the feature has successfully taught its users.
This is the quantifiable measure of the "Disappearing Path" philosophy.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

@dataclass
class FeatureUsage:
    """Track a single usage of a feature"""
    timestamp: datetime
    used_scaffold: bool  # Did they need help/hints/wizards?
    succeeded: bool      # Did they complete the task?
    user_id: Optional[str] = None  # Anonymous ID for tracking learning curves
    
@dataclass
class FeatureTeachability:
    """Track teachability metrics for a feature"""
    name: str
    introduced: datetime = field(default_factory=datetime.now)
    total_uses: int = 0
    autonomous_successes: int = 0  # Succeeded without scaffold
    scaffold_uses: int = 0         # Times scaffold was shown
    failures: int = 0               # Failed attempts
    
    @property
    def autonomous_success_rate(self) -> float:
        """Calculate ASR: % of successful uses without scaffold"""
        if self.total_uses == 0:
            return 0.0
        return (self.autonomous_successes / self.total_uses) * 100
    
    @property
    def learning_curve(self) -> str:
        """Interpret the learning curve"""
        asr = self.autonomous_success_rate
        
        if asr < 20:
            return "🌱 Early Learning - Heavy scaffold needed"
        elif asr < 40:
            return "📈 Growing - Users starting to understand"
        elif asr < 60:
            return "🎯 Progressing - Approaching independence"
        elif asr < 80:
            return "💪 Strong - Most users autonomous"
        elif asr < 95:
            return "🌟 Excellent - Nearly invisible"
        else:
            return "✨ Transcendent - Feature teaches perfectly"
    
    @property
    def disappearing_score(self) -> float:
        """
        Score how well this feature embodies the Disappearing Path.
        100 = Perfect (users never need help after learning)
        0 = Failed (users always need help)
        """
        if self.total_uses < 10:
            return 0.0  # Not enough data
        
        # Weight recent usage more heavily (assumes chronological tracking)
        return self.autonomous_success_rate


class TeachabilityTracker:
    """
    Track how well features teach users to not need them.
    
    The ultimate goal: Every feature should have an ASR approaching 100%,
    meaning users have learned to use it without assistance.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize teachability tracker"""
        self.storage_path = storage_path or Path.home() / ".luminous-nix" / "teachability.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.features: Dict[str, FeatureTeachability] = {}
        self.usage_history: Dict[str, List[FeatureUsage]] = defaultdict(list)
        
        self._load_data()
    
    def track_usage(
        self,
        feature_name: str,
        used_scaffold: bool,
        succeeded: bool,
        user_id: Optional[str] = None
    ) -> FeatureTeachability:
        """
        Track a single feature usage.
        
        Args:
            feature_name: Name of the feature used
            used_scaffold: Whether help/hints/wizard was shown
            succeeded: Whether the user completed the task
            user_id: Optional anonymous user ID for tracking individual learning
        
        Returns:
            Updated feature teachability metrics
        """
        # Create feature if new
        if feature_name not in self.features:
            self.features[feature_name] = FeatureTeachability(name=feature_name)
        
        feature = self.features[feature_name]
        
        # Update metrics
        feature.total_uses += 1
        
        if succeeded and not used_scaffold:
            feature.autonomous_successes += 1
        elif used_scaffold:
            feature.scaffold_uses += 1
        
        if not succeeded:
            feature.failures += 1
        
        # Track usage history
        usage = FeatureUsage(
            timestamp=datetime.now(),
            used_scaffold=used_scaffold,
            succeeded=succeeded,
            user_id=user_id
        )
        self.usage_history[feature_name].append(usage)
        
        # Limit history to last 1000 uses per feature
        if len(self.usage_history[feature_name]) > 1000:
            self.usage_history[feature_name] = self.usage_history[feature_name][-1000:]
        
        self._save_data()
        return feature
    
    def get_asr(self, feature_name: str) -> float:
        """Get Autonomous Success Rate for a feature"""
        if feature_name in self.features:
            return self.features[feature_name].autonomous_success_rate
        return 0.0
    
    def get_user_learning_curve(self, feature_name: str, user_id: str) -> Dict:
        """Track an individual user's learning curve for a feature"""
        if feature_name not in self.usage_history:
            return {"uses": 0, "asr": 0.0, "improving": False}
        
        user_uses = [
            u for u in self.usage_history[feature_name]
            if u.user_id == user_id
        ]
        
        if not user_uses:
            return {"uses": 0, "asr": 0.0, "improving": False}
        
        total = len(user_uses)
        autonomous = sum(1 for u in user_uses if u.succeeded and not u.used_scaffold)
        
        # Check if improving (compare first half to second half)
        if total >= 4:
            mid = total // 2
            first_half_asr = sum(1 for u in user_uses[:mid] if u.succeeded and not u.used_scaffold) / mid
            second_half_asr = sum(1 for u in user_uses[mid:] if u.succeeded and not u.used_scaffold) / (total - mid)
            improving = second_half_asr > first_half_asr
        else:
            improving = False
        
        return {
            "uses": total,
            "asr": (autonomous / total) * 100,
            "improving": improving
        }
    
    def calculate_simplicity_score(self) -> float:
        """
        Calculate overall Simplicity Score for the project.
        
        Simplicity Score = (User Value Delivered) / (Codebase Complexity)
        
        For this component, we provide the User Value side through ASR.
        """
        if not self.features:
            return 100.0  # No features = perfect simplicity
        
        # Average ASR across all features (weighted by usage)
        total_uses = sum(f.total_uses for f in self.features.values())
        if total_uses == 0:
            return 100.0
        
        weighted_asr = sum(
            f.autonomous_success_rate * f.total_uses
            for f in self.features.values()
        ) / total_uses
        
        return weighted_asr
    
    def report(self) -> str:
        """Generate teachability report"""
        if not self.features:
            return "No features tracked yet. Start using the system!"
        
        report = """
📊 Teachability Report - The Disappearing Path
================================================

Overall Simplicity Score: {:.1f}%

Feature Teachability Rankings:
""".format(self.calculate_simplicity_score())
        
        # Sort by ASR
        sorted_features = sorted(
            self.features.values(),
            key=lambda f: f.autonomous_success_rate,
            reverse=True
        )
        
        for feature in sorted_features[:10]:
            report += f"""
📌 {feature.name}
   ASR: {feature.autonomous_success_rate:.1f}%
   Status: {feature.learning_curve}
   Total Uses: {feature.total_uses}
   Autonomous: {feature.autonomous_successes}
   Scaffolded: {feature.scaffold_uses}
"""
        
        # Identify features needing attention
        struggling = [f for f in self.features.values() if f.autonomous_success_rate < 30 and f.total_uses > 20]
        if struggling:
            report += "\n⚠️ Features Needing Simplification:\n"
            for feature in struggling:
                report += f"  • {feature.name}: Only {feature.autonomous_success_rate:.1f}% autonomous\n"
        
        # Celebrate successes
        transcendent = [f for f in self.features.values() if f.autonomous_success_rate > 95 and f.total_uses > 50]
        if transcendent:
            report += "\n🎉 Transcendent Features (Users Don't Need Help!):\n"
            for feature in transcendent:
                report += f"  • {feature.name}: {feature.autonomous_success_rate:.1f}% autonomous!\n"
        
        report += """
================================================
Goal: Every feature should approach 100% ASR
This means users have learned to not need our help.
"""
        
        return report
    
    def _save_data(self):
        """Persist data to disk"""
        data = {
            'features': {
                name: {
                    'introduced': f.introduced.isoformat(),
                    'total_uses': f.total_uses,
                    'autonomous_successes': f.autonomous_successes,
                    'scaffold_uses': f.scaffold_uses,
                    'failures': f.failures
                }
                for name, f in self.features.items()
            },
            'usage_history': {
                name: [
                    {
                        'timestamp': u.timestamp.isoformat(),
                        'used_scaffold': u.used_scaffold,
                        'succeeded': u.succeeded,
                        'user_id': u.user_id
                    }
                    for u in uses
                ]
                for name, uses in self.usage_history.items()
            }
        }
        
        self.storage_path.write_text(json.dumps(data, indent=2))
    
    def _load_data(self):
        """Load data from disk"""
        if not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text())
            
            # Load features
            for name, f_data in data.get('features', {}).items():
                self.features[name] = FeatureTeachability(
                    name=name,
                    introduced=datetime.fromisoformat(f_data['introduced']),
                    total_uses=f_data['total_uses'],
                    autonomous_successes=f_data['autonomous_successes'],
                    scaffold_uses=f_data['scaffold_uses'],
                    failures=f_data.get('failures', 0)
                )
            
            # Load usage history
            for name, uses in data.get('usage_history', {}).items():
                for u_data in uses:
                    self.usage_history[name].append(FeatureUsage(
                        timestamp=datetime.fromisoformat(u_data['timestamp']),
                        used_scaffold=u_data['used_scaffold'],
                        succeeded=u_data['succeeded'],
                        user_id=u_data.get('user_id')
                    ))
        except Exception as e:
            print(f"Warning: Could not load teachability data: {e}")


# Global instance
_tracker = TeachabilityTracker()

def track(feature: str, scaffold: bool, success: bool, user: str = None) -> str:
    """Quick function to track feature teachability"""
    metrics = _tracker.track_usage(feature, scaffold, success, user)
    return f"ASR: {metrics.autonomous_success_rate:.1f}% - {metrics.learning_curve}"


# Example usage
if __name__ == "__main__":
    # Simulate usage patterns
    print("Simulating feature usage...\n")
    
    # New users need scaffold
    for i in range(5):
        print(track("package_install", scaffold=True, success=True, user=f"user_{i}"))
    
    # Some users learning
    for i in range(5):
        print(track("package_install", scaffold=False, success=True, user=f"user_{i}"))
    
    # More experienced users
    for i in range(10):
        print(track("package_install", scaffold=False, success=True, user=f"user_{i%5}"))
    
    print("\n" + _tracker.report())