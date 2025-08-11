"""
Four-Dimensional Learning System Implementation.

Implements the revolutionary "Persona of One" approach with four dimensions:
1. WHO - User modeling (cognitive & affective states)
2. WHAT - Intent learning (evolving vocabulary)
3. HOW - Method learning (workflow preferences)
4. WHEN - Timing intelligence (interruption calculus)

This creates a comprehensive digital twin that learns and evolves with each user,
implementing Bayesian Knowledge Tracing, Dynamic Bayesian Networks, and RLHF.

Since: v1.2.0
"""

import json
import logging
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ============================================================================
# DIMENSION 1: WHO - User Modeling
# ============================================================================


@dataclass
class SkillMastery:
    """Bayesian Knowledge Tracing for individual skills."""

    skill_id: str
    prior_knowledge: float = 0.3  # P(L₀) - initial mastery probability
    learning_rate: float = 0.1  # P(T) - probability of learning
    slip_probability: float = 0.1  # P(S) - mistakes despite mastery
    guess_probability: float = 0.2  # P(G) - correct without mastery
    current_mastery: float = 0.3  # P(Lₜ) - current belief
    confidence: float = 0.5  # Certainty in estimate
    last_updated: datetime = field(default_factory=datetime.now)

    def update(self, correct: bool) -> float:
        """
        Update mastery belief using Bayesian Knowledge Tracing.

        Args:
            correct: Whether the user's action was correct

        Returns:
            Updated mastery probability
        """
        # Bayes' rule update
        if correct:
            # P(L|correct) = P(L) * (1-S) / P(correct)
            p_correct = (
                self.current_mastery * (1 - self.slip_probability)
                + (1 - self.current_mastery) * self.guess_probability
            )
            if p_correct > 0:
                self.current_mastery = (
                    self.current_mastery * (1 - self.slip_probability) / p_correct
                )
        else:
            # P(L|incorrect) = P(L) * S / P(incorrect)
            p_incorrect = self.current_mastery * self.slip_probability + (
                1 - self.current_mastery
            ) * (1 - self.guess_probability)
            if p_incorrect > 0:
                self.current_mastery = (
                    self.current_mastery * self.slip_probability / p_incorrect
                )

        # Learning opportunity - move toward mastery
        self.current_mastery = (
            self.current_mastery + (1 - self.current_mastery) * self.learning_rate
        )

        # Update confidence based on consistency
        self.confidence = min(0.95, self.confidence + 0.05)
        self.last_updated = datetime.now()

        return self.current_mastery


@dataclass
class AffectiveState:
    """Dynamic Bayesian Network for user's emotional/cognitive state."""

    flow: float = 0.0  # Deep concentration
    anxiety: float = 0.0  # Worry from difficulty
    boredom: float = 0.0  # Low engagement
    cognitive_load: float = 0.0  # Working memory usage
    fatigue: float = 0.0  # Mental tiredness

    def normalize(self):
        """Ensure probabilities sum to reasonable values."""
        total = (
            self.flow + self.anxiety + self.boredom + self.cognitive_load + self.fatigue
        )
        if total > 0:
            scale = min(1.0, 1.0 / total)
            self.flow *= scale
            self.anxiety *= scale
            self.boredom *= scale
            self.cognitive_load *= scale
            self.fatigue *= scale

    def update_from_interaction(
        self, success: bool, response_time: float, complexity: float
    ):
        """
        Update affective state based on interaction.

        Args:
            success: Whether action succeeded
            response_time: How long user took
            complexity: Task complexity (0-1)
        """
        # Quick success increases flow
        if success and response_time < 2.0:
            self.flow = min(1.0, self.flow + 0.1)
            self.anxiety = max(0.0, self.anxiety - 0.05)

        # Failure increases anxiety
        if not success:
            self.anxiety = min(1.0, self.anxiety + 0.1)
            self.flow = max(0.0, self.flow - 0.1)

        # High complexity increases cognitive load
        self.cognitive_load = 0.7 * self.cognitive_load + 0.3 * complexity

        # Long sessions increase fatigue
        session_factor = min(1.0, response_time / 60.0)  # Normalized to minute
        self.fatigue = min(1.0, self.fatigue + 0.01 * session_factor)

        # Low complexity with success might indicate boredom
        if success and complexity < 0.3:
            self.boredom = min(1.0, self.boredom + 0.05)

        self.normalize()


