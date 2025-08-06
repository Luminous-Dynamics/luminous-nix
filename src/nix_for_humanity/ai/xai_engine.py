# XAI (Explainable AI) Engine
"""
Causal reasoning and explanation system for Nix for Humanity.
Implements consciousness-first explainability - helping users understand 
not just WHAT the system decided, but WHY.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Core XAI components (lightweight implementations that don't require heavy ML deps)
import math
from collections import Counter, defaultdict


class ExplanationLevel(Enum):
    """Different levels of explanation depth"""
    SIMPLE = "simple"        # One sentence for Grandma Rose
    DETAILED = "detailed"    # Paragraph for Dr. Sarah  
    TECHNICAL = "technical"  # Full reasoning for developers


class ConfidenceLevel(Enum):
    """System confidence in its explanations"""
    HIGH = "high"       # >90% confidence
    MEDIUM = "medium"   # 70-90% confidence  
    LOW = "low"         # 50-70% confidence
    UNCERTAIN = "uncertain"  # <50% confidence


@dataclass
class CausalFactor:
    """A factor that influenced a decision"""
    name: str
    importance: float  # 0.0 to 1.0
    direction: str     # "positive", "negative", "neutral"
    description: str
    evidence_count: int = 0


@dataclass
class Explanation:
    """Complete explanation for a system decision"""
    decision: str
    confidence: ConfidenceLevel
    primary_reason: str
    causal_factors: List[CausalFactor]
    alternatives_considered: List[str]
    evidence_sources: List[str]
    simple_explanation: str
    detailed_explanation: str
    technical_explanation: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class XAIEngine:
    """
    Explainable AI Engine for Nix for Humanity
    
    Provides causal reasoning and explanations that help users understand
    the system's decision-making process. Built on consciousness-first principles:
    - Transparency builds trust
    - Uncertainty is acknowledged honestly  
    - Explanations adapt to user expertise
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".config" / "nix-for-humanity" / "xai.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self._init_db()
        
        # Knowledge base for causal reasoning
        self.causal_knowledge = self._load_causal_knowledge()
        
    def _init_db(self):
        """Initialize XAI database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Decisions table - tracks all system decisions for analysis
        c.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_type TEXT NOT NULL,
                decision_value TEXT NOT NULL,
                context_data TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                user_id TEXT
            )
        ''')
        
        # Causal factors table - records what influenced each decision
        c.execute('''
            CREATE TABLE IF NOT EXISTS causal_factors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id INTEGER NOT NULL,
                factor_name TEXT NOT NULL,
                importance REAL NOT NULL,
                direction TEXT NOT NULL,
                evidence_count INTEGER DEFAULT 1,
                FOREIGN KEY (decision_id) REFERENCES decisions (id)
            )
        ''')
        
        # User explanations table - tracks explanations given to users
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_id INTEGER NOT NULL,
                explanation_level TEXT NOT NULL,
                explanation_text TEXT NOT NULL,
                user_feedback TEXT,
                helpful_rating INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (decision_id) REFERENCES decisions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_causal_knowledge(self) -> Dict[str, Any]:
        """Load causal knowledge base for reasoning"""
        return {
            # Intent recognition factors
            "intent_recognition": {
                "factors": {
                    "keyword_match": {"weight": 0.4, "description": "Direct keyword matching"},
                    "context_similarity": {"weight": 0.3, "description": "Similarity to previous commands"},
                    "user_history": {"weight": 0.2, "description": "User's typical patterns"},
                    "grammar_structure": {"weight": 0.1, "description": "Sentence structure analysis"}
                },
                "confidence_thresholds": {
                    "high": 0.9,
                    "medium": 0.7,
                    "low": 0.5
                }
            },
            
            # Package selection factors
            "package_selection": {
                "factors": {
                    "exact_name_match": {"weight": 0.5, "description": "Package name matches exactly"},
                    "description_match": {"weight": 0.2, "description": "Description contains keywords"},
                    "popularity": {"weight": 0.15, "description": "Package popularity in community"},
                    "user_preferences": {"weight": 0.1, "description": "User's historical preferences"},
                    "maintenance_status": {"weight": 0.05, "description": "Package maintenance activity"}
                }
            },
            
            # Error resolution factors
            "error_resolution": {
                "factors": {
                    "pattern_match": {"weight": 0.4, "description": "Error matches known patterns"},
                    "solution_success_rate": {"weight": 0.3, "description": "Solution worked before"},
                    "context_similarity": {"weight": 0.2, "description": "Similar context to past errors"},
                    "recency": {"weight": 0.1, "description": "How recently solution was used"}
                }
            }
        }
    
    def explain_decision(
        self, 
        decision_type: str,
        decision_value: str,
        context: Dict[str, Any],
        factors: List[CausalFactor],
        level: ExplanationLevel = ExplanationLevel.SIMPLE,
        user_expertise: str = "beginner"
    ) -> Explanation:
        """
        Generate explanation for a system decision
        
        Args:
            decision_type: Type of decision (e.g., "intent_recognition", "package_selection")
            decision_value: The actual decision made
            context: Context information that influenced the decision
            factors: Causal factors that influenced the decision
            level: Desired explanation depth
            user_expertise: User's expertise level for tailoring explanations
        """
        
        # Calculate overall confidence
        confidence = self._calculate_confidence(factors, decision_type)
        
        # Generate explanations at different levels
        simple_explanation = self._generate_simple_explanation(
            decision_type, decision_value, factors, user_expertise
        )
        
        detailed_explanation = self._generate_detailed_explanation(
            decision_type, decision_value, factors, context
        )
        
        technical_explanation = self._generate_technical_explanation(
            decision_type, decision_value, factors, context
        )
        
        # Find alternatives that were considered
        alternatives = self._find_alternatives(decision_type, decision_value, context)
        
        # Identify evidence sources
        evidence_sources = self._identify_evidence_sources(factors, context)
        
        # Primary reason (most important factor)
        primary_reason = factors[0].description if factors else "No clear reason identified"
        
        explanation = Explanation(
            decision=f"{decision_type}: {decision_value}",
            confidence=confidence,
            primary_reason=primary_reason,
            causal_factors=factors,
            alternatives_considered=alternatives,
            evidence_sources=evidence_sources,
            simple_explanation=simple_explanation,
            detailed_explanation=detailed_explanation,
            technical_explanation=technical_explanation
        )
        
        # Store the decision and explanation for learning
        self._store_decision_explanation(explanation, context)
        
        return explanation
    
    def _calculate_confidence(self, factors: List[CausalFactor], decision_type: str) -> ConfidenceLevel:
        """Calculate confidence level based on causal factors"""
        if not factors:
            return ConfidenceLevel.UNCERTAIN
            
        # Calculate weighted average of importance values
        # Evidence count provides a smaller boost (logarithmic scale)
        total_weight = 0
        total_importance = 0
        
        for f in factors:
            # Evidence boost: log scale with base 2, capped at 2x multiplier
            evidence_boost = min(2.0, 1.0 + math.log(f.evidence_count + 1) / math.log(10))
            weighted_importance = f.importance * evidence_boost
            
            # Only count positive and neutral factors towards confidence
            if f.direction in ["positive", "neutral"]:
                total_weight += weighted_importance
                total_importance += f.importance
            else:
                # Negative factors reduce confidence
                total_weight -= weighted_importance * 0.5
                total_importance += f.importance * 0.5
        
        # Calculate confidence as weighted average
        confidence_score = total_weight / total_importance if total_importance > 0 else 0
        confidence_score = max(0.0, min(1.0, confidence_score))  # Clamp to [0, 1]
        
        # Get thresholds from knowledge base
        thresholds = self.causal_knowledge.get(decision_type, {}).get("confidence_thresholds", {
            "high": 0.9, "medium": 0.7, "low": 0.5
        })
        
        if confidence_score >= thresholds["high"]:
            return ConfidenceLevel.HIGH
        elif confidence_score >= thresholds["medium"]:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= thresholds["low"]:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def _generate_simple_explanation(
        self, 
        decision_type: str, 
        decision_value: str, 
        factors: List[CausalFactor],
        user_expertise: str
    ) -> str:
        """Generate simple, one-sentence explanation"""
        
        if not factors:
            return f"I chose '{decision_value}' based on general patterns."
        
        top_factor = factors[0]
        
        # Tailor language to user expertise
        if user_expertise == "beginner":
            if decision_type == "intent_recognition":
                return f"I understood you wanted '{decision_value}' because {top_factor.description.lower()}."
            elif decision_type == "package_selection":
                return f"I chose '{decision_value}' because {top_factor.description.lower()}."
            else:
                return f"I decided on '{decision_value}' because {top_factor.description.lower()}."
        else:
            return f"Selected '{decision_value}' primarily due to {top_factor.description.lower()} (importance: {top_factor.importance:.2f})."
    
    def _generate_detailed_explanation(
        self, 
        decision_type: str, 
        decision_value: str, 
        factors: List[CausalFactor],
        context: Dict[str, Any]
    ) -> str:
        """Generate detailed paragraph explanation"""
        
        if not factors:
            return f"I selected '{decision_value}' based on general heuristics, but I don't have strong evidence for this choice."
        
        explanation_parts = [
            f"I chose '{decision_value}' based on several factors:"
        ]
        
        # Top 3 factors
        for i, factor in enumerate(factors[:3]):
            direction_word = "supported" if factor.direction == "positive" else "suggested against" if factor.direction == "negative" else "influenced"
            explanation_parts.append(
                f"{i+1}. {factor.description} ({factor.importance:.0%} importance) - this {direction_word} the decision"
            )
        
        # Add context if available
        if context.get("user_input"):
            explanation_parts.append(f"Given your input: '{context['user_input']}'")
        
        return " ".join(explanation_parts) + "."
    
    def _generate_technical_explanation(
        self, 
        decision_type: str, 
        decision_value: str, 
        factors: List[CausalFactor],
        context: Dict[str, Any]
    ) -> str:
        """Generate technical explanation with full reasoning"""
        
        tech_parts = [
            f"Decision: {decision_type} -> {decision_value}",
            f"Context: {json.dumps(context, indent=2)}",
            "Causal Analysis:"
        ]
        
        for factor in factors:
            tech_parts.append(
                f"  - {factor.name}: importance={factor.importance:.3f}, "
                f"direction={factor.direction}, evidence_count={factor.evidence_count}"
            )
        
        # Add reasoning methodology
        tech_parts.extend([
            "Methodology: Weighted causal factor analysis",
            f"Total factors considered: {len(factors)}",
            f"Primary factor: {factors[0].name if factors else 'None'}"
        ])
        
        return "\n".join(tech_parts)
    
    def _find_alternatives(self, decision_type: str, decision_value: str, context: Dict[str, Any]) -> List[str]:
        """Find alternatives that were considered"""
        # This would be expanded with actual alternative generation logic
        alternatives = []
        
        if decision_type == "package_selection":
            # Could query package database for similar packages
            alternatives = ["firefox-esr", "chromium", "brave"] if "firefox" in decision_value.lower() else []
        elif decision_type == "intent_recognition":
            # Could show other intents that scored highly
            alternatives = ["install", "search", "info"] if decision_value == "install" else []
        
        return alternatives[:3]  # Limit to top 3
    
    def _identify_evidence_sources(self, factors: List[CausalFactor], context: Dict[str, Any]) -> List[str]:
        """Identify sources of evidence for the decision"""
        sources = []
        
        for factor in factors:
            if factor.evidence_count > 0:
                if "history" in factor.name.lower():
                    sources.append("User interaction history")
                elif "match" in factor.name.lower():
                    sources.append("Pattern matching database")
                elif "popularity" in factor.name.lower():
                    sources.append("Community usage statistics")
                elif "preference" in factor.name.lower():
                    sources.append("Learned user preferences")
        
        return list(set(sources))  # Remove duplicates
    
    def _store_decision_explanation(self, explanation: Explanation, context: Dict[str, Any]):
        """Store decision and explanation for learning"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Store decision
        c.execute('''
            INSERT INTO decisions 
            (decision_type, decision_value, context_data, confidence, timestamp, session_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            explanation.decision.split(":")[0],
            explanation.decision.split(":")[1].strip() if ":" in explanation.decision else explanation.decision,
            json.dumps(context),
            explanation.confidence.value,
            explanation.timestamp,
            context.get("session_id"),
            context.get("user_id")
        ))
        
        decision_id = c.lastrowid
        
        # Store causal factors
        for factor in explanation.causal_factors:
            c.execute('''
                INSERT INTO causal_factors 
                (decision_id, factor_name, importance, direction, evidence_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                decision_id,
                factor.name,
                factor.importance,
                factor.direction,
                factor.evidence_count
            ))
        
        conn.commit()
        conn.close()
    
    def get_explanation_history(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get history of explanations provided"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''
            SELECT d.decision_type, d.decision_value, d.confidence, d.timestamp,
                   ue.explanation_level, ue.explanation_text, ue.helpful_rating
            FROM decisions d
            LEFT JOIN user_explanations ue ON d.id = ue.decision_id
        '''
        params = []
        
        if user_id:
            query += ' WHERE d.user_id = ?'
            params.append(user_id)
        
        query += ' ORDER BY d.timestamp DESC LIMIT ?'
        params.append(limit)
        
        c.execute(query, params)
        
        history = []
        for row in c.fetchall():
            history.append({
                'decision_type': row[0],
                'decision_value': row[1],
                'confidence': row[2],
                'timestamp': row[3],
                'explanation_level': row[4],
                'explanation_text': row[5],
                'helpful_rating': row[6]
            })
        
        conn.close()
        return history
    
    def record_explanation_feedback(self, decision_id: int, helpful_rating: int, feedback_text: str = ""):
        """Record user feedback on explanations for improvement"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            UPDATE user_explanations 
            SET helpful_rating = ?, user_feedback = ?
            WHERE decision_id = ?
        ''', (helpful_rating, feedback_text, decision_id))
        
        conn.commit()
        conn.close()
    
    def get_explanation_analytics(self) -> Dict[str, Any]:
        """Get analytics on explanation effectiveness"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Explanation helpfulness by type
        c.execute('''
            SELECT d.decision_type, AVG(ue.helpful_rating) as avg_rating, COUNT(*) as count
            FROM decisions d
            JOIN user_explanations ue ON d.id = ue.decision_id
            WHERE ue.helpful_rating IS NOT NULL
            GROUP BY d.decision_type
        ''')
        
        helpfulness_by_type = dict(c.fetchall())
        
        # Confidence calibration (are high confidence decisions actually better?)
        c.execute('''
            SELECT d.confidence, AVG(ue.helpful_rating) as avg_rating, COUNT(*) as count
            FROM decisions d
            JOIN user_explanations ue ON d.id = ue.decision_id
            WHERE ue.helpful_rating IS NOT NULL
            GROUP BY d.confidence
        ''')
        
        confidence_calibration = dict(c.fetchall())
        
        # Most common decision types
        c.execute('''
            SELECT decision_type, COUNT(*) as count
            FROM decisions
            GROUP BY decision_type
            ORDER BY count DESC
        ''')
        
        common_decisions = dict(c.fetchall())
        
        conn.close()
        
        return {
            'helpfulness_by_type': helpfulness_by_type,
            'confidence_calibration': confidence_calibration,
            'common_decisions': common_decisions,
            'total_explanations': sum(common_decisions.values())
        }


# Utility functions for creating causal factors
def create_causal_factor(name: str, importance: float, direction: str, description: str, evidence_count: int = 1) -> CausalFactor:
    """Helper function to create causal factors"""
    return CausalFactor(
        name=name,
        importance=max(0.0, min(1.0, importance)),  # Clamp to [0,1]
        direction=direction,
        description=description,
        evidence_count=evidence_count
    )


def analyze_intent_recognition(
    user_input: str, 
    recognized_intent: str, 
    confidence_score: float,
    context: Dict[str, Any],
    xai_engine: XAIEngine
) -> Explanation:
    """
    Analyze and explain intent recognition decisions
    
    This is an example of how to use the XAI engine for intent recognition
    """
    
    factors = []
    
    # Keyword analysis
    keywords = ["install", "remove", "search", "help", "update"]
    keyword_matches = [kw for kw in keywords if kw in user_input.lower()]
    if keyword_matches:
        factors.append(create_causal_factor(
            name="keyword_match",
            importance=0.4,
            direction="positive",
            description=f"Found keywords: {', '.join(keyword_matches)}",
            evidence_count=len(keyword_matches)
        ))
    
    # User history factor
    if context.get("user_history"):
        similar_patterns = context["user_history"].get("similar_patterns", 0)
        if similar_patterns > 0:
            factors.append(create_causal_factor(
                name="user_history",
                importance=0.2,
                direction="positive", 
                description=f"You've used similar commands {similar_patterns} times before",
                evidence_count=similar_patterns
            ))
    
    # Confidence-based factor
    if confidence_score > 0.8:
        factors.append(create_causal_factor(
            name="high_confidence",
            importance=0.3,
            direction="positive",
            description="Pattern matching was very clear",
            evidence_count=1
        ))
    elif confidence_score < 0.6:
        factors.append(create_causal_factor(
            name="low_confidence",
            importance=0.3,
            direction="negative",
            description="Pattern matching was uncertain",
            evidence_count=1
        ))
    
    # Sort factors by importance
    factors.sort(key=lambda f: f.importance, reverse=True)
    
    return xai_engine.explain_decision(
        decision_type="intent_recognition",
        decision_value=recognized_intent,
        context=context,
        factors=factors,
        level=ExplanationLevel.SIMPLE
    )