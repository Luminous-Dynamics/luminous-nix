"""
from typing import List
Context Awareness - Understanding user's current situation

This module combines ActivityWatch data with other signals to build
a comprehensive understanding of the user's context.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ..knowledge_graph.skg import SymbioticKnowledgeGraph
from .activity_monitor import ActivityMonitor


class WorkContext(Enum):
    """Types of work contexts"""

    DEEP_WORK = "deep_work"
    SHALLOW_WORK = "shallow_work"
    LEARNING = "learning"
    TROUBLESHOOTING = "troubleshooting"
    COMMUNICATION = "communication"
    PLANNING = "planning"
    BREAK = "break"
    UNKNOWN = "unknown"


class TimeContext(Enum):
    """Time-based contexts"""

    EARLY_MORNING = "early_morning"  # 5am-9am
    MORNING = "morning"  # 9am-12pm
    AFTERNOON = "afternoon"  # 12pm-5pm
    EVENING = "evening"  # 5pm-9pm
    LATE_NIGHT = "late_night"  # 9pm-12am
    NIGHT = "night"  # 12am-5am


@dataclass
class UserContext:
    """Complete user context"""

    work_context: WorkContext
    time_context: TimeContext
    energy_level: float  # 0-1
    stress_level: float  # 0-1
    focus_potential: float  # 0-1
    interruption_cost: float  # 0-1
    recommended_task_type: str
    context_stability: float  # 0-1, how stable/consistent


class ContextAwareness:
    """
    Builds comprehensive context awareness from multiple signals

    Integrates:
    1. ActivityWatch behavioral data
    2. Time of day patterns
    3. Historical user patterns
    4. Current cognitive state
    """

    def __init__(self, skg: SymbioticKnowledgeGraph, activity_monitor: ActivityMonitor):
        self.skg = skg
        self.activity_monitor = activity_monitor

        # Context tracking
        self.current_context = None
        self.context_history = []

        # User patterns
        self.daily_patterns = self._load_daily_patterns()
        self.peak_hours = self._identify_peak_hours()

    def assess_current_context(self) -> UserContext:
        """
        Assess the user's current context from all available signals
        """
        # Get activity context
        activity_context = self.activity_monitor.get_activity_context()

        # Get time context
        time_context = self._get_time_context()

        # Get cognitive state from knowledge graph
        cognitive_state = self._get_cognitive_state()

        # Determine work context
        work_context = self._determine_work_context(activity_context, cognitive_state)

        # Calculate context metrics
        energy_level = self._calculate_energy_level(time_context, activity_context)
        stress_level = self._calculate_stress_level(cognitive_state, activity_context)
        focus_potential = self._calculate_focus_potential(
            energy_level, stress_level, time_context
        )
        interruption_cost = self._calculate_interruption_cost(
            work_context, focus_potential, activity_context
        )

        # Determine recommended task type
        recommended_task = self._recommend_task_type(
            work_context, energy_level, focus_potential
        )

        # Calculate context stability
        context_stability = self._calculate_context_stability()

        # Create context object
        context = UserContext(
            work_context=work_context,
            time_context=time_context,
            energy_level=energy_level,
            stress_level=stress_level,
            focus_potential=focus_potential,
            interruption_cost=interruption_cost,
            recommended_task_type=recommended_task,
            context_stability=context_stability,
        )

        # Update tracking
        self.current_context = context
        self._record_context(context)

        return context

    def _get_time_context(self) -> TimeContext:
        """Determine time-based context"""
        hour = datetime.now().hour

        if 5 <= hour < 9:
            return TimeContext.EARLY_MORNING
        if 9 <= hour < 12:
            return TimeContext.MORNING
        if 12 <= hour < 17:
            return TimeContext.AFTERNOON
        if 17 <= hour < 21:
            return TimeContext.EVENING
        if 21 <= hour < 24:
            return TimeContext.LATE_NIGHT
        return TimeContext.NIGHT

    def _get_cognitive_state(self) -> dict:
        """Get current cognitive state from knowledge graph"""
        user_state = self.skg.phenomenological.get_current_user_state()

        # Get recent learning progress
        trajectory = self.skg.phenomenological.get_learning_trajectory()
        recent_progress = len(
            [e for e in trajectory[-10:] if e["type"] == "mastery_milestone"]
        )

        return {
            "cognitive_load": user_state.get("cognitive_load", 0.5),
            "flow_level": user_state.get("flow_level", 0),
            "frustration_level": user_state.get("frustration_level", 0),
            "learning_momentum": min(1.0, recent_progress / 3),
        }

    def _determine_work_context(
        self, activity_context: dict, cognitive_state: dict
    ) -> WorkContext:
        """Determine the type of work being done"""
        if not activity_context.get("active"):
            return WorkContext.UNKNOWN

        pattern = activity_context.get("current_pattern")
        if not pattern:
            return WorkContext.UNKNOWN

        pattern_type = pattern["pattern_type"]
        flow_level = cognitive_state.get("flow_level", 0)

        # Map activity patterns to work contexts
        if pattern_type == "deep_focus" and flow_level > 0.6:
            return WorkContext.DEEP_WORK

        if pattern_type == "focused_work":
            return WorkContext.SHALLOW_WORK

        if (
            pattern_type == "exploring"
            and cognitive_state.get("learning_momentum", 0) > 0.5
        ):
            return WorkContext.LEARNING

        if (
            pattern_type == "context_switching"
            and cognitive_state.get("frustration_level", 0) > 0.5
        ):
            return WorkContext.TROUBLESHOOTING

        if pattern_type == "break_time":
            return WorkContext.BREAK

        if "browser" in str(activity_context.get("recent_patterns", [])):
            if pattern_type == "reading":
                return WorkContext.LEARNING
            return WorkContext.PLANNING

        return WorkContext.SHALLOW_WORK

    def _calculate_energy_level(
        self, time_context: TimeContext, activity_context: dict
    ) -> float:
        """Calculate current energy level"""
        # Base energy from time of day
        time_energy = {
            TimeContext.EARLY_MORNING: 0.7,
            TimeContext.MORNING: 0.9,
            TimeContext.AFTERNOON: 0.6,
            TimeContext.EVENING: 0.5,
            TimeContext.LATE_NIGHT: 0.3,
            TimeContext.NIGHT: 0.1,
        }

        base_energy = time_energy.get(time_context, 0.5)

        # Adjust for user's peak hours
        current_hour = datetime.now().hour
        if current_hour in self.peak_hours:
            base_energy *= 1.2

        # Adjust for recent breaks
        recent_patterns = activity_context.get("recent_patterns", [])
        if "break_time" in recent_patterns:
            base_energy *= 1.1

        # Adjust for session duration
        session_minutes = self._get_session_duration()
        if session_minutes > 120:
            base_energy *= 0.8
        elif session_minutes > 180:
            base_energy *= 0.6

        return min(1.0, max(0.0, base_energy))

    def _calculate_stress_level(
        self, cognitive_state: dict, activity_context: dict
    ) -> float:
        """Calculate current stress level"""
        # Base stress from cognitive state
        frustration = cognitive_state.get("frustration_level", 0)
        cognitive_load = cognitive_state.get("cognitive_load", 0)

        stress = frustration * 0.6 + cognitive_load * 0.4

        # Increase stress for excessive context switching
        recent_patterns = activity_context.get("recent_patterns", [])
        switching_count = recent_patterns.count("context_switching")
        if switching_count > 2:
            stress += 0.2

        # Decrease stress if in flow
        if cognitive_state.get("flow_level", 0) > 0.7:
            stress *= 0.5

        return min(1.0, max(0.0, stress))

    def _calculate_focus_potential(
        self, energy: float, stress: float, time_context: TimeContext
    ) -> float:
        """Calculate potential for focused work"""
        # Base potential from energy and stress
        base_potential = energy * (1 - stress * 0.7)

        # Time-based adjustments
        time_factors = {
            TimeContext.EARLY_MORNING: 0.9,
            TimeContext.MORNING: 1.0,
            TimeContext.AFTERNOON: 0.7,
            TimeContext.EVENING: 0.6,
            TimeContext.LATE_NIGHT: 0.4,
            TimeContext.NIGHT: 0.2,
        }

        time_factor = time_factors.get(time_context, 0.5)
        focus_potential = base_potential * time_factor

        # Boost if user is in their peak hours
        if datetime.now().hour in self.peak_hours:
            focus_potential *= 1.2

        return min(1.0, max(0.0, focus_potential))

    def _calculate_interruption_cost(
        self, work_context: WorkContext, focus_potential: float, activity_context: dict
    ) -> float:
        """Calculate the cost of interrupting now"""
        # Base cost from work context
        context_costs = {
            WorkContext.DEEP_WORK: 0.9,
            WorkContext.SHALLOW_WORK: 0.4,
            WorkContext.LEARNING: 0.7,
            WorkContext.TROUBLESHOOTING: 0.6,
            WorkContext.COMMUNICATION: 0.3,
            WorkContext.PLANNING: 0.5,
            WorkContext.BREAK: 0.1,
            WorkContext.UNKNOWN: 0.5,
        }

        base_cost = context_costs.get(work_context, 0.5)

        # Adjust for focus potential
        cost = base_cost * (1 + focus_potential * 0.5)

        # Adjust for current flow state
        if activity_context.get("focus_level", 0) > 0.7:
            cost *= 1.5

        return min(1.0, max(0.0, cost))

    def _recommend_task_type(
        self, work_context: WorkContext, energy: float, focus_potential: float
    ) -> str:
        """Recommend what type of task to work on"""
        if energy < 0.3:
            return "rest_or_routine_tasks"

        if focus_potential > 0.7:
            if work_context == WorkContext.DEEP_WORK:
                return "continue_deep_work"
            return "complex_problem_solving"

        if focus_potential > 0.5:
            return "moderate_complexity_tasks"

        if energy > 0.6:
            return "collaborative_or_creative_work"

        return "administrative_or_planning"

    def _calculate_context_stability(self) -> float:
        """Calculate how stable the current context is"""
        if len(self.context_history) < 3:
            return 0.5

        # Check recent context changes
        recent_contexts = self.context_history[-5:]
        work_contexts = [c["work_context"] for c in recent_contexts]

        # Count unique contexts
        unique_contexts = len(set(work_contexts))

        # More unique contexts = less stability
        stability = 1.0 - (unique_contexts - 1) / 4

        return max(0.0, min(1.0, stability))

    def _load_daily_patterns(self) -> dict:
        """Load user's daily patterns from historical data"""
        cursor = self.skg.conn.cursor()

        # Get activity patterns by hour
        patterns = cursor.execute(
            """
            SELECT 
                strftime('%H', created_at) as hour,
                json_extract(properties, '$.pattern_type') as pattern,
                COUNT(*) as count
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type = 'activity_pattern'
            AND created_at > datetime('now', '-30 days')
            GROUP BY hour, pattern
            ORDER BY hour, count DESC
        """
        ).fetchall()

        # Organize by hour
        daily_patterns = {}
        for hour, pattern, count in patterns:
            hour_int = int(hour)
            if hour_int not in daily_patterns:
                daily_patterns[hour_int] = []
            daily_patterns[hour_int].append((pattern, count))

        return daily_patterns

    def _identify_peak_hours(self) -> list[int]:
        """Identify user's peak performance hours"""
        cursor = self.skg.conn.cursor()

        # Find hours with highest flow states
        peak_data = cursor.execute(
            """
            SELECT 
                strftime('%H', created_at) as hour,
                AVG(json_extract(properties, '$.flow_level')) as avg_flow
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type = 'cognitive_state'
            AND created_at > datetime('now', '-30 days')
            GROUP BY hour
            HAVING avg_flow > 0.6
            ORDER BY avg_flow DESC
            LIMIT 4
        """
        ).fetchall()

        peak_hours = [int(hour) for hour, _ in peak_data]

        # Default to morning hours if no data
        if not peak_hours:
            peak_hours = [9, 10, 11, 14]

        return peak_hours

    def _get_session_duration(self) -> int:
        """Get current session duration in minutes"""
        if not self.context_history:
            return 0

        first_context = self.context_history[0]
        start_time = datetime.fromisoformat(first_context["timestamp"])
        duration = (datetime.now() - start_time).seconds / 60

        return int(duration)

    def _record_context(self, context: UserContext):
        """Record context in knowledge graph"""
        context_dict = {
            "work_context": context.work_context.value,
            "time_context": context.time_context.value,
            "energy_level": context.energy_level,
            "stress_level": context.stress_level,
            "focus_potential": context.focus_potential,
            "interruption_cost": context.interruption_cost,
            "recommended_task_type": context.recommended_task_type,
            "context_stability": context.context_stability,
            "timestamp": datetime.now().isoformat(),
        }

        self.context_history.append(context_dict)

        # Record in SKG
        context_id = f"user_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cursor = self.skg.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'user_context', ?)
        """,
            (context_id, json.dumps(context_dict)),
        )

        self.skg.conn.commit()

    def predict_context_change(self) -> dict:
        """Predict when context might change"""
        if not self.current_context:
            return {"prediction": "unknown"}

        # Get typical patterns for this time
        current_hour = datetime.now().hour
        typical_patterns = self.daily_patterns.get(current_hour, [])

        # Predict based on time and patterns
        predictions = {
            "likely_next_context": self._predict_next_context(typical_patterns),
            "estimated_minutes_until_change": self._estimate_context_duration(),
            "confidence": self._calculate_prediction_confidence(),
        }

        return predictions

    def _predict_next_context(self, typical_patterns: list) -> str:
        """Predict the next likely context"""
        if not typical_patterns:
            return "unknown"

        # Most common pattern for this hour
        most_common = typical_patterns[0][0] if typical_patterns else None

        # Map pattern to context
        pattern_to_context = {
            "deep_focus": WorkContext.DEEP_WORK,
            "focused_work": WorkContext.SHALLOW_WORK,
            "exploring": WorkContext.LEARNING,
            "break_time": WorkContext.BREAK,
        }

        context = pattern_to_context.get(most_common, WorkContext.UNKNOWN)
        return context.value

    def _estimate_context_duration(self) -> int:
        """Estimate how long current context will last"""
        if not self.current_context:
            return 30

        # Average duration for this context type
        context_durations = {
            WorkContext.DEEP_WORK: 90,
            WorkContext.SHALLOW_WORK: 45,
            WorkContext.LEARNING: 60,
            WorkContext.TROUBLESHOOTING: 30,
            WorkContext.COMMUNICATION: 20,
            WorkContext.PLANNING: 30,
            WorkContext.BREAK: 15,
        }

        base_duration = context_durations.get(self.current_context.work_context, 30)

        # Adjust based on stability
        stability_factor = self.current_context.context_stability
        adjusted_duration = base_duration * (0.5 + stability_factor * 0.5)

        return int(adjusted_duration)

    def _calculate_prediction_confidence(self) -> float:
        """Calculate confidence in context prediction"""
        if len(self.context_history) < 10:
            return 0.3

        # Base confidence on stability and data availability
        stability = (
            self.current_context.context_stability if self.current_context else 0.5
        )
        data_factor = min(1.0, len(self.context_history) / 50)

        confidence = stability * 0.6 + data_factor * 0.4

        return confidence

    def get_context_recommendations(self) -> list[str]:
        """Get recommendations based on current context"""
        if not self.current_context:
            return ["No context data available"]

        recommendations = []

        # Energy-based recommendations
        if self.current_context.energy_level < 0.3:
            recommendations.append(
                "Your energy is low. Consider taking a break or switching to routine tasks."
            )

        # Stress-based recommendations
        if self.current_context.stress_level > 0.7:
            recommendations.append(
                "High stress detected. Try a breathing exercise or brief walk."
            )

        # Focus-based recommendations
        if self.current_context.focus_potential > 0.7:
            if self.current_context.work_context != WorkContext.DEEP_WORK:
                recommendations.append(
                    "Excellent focus potential! This is a great time for complex tasks."
                )

        # Context-specific recommendations
        if self.current_context.work_context == WorkContext.DEEP_WORK:
            recommendations.append(
                "You're in deep work mode. Protect this time from interruptions."
            )
        elif self.current_context.work_context == WorkContext.TROUBLESHOOTING:
            recommendations.append(
                "Troubleshooting can be frustrating. Remember to take breaks."
            )

        # Time-based recommendations
        if self.current_context.time_context == TimeContext.LATE_NIGHT:
            recommendations.append("It's getting late. Consider winding down soon.")

        return recommendations