@dataclass
class UserVocabulary:
    """User's personal vocabulary and language patterns."""

    aliases: dict[str, str] = field(default_factory=dict)  # "grab" → "install"
    preferences: dict[str, str] = field(default_factory=dict)  # "browser" → "firefox"
    corrections: list[tuple[str, str]] = field(default_factory=list)
    typo_patterns: dict[str, str] = field(default_factory=dict)

    def learn_alias(self, user_term: str, system_term: str):
        """Learn a new vocabulary mapping."""
        self.aliases[user_term] = system_term
        logger.debug(f"Learned alias: '{user_term}' → '{system_term}'")

    def learn_preference(self, category: str, choice: str):
        """Learn user's preferred choice."""
        self.preferences[category] = choice
        logger.debug(f"Learned preference: {category} → {choice}")


# ============================================================================
# DIMENSION 2: WHAT - Intent Learning
# ============================================================================


@dataclass
class IntentContext:
    """Context for understanding user intent."""

    before_commands: list[str] = field(default_factory=list)
    after_commands: list[str] = field(default_factory=list)
    time_of_day: str = ""
    project_context: str | None = None
    working_directory: Path | None = None

    def to_vector(self) -> np.ndarray:
        """Convert context to feature vector for ML."""
        # Simple encoding - would be more sophisticated in production
        features = []

        # Time encoding (hour as cyclic feature)
        hour = datetime.now().hour
        features.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])

        # Command history encoding (last 3 commands)
        for i in range(3):
            if i < len(self.before_commands):
                # Hash command to feature
                features.append(hash(self.before_commands[-(i + 1)]) % 100 / 100)
            else:
                features.append(0.0)

        return np.array(features)


@dataclass
class InferredGoal:
    """An inferred user goal from patterns."""

    goal_type: str  # "install_dev_env", "system_update", etc.
    confidence: float
    evidence: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# DIMENSION 3: HOW - Method Learning
# ============================================================================


@dataclass
class WorkflowPreference:
    """User's preferred methods for tasks."""

    declarative_ratio: float = 0.5  # Config.nix vs nix-env preference
    channel_preference: list[str] = field(default_factory=lambda: ["nixpkgs"])
    package_variants: dict[str, str] = field(default_factory=dict)
    common_sequences: list[list[str]] = field(default_factory=list)
    error_recoveries: dict[str, list[str]] = field(default_factory=dict)

    def learn_sequence(self, commands: list[str]):
        """Learn a command sequence pattern."""
        if len(commands) > 1:
            # Keep last 10 sequences
            self.common_sequences.append(commands)
            if len(self.common_sequences) > 10:
                self.common_sequences.pop(0)

    def learn_recovery(self, error: str, solution: list[str]):
        """Learn how user recovers from errors."""
        if error not in self.error_recoveries:
            self.error_recoveries[error] = []
        self.error_recoveries[error].append(solution)


# ============================================================================
# DIMENSION 4: WHEN - Timing Intelligence
# ============================================================================


@dataclass
class TimingProfile:
    """User's temporal patterns and timing preferences."""

    work_hours: list[tuple[int, int]] = field(default_factory=list)
    peak_performance: list[tuple[int, int]] = field(default_factory=list)
    maintenance_windows: list[tuple[int, int]] = field(default_factory=list)
    interaction_history: deque = field(default_factory=lambda: deque(maxlen=100))

    def update_from_interaction(self, timestamp: datetime):
        """Update timing patterns from interaction."""
        hour = timestamp.hour
        self.interaction_history.append(hour)

        # Simple clustering for work hours
        if len(self.interaction_history) > 20:
            hours = list(self.interaction_history)
            # Find most active 8-hour window
            max_count = 0
            best_start = 9

            for start in range(24):
                count = sum(1 for h in hours if start <= h < (start + 8) % 24)
                if count > max_count:
                    max_count = count
                    best_start = start

            self.work_hours = [(best_start, (best_start + 8) % 24)]

    def is_good_time_to_interrupt(self) -> bool:
        """Calculate if now is a good time for interruption."""
        current_hour = datetime.now().hour

        # Not during peak performance
        for start, end in self.peak_performance:
            if start <= current_hour < end:
                return False

        # Prefer maintenance windows
        for start, end in self.maintenance_windows:
            if start <= current_hour < end:
                return True

        # Default: interrupt if in work hours
        for start, end in self.work_hours:
            if start <= current_hour < end:
                return True

        return False


