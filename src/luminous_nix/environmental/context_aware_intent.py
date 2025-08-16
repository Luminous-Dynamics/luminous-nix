"""
Context-aware intent recognition that understands user queries
based on current system state.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple

from .system_monitor import SystemMonitor
from .predictive_assistant import PredictiveAssistant

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Enhanced intent types with context awareness"""
    # Package operations
    INSTALL = "install"
    REMOVE = "remove"
    SEARCH = "search"
    UPDATE = "update"
    
    # System operations
    ROLLBACK = "rollback"
    REBUILD = "rebuild"
    GARBAGE_COLLECT = "garbage_collect"
    OPTIMIZE = "optimize"
    
    # Troubleshooting
    FIX_PROBLEM = "fix_problem"
    CHECK_STATUS = "check_status"
    VIEW_LOGS = "view_logs"
    DIAGNOSE = "diagnose"
    
    # Configuration
    CONFIGURE = "configure"
    ENABLE_SERVICE = "enable_service"
    DISABLE_SERVICE = "disable_service"
    
    # Information
    INFO = "info"
    HELP = "help"
    EXPLAIN = "explain"
    
    # Performance
    SPEED_UP = "speed_up"
    FREE_RESOURCES = "free_resources"


@dataclass
class ContextualIntent:
    """Intent with full context from system state"""
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any]
    context: Dict[str, Any]
    suggestions: List[str]
    warnings: List[str]
    related_state: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        return f"{self.intent_type.value} (confidence: {self.confidence:.2f})"


