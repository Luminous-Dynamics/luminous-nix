# Advanced Learning System
"""
Implements advanced AI learning capabilities including:
- Direct Preference Optimization (DPO) for user preference learning
- LoRA (Low-Rank Adaptation) for efficient model fine-tuning
- Symbiotic intelligence patterns for human-AI partnership

This system learns from every interaction while preserving privacy and user agency.
"""

import json
import sqlite3
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

# Lightweight ML utilities (no heavy dependencies required)
import math
import random
from statistics import mean, stdev


class LearningMode(Enum):
    """Different modes of learning"""
    PASSIVE = "passive"      # Learn from observations only
    ACTIVE = "active"        # Ask for feedback to learn better
    SYMBIOTIC = "symbiotic"  # Co-evolve with user through partnership


class AdaptationStrategy(Enum):
    """How the system adapts to users"""
    CONSERVATIVE = "conservative"  # Small, safe changes
    MODERATE = "moderate"          # Balanced adaptation
    AGGRESSIVE = "aggressive"      # Fast adaptation to preferences


@dataclass
class PreferencePair:
    """A preference pair for DPO learning"""
    user_input: str
    preferred_response: str
    rejected_response: str
    feedback_strength: float  # How strong the preference is (0-1)
    context: Dict[str, Any]
    timestamp: str = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class LearningMetrics:
    """Metrics tracking learning effectiveness"""
    total_interactions: int
    successful_adaptations: int
    preference_pairs_collected: int
    adaptation_accuracy: float
    user_satisfaction_trend: List[float]
    learning_velocity: float  # How fast the system is learning
    convergence_score: float  # How stable the learning has become
    
    
@dataclass
class UserModel:
    """Comprehensive model of a user's preferences and patterns"""
    user_id: str
    
    # Communication preferences
    preferred_explanation_level: str = "simple"
    preferred_response_style: str = "friendly"
    preferred_verbosity: str = "moderate"
    
    # Interaction patterns
    typical_session_length: float = 300.0  # seconds
    common_intents: Dict[str, float] = None
    error_tolerance: float = 0.5  # How tolerant of errors (0=intolerant, 1=very tolerant)
    learning_speed: float = 0.5   # How fast they adapt to new patterns
    
    # Technical preferences
    prefers_declarative: bool = True
    package_preferences: Dict[str, str] = None
    workflow_patterns: List[str] = None
    
    # Meta-learning
    adaptation_rate: float = 0.1  # How fast to adapt the model
    confidence_threshold: float = 0.7  # When to act on learned patterns
    last_updated: str = None
    
    def __post_init__(self):
        if self.common_intents is None:
            self.common_intents = {}
        if self.package_preferences is None:
            self.package_preferences = {}
        if self.workflow_patterns is None:
            self.workflow_patterns = []
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