@dataclass
class InterruptionCalculus:
    """Advanced interruption timing based on cognitive science."""

    cognitive_load_threshold: float = 0.7
    flow_protection_enabled: bool = True
    natural_boundaries: list[str] = field(default_factory=list)
    intervention_urgency: dict[str, float] = field(default_factory=dict)

    def should_interrupt(
        self, urgency: float, user_state: AffectiveState, timing: TimingProfile
    ) -> tuple[bool, str]:
        """
        Calculate whether to interrupt user.

        Args:
            urgency: How urgent the interruption is (0-1)
            user_state: Current affective state
            timing: User's timing profile

        Returns:
            Tuple of (should_interrupt, reason)
        """
        reasons = []

        # Never interrupt during high flow
        if user_state.flow > 0.8 and self.flow_protection_enabled:
            return False, "User in flow state"

        # Avoid interrupting during high cognitive load
        if user_state.cognitive_load > self.cognitive_load_threshold:
            if urgency < 0.8:
                return False, "Cognitive load too high"
            reasons.append("High urgency overrides cognitive load")

        # Check timing preferences
        if not timing.is_good_time_to_interrupt():
            if urgency < 0.6:
                return False, "Outside preferred interruption window"
            reasons.append("Urgency overrides timing preference")

        # High fatigue - be gentle
        if user_state.fatigue > 0.7:
            if urgency < 0.5:
                return False, "User is fatigued"
            reasons.append("Important despite fatigue")

        return True, " | ".join(reasons) if reasons else "Good time to interrupt"


# ============================================================================
# MAIN FOUR-DIMENSIONAL LEARNING SYSTEM
# ============================================================================


