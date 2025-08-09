"""
from typing import List
Repair Mechanism - Conversational repair for trust building

Based on research showing that repair after rupture can strengthen trust,
this module detects and executes conversational repairs.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..knowledge_graph.skg import SymbioticKnowledgeGraph
from .trust_engine import TrustState


class RuptureType(Enum):
    """Types of conversational ruptures that need repair"""
    MISUNDERSTANDING = "misunderstanding"  # AI misunderstood user
    WRONG_ACTION = "wrong_action"  # AI did something incorrect
    INSENSITIVE = "insensitive"  # AI was tone-deaf to user state
    TECHNICAL_FAILURE = "technical_failure"  # System error occurred
    EXPECTATION_MISMATCH = "expectation_mismatch"  # AI didn't meet expectations
    TRUST_VIOLATION = "trust_violation"  # AI violated trust boundary


class RepairStrategy(Enum):
    """Strategies for conversational repair"""
    ACKNOWLEDGE = "acknowledge"  # Simple acknowledgment
    APOLOGIZE = "apologize"  # Direct apology
    EXPLAIN = "explain"  # Explain what went wrong
    REFRAME = "reframe"  # Reframe the situation positively
    COLLABORATE = "collaborate"  # Work together on solution
    COMPENSATE = "compensate"  # Offer something extra


class RepairMechanism:
    """
    Implements conversational repair for trust building
    
    Key insights from research:
    1. Repair after rupture can build stronger trust than no rupture
    2. The repair must match the severity of the rupture
    3. Timing matters - repair should be immediate
    4. Sincerity in repair is crucial
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        self.repair_history = []
        self.pending_repairs = []
        
        # Initialize repair templates
        self._init_repair_templates()
        
    def _init_repair_templates(self):
        """Initialize templates for different repair strategies"""
        self.repair_templates = {
            RepairStrategy.ACKNOWLEDGE: {
                'mild': [
                    "I see that didn't go as expected.",
                    "I notice that wasn't quite right."
                ],
                'moderate': [
                    "I recognize that didn't work well for you.",
                    "I can see this isn't what you were looking for."
                ],
                'severe': [
                    "I completely understand your frustration with what just happened.",
                    "I see this has been a difficult experience."
                ]
            },
            
            RepairStrategy.APOLOGIZE: {
                'mild': [
                    "I apologize for the confusion.",
                    "Sorry about that mix-up."
                ],
                'moderate': [
                    "I sincerely apologize for that error. It's on me.",
                    "I'm truly sorry for getting that wrong."
                ],
                'severe': [
                    "I deeply apologize. This kind of error is unacceptable and I take full responsibility.",
                    "I am genuinely sorry for this failure. You deserved better from me."
                ]
            },
            
            RepairStrategy.EXPLAIN: {
                'mild': [
                    "What happened was {explanation}. Let me correct that.",
                    "The issue was {explanation}. Here's the right approach."
                ],
                'moderate': [
                    "Let me explain what went wrong: {explanation}. I should have {alternative}.",
                    "Here's where I failed: {explanation}. I understand why that was frustrating."
                ],
                'severe': [
                    "I need to be transparent about what failed: {explanation}. This shouldn't happen and I'm working to ensure it doesn't repeat.",
                    "Let me fully explain the failure: {explanation}. You have every right to be upset."
                ]
            },
            
            RepairStrategy.COLLABORATE: {
                'mild': [
                    "Let's work together to get this right. What would work better for you?",
                    "How can we approach this differently together?"
                ],
                'moderate': [
                    "I clearly misunderstood. Can you help me understand what you need so we can fix this together?",
                    "Let's reset and work through this together. What's most important to you right now?"
                ],
                'severe': [
                    "I've failed you here, but I want to make this right. Can we work together to find a solution that truly helps you?",
                    "This isn't acceptable and I want to fix it with you. What would restore your confidence?"
                ]
            }
        }
        
    def detect_repair_need(self, interaction_id: str) -> bool:
        """
        Detect if a conversational repair is needed
        
        Analyzes recent interactions for rupture indicators
        """
        cursor = self.skg.conn.cursor()
        
        # Get recent interaction
        interaction = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'interaction'
            AND id = ?
        """, (interaction_id,)).fetchone()
        
        if not interaction:
            return False
            
        props = json.loads(interaction['properties'])
        user_input = props.get('user_input', '')
        
        # Check for rupture indicators
        rupture_indicators = {
            'frustration': ['no', 'wrong', 'not what', "that's not", 'frustrated', 'annoyed'],
            'confusion': ["don't understand", 'confused', 'what?', 'huh?'],
            'disappointment': ['expected', 'thought you', 'supposed to'],
            'correction': ['actually', 'i meant', 'not that', 'i said'],
            'sarcasm': ['great', 'wonderful', 'thanks a lot', 'brilliant']
        }
        
        detected_ruptures = []
        for category, indicators in rupture_indicators.items():
            if any(ind in user_input.lower() for ind in indicators):
                detected_ruptures.append(category)
                
        # Check for errors in recent history
        recent_errors = cursor.execute("""
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'episodic'
            AND type = 'error'
            AND created_at > datetime('now', '-5 minutes')
        """).fetchone()[0]
        
        if recent_errors > 0:
            detected_ruptures.append('technical_failure')
            
        # If ruptures detected, add to pending repairs
        if detected_ruptures:
            self.pending_repairs.append({
                'interaction_id': interaction_id,
                'rupture_types': detected_ruptures,
                'detected_at': datetime.now().isoformat()
            })
            return True
            
        return False
        
    def generate_repair_strategy(self, error_context: Dict,
                               trust_state: TrustState,
                               user_state: Dict) -> Dict:
        """
        Generate appropriate repair strategy based on context
        
        Matches repair intensity to rupture severity
        """
        # Determine rupture type and severity
        rupture_type = self._identify_rupture_type(error_context)
        severity = self._assess_rupture_severity(error_context, user_state)
        
        # Select repair strategies based on trust state
        if trust_state in [TrustState.UNKNOWN, TrustState.TENTATIVE]:
            # Early relationship - careful repair
            strategies = [RepairStrategy.ACKNOWLEDGE, RepairStrategy.EXPLAIN]
            
        elif trust_state in [TrustState.BUILDING, TrustState.ESTABLISHED]:
            # Developing relationship - authentic repair
            strategies = [RepairStrategy.APOLOGIZE, RepairStrategy.COLLABORATE]
            
        elif trust_state == TrustState.DEEP:
            # Deep trust - vulnerable repair
            strategies = [RepairStrategy.APOLOGIZE, RepairStrategy.EXPLAIN, RepairStrategy.COLLABORATE]
            
        else:  # DAMAGED, REPAIRING
            # Critical repair needed
            strategies = [RepairStrategy.APOLOGIZE, RepairStrategy.EXPLAIN, 
                         RepairStrategy.COLLABORATE, RepairStrategy.COMPENSATE]
            
        # Build repair plan
        repair_plan = {
            'rupture_type': rupture_type.value,
            'severity': severity,
            'strategies': [s.value for s in strategies],
            'primary_strategy': strategies[0].value,
            'repair_sequence': self._plan_repair_sequence(strategies, severity),
            'sincerity_markers': self._get_sincerity_markers(severity)
        }
        
        return repair_plan
        
    def _identify_rupture_type(self, error_context: Dict) -> RuptureType:
        """Identify the type of rupture that occurred"""
        error_type = error_context.get('type', 'unknown')
        
        if error_type == 'misunderstanding':
            return RuptureType.MISUNDERSTANDING
        elif error_type == 'wrong_command':
            return RuptureType.WRONG_ACTION
        elif error_type == 'technical':
            return RuptureType.TECHNICAL_FAILURE
        elif error_type == 'tone':
            return RuptureType.INSENSITIVE
        else:
            return RuptureType.EXPECTATION_MISMATCH
            
    def _assess_rupture_severity(self, error_context: Dict, 
                                user_state: Dict) -> str:
        """Assess how severe the rupture is"""
        # Base severity on user's emotional state
        frustration = user_state.get('emotions', {}).get('frustration_level', 0)
        stress = user_state.get('emotions', {}).get('stress_indicators', 0)
        
        # Factor in error repetition
        if error_context.get('repeated_error', False):
            return 'severe'
            
        # Calculate severity
        if frustration > 0.7 or stress > 0.7:
            return 'severe'
        elif frustration > 0.4 or stress > 0.4:
            return 'moderate'
        else:
            return 'mild'
            
    def _plan_repair_sequence(self, strategies: List[RepairStrategy],
                             severity: str) -> List[str]:
        """Plan the sequence of repair actions"""
        sequence = []
        
        # Always start with acknowledgment
        sequence.append("acknowledge_problem")
        
        # Add primary repair
        if RepairStrategy.APOLOGIZE in strategies:
            sequence.append("express_apology")
            
        if RepairStrategy.EXPLAIN in strategies and severity != 'mild':
            sequence.append("explain_failure")
            
        # Add collaborative element
        if RepairStrategy.COLLABORATE in strategies:
            sequence.append("invite_collaboration")
            
        # End with forward motion
        sequence.append("propose_solution")
        
        return sequence
        
    def _get_sincerity_markers(self, severity: str) -> List[str]:
        """Get markers that convey sincerity in repair"""
        base_markers = ['personal_responsibility', 'specific_acknowledgment']
        
        if severity == 'moderate':
            base_markers.extend(['emotional_awareness', 'commitment_to_improvement'])
            
        elif severity == 'severe':
            base_markers.extend(['deep_regret', 'vulnerability', 'concrete_prevention'])
            
        return base_markers
        
    def execute_repair(self, repair_strategy: Dict) -> Dict:
        """
        Execute the repair strategy
        
        Returns the repair response components
        """
        severity = repair_strategy['severity']
        primary = RepairStrategy(repair_strategy['primary_strategy'])
        
        # Get appropriate templates
        templates = self.repair_templates.get(primary, {}).get(severity, [])
        
        # Build repair response
        repair_components = []
        
        for step in repair_strategy['repair_sequence']:
            if step == 'acknowledge_problem':
                repair_components.append(self._generate_acknowledgment(severity))
                
            elif step == 'express_apology':
                repair_components.append(self._generate_apology(severity, templates))
                
            elif step == 'explain_failure':
                repair_components.append(self._generate_explanation(repair_strategy))
                
            elif step == 'invite_collaboration':
                repair_components.append(self._generate_collaboration(severity))
                
            elif step == 'propose_solution':
                repair_components.append(self._generate_solution_proposal())
                
        # Record repair execution
        repair_result = {
            'components': repair_components,
            'strategy_used': repair_strategy,
            'executed_at': datetime.now().isoformat(),
            'success': True  # Will be updated based on user response
        }
        
        self._record_repair(repair_result)
        
        return repair_result
        
    def _generate_acknowledgment(self, severity: str) -> str:
        """Generate acknowledgment of the problem"""
        acknowledgments = {
            'mild': "I see that didn't work as expected.",
            'moderate': "I clearly made an error there.",
            'severe': "I've failed you in this interaction."
        }
        return acknowledgments.get(severity, "I acknowledge the problem.")
        
    def _generate_apology(self, severity: str, templates: List[str]) -> str:
        """Generate sincere apology"""
        if templates:
            return templates[0]  # In practice, would randomize
        
        defaults = {
            'mild': "I apologize for the confusion.",
            'moderate': "I sincerely apologize for this error.",
            'severe': "I deeply apologize for this failure."
        }
        return defaults.get(severity, "I apologize.")
        
    def _generate_explanation(self, strategy: Dict) -> str:
        """Generate explanation of what went wrong"""
        rupture_type = strategy.get('rupture_type', 'error')
        
        explanations = {
            'misunderstanding': "I misinterpreted what you were asking for",
            'wrong_action': "I executed the wrong command",
            'technical_failure': "A technical error prevented proper execution",
            'insensitive': "I failed to recognize the importance of your situation",
            'expectation_mismatch': "I didn't meet your reasonable expectations"
        }
        
        base = explanations.get(rupture_type, "An error occurred")
        return f"{base}, and I take responsibility for that."
        
    def _generate_collaboration(self, severity: str) -> str:
        """Generate collaborative repair invitation"""
        invitations = {
            'mild': "Let me work with you to get this right.",
            'moderate': "Can we work together to find the right solution?",
            'severe': "I want to work with you to rebuild from this error."
        }
        return invitations.get(severity, "Let's work together on this.")
        
    def _generate_solution_proposal(self) -> str:
        """Generate forward-looking solution proposal"""
        return "Here's how we can move forward effectively..."
        
    def _record_repair(self, repair_result: Dict):
        """Record repair in history and knowledge graph"""
        self.repair_history.append(repair_result)
        
        # Record in SKG
        repair_id = f"repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'conversational_repair', ?)
        """, (
            repair_id,
            json.dumps(repair_result)
        ))
        
        self.skg.conn.commit()
        
    def get_repair_history(self) -> List[Dict]:
        """Get history of repairs"""
        return self.repair_history
        
    def get_repair_success_rate(self) -> float:
        """Calculate success rate of repairs"""
        if not self.repair_history:
            return 0.0
            
        successful = sum(1 for r in self.repair_history if r.get('success', False))
        return successful / len(self.repair_history)
        
    def mark_repair_outcome(self, repair_id: str, successful: bool,
                          user_response: str):
        """
        Mark the outcome of a repair attempt
        
        This helps learn what repair strategies work
        """
        # Update repair record
        for repair in self.repair_history:
            if repair.get('executed_at', '') in repair_id:
                repair['success'] = successful
                repair['user_response'] = user_response
                repair['outcome_recorded'] = datetime.now().isoformat()
                break
                
        # Analyze response for learning
        if successful:
            self._learn_from_successful_repair(repair, user_response)
        else:
            self._learn_from_failed_repair(repair, user_response)
            
    def _learn_from_successful_repair(self, repair: Dict, response: str):
        """Learn what made a repair successful"""
        # In a full implementation, this would update repair strategy weights
        # based on what worked
        pass
        
    def _learn_from_failed_repair(self, repair: Dict, response: str):
        """Learn what made a repair fail"""
        # In a full implementation, this would adjust strategies to avoid
        # failed approaches
        pass