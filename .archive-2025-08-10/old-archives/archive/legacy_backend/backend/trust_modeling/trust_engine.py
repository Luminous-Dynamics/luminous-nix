"""
from typing import Optional
Trust Engine - Main orchestrator for Theory of Mind trust modeling

This implements the core trust dynamics from SOUL_OF_PARTNERSHIP research,
enabling genuine human-AI partnership through vulnerability, repair, and
mutual understanding.
"""

import json
import logging
from datetime import datetime
from enum import Enum

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class TrustState(Enum):
    """Trust states based on CASA research"""

    UNKNOWN = "unknown"
    TENTATIVE = "tentative"
    BUILDING = "building"
    ESTABLISHED = "established"
    DEEP = "deep"
    DAMAGED = "damaged"
    REPAIRING = "repairing"


class TrustEngine:
    """
    Orchestrates trust building through Theory of Mind modeling

    Key innovations from research:
    1. CASA paradigm - AI as social actor
    2. Trust through vulnerability
    3. Repair as trust catalyst
    4. Bi-directional mental modeling
    """

    def __init__(self, skg: SymbioticKnowledgeGraph | None = None):
        self.skg = skg or SymbioticKnowledgeGraph()
        self.logger = logging.getLogger(__name__)

        # Initialize components
        from .mental_state_model import MentalStateModel
        from .repair_mechanism import RepairMechanism
        from .trust_metrics import TrustMetrics
        from .vulnerability_tracker import VulnerabilityTracker

        self.mental_model = MentalStateModel(self.skg)
        self.vulnerability = VulnerabilityTracker(self.skg)
        self.repair = RepairMechanism(self.skg)
        self.metrics = TrustMetrics(self.skg)

        # Trust state tracking
        self.current_state = TrustState.UNKNOWN
        self.trust_history = []

        # Initialize trust model in SKG
        self._init_trust_model()

    def _init_trust_model(self):
        """Initialize trust model in the knowledge graph"""
        cursor = self.skg.conn.cursor()

        # Check if trust model exists
        trust_model = cursor.execute(
            """
            SELECT id FROM nodes 
            WHERE layer = 'metacognitive' 
            AND type = 'trust_model'
            LIMIT 1
        """
        ).fetchone()

        if not trust_model:
            # Create initial trust model
            cursor.execute(
                """
                INSERT INTO nodes (id, layer, type, properties)
                VALUES ('trust_model_core', 'metacognitive', 'trust_model', ?)
            """,
                (
                    json.dumps(
                        {
                            "state": self.current_state.value,
                            "vulnerability_level": 0.0,
                            "repair_count": 0,
                            "trust_score": 0.5,
                            "initialized": datetime.now().isoformat(),
                        }
                    ),
                ),
            )
            self.skg.conn.commit()

    def process_interaction(
        self, interaction_id: str, user_input: str, ai_response: str
    ) -> dict:
        """
        Process an interaction and update trust dynamics

        This is the core entry point that orchestrates all trust components
        """
        # Update mental state model
        mental_state = self.mental_model.update_from_interaction(
            interaction_id, user_input, ai_response
        )

        # Check for vulnerability opportunities
        vulnerability_action = self.vulnerability.check_vulnerability_opportunity(
            mental_state
        )

        # Check if repair is needed
        repair_needed = self.repair.detect_repair_need(interaction_id)

        # Calculate current trust level
        trust_level = self.metrics.calculate_trust_score(
            mental_state,
            self.vulnerability.get_vulnerability_history(),
            self.repair.get_repair_history(),
        )

        # Update trust state
        new_state = self._determine_trust_state(trust_level, repair_needed)
        if new_state != self.current_state:
            self._transition_trust_state(new_state, interaction_id)

        # Generate trust context for response adaptation
        trust_context = {
            "state": self.current_state.value,
            "trust_level": trust_level,
            "mental_state": mental_state,
            "vulnerability_action": vulnerability_action,
            "repair_needed": repair_needed,
            "adaptation_hints": self._generate_adaptation_hints(),
        }

        # Record in SKG
        self._record_trust_update(interaction_id, trust_context)

        return trust_context

    def _determine_trust_state(
        self, trust_level: float, repair_needed: bool
    ) -> TrustState:
        """Determine appropriate trust state based on metrics"""
        if repair_needed:
            return TrustState.REPAIRING
        if trust_level < 0.2:
            return TrustState.DAMAGED
        if trust_level < 0.4:
            return TrustState.TENTATIVE
        if trust_level < 0.6:
            return TrustState.BUILDING
        if trust_level < 0.8:
            return TrustState.ESTABLISHED
        return TrustState.DEEP

    def _transition_trust_state(self, new_state: TrustState, interaction_id: str):
        """Handle trust state transitions"""
        old_state = self.current_state
        self.current_state = new_state

        # Record transition
        self.trust_history.append(
            {
                "from": old_state.value,
                "to": new_state.value,
                "interaction": interaction_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        self.logger.info(
            f"Trust state transition: {old_state.value} → {new_state.value}"
        )

    def _generate_adaptation_hints(self) -> dict:
        """Generate hints for response adaptation based on trust state"""
        hints = {
            "formality_level": "neutral",
            "vulnerability_appropriate": False,
            "repair_language": False,
            "uncertainty_expression": "moderate",
        }

        if self.current_state == TrustState.TENTATIVE:
            hints["formality_level"] = "slightly_formal"
            hints["uncertainty_expression"] = "explicit"

        elif self.current_state == TrustState.BUILDING:
            hints["vulnerability_appropriate"] = True
            hints["uncertainty_expression"] = "balanced"

        elif self.current_state == TrustState.ESTABLISHED:
            hints["formality_level"] = "casual"
            hints["vulnerability_appropriate"] = True

        elif self.current_state == TrustState.DEEP:
            hints["formality_level"] = "intimate"
            hints["vulnerability_appropriate"] = True
            hints["uncertainty_expression"] = "natural"

        elif self.current_state == TrustState.REPAIRING:
            hints["repair_language"] = True
            hints["vulnerability_appropriate"] = True
            hints["uncertainty_expression"] = "explicit"

        return hints

    def _record_trust_update(self, interaction_id: str, trust_context: dict):
        """Record trust update in knowledge graph"""
        trust_update_id = f"trust_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        cursor = self.skg.conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'trust_update', ?)
        """,
            (
                trust_update_id,
                json.dumps(
                    {"context": trust_context, "timestamp": datetime.now().isoformat()}
                ),
            ),
        )

        # Link to interaction
        edge_id = f"edge_trust_{trust_update_id}_{interaction_id}"
        cursor.execute(
            """
            INSERT INTO edges (id, type, from_node, to_node, properties)
            VALUES (?, 'TRUST_CONTEXT_FOR', ?, ?, ?)
        """,
            (
                edge_id,
                trust_update_id,
                interaction_id,
                json.dumps({"trust_level": trust_context["trust_level"]}),
            ),
        )

        self.skg.conn.commit()

    def express_vulnerability(self, vulnerability_type: str, context: dict) -> dict:
        """
        Express appropriate vulnerability to build trust

        Based on research showing vulnerability as trust catalyst
        """
        vulnerability_expression = self.vulnerability.generate_vulnerability(
            vulnerability_type, self.current_state, context
        )

        # Record vulnerability expression
        self.vulnerability.record_vulnerability(
            vulnerability_type, vulnerability_expression, context
        )

        return vulnerability_expression

    def initiate_repair(self, error_context: dict) -> dict:
        """
        Initiate conversational repair when needed

        Implements the insight that repair builds stronger trust
        """
        repair_strategy = self.repair.generate_repair_strategy(
            error_context, self.current_state, self.mental_model.get_user_state()
        )

        # Execute repair
        repair_result = self.repair.execute_repair(repair_strategy)

        return repair_result

    def get_trust_summary(self) -> dict:
        """Get comprehensive trust summary"""
        return {
            "current_state": self.current_state.value,
            "trust_score": self.metrics.get_current_trust_score(),
            "mental_model": self.mental_model.get_model_summary(),
            "vulnerability_count": len(self.vulnerability.get_vulnerability_history()),
            "repair_success_rate": self.repair.get_repair_success_rate(),
            "relationship_duration": self._calculate_relationship_duration(),
            "trust_trajectory": self._analyze_trust_trajectory(),
        }

    def _calculate_relationship_duration(self) -> dict:
        """Calculate how long the relationship has existed"""
        cursor = self.skg.conn.cursor()

        first_interaction = cursor.execute(
            """
            SELECT created_at FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            ORDER BY created_at ASC
            LIMIT 1
        """
        ).fetchone()

        if first_interaction:
            start = datetime.fromisoformat(first_interaction["created_at"])
            duration = datetime.now() - start
            return {
                "days": duration.days,
                "interactions": self._count_total_interactions(),
            }

        return {"days": 0, "interactions": 0}

    def _count_total_interactions(self) -> int:
        """Count total number of interactions"""
        cursor = self.skg.conn.cursor()
        return cursor.execute(
            """
            SELECT COUNT(*) FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
        """
        ).fetchone()[0]

    def _analyze_trust_trajectory(self) -> str:
        """Analyze the trajectory of trust development"""
        if len(self.trust_history) < 2:
            return "emerging"

        # Look at recent transitions
        recent = self.trust_history[-5:]
        states = [t["to"] for t in recent]

        # Check trajectory
        if all(s in ["established", "deep"] for s in states):
            return "stable_high"
        if "damaged" in states or "repairing" in states:
            return "recovering"
        if states[-1] in ["building", "established"]:
            return "ascending"
        return "variable"
