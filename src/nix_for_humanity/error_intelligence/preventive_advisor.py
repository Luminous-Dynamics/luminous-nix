"""
Preventive Advisor - Suggests preventive measures before errors occur

This module analyzes user patterns and system state to suggest preventive
actions that can help users avoid common errors before they happen.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from datetime import datetime, timedelta
from enum import Enum
import logging

from .error_analyzer import ErrorCategory, ErrorPattern
from .error_learner import ErrorLearner, ErrorResolution
from ..core.types import Context
from ..xai.causal_engine import CausalXAI

logger = logging.getLogger(__name__)


class PreventionType(Enum):
    """Types of preventive interventions"""
    EDUCATIONAL = "educational"      # Teach about potential issues
    SUGGESTIVE = "suggestive"        # Suggest better alternatives
    PROTECTIVE = "protective"        # Block dangerous actions
    PREPARATORY = "preparatory"      # Prepare system for success


@dataclass
class PreventiveSuggestion:
    """A suggestion to prevent potential errors"""
    id: str
    type: PreventionType
    title: str
    reason: str
    action: str
    confidence: float
    urgency: float = 0.5  # 0-1, how urgent is this
    context_specific: bool = True
    estimated_prevention_value: float = 0.0  # How much trouble this saves


@dataclass
class SystemHealthCheck:
    """Results of a system health check"""
    disk_space_ok: bool
    memory_available: int  # MB
    network_connected: bool
    nixos_channel_updated: bool
    last_update_days: int
    potential_issues: List[str] = field(default_factory=list)


class PreventiveAdvisor:
    """
    Analyzes patterns and context to suggest preventive measures
    before users encounter errors.
    
    Features:
    - Contextual prevention based on current task
    - System health monitoring
    - Pattern-based prediction of likely errors
    - Educational interventions for common mistakes
    """
    
    def __init__(self, error_learner: Optional[ErrorLearner] = None):
        self.error_learner = error_learner
        self.xai_engine = CausalXAI()
        
        # Common prevention patterns
        self._init_prevention_patterns()
        
        # Track recent suggestions to avoid repetition
        self.recent_suggestions: Dict[str, datetime] = {}
        self.suggestion_cooldown = timedelta(hours=24)
    
    def _init_prevention_patterns(self):
        """Initialize common prevention patterns"""
        self.prevention_patterns = {
            "disk_space": {
                "check": self._check_disk_space,
                "threshold": 1024,  # MB
                "suggestion": PreventiveSuggestion(
                    id="low_disk_space",
                    type=PreventionType.PREPARATORY,
                    title="Low disk space detected",
                    reason="Package installations may fail with low disk space",
                    action="Run 'nix-collect-garbage -d' to free up space",
                    confidence=0.9,
                    urgency=0.8,
                    estimated_prevention_value=0.9
                )
            },
            "channel_update": {
                "check": self._check_channel_age,
                "threshold": 30,  # days
                "suggestion": PreventiveSuggestion(
                    id="outdated_channel",
                    type=PreventionType.SUGGESTIVE,
                    title="NixOS channel is outdated",
                    reason="Old channels may have missing or broken packages",
                    action="Update with 'sudo nix-channel --update'",
                    confidence=0.8,
                    urgency=0.5,
                    estimated_prevention_value=0.7
                )
            },
            "memory_low": {
                "check": self._check_memory,
                "threshold": 500,  # MB
                "suggestion": PreventiveSuggestion(
                    id="low_memory",
                    type=PreventionType.PROTECTIVE,
                    title="Low memory available",
                    reason="Complex operations may fail or be very slow",
                    action="Close some applications or add swap space",
                    confidence=0.85,
                    urgency=0.7,
                    estimated_prevention_value=0.8
                )
            }
        }
    
    def analyze_for_prevention(
        self,
        intent: str,
        context: Optional[Context] = None
    ) -> List[PreventiveSuggestion]:
        """
        Analyze current intent and context to suggest preventive measures
        
        Args:
            intent: What the user is trying to do
            context: Current context including system state
        
        Returns:
            List of preventive suggestions sorted by priority
        """
        suggestions = []
        
        # Check system health
        health = self._perform_health_check(context)
        suggestions.extend(self._get_health_suggestions(health))
        
        # Check intent-specific preventions
        intent_suggestions = self._get_intent_specific_suggestions(intent, context)
        suggestions.extend(intent_suggestions)
        
        # Learn from past errors
        if self.error_learner:
            learned_suggestions = self._get_learned_preventions(intent, context)
            suggestions.extend(learned_suggestions)
        
        # Filter out recently shown suggestions
        filtered = self._filter_recent_suggestions(suggestions)
        
        # Sort by priority (urgency * confidence * prevention_value)
        filtered.sort(
            key=lambda s: s.urgency * s.confidence * s.estimated_prevention_value,
            reverse=True
        )
        
        return filtered[:3]  # Top 3 suggestions
    
    def _perform_health_check(self, context: Optional[Context]) -> SystemHealthCheck:
        """Perform a system health check"""
        # In real implementation, these would check actual system state
        # For now, we'll simulate with context data
        
        health = SystemHealthCheck(
            disk_space_ok=True,
            memory_available=2048,
            network_connected=True,
            nixos_channel_updated=True,
            last_update_days=7
        )
        
        # Check each metric
        if context and hasattr(context, 'system_state'):
            state = context.system_state
            
            # Disk space
            if 'disk_free_mb' in state:
                health.disk_space_ok = state['disk_free_mb'] > 1024
                if not health.disk_space_ok:
                    health.potential_issues.append("Low disk space")
            
            # Memory
            if 'memory_free_mb' in state:
                health.memory_available = state['memory_free_mb']
                if health.memory_available < 500:
                    health.potential_issues.append("Low memory")
            
            # Network
            if 'network_connected' in state:
                health.network_connected = state['network_connected']
                if not health.network_connected:
                    health.potential_issues.append("No network connection")
            
            # Channel age
            if 'channel_last_update' in state:
                last_update = datetime.fromisoformat(state['channel_last_update'])
                health.last_update_days = (datetime.now() - last_update).days
                health.nixos_channel_updated = health.last_update_days < 30
                if not health.nixos_channel_updated:
                    health.potential_issues.append("Outdated NixOS channel")
        
        return health
    
    def _get_health_suggestions(
        self,
        health: SystemHealthCheck
    ) -> List[PreventiveSuggestion]:
        """Get suggestions based on system health"""
        suggestions = []
        
        # Check each health metric
        for pattern_id, pattern in self.prevention_patterns.items():
            if pattern_id == "disk_space" and not health.disk_space_ok:
                suggestion = pattern["suggestion"]
                suggestion.context_specific = False
                suggestions.append(suggestion)
            
            elif pattern_id == "channel_update" and not health.nixos_channel_updated:
                suggestion = pattern["suggestion"]
                suggestion.reason = f"Channel hasn't been updated in {health.last_update_days} days"
                suggestion.context_specific = False
                suggestions.append(suggestion)
            
            elif pattern_id == "memory_low" and health.memory_available < 500:
                suggestion = pattern["suggestion"]
                suggestion.reason = f"Only {health.memory_available}MB memory available"
                suggestions.append(suggestion)
        
        return suggestions
    
    def _get_intent_specific_suggestions(
        self,
        intent: str,
        context: Optional[Context]
    ) -> List[PreventiveSuggestion]:
        """Get suggestions specific to the current intent"""
        suggestions = []
        
        # Package installation preventions
        if "install" in intent.lower():
            # Suggest searching first if package name is ambiguous
            if any(word in intent.lower() for word in ["editor", "browser", "player"]):
                suggestions.append(PreventiveSuggestion(
                    id="search_first",
                    type=PreventionType.EDUCATIONAL,
                    title="Search for packages first",
                    reason="Generic terms like 'editor' have many options",
                    action="Try 'search text editor' to see all options",
                    confidence=0.7,
                    urgency=0.3,
                    estimated_prevention_value=0.6
                ))
            
            # Warn about common package name differences
            if "vscode" in intent.lower():
                suggestions.append(PreventiveSuggestion(
                    id="vscode_name",
                    type=PreventionType.EDUCATIONAL,
                    title="VS Code has different package names",
                    reason="VS Code is available as 'vscode' or 'vscodium' (open source)",
                    action="Choose 'vscodium' for fully open source version",
                    confidence=0.9,
                    urgency=0.4,
                    estimated_prevention_value=0.5
                ))
        
        # System update preventions
        elif "update" in intent.lower() or "upgrade" in intent.lower():
            suggestions.append(PreventiveSuggestion(
                id="update_preparation",
                type=PreventionType.PREPARATORY,
                title="Prepare for system update",
                reason="Updates can take time and may require restarts",
                action="Save your work and close important applications",
                confidence=0.8,
                urgency=0.6,
                estimated_prevention_value=0.7
            ))
        
        # Configuration change preventions
        elif "config" in intent.lower() or "configuration.nix" in intent.lower():
            suggestions.append(PreventiveSuggestion(
                id="config_backup",
                type=PreventionType.PROTECTIVE,
                title="Back up configuration before changes",
                reason="Configuration errors can prevent system boot",
                action="Copy /etc/nixos/configuration.nix to a safe location",
                confidence=0.9,
                urgency=0.7,
                estimated_prevention_value=0.9
            ))
        
        return suggestions
    
    def _get_learned_preventions(
        self,
        intent: str,
        context: Optional[Context]
    ) -> List[PreventiveSuggestion]:
        """Get preventions based on learned error patterns"""
        if not self.error_learner:
            return []
        
        suggestions = []
        
        # Get common failures for this type of operation
        warnings = self.error_learner.get_failure_warnings(
            self._intent_to_mock_error(intent)
        )
        
        for i, warning in enumerate(warnings[:2]):  # Top 2 warnings
            suggestions.append(PreventiveSuggestion(
                id=f"learned_prevention_{i}",
                type=PreventionType.EDUCATIONAL,
                title="Common issue warning",
                reason=warning,
                action="Double-check your command or try an alternative approach",
                confidence=0.6,
                urgency=0.5,
                estimated_prevention_value=0.6
            ))
        
        return suggestions
    
    def _intent_to_mock_error(self, intent: str):
        """Convert intent to a mock error for pattern matching"""
        # This is a simplified mapping - real implementation would be more sophisticated
        from .error_analyzer import AnalyzedError
        
        category = ErrorCategory.USER_INPUT  # Default
        if "install" in intent.lower():
            category = ErrorCategory.NOT_FOUND
        elif "permission" in intent.lower() or "sudo" in intent.lower():
            category = ErrorCategory.PERMISSION
        
        return AnalyzedError(
            original_error=intent,
            pattern=None,
            category=category,
            severity=None,
            solutions=[],
            context_factors={}
        )
    
    def _filter_recent_suggestions(
        self,
        suggestions: List[PreventiveSuggestion]
    ) -> List[PreventiveSuggestion]:
        """Filter out recently shown suggestions"""
        filtered = []
        now = datetime.now()
        
        for suggestion in suggestions:
            last_shown = self.recent_suggestions.get(suggestion.id)
            
            # If never shown or cooldown expired
            if not last_shown or (now - last_shown) > self.suggestion_cooldown:
                filtered.append(suggestion)
            # If urgent and cooldown half expired
            elif suggestion.urgency > 0.8 and \
                 (now - last_shown) > (self.suggestion_cooldown / 2):
                filtered.append(suggestion)
        
        # Update recent suggestions
        for suggestion in filtered:
            self.recent_suggestions[suggestion.id] = now
        
        return filtered
    
    def explain_prevention(
        self,
        suggestion: PreventiveSuggestion,
        detail_level: str = "simple"
    ) -> str:
        """
        Explain why a prevention is suggested using XAI
        
        Args:
            suggestion: The preventive suggestion
            detail_level: How detailed the explanation should be
        
        Returns:
            Human-readable explanation
        """
        # Use XAI to explain the causal chain
        causal_explanation = self.xai_engine.explain_prevention(
            prevention_type=suggestion.type.value,
            reason=suggestion.reason,
            estimated_impact=suggestion.estimated_prevention_value
        )
        
        if detail_level == "simple":
            return suggestion.reason
        elif detail_level == "detailed":
            return f"{suggestion.reason} {causal_explanation.simple_explanation}"
        else:  # technical
            return f"{suggestion.reason}\n\nCausal analysis: {causal_explanation.detailed_explanation}"
    
    def should_intervene(
        self,
        suggestion: PreventiveSuggestion,
        user_flow_state: float = 0.5
    ) -> bool:
        """
        Decide whether to show a prevention based on flow state
        
        Args:
            suggestion: The preventive suggestion
            user_flow_state: Current flow state (0-1, higher = deeper flow)
        
        Returns:
            Whether to intervene with the suggestion
        """
        # Calculate intervention threshold based on urgency and flow
        # High flow state = higher threshold needed to interrupt
        threshold = 0.5 + (user_flow_state * 0.3)
        
        # Calculate suggestion score
        score = suggestion.urgency * suggestion.confidence
        
        # Only intervene if score exceeds threshold
        # OR if it's a protective suggestion (always show those)
        return score > threshold or suggestion.type == PreventionType.PROTECTIVE
    
    def format_suggestion_for_ui(
        self,
        suggestion: PreventiveSuggestion,
        ui_type: str = "cli"
    ) -> Dict[str, Any]:
        """Format suggestion for different UI types"""
        base_format = {
            "id": suggestion.id,
            "title": suggestion.title,
            "reason": suggestion.reason,
            "action": suggestion.action,
            "type": suggestion.type.value,
            "urgency": suggestion.urgency
        }
        
        if ui_type == "cli":
            # Simple text format
            base_format["display"] = f"💡 {suggestion.title}\n   {suggestion.action}"
        
        elif ui_type == "tui":
            # Rich format for TUI
            base_format["panel_type"] = "warning" if suggestion.urgency > 0.7 else "info"
            base_format["icon"] = self._get_suggestion_icon(suggestion.type)
            base_format["color"] = self._get_urgency_color(suggestion.urgency)
        
        elif ui_type == "voice":
            # Natural language for voice
            base_format["spoken"] = f"Just a heads up: {suggestion.reason}. " \
                                   f"I suggest you {suggestion.action.lower()}"
        
        return base_format
    
    def _get_suggestion_icon(self, prevention_type: PreventionType) -> str:
        """Get icon for prevention type"""
        icons = {
            PreventionType.EDUCATIONAL: "📚",
            PreventionType.SUGGESTIVE: "💡",
            PreventionType.PROTECTIVE: "🛡️",
            PreventionType.PREPARATORY: "🔧"
        }
        return icons.get(prevention_type, "💡")
    
    def _get_urgency_color(self, urgency: float) -> str:
        """Get color based on urgency"""
        if urgency > 0.8:
            return "red"
        elif urgency > 0.5:
            return "yellow"
        else:
            return "blue"
    
    def _check_disk_space(self, context: Optional[Context]) -> float:
        """Check available disk space in MB"""
        if context and hasattr(context, 'system_state'):
            return context.system_state.get('disk_free_mb', 5000)
        return 5000  # Default assumption
    
    def _check_channel_age(self, context: Optional[Context]) -> int:
        """Check channel age in days"""
        if context and hasattr(context, 'system_state'):
            if 'channel_last_update' in context.system_state:
                last_update = datetime.fromisoformat(
                    context.system_state['channel_last_update']
                )
                return (datetime.now() - last_update).days
        return 7  # Default assumption
    
    def _check_memory(self, context: Optional[Context]) -> int:
        """Check available memory in MB"""
        if context and hasattr(context, 'system_state'):
            return context.system_state.get('memory_free_mb', 2048)
        return 2048  # Default assumption
    
    def get_success_preparation(self, intent: str) -> List[str]:
        """Get preparation steps for successful operation"""
        preparations = []
        
        if "install" in intent.lower():
            preparations.extend([
                "Checking package availability...",
                "Ensuring sufficient disk space...",
                "Verifying network connection..."
            ])
        elif "update" in intent.lower():
            preparations.extend([
                "Checking for configuration syntax errors...",
                "Creating backup of current generation...",
                "Calculating update size..."
            ])
        elif "remove" in intent.lower():
            preparations.extend([
                "Checking package dependencies...",
                "Ensuring no critical services depend on this...",
                "Preparing safe removal..."
            ])
        
        return preparations