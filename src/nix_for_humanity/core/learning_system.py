# Learning System
"""
Continuous learning and adaptation from user interactions
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict

# Import the revolutionary BKT system
try:
    from .bayesian_knowledge_tracer import BayesianKnowledgeTracer, SkillObservation
    BKT_AVAILABLE = True
except ImportError:
    BKT_AVAILABLE = False


@dataclass
class Interaction:
    """Record of a user interaction"""
    query: str
    intent: str
    response: str
    success: bool
    helpful: Optional[bool] = None
    timestamp: str = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # NEW: Enhanced context for BKT integration
    command_executed: Optional[str] = None
    error_type: Optional[str] = None
    response_time_ms: Optional[int] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Preference:
    """User preference record"""
    user_id: str
    preference_type: str
    value: str
    count: int = 1
    last_used: str = None
    
    def __post_init__(self):
        if self.last_used is None:
            self.last_used = datetime.now().isoformat()


class LearningSystem:
    """Revolutionary Educational Data Mining system with Bayesian Knowledge Tracing"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".config" / "nix-for-humanity" / "learning.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self.federated_learning_enabled = False
        
        # Initialize revolutionary BKT system if available
        self.bkt_tracer = None
        if BKT_AVAILABLE:
            try:
                self.bkt_tracer = BayesianKnowledgeTracer()
                print("🧠 Revolutionary BKT system initialized!")
            except Exception as e:
                print(f"⚠️ BKT initialization warning: {e}")
                self.bkt_tracer = None
        
        self._init_db()
        
    def _init_db(self):
        """Initialize learning database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Interactions table
        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                intent TEXT NOT NULL,
                response TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                helpful BOOLEAN,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                user_id TEXT
            )
        ''')
        
        # Preferences table
        c.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_type TEXT NOT NULL,
                value TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                last_used TEXT NOT NULL,
                UNIQUE(user_id, preference_type, value)
            )
        ''')
        
        # Error patterns table
        c.execute('''
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_message TEXT NOT NULL,
                solution TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                last_seen TEXT NOT NULL
            )
        ''')
        
        # Command patterns table
        c.execute('''
            CREATE TABLE IF NOT EXISTS command_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intent TEXT NOT NULL,
                pattern TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 1.0,
                last_used TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def record_interaction(self, interaction: Interaction):
        """Record a user interaction with revolutionary BKT enhancement"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO interactions 
            (query, intent, response, success, helpful, timestamp, session_id, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            interaction.query,
            interaction.intent,
            interaction.response,
            interaction.success,
            interaction.helpful,
            interaction.timestamp,
            interaction.session_id,
            interaction.user_id
        ))
        
        conn.commit()
        conn.close()
        
        # Revolutionary BKT Integration: Track skill mastery evolution
        if self.bkt_tracer and interaction.intent and interaction.user_id:
            try:
                # Map intent to NixOS skills
                skills = self._map_intent_to_skills(interaction.intent)
                
                for skill_id in skills:
                    # Create context dictionary for BKT integration
                    context = {
                        'error_type': interaction.error_type,
                        'response_time_ms': interaction.response_time_ms,
                        'command_executed': interaction.command_executed,
                        'original_query': interaction.query,
                        'intent': interaction.intent
                    }
                    
                    skill_observation = SkillObservation(
                        user_id=interaction.user_id,
                        skill_id=skill_id,
                        success=interaction.success,
                        context=context,
                        timestamp=interaction.timestamp
                    )
                    
                    # Update Bayesian skill mastery tracking
                    updated_params = self.bkt_tracer.update_mastery(skill_observation)
                    
                    # Log the BKT evolution for debugging
                    if updated_params:
                        print(f"🧠 BKT: Skill '{skill_id}' mastery updated to {updated_params.current_mastery:.3f}")
                        
            except Exception as e:
                print(f"⚠️ BKT integration warning: {e}")
                # Graceful degradation - continue without BKT if there are issues
        
    def learn_preference(self, user_id: str, preference_type: str, value: str):
        """Learn or update a user preference"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Try to update existing preference
        c.execute('''
            UPDATE preferences 
            SET count = count + 1, last_used = ?
            WHERE user_id = ? AND preference_type = ? AND value = ?
        ''', (datetime.now().isoformat(), user_id, preference_type, value))
        
        if c.rowcount == 0:
            # Insert new preference
            c.execute('''
                INSERT INTO preferences (user_id, preference_type, value, last_used)
                VALUES (?, ?, ?, ?)
            ''', (user_id, preference_type, value, datetime.now().isoformat()))
            
        conn.commit()
        conn.close()
        
    def get_user_preferences(self, user_id: str) -> Dict[str, str]:
        """Get user's learned preferences"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT preference_type, value, count
            FROM preferences
            WHERE user_id = ?
            ORDER BY count DESC, last_used DESC
        ''', (user_id,))
        
        preferences = {}
        for pref_type, value, count in c.fetchall():
            if pref_type not in preferences or count > preferences[pref_type][1]:
                preferences[pref_type] = (value, count)
                
        conn.close()
        
        # Return just the values, not the counts
        return {k: v[0] for k, v in preferences.items()}
        
    def learn_error_solution(self, error: str, solution: str, success: bool = True):
        """Learn from error resolutions"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if success:
            # Check if error-solution pair already exists
            c.execute('''
                SELECT success_count FROM error_patterns 
                WHERE error_message = ? AND solution = ?
            ''', (error, solution))
            
            existing = c.fetchone()
            
            if existing:
                # Update existing record
                c.execute('''
                    UPDATE error_patterns 
                    SET success_count = success_count + 1, last_seen = ?
                    WHERE error_message = ? AND solution = ?
                ''', (datetime.now().isoformat(), error, solution))
            else:
                # Insert new record
                c.execute('''
                    INSERT INTO error_patterns 
                    (error_message, solution, success_count, last_seen)
                    VALUES (?, ?, 1, ?)
                ''', (error, solution, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def get_error_solution(self, error: str) -> Optional[str]:
        """Get learned solution for an error"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Look for exact or similar errors
        c.execute('''
            SELECT solution, success_count
            FROM error_patterns
            WHERE error_message LIKE ?
            ORDER BY success_count DESC
            LIMIT 1
        ''', (f'%{error}%',))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
        
    def get_success_rate(self, intent: str) -> float:
        """Get success rate for a specific intent"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT 
                COUNT(CASE WHEN success = 1 THEN 1 END) as successes,
                COUNT(*) as total
            FROM interactions
            WHERE intent = ?
            AND timestamp > datetime('now', '-30 days')
        ''', (intent,))
        
        successes, total = c.fetchone()
        conn.close()
        
        if total == 0:
            return 0.0
        return successes / total
        
    def get_common_patterns(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most common query patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT query, COUNT(*) as count
            FROM interactions
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY query
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        
        patterns = c.fetchall()
        conn.close()
        
        return patterns
        
    def get_feedback_summary(self) -> Dict:
        """Get summary of user feedback"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Overall stats
        c.execute('''
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN helpful = 1 THEN 1 END) as helpful,
                COUNT(CASE WHEN helpful = 0 THEN 1 END) as not_helpful
            FROM interactions
            WHERE helpful IS NOT NULL
        ''')
        
        total, helpful, not_helpful = c.fetchone()
        
        # Recent trend
        c.execute('''
            SELECT 
                COUNT(CASE WHEN helpful = 1 THEN 1 END) * 100.0 / COUNT(*) as rate
            FROM interactions
            WHERE helpful IS NOT NULL
            AND timestamp > datetime('now', '-7 days')
        ''')
        
        recent_rate = c.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_feedback': total,
            'helpful_count': helpful,
            'not_helpful_count': not_helpful,
            'helpfulness_rate': helpful / total if total > 0 else 0.0,
            'recent_helpfulness_rate': recent_rate / 100.0
        }
    
    def record_feedback(self, interaction_id: str, helpful: bool, user_id: Optional[str] = None):
        """Record user feedback on a specific interaction"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Try to update by ID first
        c.execute('''
            UPDATE interactions 
            SET helpful = ?
            WHERE id = ?
        ''', (helpful, interaction_id))
        
        # If no rows were updated, try by session_id
        if c.rowcount == 0:
            c.execute('''
                UPDATE interactions 
                SET helpful = ?
                WHERE session_id = ?
            ''', (helpful, interaction_id))
            
        # If still no rows and user_id provided, try by user_id + session_id
        if c.rowcount == 0 and user_id:
            c.execute('''
                UPDATE interactions 
                SET helpful = ?
                WHERE session_id = ? AND user_id = ?
            ''', (helpful, interaction_id, user_id))
        
        conn.commit()
        conn.close()
        
    def update_user_preference(self, preference: str, value: str, user_id: str = "default"):
        """Update a specific user preference"""
        self.learn_preference(user_id, preference, value)
        
    def get_pattern_insights(self) -> Dict[str, any]:
        """Get insights from usage patterns"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Common intents
        c.execute('''
            SELECT intent, COUNT(*) as count
            FROM interactions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY intent
            ORDER BY count DESC
            LIMIT 10
        ''')
        common_intents = dict(c.fetchall())
        
        # Common errors (from error patterns)
        c.execute('''
            SELECT error_message, success_count
            FROM error_patterns
            ORDER BY success_count DESC
            LIMIT 10
        ''')
        common_errors = dict(c.fetchall())
        
        # Success patterns
        c.execute('''
            SELECT intent, 
                   COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM interactions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY intent
            HAVING COUNT(*) >= 3
            ORDER BY success_rate DESC
        ''')
        success_patterns = dict(c.fetchall())
        
        # Improvement areas (low success rate intents)
        c.execute('''
            SELECT intent, 
                   COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM interactions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY intent
            HAVING COUNT(*) >= 3
            ORDER BY success_rate ASC
            LIMIT 5
        ''')
        improvement_areas = dict(c.fetchall())
        
        conn.close()
        
        return {
            'common_intents': common_intents,
            'common_errors': common_errors,
            'success_patterns': success_patterns,
            'improvement_areas': improvement_areas
        }
        
    def suggest_improvements(self, intent_type: str) -> List[str]:
        """Suggest improvements based on learning data"""
        suggestions = []
        
        # Get success rate for this intent
        success_rate = self.get_success_rate(intent_type)
        
        if success_rate < 0.5:
            suggestions.append(f"Consider improving error handling for '{intent_type}' - current success rate is {success_rate:.1%}")
            
        # Check for common errors related to this intent
        error_solution = self.get_error_solution(intent_type)
        if error_solution:
            suggestions.append(f"Common solution for '{intent_type}' issues: {error_solution}")
            
        # Get patterns for suggestions
        patterns = self.get_common_patterns(5)
        intent_patterns = [p for p in patterns if intent_type.lower() in p[0].lower()]
        if intent_patterns:
            suggestions.append(f"Users commonly try: {', '.join([p[0] for p in intent_patterns[:3]])}")
            
        return suggestions
        
    def export_learning_data(self, user_id: Optional[str] = None) -> Dict[str, any]:
        """Export learning data for a user (privacy feature)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        data = {}
        
        if user_id:
            # Export specific user data
            c.execute('SELECT * FROM interactions WHERE user_id = ?', (user_id,))
            interactions = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
            
            c.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,))
            preferences = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
            
            data = {
                'user_id': user_id,
                'interactions': interactions,
                'preferences': preferences,
                'export_timestamp': datetime.now().isoformat()
            }
        else:
            # Export aggregated data (anonymized)
            data = {
                'total_interactions': c.execute('SELECT COUNT(*) FROM interactions').fetchone()[0],
                'total_users': c.execute('SELECT COUNT(DISTINCT user_id) FROM interactions WHERE user_id IS NOT NULL').fetchone()[0],
                'common_patterns': self.get_common_patterns(10),
                'pattern_insights': self.get_pattern_insights(),
                'export_timestamp': datetime.now().isoformat()
            }
        
        conn.close()
        return data
        
    def reset_learning_data(self, user_id: Optional[str] = None):
        """Reset all learning data for a user (privacy feature)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if user_id:
            # Reset specific user data
            c.execute('DELETE FROM interactions WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM preferences WHERE user_id = ?', (user_id,))
        else:
            # Reset all data
            c.execute('DELETE FROM interactions')
            c.execute('DELETE FROM preferences')
            c.execute('DELETE FROM error_patterns')
            c.execute('DELETE FROM command_patterns')
            
        conn.commit()
        conn.close()
        
    def get_learning_statistics(self) -> Dict[str, any]:
        """Get statistics about the learning system"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Total interactions
        c.execute('SELECT COUNT(*) FROM interactions')
        total_interactions = c.fetchone()[0]
        
        # Total feedback
        c.execute('SELECT COUNT(*) FROM interactions WHERE helpful IS NOT NULL')
        total_feedback = c.fetchone()[0]
        
        # Positive feedback rate
        c.execute('''
            SELECT COUNT(CASE WHEN helpful = 1 THEN 1 END) * 100.0 / COUNT(*)
            FROM interactions WHERE helpful IS NOT NULL
        ''')
        result = c.fetchone()[0]
        positive_feedback_rate = result if result else 0.0
        
        # Active users (users with activity in last 30 days)
        c.execute('''
            SELECT COUNT(DISTINCT user_id)
            FROM interactions
            WHERE user_id IS NOT NULL 
            AND timestamp > datetime('now', '-30 days')
        ''')
        active_users = c.fetchone()[0]
        
        # Learning improvements (number of patterns learned)
        c.execute('SELECT COUNT(*) FROM error_patterns')
        error_patterns_learned = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM preferences')
        preferences_learned = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_interactions': total_interactions,
            'total_feedback': total_feedback,
            'positive_feedback_rate': positive_feedback_rate / 100.0,
            'learning_improvements': error_patterns_learned + preferences_learned,
            'active_users': active_users,
            'patterns_learned': {
                'error_solutions': error_patterns_learned,
                'user_preferences': preferences_learned
            }
        }
        
    def enable_federated_learning(self, consent: bool):
        """Enable or disable federated learning"""
        self.federated_learning_enabled = consent
        
        # Could store this in database for persistence
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create settings table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        c.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES ('federated_learning', ?, ?)
        ''', (str(consent), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def _map_intent_to_skills(self, intent: str) -> List[str]:
        """Map user intent to relevant NixOS skills for BKT tracking"""
        # Revolutionary Educational Data Mining: Map every intent to skill development
        intent_skill_mapping = {
            # Package Management Skills
            'install': ['basic_package_installation', 'package_search'],
            'remove': ['package_removal', 'basic_package_installation'],
            'search': ['package_search', 'nixpkgs_navigation'],
            'upgrade': ['system_maintenance', 'package_management'],
            
            # System Management Skills  
            'update': ['system_maintenance', 'nix_channels'],
            'rebuild': ['nixos_configuration', 'system_maintenance'],
            'rollback': ['system_generations', 'system_maintenance'],
            'generations': ['system_generations', 'nixos_concepts'],
            
            # Configuration Skills
            'configure': ['nixos_configuration', 'nix_language'],
            'service': ['systemd_services', 'system_configuration'],
            'module': ['nixos_modules', 'nix_language'],
            
            # Troubleshooting Skills
            'debug': ['system_debugging', 'log_analysis'],
            'fix': ['problem_solving', 'system_debugging'],
            'check': ['system_monitoring', 'system_health'],
            
            # Advanced Skills
            'shell': ['nix_shell', 'development_environments'],
            'flake': ['nix_flakes', 'modern_nix'],
            'build': ['nix_builds', 'derivations'],
        }
        
        # Get skills for this intent, default to general NixOS if unknown
        skills = intent_skill_mapping.get(intent.lower(), ['general_nixos_usage'])
        
        # Always include general usage for breadth tracking
        if 'general_nixos_usage' not in skills:
            skills.append('general_nixos_usage')
            
        return skills
        
    def get_bkt_skill_mastery(self, user_id: str, skill_id: str = None) -> Dict:
        """Get current Bayesian Knowledge Tracing skill mastery for user"""
        if not self.bkt_tracer:
            return {"error": "BKT system not available"}
            
        try:
            if skill_id:
                # Get specific skill mastery
                params = self.bkt_tracer.get_or_create_parameters(user_id, skill_id)
                return {
                    "skill_id": skill_id,
                    "current_mastery": params.current_mastery,
                    "confidence": 1.0 - abs(params.current_mastery - 0.5) * 2,  # High at extremes
                    "learning_rate": params.learning_rate,
                    "observations": params.observation_count
                }
            else:
                # Get all skills mastery overview
                skill_graph = self.bkt_tracer.skill_graph
                user_data = self.bkt_tracer.user_parameters.get(user_id, {})
                
                skills_overview = {}
                for skill_id in skill_graph.nodes:
                    params = user_data.get(skill_id)
                    if params:
                        skills_overview[skill_id] = {
                            "mastery": params.current_mastery,
                            "confidence": 1.0 - abs(params.current_mastery - 0.5) * 2,
                            "observations": params.observation_count
                        }
                    else:
                        # Use default values for skills not yet observed
                        skills_overview[skill_id] = {
                            "mastery": 0.1,  # Low initial assumption
                            "confidence": 0.1,  # Very uncertain
                            "observations": 0
                        }
                        
                return {
                    "user_id": user_id,
                    "total_skills": len(skills_overview),
                    "skills": skills_overview,
                    "average_mastery": sum(s["mastery"] for s in skills_overview.values()) / len(skills_overview),
                    "mastered_skills": len([s for s in skills_overview.values() if s["mastery"] > 0.7])
                }
                
        except Exception as e:
            return {"error": f"BKT error: {e}"}
            
    def get_bkt_learning_insights(self, user_id: str) -> Dict:
        """Get educational insights from BKT tracking"""
        if not self.bkt_tracer:
            return {"error": "BKT system not available"}
            
        try:
            # Get current skill state
            skills_data = self.get_bkt_skill_mastery(user_id)
            if "error" in skills_data:
                return skills_data
                
            # Educational Data Mining insights
            insights = {
                "user_id": user_id,
                "learning_progress": {
                    "total_skills": skills_data["total_skills"],
                    "mastered_skills": skills_data["mastered_skills"],
                    "progress_percentage": (skills_data["mastered_skills"] / skills_data["total_skills"]) * 100,
                    "average_mastery": skills_data["average_mastery"]
                },
                "recommendations": [],
                "skill_path": []
            }
            
            # Identify skills that need attention (low mastery, recent activity)
            needs_practice = []
            ready_to_advance = []
            
            for skill_id, skill_data in skills_data["skills"].items():
                if skill_data["observations"] > 0:  # Only consider observed skills
                    if skill_data["mastery"] < 0.4:
                        needs_practice.append((skill_id, skill_data["mastery"]))
                    elif skill_data["mastery"] > 0.7:
                        ready_to_advance.append((skill_id, skill_data["mastery"]))
            
            # Generate educational recommendations
            if needs_practice:
                insights["recommendations"].append({
                    "type": "practice_needed",
                    "message": f"Consider practicing: {', '.join([s[0] for s in needs_practice[:3]])}",
                    "skills": needs_practice
                })
                
            if ready_to_advance:
                insights["recommendations"].append({
                    "type": "ready_to_advance", 
                    "message": f"You've mastered: {', '.join([s[0] for s in ready_to_advance[:3]])}. Ready for advanced topics!",
                    "skills": ready_to_advance
                })
                
            # Suggest learning path based on skill dependencies
            skill_graph = self.bkt_tracer.skill_graph
            unmastered_skills = [(skill_id, data["mastery"]) for skill_id, data in skills_data["skills"].items() 
                               if data["mastery"] < 0.6]
            unmastered_skills.sort(key=lambda x: x[1], reverse=True)  # Start with partially learned
            
            for skill_id, mastery in unmastered_skills[:5]:  # Top 5 next skills
                prerequisites = skill_graph.get_prerequisites(skill_id)
                prereq_mastery = [skills_data["skills"][prereq]["mastery"] for prereq in prerequisites]
                
                if not prerequisites or all(m > 0.6 for m in prereq_mastery):
                    insights["skill_path"].append({
                        "skill": skill_id,
                        "current_mastery": mastery,
                        "ready": True,
                        "prerequisites_met": True
                    })
                else:
                    insights["skill_path"].append({
                        "skill": skill_id, 
                        "current_mastery": mastery,
                        "ready": False,
                        "missing_prerequisites": [prereq for i, prereq in enumerate(prerequisites) 
                                               if prereq_mastery[i] <= 0.6]
                    })
                    
            return insights
            
        except Exception as e:
            return {"error": f"Insights error: {e}"}