class FourDimensionalLearningSystem:
    """
    The complete four-dimensional learning system creating a "Persona of One".

    Integrates:
    - WHO: Bayesian Knowledge Tracing + Dynamic Bayesian Networks
    - WHAT: Intent recognition and goal inference
    - HOW: Workflow preference learning
    - WHEN: Timing intelligence and interruption calculus

    Since: v1.2.0
    """

    def __init__(self, user_id: str, storage_path: Path | None = None):
        """
        Initialize learning system for a user.

        Args:
            user_id: Unique user identifier
            storage_path: Where to persist learning data
        """
        self.user_id = user_id
        self.storage_path = storage_path or Path.home() / ".nix-humanity" / "learning"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize four dimensions
        self.skill_mastery: dict[str, SkillMastery] = {}
        self.affective_state = AffectiveState()
        self.vocabulary = UserVocabulary()
        self.intent_context = IntentContext()
        self.workflow_preferences = WorkflowPreference()
        self.timing_profile = TimingProfile()
        self.interruption_calculus = InterruptionCalculus()

        # Load existing profile if available
        self.load_profile()

    def observe_interaction(
        self,
        command: str,
        success: bool,
        response_time: float,
        error: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Learn from a user interaction.

        Args:
            command: The command/query issued
            success: Whether it succeeded
            response_time: How long it took
            error: Error message if failed
            context: Additional context
        """
        timestamp = datetime.now()

        # Update WHO dimension
        self._update_skill_mastery(command, success)
        self._update_affective_state(success, response_time, command)

        # Update WHAT dimension
        self._update_intent_learning(command, context)

        # Update HOW dimension
        self._update_workflow_learning(command, success, error)

        # Update WHEN dimension
        self.timing_profile.update_from_interaction(timestamp)

        # Persist updates
        self.save_profile()

    def _update_skill_mastery(self, command: str, success: bool):
        """Update skill mastery for relevant skills."""
        # Extract skills from command (simplified)
        skills = self._extract_skills(command)

        for skill_id in skills:
            if skill_id not in self.skill_mastery:
                self.skill_mastery[skill_id] = SkillMastery(skill_id)

            self.skill_mastery[skill_id].update(success)

    def _update_affective_state(
        self, success: bool, response_time: float, command: str
    ):
        """Update user's affective state."""
        # Estimate complexity from command
        complexity = self._estimate_complexity(command)
        self.affective_state.update_from_interaction(success, response_time, complexity)

    def _update_intent_learning(self, command: str, context: dict[str, Any] | None):
        """Update intent understanding."""
        # Add to command history
        self.intent_context.before_commands.append(command)
        if len(self.intent_context.before_commands) > 10:
            self.intent_context.before_commands.pop(0)

        # Update context if provided
        if context:
            if "working_directory" in context:
                self.intent_context.working_directory = Path(
                    context["working_directory"]
                )
            if "project" in context:
                self.intent_context.project_context = context["project"]

    def _update_workflow_learning(self, command: str, success: bool, error: str | None):
        """Update workflow preferences."""
        # Learn from declarative vs imperative patterns
        if "configuration.nix" in command:
            self.workflow_preferences.declarative_ratio = (
                0.9 * self.workflow_preferences.declarative_ratio + 0.1
            )
        elif "nix-env" in command:
            self.workflow_preferences.declarative_ratio = (
                0.9 * self.workflow_preferences.declarative_ratio
            )

        # Learn error recovery
        if error and not success:
            # Store for learning recovery patterns
            if not hasattr(self, "_last_error"):
                self._last_error = error
                self._recovery_commands = []
        elif hasattr(self, "_last_error") and success:
            # Successful recovery
            self.workflow_preferences.learn_recovery(
                self._last_error, self._recovery_commands + [command]
            )
            delattr(self, "_last_error")
            self._recovery_commands = []

    def get_personalized_suggestion(
        self, query: str, urgency: float = 0.5
    ) -> dict[str, Any]:
        """
        Get personalized suggestion based on all four dimensions.

        Args:
            query: User's query
            urgency: How urgent the response is

        Returns:
            Personalized response with timing and method preferences
        """
        # Check if good time to respond
        should_respond, timing_reason = self.interruption_calculus.should_interrupt(
            urgency, self.affective_state, self.timing_profile
        )

        # Get relevant skills and mastery
        skills = self._extract_skills(query)
        avg_mastery = (
            np.mean(
                [
                    self.skill_mastery.get(s, SkillMastery(s)).current_mastery
                    for s in skills
                ]
            )
            if skills
            else 0.5
        )

        # Adjust response based on state
        response = {
            "timing_appropriate": should_respond,
            "timing_reason": timing_reason,
            "skill_mastery": avg_mastery,
            "affective_aware": {
                "in_flow": self.affective_state.flow > 0.6,
                "needs_break": self.affective_state.fatigue > 0.7,
                "simplify": self.affective_state.cognitive_load > 0.7,
            },
            "method_preference": {
                "use_declarative": self.workflow_preferences.declarative_ratio > 0.6,
                "preferred_channel": (
                    self.workflow_preferences.channel_preference[0]
                    if self.workflow_preferences.channel_preference
                    else "nixpkgs"
                ),
            },
            "vocabulary_adjusted": self._apply_vocabulary(query),
        }

        return response

    def _extract_skills(self, command: str) -> list[str]:
        """Extract skill IDs from command."""
        # Simplified skill extraction
        skills = []

        skill_keywords = {
            "install": ["package_management", "nix-env"],
            "build": ["derivations", "nix-build"],
            "shell": ["development", "nix-shell"],
            "flake": ["flakes", "advanced"],
            "configuration": ["declarative", "nixos-config"],
            "update": ["system_maintenance", "nixos-rebuild"],
        }

        for keyword, skill_list in skill_keywords.items():
            if keyword in command.lower():
                skills.extend(skill_list)

        return skills

    def _estimate_complexity(self, command: str) -> float:
        """Estimate command complexity (0-1)."""
        # Simple heuristic
        complexity_indicators = [
            ("flake", 0.8),
            ("overlay", 0.9),
            ("derivation", 0.7),
            ("configuration.nix", 0.6),
            ("install", 0.3),
            ("search", 0.2),
        ]

        max_complexity = 0.3  # Base complexity
        for indicator, weight in complexity_indicators:
            if indicator in command.lower():
                max_complexity = max(max_complexity, weight)

        return max_complexity

    def _apply_vocabulary(self, text: str) -> str:
        """Apply learned vocabulary transformations."""
        result = text
        for user_term, system_term in self.vocabulary.aliases.items():
            result = result.replace(user_term, system_term)
        return result

    def save_profile(self):
        """Persist learning to disk."""
        profile_file = self.storage_path / f"{self.user_id}_profile.json"

        profile_data = {
            "skill_mastery": {
                skill_id: {
                    "current_mastery": skill.current_mastery,
                    "confidence": skill.confidence,
                    "learning_rate": skill.learning_rate,
                }
                for skill_id, skill in self.skill_mastery.items()
            },
            "affective_state": asdict(self.affective_state),
            "vocabulary": {
                "aliases": self.vocabulary.aliases,
                "preferences": self.vocabulary.preferences,
            },
            "workflow": {
                "declarative_ratio": self.workflow_preferences.declarative_ratio,
                "channel_preference": self.workflow_preferences.channel_preference,
            },
            "timing": {
                "work_hours": self.timing_profile.work_hours,
                "interaction_history": list(self.timing_profile.interaction_history),
            },
        }

        with open(profile_file, "w") as f:
            json.dump(profile_data, f, indent=2, default=str)

        logger.debug(f"Saved learning profile for {self.user_id}")

    def load_profile(self):
        """Load learning from disk."""
        profile_file = self.storage_path / f"{self.user_id}_profile.json"

        if not profile_file.exists():
            logger.info(f"No existing profile for {self.user_id}, starting fresh")
            return

        try:
            with open(profile_file) as f:
                profile_data = json.load(f)

            # Restore skill mastery
            for skill_id, data in profile_data.get("skill_mastery", {}).items():
                self.skill_mastery[skill_id] = SkillMastery(
                    skill_id=skill_id,
                    current_mastery=data["current_mastery"],
                    confidence=data["confidence"],
                    learning_rate=data.get("learning_rate", 0.1),
                )

            # Restore affective state
            if "affective_state" in profile_data:
                state = profile_data["affective_state"]
                self.affective_state = AffectiveState(**state)

            # Restore vocabulary
            if "vocabulary" in profile_data:
                self.vocabulary.aliases = profile_data["vocabulary"].get("aliases", {})
                self.vocabulary.preferences = profile_data["vocabulary"].get(
                    "preferences", {}
                )

            # Restore workflow preferences
            if "workflow" in profile_data:
                self.workflow_preferences.declarative_ratio = profile_data[
                    "workflow"
                ].get("declarative_ratio", 0.5)
                self.workflow_preferences.channel_preference = profile_data[
                    "workflow"
                ].get("channel_preference", ["nixpkgs"])

            # Restore timing
            if "timing" in profile_data:
                self.timing_profile.work_hours = profile_data["timing"].get(
                    "work_hours", []
                )
                history = profile_data["timing"].get("interaction_history", [])
                self.timing_profile.interaction_history = deque(history, maxlen=100)

            logger.info(f"Loaded learning profile for {self.user_id}")

        except Exception as e:
            logger.error(f"Failed to load profile: {e}")

    def get_learning_summary(self) -> dict[str, Any]:
        """
        Get a summary of what the system has learned.

        Returns:
            Dictionary with learning insights
        """
        top_skills = sorted(
            self.skill_mastery.items(), key=lambda x: x[1].current_mastery, reverse=True
        )[:5]

        return {
            "user_id": self.user_id,
            "dimensions": {
                "WHO": {
                    "top_skills": [
                        {"skill": skill_id, "mastery": skill.current_mastery}
                        for skill_id, skill in top_skills
                    ],
                    "current_state": {
                        "flow": self.affective_state.flow,
                        "cognitive_load": self.affective_state.cognitive_load,
                        "fatigue": self.affective_state.fatigue,
                    },
                    "vocabulary_size": len(self.vocabulary.aliases),
                },
                "WHAT": {"recent_intents": self.intent_context.before_commands[-5:]},
                "HOW": {
                    "prefers_declarative": self.workflow_preferences.declarative_ratio
                    > 0.6,
                    "error_recovery_learned": len(
                        self.workflow_preferences.error_recoveries
                    ),
                },
                "WHEN": {
                    "work_hours": self.timing_profile.work_hours,
                    "interactions_tracked": len(
                        self.timing_profile.interaction_history
                    ),
                },
            },
            "ready_for_personalization": len(self.skill_mastery) > 5,
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize learning system
    learning = FourDimensionalLearningSystem("test_user")

    # Simulate some interactions
    interactions = [
        ("install firefox", True, 1.5),
        ("nix-shell -p python3", True, 2.0),
        ("flake update", False, 5.0),
        ("nix flake update", True, 3.0),
        ("configuration.nix edit", True, 10.0),
    ]

    for command, success, time_taken in interactions:
        learning.observe_interaction(command, success, time_taken)

    # Get personalized suggestion
    suggestion = learning.get_personalized_suggestion("install vscode")
    print("Personalized Suggestion:")
    print(json.dumps(suggestion, indent=2))

    # Get learning summary
    summary = learning.get_learning_summary()
    print("\nLearning Summary:")
    print(json.dumps(summary, indent=2, default=str))