class ContextAwareIntentRecognizer:
    """Recognize intent with system context"""
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.assistant = PredictiveAssistant(monitor)
        
        # Intent patterns with context triggers
        self.patterns = {
            IntentType.INSTALL: [
                r'\b(install|add|get|setup)\b.*?(\w+)',
                r'\bi need\b.*?(\w+)',
                r'\bcan you install\b.*?(\w+)'
            ],
            IntentType.REMOVE: [
                r'\b(remove|uninstall|delete)\b.*?(\w+)',
                r'\bget rid of\b.*?(\w+)'
            ],
            IntentType.SEARCH: [
                r'\b(search|find|look for|what)\b.*?(\w+)',
                r'\bis there.*?(\w+)',
                r'\bshow me.*?(\w+)'
            ],
            IntentType.UPDATE: [
                r'\b(update|upgrade|refresh)\b',
                r'\bget.*?latest\b'
            ],
            IntentType.ROLLBACK: [
                r'\b(rollback|revert|undo|go back)\b',
                r'\bprevious.*?(generation|version)\b'
            ],
            IntentType.FIX_PROBLEM: [
                r'\b(fix|repair|solve|broken|failed)\b',
                r'\bnot working\b',
                r'\bwon\'t (start|work|run)\b'
            ],
            IntentType.DIAGNOSE: [
                r'\b(slow|sluggish|frozen|hanging)\b',
                r'\bwhy is.*?(slow|broken|failing)\b',
                r'\bperformance.*?issue\b'
            ],
            IntentType.GARBAGE_COLLECT: [
                r'\b(clean|cleanup|garbage|gc)\b',
                r'\bfree.*?space\b',
                r'\bdelete.*?old\b'
            ],
            IntentType.CHECK_STATUS: [
                r'\b(status|state|check|show)\b',
                r'\bwhat.*?(running|installed|active)\b',
                r'\bhow.*?much.*?(space|memory|cpu)\b'
            ],
            IntentType.SPEED_UP: [
                r'\b(speed up|faster|optimize|improve)\b',
                r'\bmake.*?fast\b',
                r'\bperformance\b'
            ],
            IntentType.FREE_RESOURCES: [
                r'\b(free|release|clear).*?(memory|ram|space|disk)\b',
                r'\bout of.*?(memory|space)\b',
                r'\bkill.*?process\b'
            ]
        }
        
        # Context keywords that modify intent
        self.context_modifiers = {
            'urgent': ['now', 'immediately', 'urgent', 'asap', 'quickly'],
            'careful': ['safe', 'careful', 'test', 'dry-run', 'preview'],
            'force': ['force', 'anyway', 'ignore', 'override'],
            'all': ['all', 'everything', 'entire', 'complete']
        }
    
    def recognize(self, query: str) -> ContextualIntent:
        """Recognize intent with full system context"""
        query_lower = query.lower()
        
        # Get current system state
        state = self.monitor.get_state()
        quick_status = self.monitor.get_quick_status()
        predictions = self.assistant.analyze_system()
        
        # Try pattern matching first
        intent = self._match_patterns(query_lower)
        
        # Enhance with context if we found a base intent
        if intent:
            intent = self._enhance_with_context(intent, query_lower, state, quick_status, predictions)
        else:
            # Try context-based recognition
            intent = self._recognize_from_context(query_lower, state, quick_status, predictions)
        
        # If still no intent, default to help
        if not intent:
            intent = ContextualIntent(
                intent_type=IntentType.HELP,
                confidence=0.3,
                entities={'query': query},
                context={},
                suggestions=["Try being more specific about what you want to do"],
                warnings=[]
            )
        
        return intent
    
    def _match_patterns(self, query: str) -> Optional[ContextualIntent]:
        """Match query against intent patterns"""
        best_match = None
        best_confidence = 0.0
        
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    confidence = self._calculate_pattern_confidence(match, query)
                    
                    if confidence > best_confidence:
                        entities = self._extract_entities(match, query, intent_type)
                        best_match = ContextualIntent(
                            intent_type=intent_type,
                            confidence=confidence,
                            entities=entities,
                            context={},
                            suggestions=[],
                            warnings=[]
                        )
                        best_confidence = confidence
        
        return best_match
    
    def _calculate_pattern_confidence(self, match, query: str) -> float:
        """Calculate confidence based on match quality"""
        # Base confidence
        confidence = 0.6
        
        # Boost for exact matches
        if match.group(0) == query:
            confidence += 0.3
        
        # Boost for match at beginning
        if match.start() == 0:
            confidence += 0.1
        
        # Reduce for very short queries
        if len(query) < 10:
            confidence -= 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    def _extract_entities(self, match, query: str, intent_type: IntentType) -> Dict[str, Any]:
        """Extract entities from matched pattern"""
        entities = {}
        
        # Get matched groups
        groups = match.groups()
        
        if intent_type in [IntentType.INSTALL, IntentType.REMOVE, IntentType.SEARCH]:
            if len(groups) > 0:
                # Last group is usually the package/target
                entities['target'] = groups[-1] if groups[-1] else query.split()[-1]
        
        # Extract modifiers
        for modifier_type, keywords in self.context_modifiers.items():
            for keyword in keywords:
                if keyword in query:
                    entities[modifier_type] = True
                    break
        
        return entities
    
    def _enhance_with_context(self, intent: ContextualIntent, query: str, 
                            state: Dict, status: Dict, predictions: List) -> ContextualIntent:
        """Enhance intent with system context"""
        
        # Add performance context for slow/performance queries
        if 'slow' in query or 'performance' in query:
            intent.context['cpu_usage'] = status.get('cpu_percent', 0)
            intent.context['memory_usage'] = status.get('memory_percent', 0)
            intent.context['load_average'] = status.get('load_average', (0, 0, 0))
            
            # Add specific suggestions based on metrics
            if status.get('memory_percent', 0) > 80:
                intent.suggestions.append("Memory usage is high - consider closing applications")
                intent.intent_type = IntentType.FREE_RESOURCES
                intent.confidence = min(intent.confidence + 0.2, 1.0)
            
            if status.get('cpu_percent', 0) > 80:
                intent.suggestions.append("CPU usage is high - check for intensive processes")
        
        # Add disk context for space-related queries
        if 'space' in query or 'disk' in query or 'storage' in query:
            disk_usage = status.get('disk_usage', {})
            intent.context['disk_usage'] = disk_usage
            
            # Find critical disks
            for mount, percent in disk_usage.items():
                if percent > 90:
                    intent.warnings.append(f"Disk {mount} is {percent:.1f}% full!")
                    intent.intent_type = IntentType.GARBAGE_COLLECT
                    intent.confidence = 0.9
        
        # Add service context for fix/broken queries
        if intent.intent_type == IntentType.FIX_PROBLEM:
            services = state.get('services', [])
            failed = [s for s in services if hasattr(s, 'status') and s.status == 'failed']
            
            if failed:
                intent.context['failed_services'] = [s.name for s in failed]
                intent.suggestions.append(f"Found failed services: {', '.join(s.name for s in failed)}")
                intent.entities['services'] = failed
        
        # Add predictions as suggestions
        if predictions and intent.intent_type in [IntentType.DIAGNOSE, IntentType.FIX_PROBLEM]:
            for pred in predictions[:2]:  # Top 2 predictions
                if pred.confidence > 0.6:
                    intent.suggestions.append(f"Recommended: {pred.action} ({pred.reason})")
        
        # Check for urgent context
        if intent.entities.get('urgent'):
            intent.context['priority'] = 'high'
            intent.suggestions.insert(0, "Executing with high priority")
        
        # Check for safety context
        if intent.entities.get('careful'):
            intent.context['dry_run'] = True
            intent.suggestions.append("Will run in dry-run mode for safety")
        
        return intent
    
    def _recognize_from_context(self, query: str, state: Dict, 
                               status: Dict, predictions: List) -> Optional[ContextualIntent]:
        """Recognize intent purely from context when patterns don't match"""
        
        # Check if query relates to current problems
        if predictions:
            top_prediction = predictions[0]
            
            # Map prediction categories to intents
            category_map = {
                'performance': IntentType.SPEED_UP,
                'maintenance': IntentType.GARBAGE_COLLECT,
                'security': IntentType.FIX_PROBLEM
            }
            
            if top_prediction.confidence > 0.7:
                intent_type = category_map.get(top_prediction.category, IntentType.DIAGNOSE)
                
                return ContextualIntent(
                    intent_type=intent_type,
                    confidence=top_prediction.confidence * 0.8,
                    entities={'action': top_prediction.action},
                    context={'prediction': top_prediction.to_dict()},
                    suggestions=[top_prediction.action],
                    warnings=[],
                    related_state={'predictions': [p.to_dict() for p in predictions[:3]]}
                )
        
        # Check for vague problem descriptions
        problem_words = ['problem', 'issue', 'wrong', 'help', 'broken', 'error']
        if any(word in query for word in problem_words):
            # Diagnose based on system state
            issues = []
            
            if status.get('memory_percent', 0) > 80:
                issues.append("High memory usage detected")
            
            if status.get('cpu_percent', 0) > 80:
                issues.append("High CPU usage detected")
            
            disk_usage = status.get('disk_usage', {})
            for mount, percent in disk_usage.items():
                if percent > 90:
                    issues.append(f"Disk {mount} nearly full")
            
            if issues:
                return ContextualIntent(
                    intent_type=IntentType.DIAGNOSE,
                    confidence=0.6,
                    entities={},
                    context={'detected_issues': issues},
                    suggestions=issues,
                    warnings=[]
                )
        
        return None
    
    def explain_recognition(self, intent: ContextualIntent) -> str:
        """Explain why an intent was recognized"""
        explanation = f"I understood that you want to: **{intent.intent_type.value}**\n\n"
        
        if intent.confidence < 0.5:
            explanation += "*(Low confidence - you may want to be more specific)*\n\n"
        
        if intent.context:
            explanation += "**Context I considered:**\n"
            
            if 'cpu_usage' in intent.context:
                explanation += f"- CPU usage: {intent.context['cpu_usage']:.1f}%\n"
            
            if 'memory_usage' in intent.context:
                explanation += f"- Memory usage: {intent.context['memory_usage']:.1f}%\n"
            
            if 'disk_usage' in intent.context:
                explanation += "- Disk usage levels\n"
            
            if 'failed_services' in intent.context:
                explanation += f"- Failed services: {', '.join(intent.context['failed_services'])}\n"
            
            if 'priority' in intent.context:
                explanation += f"- Priority: {intent.context['priority']}\n"
            
            explanation += "\n"
        
        if intent.suggestions:
            explanation += "**Suggestions:**\n"
            for suggestion in intent.suggestions:
                explanation += f"- {suggestion}\n"
            explanation += "\n"
        
        if intent.warnings:
            explanation += "**⚠️ Warnings:**\n"
            for warning in intent.warnings:
                explanation += f"- {warning}\n"
        
        return explanation


# Example integration
def process_query_with_context(query: str, monitor: SystemMonitor) -> Tuple[ContextualIntent, str]:
    """Process a query with full context awareness"""
    recognizer = ContextAwareIntentRecognizer(monitor)
    
    # Recognize intent
    intent = recognizer.recognize(query)
    
    # Generate explanation
    explanation = recognizer.explain_recognition(intent)
    
    return intent, explanation