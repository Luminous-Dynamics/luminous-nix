"""
from typing import List, Dict
Mental State Model - Theory of Mind implementation for user modeling

This implements computational Theory of Mind, enabling the AI to model
the user's beliefs, desires, intentions, and emotional states.
"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class BeliefState:
    """User's beliefs about the system and their own abilities"""

    system_capabilities: float  # 0-1: belief in what the system can do
    self_efficacy: float  # 0-1: belief in their own technical ability
    trust_in_ai: float  # 0-1: general trust in AI systems
    understanding_level: float  # 0-1: how well they understand NixOS


@dataclass
class DesireState:
    """User's current goals and desires"""

    primary_goal: str
    urgency_level: float  # 0-1: how urgent is their need
    learning_desire: float  # 0-1: do they want to learn or just get it done
    autonomy_preference: float  # 0-1: want to do it themselves vs be helped


@dataclass
class IntentionState:
    """User's immediate intentions"""

    current_intent: str
    commitment_level: float  # 0-1: how committed to current path
    exploration_tendency: float  # 0-1: willing to try alternatives
    persistence: float  # 0-1: likelihood to keep trying despite obstacles


@dataclass
class EmotionalState:
    """User's emotional/affective state"""

    frustration_level: float  # 0-1
    confidence_level: float  # 0-1
    engagement_level: float  # 0-1
    stress_indicators: float  # 0-1


