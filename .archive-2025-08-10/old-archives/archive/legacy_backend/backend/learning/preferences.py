"""
from typing import List, Dict, Optional
User preference learning and management

This module tracks and learns user preferences to provide a more personalized experience.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any


class PreferenceManager:
    """Manage and learn user preferences"""

    def __init__(self, data_dir: Path | None = None):
        """
        Initialize preference manager

        Args:
            data_dir: Directory for storing preference data
        """
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "nix-for-humanity"

        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.data_dir / "preferences.db"
        self._init_database()

    def _init_database(self):
        """Initialize the preferences database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # User preferences table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_key)
            )
        """
        )

        # Interaction patterns table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Command history table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY,
                user_id TEXT NOT NULL,
                command TEXT NOT NULL,
                success BOOLEAN,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def get_preferences(self, user_id: str) -> dict[str, Any]:
        """Get all preferences for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """
            SELECT preference_key, preference_value, confidence
            FROM preferences
            WHERE user_id = ?
        """,
            (user_id,),
        )

        preferences = {}
        for key, value, confidence in c.fetchall():
            try:
                # Try to parse as JSON
                parsed_value = json.loads(value)
            except Exception:
                parsed_value = value

            preferences[key] = {"value": parsed_value, "confidence": confidence}

        conn.close()
        return preferences

    def set_preference(
        self, user_id: str, key: str, value: Any, confidence: float = 0.5
    ):
        """Set a user preference"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Serialize value to JSON
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)

        c.execute(
            """
            INSERT OR REPLACE INTO preferences
            (user_id, preference_key, preference_value, confidence, last_updated)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (user_id, key, value_str, confidence),
        )

        conn.commit()
        conn.close()

    def learn_from_interaction(self, user_id: str, interaction: dict[str, Any]):
        """Learn from a user interaction"""
        # Extract relevant signals
        intent_type = interaction.get("intent_type")
        success = interaction.get("success", True)
        response_time = interaction.get("response_time")
        personality_used = interaction.get("personality", "friendly")

        # Update personality preference
        if success:
            self._update_personality_preference(user_id, personality_used)

        # Track command patterns
        if intent_type == "install_package":
            package = interaction.get("package")
            if package:
                self._track_package_preference(user_id, package)

        # Track interaction timing
        if response_time:
            self._track_timing_preference(user_id, response_time)

    def _update_personality_preference(self, user_id: str, personality: str):
        """Update personality preference based on successful interaction"""
        current_prefs = self.get_preferences(user_id)
        personality_scores = current_prefs.get("personality_scores", {}).get(
            "value", {}
        )

        # Increment score for used personality
        if personality not in personality_scores:
            personality_scores[personality] = 0
        personality_scores[personality] += 1

        # Calculate preferred personality
        if personality_scores:
            preferred = max(personality_scores, key=personality_scores.get)
            total_interactions = sum(personality_scores.values())
            confidence = personality_scores[preferred] / total_interactions

            self.set_preference(user_id, "preferred_personality", preferred, confidence)
            self.set_preference(user_id, "personality_scores", personality_scores)

            # Also store personality traits for fine-grained adaptation
            self._update_personality_traits(user_id, personality, confidence)

    def _update_personality_traits(
        self, user_id: str, personality: str, confidence: float
    ):
        """Update fine-grained personality traits based on usage patterns"""
        # Map personality styles to trait adjustments
        trait_adjustments = {
            "minimal": {"verbosity": -0.1, "technicality": 0.1},
            "friendly": {"emotiveness": 0.1, "formality": -0.1},
            "encouraging": {"encouragement": 0.1, "patience": 0.1},
            "playful": {"playfulness": 0.1, "formality": -0.1},
            "sacred": {"spirituality": 0.1, "patience": 0.1},
            "professional": {"formality": 0.1, "emotiveness": -0.1},
            "teacher": {"patience": 0.1, "verbosity": 0.1},
            "companion": {"emotiveness": 0.1, "encouragement": 0.1},
            "hacker": {"technicality": 0.2, "verbosity": -0.1},
            "zen": {"spirituality": 0.1, "verbosity": -0.1},
        }

        if personality in trait_adjustments:
            current_traits = (
                self.get_preferences(user_id)
                .get("personality_traits", {})
                .get("value", {})
            )

            # Apply adjustments scaled by confidence
            for trait, adjustment in trait_adjustments[personality].items():
                current_value = current_traits.get(trait, 0.5)
                new_value = max(
                    0.0, min(1.0, current_value + (adjustment * confidence))
                )
                current_traits[trait] = new_value

            self.set_preference(
                user_id, "personality_traits", current_traits, confidence
            )

    def _track_package_preference(self, user_id: str, package: str):
        """Track package installation patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Record in patterns
        c.execute(
            """
            INSERT INTO patterns (user_id, pattern_type, pattern_data)
            VALUES (?, 'package_install', ?)
            ON CONFLICT DO UPDATE SET
            frequency = frequency + 1,
            last_seen = CURRENT_TIMESTAMP
        """,
            (user_id, package),
        )

        conn.commit()
        conn.close()

    def _track_timing_preference(self, user_id: str, response_time: float):
        """Track timing preferences"""
        current_prefs = self.get_preferences(user_id)
        timing_data = current_prefs.get("timing_preferences", {}).get("value", {})

        # Update average response time preference
        if "avg_response_time" not in timing_data:
            timing_data["avg_response_time"] = response_time
            timing_data["count"] = 1
        else:
            count = timing_data["count"]
            avg = timing_data["avg_response_time"]
            new_avg = (avg * count + response_time) / (count + 1)
            timing_data["avg_response_time"] = new_avg
            timing_data["count"] = count + 1

        self.set_preference(user_id, "timing_preferences", timing_data)

    def get_package_recommendations(self, user_id: str) -> list[str]:
        """Get package recommendations based on history"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Get frequently installed packages
        c.execute(
            """
            SELECT pattern_data, frequency
            FROM patterns
            WHERE user_id = ? AND pattern_type = 'package_install'
            ORDER BY frequency DESC
            LIMIT 10
        """,
            (user_id,),
        )

        recommendations = []
        for package, frequency in c.fetchall():
            if frequency > 1:  # Only recommend if installed more than once
                recommendations.append(package)

        conn.close()
        return recommendations

    def record_command(self, user_id: str, command: str, success: bool):
        """Record a command execution"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO command_history (user_id, command, success)
            VALUES (?, ?, ?)
        """,
            (user_id, command, success),
        )

        conn.commit()
        conn.close()

    def get_command_success_rate(self, user_id: str) -> float:
        """Get the command success rate for a user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute(
            """
            SELECT 
                COUNT(CASE WHEN success = 1 THEN 1 END) as successes,
                COUNT(*) as total
            FROM command_history
            WHERE user_id = ?
        """,
            (user_id,),
        )

        result = c.fetchone()
        conn.close()

        if result and result[1] > 0:
            return result[0] / result[1]
        return 0.0

    def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """Get a comprehensive user profile"""
        preferences = self.get_preferences(user_id)

        profile = {
            "user_id": user_id,
            "preferred_personality": preferences.get("preferred_personality", {}).get(
                "value", "friendly"
            ),
            "command_success_rate": self.get_command_success_rate(user_id),
            "package_recommendations": self.get_package_recommendations(user_id),
            "preferences": preferences,
        }

        return profile
