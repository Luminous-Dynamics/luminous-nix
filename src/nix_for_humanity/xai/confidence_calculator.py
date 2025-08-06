"""
Confidence calculation for XAI explanations
Provides detailed confidence metrics and scoring
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
# Note: Numpy import is optional for basic functionality
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Create mock numpy for basic operations
    class MockNumpy:
        def array(self, data):
            return data
        def mean(self, data):
            return sum(data) / len(data) if data else 0
        def std(self, data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            return variance ** 0.5
        def var(self, data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)
    np = MockNumpy()
    logging.warning("Numpy not available. Using simplified numerical operations.")

import logging
from datetime import datetime, timedelta


class ConfidenceSource(Enum):
    """Sources of confidence in decisions"""
    PATTERN_MATCH = "pattern_match"      # How well input matches known patterns
    HISTORICAL = "historical"            # Based on past success rate
    KNOWLEDGE_BASE = "knowledge_base"    # Confidence in KB data
    USER_FEEDBACK = "user_feedback"      # Previous user satisfaction
    SYSTEM_STATE = "system_state"        # Current system conditions
    CONTEXT = "context"                  # Contextual appropriateness


@dataclass
class ConfidenceComponent:
    """Individual component of confidence calculation"""
    source: ConfidenceSource
    value: float  # 0.0 to 1.0
    weight: float  # Importance weight
    description: str
    evidence: List[str]
    
    @property
    def weighted_value(self) -> float:
        """Get weighted confidence value"""
        return self.value * self.weight


@dataclass
class ConfidenceMetrics:
    """Complete confidence metrics for a decision"""
    overall_confidence: float
    components: List[ConfidenceComponent]
    uncertainty_factors: List[str]
    confidence_trend: str  # "increasing", "stable", "decreasing"
    reliability_score: float  # How reliable is this confidence estimate
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'overall_confidence': self.overall_confidence,
            'components': [
                {
                    'source': c.source.value,
                    'value': c.value,
                    'weight': c.weight,
                    'description': c.description,
                    'evidence': c.evidence
                }
                for c in self.components
            ],
            'uncertainty_factors': self.uncertainty_factors,
            'confidence_trend': self.confidence_trend,
            'reliability_score': self.reliability_score,
            'timestamp': self.timestamp.isoformat()
        }


class ConfidenceCalculator:
    """Calculate detailed confidence metrics for AI decisions"""
    
    def __init__(self, knowledge_base=None, learning_system=None):
        self.knowledge_base = knowledge_base
        self.learning_system = learning_system
        self.logger = logging.getLogger(__name__)
        self.confidence_history: List[ConfidenceMetrics] = []
        
        # Default weights for different confidence sources
        self.source_weights = {
            ConfidenceSource.PATTERN_MATCH: 0.3,
            ConfidenceSource.HISTORICAL: 0.25,
            ConfidenceSource.KNOWLEDGE_BASE: 0.2,
            ConfidenceSource.USER_FEEDBACK: 0.15,
            ConfidenceSource.SYSTEM_STATE: 0.05,
            ConfidenceSource.CONTEXT: 0.05
        }
    
    def calculate_confidence(
        self,
        decision: str,
        context: Dict[str, Any],
        detailed: bool = True
    ) -> ConfidenceMetrics:
        """
        Calculate comprehensive confidence metrics for a decision
        
        Args:
            decision: The decision being made
            context: Context information
            detailed: Whether to include detailed component analysis
            
        Returns:
            ConfidenceMetrics object
        """
        components = []
        
        # Calculate pattern match confidence
        pattern_confidence = self._calculate_pattern_confidence(decision, context)
        components.append(pattern_confidence)
        
        # Calculate historical confidence
        historical_confidence = self._calculate_historical_confidence(decision, context)
        components.append(historical_confidence)
        
        # Calculate knowledge base confidence
        kb_confidence = self._calculate_kb_confidence(decision, context)
        components.append(kb_confidence)
        
        # Calculate user feedback confidence
        feedback_confidence = self._calculate_feedback_confidence(decision, context)
        components.append(feedback_confidence)
        
        # Calculate system state confidence
        system_confidence = self._calculate_system_confidence(context)
        components.append(system_confidence)
        
        # Calculate contextual confidence
        context_confidence = self._calculate_context_confidence(decision, context)
        components.append(context_confidence)
        
        # Calculate overall confidence
        overall = self._calculate_overall(components)
        
        # Identify uncertainty factors
        uncertainty_factors = self._identify_uncertainties(components, context)
        
        # Determine confidence trend
        trend = self._calculate_trend(overall)
        
        # Calculate reliability of this confidence estimate
        reliability = self._calculate_reliability(components, context)
        
        metrics = ConfidenceMetrics(
            overall_confidence=overall,
            components=components if detailed else [],
            uncertainty_factors=uncertainty_factors,
            confidence_trend=trend,
            reliability_score=reliability,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.confidence_history.append(metrics)
        
        return metrics
    
    def _calculate_pattern_confidence(self, decision: str, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on pattern matching"""
        evidence = []
        
        # Check exact match
        if context.get('exact_match', False):
            value = 0.95
            evidence.append("Exact pattern match found")
        # Check fuzzy match
        elif context.get('fuzzy_match_score', 0) > 0:
            value = context['fuzzy_match_score']
            evidence.append(f"Fuzzy match with score {value:.2f}")
        # Check partial match
        elif context.get('partial_match', False):
            value = 0.6
            evidence.append("Partial pattern match")
        else:
            value = 0.3
            evidence.append("No strong pattern match")
        
        # Adjust for typo corrections
        if context.get('typos_corrected', 0) > 0:
            value *= 0.9
            evidence.append(f"Corrected {context['typos_corrected']} typos")
        
        return ConfidenceComponent(
            source=ConfidenceSource.PATTERN_MATCH,
            value=value,
            weight=self.source_weights[ConfidenceSource.PATTERN_MATCH],
            description="Pattern matching confidence",
            evidence=evidence
        )
    
    def _calculate_historical_confidence(self, decision: str, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on historical success"""
        evidence = []
        
        if self.learning_system:
            # Get historical success rate for similar decisions
            success_rate = self.learning_system.get_success_rate(decision)
            occurrence_count = self.learning_system.get_occurrence_count(decision)
            
            if occurrence_count > 10:
                value = success_rate
                evidence.append(f"Based on {occurrence_count} previous occurrences")
                evidence.append(f"Historical success rate: {success_rate:.1%}")
            elif occurrence_count > 0:
                # Less confident with fewer samples
                value = 0.5 + (success_rate - 0.5) * (occurrence_count / 10)
                evidence.append(f"Limited history: {occurrence_count} occurrences")
            else:
                value = 0.5
                evidence.append("No historical data available")
        else:
            value = 0.5
            evidence.append("Learning system not available")
        
        return ConfidenceComponent(
            source=ConfidenceSource.HISTORICAL,
            value=value,
            weight=self.source_weights[ConfidenceSource.HISTORICAL],
            description="Historical success confidence",
            evidence=evidence
        )
    
    def _calculate_kb_confidence(self, decision: str, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on knowledge base"""
        evidence = []
        
        if self.knowledge_base:
            # Check if decision relates to known information
            kb_match = self.knowledge_base.query_relevance(decision)
            
            if kb_match > 0.9:
                value = 0.95
                evidence.append("Strong knowledge base support")
            elif kb_match > 0.7:
                value = 0.8
                evidence.append("Good knowledge base match")
            elif kb_match > 0.5:
                value = 0.6
                evidence.append("Moderate knowledge base support")
            else:
                value = 0.4
                evidence.append("Limited knowledge base information")
            
            # Check data freshness
            if context.get('kb_data_age_days', 0) > 30:
                value *= 0.9
                evidence.append("Knowledge base data may be outdated")
        else:
            value = 0.5
            evidence.append("Knowledge base not available")
        
        return ConfidenceComponent(
            source=ConfidenceSource.KNOWLEDGE_BASE,
            value=value,
            weight=self.source_weights[ConfidenceSource.KNOWLEDGE_BASE],
            description="Knowledge base confidence",
            evidence=evidence
        )
    
    def _calculate_feedback_confidence(self, decision: str, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on user feedback"""
        evidence = []
        
        if self.learning_system:
            # Get user satisfaction for similar decisions
            satisfaction = self.learning_system.get_user_satisfaction(decision)
            feedback_count = self.learning_system.get_feedback_count(decision)
            
            if feedback_count > 5:
                value = satisfaction
                evidence.append(f"User satisfaction: {satisfaction:.1%}")
                evidence.append(f"Based on {feedback_count} feedback instances")
            elif feedback_count > 0:
                value = 0.6 + (satisfaction - 0.5) * 0.4
                evidence.append(f"Limited feedback: {feedback_count} instances")
            else:
                value = 0.7  # Optimistic default
                evidence.append("No user feedback yet")
        else:
            value = 0.7
            evidence.append("Feedback system not available")
        
        return ConfidenceComponent(
            source=ConfidenceSource.USER_FEEDBACK,
            value=value,
            weight=self.source_weights[ConfidenceSource.USER_FEEDBACK],
            description="User feedback confidence",
            evidence=evidence
        )
    
    def _calculate_system_confidence(self, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on system state"""
        evidence = []
        value = 1.0
        
        # Check system resources
        if context.get('low_memory', False):
            value *= 0.9
            evidence.append("System memory is low")
        
        if context.get('high_load', False):
            value *= 0.9
            evidence.append("System under high load")
        
        # Check network availability
        if context.get('offline_mode', False):
            value *= 0.95
            evidence.append("Operating in offline mode")
        
        # Check permissions
        if context.get('elevated_permissions', False):
            value *= 1.05  # Slightly more confident with proper permissions
            value = min(value, 1.0)
            evidence.append("Elevated permissions available")
        
        if value == 1.0:
            evidence.append("System operating normally")
        
        return ConfidenceComponent(
            source=ConfidenceSource.SYSTEM_STATE,
            value=value,
            weight=self.source_weights[ConfidenceSource.SYSTEM_STATE],
            description="System state confidence",
            evidence=evidence
        )
    
    def _calculate_context_confidence(self, decision: str, context: Dict[str, Any]) -> ConfidenceComponent:
        """Calculate confidence based on contextual appropriateness"""
        evidence = []
        value = 1.0
        
        # Check timing appropriateness
        current_hour = datetime.now().hour
        if 'system_update' in decision.lower() and (current_hour < 6 or current_hour > 22):
            value *= 0.8
            evidence.append("Unusual time for system updates")
        
        # Check user expertise level
        user_level = context.get('user_expertise', 'intermediate')
        if 'advanced' in decision.lower() and user_level == 'beginner':
            value *= 0.7
            evidence.append("Advanced operation for beginner user")
        
        # Check recent similar operations
        if context.get('recent_similar_operations', 0) > 3:
            value *= 0.9
            evidence.append("Multiple similar operations recently")
        
        if value == 1.0:
            evidence.append("Context is appropriate")
        
        return ConfidenceComponent(
            source=ConfidenceSource.CONTEXT,
            value=value,
            weight=self.source_weights[ConfidenceSource.CONTEXT],
            description="Contextual confidence",
            evidence=evidence
        )
    
    def _calculate_overall(self, components: List[ConfidenceComponent]) -> float:
        """Calculate overall confidence from components"""
        if not components:
            return 0.5
        
        # Weighted average
        total_weight = sum(c.weight for c in components)
        if total_weight == 0:
            return 0.5
        
        weighted_sum = sum(c.weighted_value for c in components)
        return weighted_sum / total_weight
    
    def _identify_uncertainties(self, components: List[ConfidenceComponent], context: Dict[str, Any]) -> List[str]:
        """Identify factors contributing to uncertainty"""
        uncertainties = []
        
        # Check for low confidence components
        for component in components:
            if component.value < 0.5:
                uncertainties.append(f"Low {component.source.value} confidence: {component.value:.1%}")
        
        # Check for missing information
        if not self.knowledge_base:
            uncertainties.append("Knowledge base unavailable")
        
        if not self.learning_system:
            uncertainties.append("Learning system unavailable")
        
        # Check for conflicting signals
        values = [c.value for c in components]
        if values and (max(values) - min(values)) > 0.5:
            uncertainties.append("Conflicting confidence signals")
        
        # Context-specific uncertainties
        if context.get('ambiguous_input', False):
            uncertainties.append("Input was ambiguous")
        
        if context.get('multiple_interpretations', False):
            uncertainties.append("Multiple valid interpretations possible")
        
        return uncertainties
    
    def _calculate_trend(self, current_confidence: float) -> str:
        """Calculate confidence trend based on history"""
        if len(self.confidence_history) < 2:
            return "stable"
        
        # Get recent confidence values
        recent_values = [h.overall_confidence for h in self.confidence_history[-5:]]
        recent_values.append(current_confidence)
        
        # Calculate trend
        if len(recent_values) >= 3:
            diffs = [recent_values[i+1] - recent_values[i] for i in range(len(recent_values)-1)]
            avg_diff = np.mean(diffs)
            
            if avg_diff > 0.05:
                return "increasing"
            elif avg_diff < -0.05:
                return "decreasing"
        
        return "stable"
    
    def _calculate_reliability(self, components: List[ConfidenceComponent], context: Dict[str, Any]) -> float:
        """Calculate how reliable this confidence estimate is"""
        reliability = 1.0
        
        # Reduce reliability if missing key components
        if not self.learning_system:
            reliability *= 0.8
        
        if not self.knowledge_base:
            reliability *= 0.8
        
        # Reduce reliability for new/rare decisions
        if context.get('occurrence_count', 0) < 5:
            reliability *= 0.9
        
        # Reduce reliability for high variance in components
        if components:
            values = [c.value for c in components]
            variance = np.var(values)
            if variance > 0.1:
                reliability *= (1 - variance/2)
        
        # Increase reliability for consistent historical performance
        if len(self.confidence_history) > 10:
            recent_accuracies = [h.reliability_score for h in self.confidence_history[-10:]]
            if all(acc > 0.8 for acc in recent_accuracies):
                reliability *= 1.1
        
        return min(reliability, 1.0)
    
    def explain_confidence(
        self,
        metrics: ConfidenceMetrics,
        level: str = "simple"
    ) -> str:
        """Generate human-readable confidence explanation"""
        if level == "simple":
            confidence_word = self._confidence_to_word(metrics.overall_confidence)
            return f"I'm {confidence_word} about this decision ({metrics.overall_confidence:.0%} confident)"
        
        elif level == "detailed":
            lines = [
                f"Overall confidence: {metrics.overall_confidence:.1%}",
                f"Confidence trend: {metrics.confidence_trend}",
                ""
            ]
            
            if metrics.components:
                lines.append("Confidence factors:")
                for comp in sorted(metrics.components, key=lambda c: c.weighted_value, reverse=True):
                    lines.append(f"  • {comp.description}: {comp.value:.1%}")
                    if comp.evidence:
                        lines.append(f"    - {comp.evidence[0]}")
            
            if metrics.uncertainty_factors:
                lines.append("\nUncertainties:")
                for uncertainty in metrics.uncertainty_factors:
                    lines.append(f"  • {uncertainty}")
            
            return "\n".join(lines)
        
        else:  # expert
            return self._generate_expert_explanation(metrics)
    
    def _confidence_to_word(self, confidence: float) -> str:
        """Convert confidence value to word"""
        if confidence >= 0.95:
            return "very confident"
        elif confidence >= 0.8:
            return "confident"
        elif confidence >= 0.6:
            return "fairly confident"
        elif confidence >= 0.4:
            return "somewhat confident"
        else:
            return "not very confident"
    
    def _generate_expert_explanation(self, metrics: ConfidenceMetrics) -> str:
        """Generate expert-level confidence explanation"""
        import json
        return json.dumps(metrics.to_dict(), indent=2)
    
    def get_confidence_history(self, limit: int = 10) -> List[ConfidenceMetrics]:
        """Get recent confidence history"""
        return self.confidence_history[-limit:]
    
    def get_average_confidence(self, time_window: timedelta = timedelta(hours=1)) -> float:
        """Get average confidence over time window"""
        cutoff = datetime.now() - time_window
        recent = [h.overall_confidence for h in self.confidence_history 
                 if h.timestamp > cutoff]
        
        if recent:
            return np.mean(recent)
        return 0.5