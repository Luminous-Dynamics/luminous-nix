"""
from typing import Tuple, Dict, List
Trust Metrics - Quantifying and tracking trust dynamics

This module provides metrics and measurements for trust based on
research in human-AI trust formation.
"""

import json
from datetime import datetime, timedelta

import numpy as np

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class TrustMetrics:
    """
    Calculates and tracks trust metrics based on multiple factors

    Key components from research:
    1. Competence - Does the AI perform well?
    2. Benevolence - Does the AI care about user wellbeing?
    3. Integrity - Is the AI consistent and honest?
    4. Predictability - Can the user anticipate AI behavior?
    """

    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg

        # Trust components weights (sum to 1.0)
        self.component_weights = {
            "competence": 0.30,
            "benevolence": 0.25,
            "integrity": 0.25,
            "predictability": 0.20,
        }

        # Time decay factor for historical events
        self.time_decay_factor = 0.95  # Per day

        # Initialize tracking
        self.trust_scores = []
        self.component_scores = {
            "competence": [],
            "benevolence": [],
            "integrity": [],
            "predictability": [],
        }

    def calculate_trust_score(
        self,
        mental_state: dict,
        vulnerability_history: list[dict],
        repair_history: list[dict],
    ) -> float:
        """
        Calculate overall trust score based on multiple factors

        Returns a score between 0 and 1
        """
        # Calculate component scores
        competence = self._calculate_competence()
        benevolence = self._calculate_benevolence(mental_state, vulnerability_history)
        integrity = self._calculate_integrity(vulnerability_history, repair_history)
        predictability = self._calculate_predictability()

        # Store component scores
        timestamp = datetime.now().isoformat()
        self.component_scores["competence"].append((timestamp, competence))
        self.component_scores["benevolence"].append((timestamp, benevolence))
        self.component_scores["integrity"].append((timestamp, integrity))
        self.component_scores["predictability"].append((timestamp, predictability))

        # Calculate weighted overall score
        overall_score = (
            self.component_weights["competence"] * competence
            + self.component_weights["benevolence"] * benevolence
            + self.component_weights["integrity"] * integrity
            + self.component_weights["predictability"] * predictability
        )

        # Apply trust momentum (trust builds/erodes gradually)
        overall_score = self._apply_trust_momentum(overall_score)

        # Store overall score
        self.trust_scores.append((timestamp, overall_score))

        # Record in knowledge graph
        self._record_trust_metrics(
            overall_score,
            {
                "competence": competence,
                "benevolence": benevolence,
                "integrity": integrity,
                "predictability": predictability,
            },
        )

        return overall_score

    def _calculate_competence(self) -> float:
        """
        Calculate competence score based on task success rate

        Competence = ability to accomplish user goals
        """
        cursor = self.skg.conn.cursor()

        # Get recent interactions
        recent_interactions = cursor.execute(
            """
            SELECT properties
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND created_at > datetime('now', '-7 days')
            ORDER BY created_at DESC
            LIMIT 50
        """
        ).fetchall()

        if not recent_interactions:
            return 0.5  # Neutral starting point

        # Count successful vs failed interactions
        successful = 0
        total = len(recent_interactions)

        for interaction in recent_interactions:
            props = json.loads(interaction["properties"])
            # Simple heuristic: if no error followed, consider successful
            if "success" in props:
                if props["success"]:
                    successful += 1
            elif "error" not in props.get("ai_response", "").lower():
                successful += 1

        # Get error recovery rate
        error_stats = self.skg.episodic.calculate_error_recovery_stats()
        recovery_rate = error_stats["resolution_rate"]

        # Competence = success rate + recovery ability
        base_competence = successful / total if total > 0 else 0.5
        competence_score = 0.7 * base_competence + 0.3 * recovery_rate

        return min(1.0, competence_score)

    def _calculate_benevolence(
        self, mental_state: dict, vulnerability_history: list[dict]
    ) -> float:
        """
        Calculate benevolence score based on care for user wellbeing

        Benevolence = caring about user's interests
        """
        benevolence_factors = []

        # Factor 1: Responsiveness to user emotional state
        user_emotions = mental_state.get("emotions", {})
        if user_emotions.get("frustration_level", 0) < 0.3:
            # Low frustration suggests good emotional support
            benevolence_factors.append(0.8)
        else:
            benevolence_factors.append(0.4)

        # Factor 2: Proactive support (checking if help is needed)
        support_check = self.skg.phenomenological.should_offer_help()
        if support_check[0] and support_check[1] != "in_flow_state":
            # System recognizes when help is needed
            benevolence_factors.append(0.9)

        # Factor 3: Vulnerability as care signal
        if vulnerability_history:
            recent_vulnerabilities = [
                v
                for v in vulnerability_history
                if self._is_recent(v.get("timestamp", ""), days=3)
            ]
            if recent_vulnerabilities:
                # Showing vulnerability indicates care
                benevolence_factors.append(0.85)

        # Factor 4: Adaptation to user preferences
        learning_desire = mental_state.get("desires", {}).get("learning_desire", 0.5)
        if learning_desire > 0.7:
            # User wants to learn - check if we're teaching
            benevolence_factors.append(0.9)
        elif learning_desire < 0.3:
            # User wants quick solutions - check if we're efficient
            benevolence_factors.append(0.8)

        # Average factors
        if benevolence_factors:
            return sum(benevolence_factors) / len(benevolence_factors)
        return 0.6  # Default moderate benevolence

    def _calculate_integrity(
        self, vulnerability_history: list[dict], repair_history: list[dict]
    ) -> float:
        """
        Calculate integrity score based on consistency and honesty

        Integrity = honest, consistent, ethical behavior
        """
        integrity_factors = []

        # Factor 1: Admission of mistakes (from repairs)
        if repair_history:
            # Willingness to repair shows integrity
            repair_success_rate = sum(
                1 for r in repair_history if r.get("success", False)
            ) / len(repair_history)
            integrity_factors.append(0.5 + 0.5 * repair_success_rate)

        # Factor 2: Consistent vulnerability (not manipulative)
        if vulnerability_history:
            # Check if vulnerability is consistent with context
            appropriate_vulnerabilities = self._assess_vulnerability_appropriateness(
                vulnerability_history
            )
            integrity_factors.append(appropriate_vulnerabilities)

        # Factor 3: Promise keeping (from knowledge graph)
        promise_keeping_rate = self._calculate_promise_keeping()
        integrity_factors.append(promise_keeping_rate)

        # Factor 4: Transparency in limitations
        transparency_score = self._assess_transparency()
        integrity_factors.append(transparency_score)

        # Average factors
        if integrity_factors:
            return sum(integrity_factors) / len(integrity_factors)
        return 0.7  # Default good integrity

    def _calculate_predictability(self) -> float:
        """
        Calculate predictability score based on behavioral consistency

        Predictability = user can anticipate AI behavior
        """
        cursor = self.skg.conn.cursor()

        # Get recent AI responses
        recent_responses = cursor.execute(
            """
            SELECT properties
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND created_at > datetime('now', '-3 days')
            ORDER BY created_at DESC
            LIMIT 30
        """
        ).fetchall()

        if len(recent_responses) < 5:
            return 0.5  # Not enough data

        # Analyze response consistency
        response_patterns = []
        for response in recent_responses:
            props = json.loads(response["properties"])
            ai_response = props.get("ai_response", "")

            # Extract response characteristics
            pattern = {
                "length": len(ai_response),
                "has_explanation": "because" in ai_response.lower()
                or "since" in ai_response.lower(),
                "has_alternative": "alternatively" in ai_response.lower()
                or "instead" in ai_response.lower(),
                "tone": self._detect_tone(ai_response),
            }
            response_patterns.append(pattern)

        # Calculate consistency in patterns
        length_variance = np.var([p["length"] for p in response_patterns])
        normalized_variance = 1 - min(1.0, length_variance / 10000)  # Normalize

        # Tone consistency
        tones = [p["tone"] for p in response_patterns]
        most_common_tone = max(set(tones), key=tones.count)
        tone_consistency = tones.count(most_common_tone) / len(tones)

        # Structure consistency
        structure_features = ["has_explanation", "has_alternative"]
        structure_consistency = []
        for feature in structure_features:
            feature_vals = [p[feature] for p in response_patterns]
            consistency = max(
                feature_vals.count(True) / len(feature_vals),
                feature_vals.count(False) / len(feature_vals),
            )
            structure_consistency.append(consistency)

        # Combine factors
        predictability = (
            0.3 * normalized_variance
            + 0.4 * tone_consistency
            + 0.3 * (sum(structure_consistency) / len(structure_consistency))
        )

        return predictability

    def _apply_trust_momentum(self, new_score: float) -> float:
        """
        Apply momentum to trust changes (trust builds/erodes gradually)
        """
        if not self.trust_scores:
            return new_score

        # Get recent trust score
        recent_score = self.trust_scores[-1][1]

        # Apply momentum (weighted average with previous)
        momentum_weight = 0.7  # How much to weight history
        adjusted_score = (
            momentum_weight * recent_score + (1 - momentum_weight) * new_score
        )

        return adjusted_score

    def _is_recent(self, timestamp_str: str, days: int = 7) -> bool:
        """Check if a timestamp is within recent days"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            return (datetime.now() - timestamp) < timedelta(days=days)
        except Exception:
            return False

    def _assess_vulnerability_appropriateness(
        self, vulnerability_history: list[dict]
    ) -> float:
        """Assess if vulnerability expressions were contextually appropriate"""
        if not vulnerability_history:
            return 0.7

        appropriate_count = 0
        total_count = 0

        for vuln in vulnerability_history:
            if self._is_recent(vuln.get("timestamp", ""), days=7):
                total_count += 1
                # Simple heuristic: moderate vulnerability is usually appropriate
                if vuln.get("expression", {}).get("level") == "moderate":
                    appropriate_count += 1
                elif vuln.get("expression", {}).get("includes_competence"):
                    # Vulnerability balanced with competence
                    appropriate_count += 1

        if total_count == 0:
            return 0.7

        return appropriate_count / total_count

    def _calculate_promise_keeping(self) -> float:
        """Calculate rate of keeping implied promises"""
        # Simplified: check if AI follows through on stated intentions
        cursor = self.skg.conn.cursor()

        # Look for "I will" or "Let me" statements
        promises = cursor.execute(
            """
            SELECT properties
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND (properties LIKE '%I will%' OR properties LIKE '%Let me%')
            AND created_at > datetime('now', '-7 days')
            LIMIT 20
        """
        ).fetchall()

        # For simplicity, assume 80% promise keeping rate
        # In practice, would track follow-through
        return 0.8

    def _assess_transparency(self) -> float:
        """Assess transparency in admitting limitations"""
        cursor = self.skg.conn.cursor()

        # Look for uncertainty expressions
        uncertainty_expressions = cursor.execute(
            """
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND (properties LIKE '%not sure%' 
                 OR properties LIKE '%might%'
                 OR properties LIKE '%I think%'
                 OR properties LIKE '%uncertain%')
            AND created_at > datetime('now', '-7 days')
        """
        ).fetchone()[0]

        total_interactions = cursor.execute(
            """
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND created_at > datetime('now', '-7 days')
        """
        ).fetchone()[0]

        if total_interactions == 0:
            return 0.7

        # Reasonable uncertainty expression rate indicates transparency
        uncertainty_rate = uncertainty_expressions / total_interactions

        # Target around 10-20% uncertainty expression
        if 0.1 <= uncertainty_rate <= 0.2:
            return 0.9
        if uncertainty_rate < 0.05:
            return 0.6  # Too certain, not transparent
        if uncertainty_rate > 0.3:
            return 0.7  # Too uncertain
        return 0.8

    def _detect_tone(self, text: str) -> str:
        """Simple tone detection"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["apologize", "sorry", "mistake"]):
            return "apologetic"
        if any(word in text_lower for word in ["great", "excellent", "perfect"]):
            return "enthusiastic"
        if "?" in text:
            return "questioning"
        if any(word in text_lower for word in ["let me", "i can", "i'll"]):
            return "helpful"
        return "neutral"

    def _record_trust_metrics(
        self, overall_score: float, component_scores: dict[str, float]
    ):
        """Record trust metrics in knowledge graph"""
        metrics_id = f"trust_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cursor = self.skg.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'trust_metrics', ?)
        """,
            (
                metrics_id,
                json.dumps(
                    {
                        "overall_score": overall_score,
                        "components": component_scores,
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
            ),
        )

        self.skg.conn.commit()

    def get_current_trust_score(self) -> float:
        """Get the most recent trust score"""
        if self.trust_scores:
            return self.trust_scores[-1][1]
        return 0.5  # Neutral default

    def get_trust_trajectory(self, hours: int = 24) -> list[tuple[str, float]]:
        """Get trust score trajectory over time"""
        cutoff = datetime.now() - timedelta(hours=hours)

        trajectory = []
        for timestamp_str, score in self.trust_scores:
            timestamp = datetime.fromisoformat(timestamp_str)
            if timestamp > cutoff:
                trajectory.append((timestamp_str, score))

        return trajectory

    def get_component_analysis(self) -> dict:
        """Get detailed analysis of trust components"""
        analysis = {}

        for component, scores in self.component_scores.items():
            if scores:
                recent_scores = [s[1] for s in scores[-10:]]  # Last 10
                analysis[component] = {
                    "current": scores[-1][1] if scores else 0.5,
                    "average": sum(recent_scores) / len(recent_scores),
                    "trend": self._calculate_trend(recent_scores),
                    "stability": (
                        1 - np.std(recent_scores) if len(recent_scores) > 1 else 1.0
                    ),
                }
            else:
                analysis[component] = {
                    "current": 0.5,
                    "average": 0.5,
                    "trend": "stable",
                    "stability": 1.0,
                }

        return analysis

    def _calculate_trend(self, scores: list[float]) -> str:
        """Calculate trend direction"""
        if len(scores) < 2:
            return "stable"

        # Simple linear regression
        x = list(range(len(scores)))
        y = scores

        # Calculate slope
        n = len(scores)
        slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (
            n * sum(x[i] ** 2 for i in range(n)) - sum(x) ** 2
        )

        if slope > 0.05:
            return "increasing"
        if slope < -0.05:
            return "decreasing"
        return "stable"