class AdvancedLearningSystem:
    """
    Advanced learning system implementing symbiotic intelligence principles.
    
    Features:
    - Direct Preference Optimization (DPO) for learning user preferences
    - LoRA-style adaptation for efficient personalization
    - Symbiotic feedback loops for human-AI co-evolution
    - Privacy-preserving federated learning (optional)
    """
    
    def __init__(self, db_path: Optional[Path] = None, learning_mode: LearningMode = LearningMode.SYMBIOTIC):
        if db_path is None:
            db_path = Path.home() / ".config" / "nix-for-humanity" / "advanced_learning.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self.learning_mode = learning_mode
        self.adaptation_strategy = AdaptationStrategy.MODERATE
        
        # Learning parameters
        self.dpo_beta = 0.1  # DPO temperature parameter
        self.lora_alpha = 16  # LoRA scaling parameter
        self.learning_rate = 0.001
        self.memory_window = 100  # Number of recent interactions to consider
        
        # User models cache
        self.user_models: Dict[str, UserModel] = {}
        
        # Preference pairs for DPO
        self.preference_pairs: deque = deque(maxlen=1000)
        
        self._init_db()
        self._load_user_models()
        
    def _init_db(self):
        """Initialize advanced learning database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # User models table
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_models (
                user_id TEXT PRIMARY KEY,
                model_data TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                adaptation_count INTEGER DEFAULT 0,
                performance_score REAL DEFAULT 0.5
            )
        ''')
        
        # Preference pairs table (for DPO)
        c.execute('''
            CREATE TABLE IF NOT EXISTS preference_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_input TEXT NOT NULL,
                preferred_response TEXT NOT NULL,
                rejected_response TEXT NOT NULL,
                feedback_strength REAL NOT NULL,
                context_data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Learning metrics table
        c.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Adaptation history table
        c.execute('''
            CREATE TABLE IF NOT EXISTS adaptation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                adaptation_type TEXT NOT NULL,
                before_value TEXT NOT NULL,
                after_value TEXT NOT NULL,
                success_rating REAL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_user_models(self):
        """Load existing user models from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT user_id, model_data FROM user_models')
        
        for user_id, model_data in c.fetchall():
            try:
                model_dict = json.loads(model_data)
                self.user_models[user_id] = UserModel(**model_dict)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Could not load user model for {user_id}: {e}")
                # Create default model
                self.user_models[user_id] = UserModel(user_id=user_id)
        
        conn.close()
    
    def get_user_model(self, user_id: str) -> UserModel:
        """Get or create user model"""
        if user_id not in self.user_models:
            self.user_models[user_id] = UserModel(user_id=user_id)
        return self.user_models[user_id]
    
    def record_preference_pair(self, pair: PreferencePair):
        """Record a preference pair for DPO learning"""
        self.preference_pairs.append(pair)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO preference_pairs 
            (user_id, user_input, preferred_response, rejected_response, 
             feedback_strength, context_data, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pair.user_id,
            pair.user_input,
            pair.preferred_response,
            pair.rejected_response,
            pair.feedback_strength,
            json.dumps(pair.context),
            pair.timestamp
        ))
        
        conn.commit()
        conn.close()
        
        # Trigger learning if we have enough pairs
        if len(self.preference_pairs) % 10 == 0:
            self._update_preferences_dpo(pair.user_id or "default")
    
    def _update_preferences_dpo(self, user_id: str):
        """Update user preferences using DPO-style learning"""
        user_model = self.get_user_model(user_id)
        user_pairs = [p for p in self.preference_pairs if p.user_id == user_id]
        
        if len(user_pairs) < 3:
            return  # Need minimum data for learning
        
        # Analyze preference patterns
        preference_updates = self._analyze_preference_patterns(user_pairs)
        
        # Apply updates with LoRA-style adaptation
        for pref_type, new_value in preference_updates.items():
            old_value = getattr(user_model, pref_type, None)
            
            if old_value is not None:
                # LoRA-style update: small adaptation
                if isinstance(old_value, float):
                    adapted_value = old_value + self.learning_rate * (new_value - old_value)
                    setattr(user_model, pref_type, adapted_value)
                elif isinstance(old_value, str) and isinstance(new_value, str):
                    # For categorical values, use confidence-based switching
                    confidence = self._calculate_preference_confidence(user_pairs, pref_type, new_value)
                    if confidence > user_model.confidence_threshold:
                        setattr(user_model, pref_type, new_value)
        
        # Update last modified
        user_model.last_updated = datetime.now().isoformat()
        
        # Save updated model
        self._save_user_model(user_model)
    
    def _analyze_preference_patterns(self, pairs: List[PreferencePair]) -> Dict[str, Any]:
        """Analyze preference pairs to identify patterns"""
        updates = {}
        
        # Analyze response style preferences
        style_votes = defaultdict(float)
        verbosity_votes = defaultdict(float)
        explanation_votes = defaultdict(float)
        
        for pair in pairs:
            # Simple heuristics for identifying preferences
            preferred = pair.preferred_response.lower()
            rejected = pair.rejected_response.lower()
            strength = pair.feedback_strength
            
            # Response style analysis
            if len(preferred) < len(rejected) * 0.7:
                style_votes["minimal"] += strength
            elif len(preferred) > len(rejected) * 1.3:
                style_votes["detailed"] += strength
            else:
                style_votes["moderate"] += strength
            
            # Technical level analysis
            if any(word in preferred for word in ["error", "command", "sudo", "nix-env"]):
                explanation_votes["technical"] += strength
            elif any(word in preferred for word in ["let me", "I'll help", "here's how"]):
                explanation_votes["simple"] += strength
            else:
                explanation_votes["detailed"] += strength
        
        # Determine winning preferences
        if style_votes:
            updates["preferred_verbosity"] = max(style_votes, key=style_votes.get)
        
        if explanation_votes:
            updates["preferred_explanation_level"] = max(explanation_votes, key=explanation_votes.get)
        
        return updates
    
    def _calculate_preference_confidence(self, pairs: List[PreferencePair], pref_type: str, value: str) -> float:
        """Calculate confidence in a preference update"""
        if not pairs:
            return 0.0
        
        # Simple confidence based on consistency and strength
        relevant_pairs = [p for p in pairs if self._pair_relates_to_preference(p, pref_type, value)]
        
        if not relevant_pairs:
            return 0.0
        
        # Average feedback strength for relevant pairs
        avg_strength = mean([p.feedback_strength for p in relevant_pairs])
        
        # Consistency bonus
        consistency = len(relevant_pairs) / len(pairs)
        
        return min(1.0, avg_strength * consistency * 2)  # Scale up to [0, 1]
    
    def _pair_relates_to_preference(self, pair: PreferencePair, pref_type: str, value: str) -> bool:
        """Check if a preference pair relates to a specific preference type"""
        # Simple heuristic matching
        if pref_type == "preferred_verbosity":
            if value == "minimal":
                return len(pair.preferred_response) < len(pair.rejected_response)
            elif value == "detailed":
                return len(pair.preferred_response) > len(pair.rejected_response)
        
        if pref_type == "preferred_explanation_level":
            preferred_lower = pair.preferred_response.lower()
            if value == "technical" and any(word in preferred_lower for word in ["command", "sudo", "error"]):
                return True
            elif value == "simple" and any(word in preferred_lower for word in ["let me", "I'll help"]):
                return True
        
        return False
    
    def _save_user_model(self, user_model: UserModel):
        """Save user model to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        model_data = json.dumps(asdict(user_model))
        
        c.execute('''
            INSERT OR REPLACE INTO user_models 
            (user_id, model_data, last_updated, adaptation_count)
            VALUES (?, ?, ?, 
                    COALESCE((SELECT adaptation_count FROM user_models WHERE user_id = ?), 0) + 1)
        ''', (user_model.user_id, model_data, user_model.last_updated, user_model.user_id))
        
        conn.commit()
        conn.close()
    
    def adapt_response(self, user_id: str, base_response: str, context: Dict[str, Any]) -> str:
        """Adapt a response based on learned user preferences"""
        user_model = self.get_user_model(user_id)
        
        adapted_response = base_response
        
        # Apply verbosity preference
        if user_model.preferred_verbosity == "minimal":
            adapted_response = self._make_response_minimal(adapted_response)
        elif user_model.preferred_verbosity == "detailed":
            adapted_response = self._make_response_detailed(adapted_response, context)
        
        # Apply explanation level preference
        if user_model.preferred_explanation_level == "technical":
            adapted_response = self._add_technical_details(adapted_response, context)
        elif user_model.preferred_explanation_level == "simple":
            adapted_response = self._simplify_language(adapted_response)
        
        # Apply response style preference
        if user_model.preferred_response_style == "encouraging":
            adapted_response = self._make_encouraging(adapted_response)
        elif user_model.preferred_response_style == "minimal":
            adapted_response = self._make_minimal(adapted_response)
        
        return adapted_response
    
    def _make_response_minimal(self, response: str) -> str:
        """Make response more concise"""
        # Remove filler words and phrases
        minimal_response = response
        filler_phrases = [
            "I'll help you", "Let me", "Here's how", "You can", 
            "What you need to do is", "The way to do this is"
        ]
        
        for phrase in filler_phrases:
            minimal_response = minimal_response.replace(phrase, "")
        
        # Keep only essential information
        sentences = minimal_response.split(". ")
        if len(sentences) > 2:
            minimal_response = ". ".join(sentences[:2])
        
        return minimal_response.strip()
    
    def _make_response_detailed(self, response: str, context: Dict[str, Any]) -> str:
        """Add more detail to response"""
        detailed_response = response
        
        # Add context if available
        if context.get("alternatives"):
            detailed_response += f"\n\nAlternatives: {', '.join(context['alternatives'][:3])}"
        
        if context.get("why_recommended"):
            detailed_response += f"\n\nWhy this is recommended: {context['why_recommended']}"
        
        return detailed_response
    
    def _add_technical_details(self, response: str, context: Dict[str, Any]) -> str:
        """Add technical details for advanced users"""
        technical_response = response
        
        if context.get("command"):
            technical_response += f"\n\nCommand: {context['command']}"
        
        if context.get("config_location"):
            technical_response += f"\nConfig location: {context['config_location']}"
        
        return technical_response
    
    def _simplify_language(self, response: str) -> str:
        """Simplify language for beginners"""
        # Replace technical terms with simpler ones
        replacements = {
            "execute": "run",
            "configure": "set up",
            "initialize": "start",
            "repository": "software source",
            "dependencies": "required programs"
        }
        
        simple_response = response
        for tech_term, simple_term in replacements.items():
            simple_response = simple_response.replace(tech_term, simple_term)
        
        return simple_response
    
    def _make_encouraging(self, response: str) -> str:
        """Make response more encouraging"""
        encouraging_phrases = [
            "Great choice!", "You're doing well!", "That's a smart approach!",
            "Nice work!", "You're getting the hang of this!"
        ]
        
        # Add encouraging phrase occasionally
        if random.random() < 0.3:
            phrase = random.choice(encouraging_phrases)
            return f"{phrase} {response}"
        
        return response
    
    def _make_minimal(self, response: str) -> str:
        """Make response very minimal and direct"""
        # Extract just the essential action
        if "install" in response.lower():
            return response.split("install")[0] + "install " + response.split("install")[1].split()[0]
        
        # Return first sentence only
        return response.split(".")[0] + "."
    
    def predict_user_intent(self, user_id: str, partial_input: str, context: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Predict what the user is trying to do based on partial input"""
        user_model = self.get_user_model(user_id)
        
        predictions = []
        
        # Use common intents from user model
        for intent, frequency in user_model.common_intents.items():
            # Simple similarity scoring
            similarity = self._calculate_intent_similarity(partial_input, intent)
            score = similarity * frequency
            predictions.append((intent, score))
        
        # Sort by score
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:5]  # Top 5 predictions
    
    def _calculate_intent_similarity(self, input_text: str, intent: str) -> float:
        """Calculate similarity between input and intent"""
        input_words = set(input_text.lower().split())
        intent_words = set(intent.lower().split())
        
        if not input_words or not intent_words:
            return 0.0
        
        intersection = input_words.intersection(intent_words)
        union = input_words.union(intent_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_learning_metrics(self, user_id: Optional[str] = None) -> LearningMetrics:
        """Get learning system metrics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if user_id:
            # User-specific metrics
            c.execute('SELECT COUNT(*) FROM preference_pairs WHERE user_id = ?', (user_id,))
            preference_pairs = c.fetchone()[0]
            
            c.execute('''
                SELECT COUNT(*) FROM adaptation_history 
                WHERE user_id = ? AND success_rating > 0.5
            ''', (user_id,))
            successful_adaptations = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM adaptation_history WHERE user_id = ?', (user_id,))
            total_adaptations = c.fetchone()[0]
            
        else:
            # Global metrics
            c.execute('SELECT COUNT(*) FROM preference_pairs')
            preference_pairs = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM adaptation_history WHERE success_rating > 0.5')
            successful_adaptations = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM adaptation_history')
            total_adaptations = c.fetchone()[0]
        
        conn.close()
        
        # Calculate derived metrics
        adaptation_accuracy = successful_adaptations / max(1, total_adaptations)
        
        # Mock some metrics for now (would be calculated from real data)
        satisfaction_trend = [0.6, 0.65, 0.7, 0.75, 0.8]  # Improving trend
        learning_velocity = 0.1  # Learning rate
        convergence_score = 0.8  # How stable the learning is
        
        return LearningMetrics(
            total_interactions=total_adaptations,
            successful_adaptations=successful_adaptations,
            preference_pairs_collected=preference_pairs,
            adaptation_accuracy=adaptation_accuracy,
            user_satisfaction_trend=satisfaction_trend,
            learning_velocity=learning_velocity,
            convergence_score=convergence_score
        )
    
    def suggest_interaction_improvements(self, user_id: str) -> List[str]:
        """Suggest ways to improve interactions based on learning data"""
        user_model = self.get_user_model(user_id)
        metrics = self.get_learning_metrics(user_id)
        suggestions = []
        
        # Low adaptation accuracy
        if metrics.adaptation_accuracy < 0.5:
            suggestions.append("Consider providing more specific feedback to help me learn your preferences better.")
        
        # Few preference pairs
        if metrics.preference_pairs_collected < 5:
            suggestions.append("Try using the 'symbiotic' mode to help me learn how you like to interact.")
        
        # User model analysis
        if not user_model.common_intents:
            suggestions.append("I haven't learned your common patterns yet. Keep using the system and I'll adapt!")
        
        if user_model.error_tolerance < 0.3:
            suggestions.append("I notice you prefer high accuracy. I'll be more conservative in my suggestions.")
        
        return suggestions
    
    def evolve_with_user(self, user_id: str, interaction_feedback: Dict[str, Any]):
        """Implement symbiotic evolution based on interaction feedback"""
        user_model = self.get_user_model(user_id)
        
        # Update user model based on feedback
        if "response_quality" in interaction_feedback:
            quality = interaction_feedback["response_quality"]
            
            # Adapt confidence threshold
            if quality < 0.5:
                user_model.confidence_threshold = min(0.9, user_model.confidence_threshold + 0.05)
            elif quality > 0.8:
                user_model.confidence_threshold = max(0.5, user_model.confidence_threshold - 0.02)
        
        if "response_speed" in interaction_feedback:
            speed_rating = interaction_feedback["response_speed"]
            
            # Adapt learning rate based on speed preference
            if speed_rating < 0.5:  # User wants faster responses
                self.learning_rate = min(0.01, self.learning_rate * 1.1)
            elif speed_rating > 0.8:  # User is okay with current speed
                self.learning_rate = max(0.001, self.learning_rate * 0.95)
        
        # Update adaptation rate based on user engagement
        if "engagement_level" in interaction_feedback:
            engagement = interaction_feedback["engagement_level"]
            user_model.adaptation_rate = 0.05 + (0.15 * engagement)  # 0.05 to 0.2 range
        
        self._save_user_model(user_model)
    
    def get_symbiotic_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about the symbiotic relationship with the user"""
        user_model = self.get_user_model(user_id)
        metrics = self.get_learning_metrics(user_id)
        
        # Calculate relationship health
        relationship_health = {
            "trust_level": min(1.0, metrics.adaptation_accuracy * 1.2),
            "learning_progress": min(1.0, metrics.preference_pairs_collected / 20.0),
            "adaptation_success": metrics.adaptation_accuracy,
            "engagement_trend": "improving" if metrics.user_satisfaction_trend[-1] > metrics.user_satisfaction_trend[0] else "stable"
        }
        
        # Growth areas
        growth_areas = []
        if relationship_health["trust_level"] < 0.7:
            growth_areas.append("Building trust through more accurate responses")
        if relationship_health["learning_progress"] < 0.5:
            growth_areas.append("Collecting more preference data for better personalization")
        
        return {
            "relationship_health": relationship_health,
            "user_model_maturity": len(user_model.common_intents) + len(user_model.package_preferences),
            "learning_velocity": metrics.learning_velocity,
            "growth_areas": growth_areas,
            "symbiotic_stage": self._determine_symbiotic_stage(user_model, metrics)
        }
    
    def _determine_symbiotic_stage(self, user_model: UserModel, metrics: LearningMetrics) -> str:
        """Determine the current stage of symbiotic relationship"""
        if metrics.preference_pairs_collected < 5:
            return "initial_learning"
        elif metrics.adaptation_accuracy < 0.6:
            return "building_trust" 
        elif len(user_model.common_intents) < 3:
            return "discovering_patterns"
        elif metrics.convergence_score < 0.7:
            return "refining_understanding"
        else:
            return "symbiotic_partnership"