class MentalStateModel:
    """
    Implements Theory of Mind for modeling user's mental states

    Based on research showing that modeling mental states enables
    more empathetic and effective AI interactions.
    """

    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg

        # Initialize default mental states
        self.beliefs = BeliefState(
            system_capabilities=0.5,
            self_efficacy=0.5,
            trust_in_ai=0.5,
            understanding_level=0.3,
        )

        self.desires = DesireState(
            primary_goal="unknown",
            urgency_level=0.5,
            learning_desire=0.5,
            autonomy_preference=0.5,
        )

        self.intentions = IntentionState(
            current_intent="exploring",
            commitment_level=0.5,
            exploration_tendency=0.5,
            persistence=0.5,
        )

        self.emotions = EmotionalState(
            frustration_level=0.0,
            confidence_level=0.5,
            engagement_level=0.5,
            stress_indicators=0.0,
        )

        # Pattern matchers for state inference
        self._init_pattern_matchers()

    def _init_pattern_matchers(self):
        """Initialize patterns for inferring mental states from text"""
        # Belief indicators
        self.belief_patterns = {
            "doubt": re.compile(r"\b(don\'t think|doubt|unsure|confused|lost)\b", re.I),
            "confidence": re.compile(
                r"\b(i know|understand|got it|makes sense)\b", re.I
            ),
            "trust": re.compile(r"\b(trust|believe|rely on|count on)\b", re.I),
            "distrust": re.compile(
                r"\b(don\'t trust|worried|concerned|suspicious)\b", re.I
            ),
        }

        # Desire indicators
        self.desire_patterns = {
            "urgent": re.compile(
                r"\b(asap|urgent|quickly|right now|immediately)\b", re.I
            ),
            "learning": re.compile(
                r"\b(learn|understand|explain|teach|how does)\b", re.I
            ),
            "just_do_it": re.compile(r"\b(just|simply|only|don\'t care how)\b", re.I),
        }

        # Emotion indicators
        self.emotion_patterns = {
            "frustration": re.compile(
                r"\b(frustrated|annoyed|irritated|ugh|argh)\b", re.I
            ),
            "happiness": re.compile(r"\b(great|awesome|perfect|thank|love)\b", re.I),
            "confusion": re.compile(
                r"\b(confused|lost|don\'t understand|huh|\?+)\b", re.I
            ),
        }

    def update_from_interaction(
        self, interaction_id: str, user_input: str, ai_response: str
    ) -> dict:
        """
        Update mental state model based on interaction

        This is the core ToM function - inferring mental states from behavior
        """
        # Analyze linguistic cues
        belief_updates = self._analyze_beliefs(user_input)
        desire_updates = self._analyze_desires(user_input)
        emotion_updates = self._analyze_emotions(user_input)
        intention_updates = self._analyze_intentions(user_input)

        # Update states with decay
        self._update_beliefs(belief_updates)
        self._update_desires(desire_updates)
        self._update_emotions(emotion_updates)
        self._update_intentions(intention_updates)

        # Get context from knowledge graph
        user_context = self._get_user_context_from_skg()

        # Synthesize complete mental state
        mental_state = self._synthesize_mental_state(user_context)

        # Record in knowledge graph
        self._record_mental_state(interaction_id, mental_state)

        return mental_state

    def _analyze_beliefs(self, text: str) -> dict[str, float]:
        """Analyze text for belief indicators"""
        updates = {}

        if self.belief_patterns["doubt"].search(text):
            updates["system_capabilities"] = -0.1
            updates["self_efficacy"] = -0.1

        if self.belief_patterns["confidence"].search(text):
            updates["self_efficacy"] = 0.1
            updates["understanding_level"] = 0.1

        if self.belief_patterns["trust"].search(text):
            updates["trust_in_ai"] = 0.1

        if self.belief_patterns["distrust"].search(text):
            updates["trust_in_ai"] = -0.2

        return updates

    def _analyze_desires(self, text: str) -> dict[str, float]:
        """Analyze text for desire indicators"""
        updates = {}

        if self.desire_patterns["urgent"].search(text):
            updates["urgency_level"] = 0.3
            updates["learning_desire"] = -0.1

        if self.desire_patterns["learning"].search(text):
            updates["learning_desire"] = 0.2
            updates["autonomy_preference"] = 0.1

        if self.desire_patterns["just_do_it"].search(text):
            updates["learning_desire"] = -0.2
            updates["autonomy_preference"] = -0.2

        return updates

    def _analyze_emotions(self, text: str) -> dict[str, float]:
        """Analyze text for emotional indicators"""
        updates = {}

        if self.emotion_patterns["frustration"].search(text):
            updates["frustration_level"] = 0.2
            updates["confidence_level"] = -0.1
            updates["stress_indicators"] = 0.1

        if self.emotion_patterns["happiness"].search(text):
            updates["frustration_level"] = -0.2
            updates["confidence_level"] = 0.1
            updates["engagement_level"] = 0.1

        if self.emotion_patterns["confusion"].search(text):
            updates["confidence_level"] = -0.1
            updates["stress_indicators"] = 0.1

        # Check for multiple question marks (strong confusion)
        question_marks = text.count("?")
        if question_marks > 2:
            updates["confidence_level"] = -0.2
            updates["stress_indicators"] = 0.2

        return updates

    def _analyze_intentions(self, text: str) -> dict[str, float]:
        """Analyze text for intention indicators"""
        updates = {}

        # Command-like language suggests high commitment
        if text.strip().startswith(("install", "remove", "update", "configure")):
            updates["commitment_level"] = 0.2
            updates["exploration_tendency"] = -0.1

        # Questions suggest exploration
        if "?" in text:
            updates["exploration_tendency"] = 0.1
            updates["commitment_level"] = -0.1

        # "Try" language suggests lower commitment
        if re.search(r"\b(try|attempt|maybe|might)\b", text, re.I):
            updates["commitment_level"] = -0.1
            updates["exploration_tendency"] = 0.1

        return updates

    def _update_beliefs(self, updates: dict[str, float]):
        """Update belief states with bounds checking"""
        for attr, delta in updates.items():
            if hasattr(self.beliefs, attr):
                current = getattr(self.beliefs, attr)
                new_value = max(0, min(1, current + delta))
                setattr(self.beliefs, attr, new_value)

    def _update_desires(self, updates: dict[str, float]):
        """Update desire states with bounds checking"""
        for attr, delta in updates.items():
            if hasattr(self.desires, attr):
                current = getattr(self.desires, attr)
                new_value = max(0, min(1, current + delta))
                setattr(self.desires, attr, new_value)

    def _update_emotions(self, updates: dict[str, float]):
        """Update emotional states with decay"""
        # Apply decay to transient emotions
        self.emotions.frustration_level *= 0.9
        self.emotions.stress_indicators *= 0.95

        # Apply updates
        for attr, delta in updates.items():
            if hasattr(self.emotions, attr):
                current = getattr(self.emotions, attr)
                new_value = max(0, min(1, current + delta))
                setattr(self.emotions, attr, new_value)

    def _update_intentions(self, updates: dict[str, float]):
        """Update intention states"""
        for attr, delta in updates.items():
            if hasattr(self.intentions, attr):
                current = getattr(self.intentions, attr)
                new_value = max(0, min(1, current + delta))
                setattr(self.intentions, attr, new_value)

    def _get_user_context_from_skg(self) -> dict:
        """Get additional context from knowledge graph"""
        # Get user's current state from phenomenological layer
        user_state = self.skg.phenomenological.get_current_user_state()

        # Get learning trajectory
        trajectory = self.skg.phenomenological.get_learning_trajectory()

        # Get error/success patterns
        error_stats = self.skg.episodic.calculate_error_recovery_stats()

        return {
            "cognitive_load": user_state.get("cognitive_load", 0.5),
            "flow_level": user_state.get("flow_level", 0.0),
            "learning_momentum": self._calculate_learning_momentum(trajectory),
            "success_rate": 1.0
            - (error_stats["unresolved_errors"] / max(1, error_stats["total_errors"])),
        }

    def _calculate_learning_momentum(self, trajectory: list[dict]) -> float:
        """Calculate if user is making progress in learning"""
        if not trajectory:
            return 0.5

        recent_events = trajectory[-10:]  # Last 10 events
        mastery_count = sum(
            1 for e in recent_events if e["type"] == "mastery_milestone"
        )
        struggle_count = sum(1 for e in recent_events if e["type"] == "struggle_point")

        if mastery_count + struggle_count == 0:
            return 0.5

        return mastery_count / (mastery_count + struggle_count)

    def _synthesize_mental_state(self, context: dict) -> dict:
        """Synthesize complete mental state representation"""
        return {
            "beliefs": asdict(self.beliefs),
            "desires": asdict(self.desires),
            "intentions": asdict(self.intentions),
            "emotions": asdict(self.emotions),
            "context": context,
            "overall_state": self._determine_overall_state(),
            "support_needed": self._determine_support_need(),
        }

    def _determine_overall_state(self) -> str:
        """Determine high-level mental state category"""
        if self.emotions.frustration_level > 0.7:
            return "frustrated"
        if self.emotions.confidence_level > 0.7 and self.beliefs.self_efficacy > 0.7:
            return "confident"
        if self.desires.learning_desire > 0.7:
            return "curious"
        if self.desires.urgency_level > 0.7:
            return "urgent"
        if self.emotions.engagement_level < 0.3:
            return "disengaged"
        return "neutral"

    def _determine_support_need(self) -> str:
        """Determine what kind of support the user needs"""
        if self.emotions.frustration_level > 0.6:
            return "emotional_support"
        if self.beliefs.understanding_level < 0.3:
            return "educational_support"
        if self.desires.learning_desire > 0.7:
            return "detailed_explanation"
        if self.desires.urgency_level > 0.7:
            return "quick_solution"
        if self.desires.autonomy_preference > 0.7:
            return "minimal_guidance"
        return "balanced_support"

    def _record_mental_state(self, interaction_id: str, mental_state: dict):
        """Record mental state in knowledge graph"""
        state_id = f"mental_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cursor = self.skg.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'mental_state_model', ?)
        """,
            (state_id, json.dumps(mental_state)),
        )

        # Link to interaction
        edge_id = f"edge_mental_{state_id}_{interaction_id}"
        cursor.execute(
            """
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'MENTAL_STATE_DURING', ?, ?, ?)
        """,
            (
                edge_id,
                state_id,
                interaction_id,
                json.dumps({"inference_confidence": 0.8}),
            ),
        )

        self.skg.conn.commit()

    def get_user_state(self) -> dict:
        """Get current user mental state"""
        return self._synthesize_mental_state(self._get_user_context_from_skg())

    def get_model_summary(self) -> dict:
        """Get summary of mental model"""
        return {
            "overall_state": self._determine_overall_state(),
            "key_beliefs": {
                "trusts_system": self.beliefs.trust_in_ai > 0.6,
                "feels_capable": self.beliefs.self_efficacy > 0.6,
                "understands_nixos": self.beliefs.understanding_level > 0.5,
            },
            "primary_need": self._determine_support_need(),
            "emotional_tone": self._get_emotional_tone(),
        }

    def _get_emotional_tone(self) -> str:
        """Determine overall emotional tone"""
        if self.emotions.frustration_level > 0.6:
            return "frustrated"
        if self.emotions.confidence_level > 0.7:
            return "confident"
        if self.emotions.engagement_level > 0.7:
            return "engaged"
        if self.emotions.stress_indicators > 0.6:
            return "stressed"
        return "neutral"
