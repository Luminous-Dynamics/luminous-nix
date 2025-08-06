"""
Bayesian Knowledge Tracing (BKT) Implementation for Nix for Humanity

Revolutionary Educational Data Mining approach that creates a "Persona of One" -
a dynamic, high-fidelity individual representation of each user's skill mastery.

This implementation moves beyond static user models to probabilistic cognitive twins
that track skill mastery using Bayesian inference and the NixOS Skill Graph.
"""

import json
import sqlite3
import math
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum


class SkillType(Enum):
    """Types of skills in the NixOS ecosystem"""
    COMMAND = "command"           # nix-build, nix-shell, etc.
    FUNCTION = "function"         # builtins.fetchGit, pkgs.mkShell
    CONCEPT = "concept"           # derivations, flakes, overlays
    ARCHITECTURE = "architecture" # modules, configurations


@dataclass
class BKTParameters:
    """Bayesian Knowledge Tracing parameters for a specific skill"""
    skill_id: str
    prior_knowledge: float = 0.1    # P(L₀) - initial mastery probability
    learning_rate: float = 0.3      # P(T) - probability of learning from practice
    slip_probability: float = 0.1   # P(S) - chance of mistakes despite mastery  
    guess_probability: float = 0.1  # P(G) - chance of success without mastery
    current_mastery: float = 0.1    # P(Lₜ) - current belief in mastery
    confidence: float = 0.5         # Certainty in the estimate
    observation_count: int = 0      # Number of observations
    last_updated: str = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()
        # Initialize current mastery to prior knowledge if not set
        if self.current_mastery == 0.1 and self.prior_knowledge != 0.1:
            self.current_mastery = self.prior_knowledge


@dataclass
class NixOSSkill:
    """A skill in the NixOS ecosystem"""
    skill_id: str
    name: str
    skill_type: SkillType
    prerequisites: List[str]        # Skills required before this one
    difficulty: float              # 0.0 (easy) to 1.0 (expert)
    learning_objectives: List[str] # What mastery means
    examples: List[str]            # Example commands/concepts
    
    
@dataclass 
class SkillObservation:
    """Record of practicing a skill"""
    skill_id: str
    user_id: str
    success: bool
    context: Dict            # Command, error type, timing, etc.
    timestamp: str = None
    confidence_self_report: Optional[float] = None  # User's self-assessment
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class NixOSSkillGraph:
    """The complete skill graph for NixOS"""
    
    def __init__(self):
        self.skills: Dict[str, NixOSSkill] = {}
        self.edges: Dict[str, Dict[str, float]] = {}  # skill_id -> {prerequisite: strength}
        self._build_skill_graph()
    
    def _build_skill_graph(self):
        """Build the comprehensive NixOS skill graph"""
        
        # Foundational concepts
        self.add_skill(NixOSSkill(
            skill_id="nix_basics",
            name="Nix Package Manager Basics",
            skill_type=SkillType.CONCEPT,
            prerequisites=[],
            difficulty=0.1,
            learning_objectives=["Understand declarative package management", "Know what Nix stores are"],
            examples=["nix-env -i", "nix-store --query"]
        ))
        
        self.add_skill(NixOSSkill(
            skill_id="nixos_configuration",
            name="NixOS System Configuration",
            skill_type=SkillType.CONCEPT,
            prerequisites=["nix_basics"],
            difficulty=0.3,
            learning_objectives=["Edit configuration.nix", "Understand system rebuilds"],
            examples=["nixos-rebuild switch", "configuration.nix editing"]
        ))
        
        # Commands - Basic
        self.add_skill(NixOSSkill(
            skill_id="nix_env",
            name="nix-env Package Management",
            skill_type=SkillType.COMMAND,
            prerequisites=["nix_basics"],
            difficulty=0.2,
            learning_objectives=["Install packages imperatively", "Manage user environment"],
            examples=["nix-env -iA nixos.firefox", "nix-env --rollback"]
        ))
        
        self.add_skill(NixOSSkill(
            skill_id="nix_shell",
            name="nix-shell Development Environments", 
            skill_type=SkillType.COMMAND,
            prerequisites=["nix_basics"],
            difficulty=0.4,
            learning_objectives=["Create temporary environments", "Development workflows"],
            examples=["nix-shell -p python3", "nix-shell --run 'python --version'"]
        ))
        
        # Commands - Intermediate
        self.add_skill(NixOSSkill(
            skill_id="nixos_rebuild",
            name="nixos-rebuild System Management",
            skill_type=SkillType.COMMAND,
            prerequisites=["nixos_configuration"],
            difficulty=0.5,
            learning_objectives=["Rebuild system safely", "Understand generations"],
            examples=["nixos-rebuild switch", "nixos-rebuild test", "nixos-rebuild rollback"]
        ))
        
        self.add_skill(NixOSSkill(
            skill_id="nix_store",
            name="Nix Store Operations",
            skill_type=SkillType.COMMAND, 
            prerequisites=["nix_basics"],
            difficulty=0.6,
            learning_objectives=["Query store", "Garbage collection"],
            examples=["nix-store --query --references", "nix-collect-garbage"]
        ))
        
        # Advanced concepts
        self.add_skill(NixOSSkill(
            skill_id="nix_expressions",
            name="Nix Expression Language",
            skill_type=SkillType.CONCEPT,
            prerequisites=["nix_basics"],
            difficulty=0.7,
            learning_objectives=["Write Nix expressions", "Understand lazy evaluation"],
            examples=["{ pkgs ? import <nixpkgs> {} }: ...", "rec { ... }"]
        ))
        
        self.add_skill(NixOSSkill(
            skill_id="flakes",
            name="Nix Flakes",
            skill_type=SkillType.ARCHITECTURE,
            prerequisites=["nix_expressions", "nixos_configuration"],
            difficulty=0.8,
            learning_objectives=["Create reproducible flakes", "Lock dependencies"],
            examples=["nix flake init", "flake.nix", "flake.lock"]
        ))
        
        self.add_skill(NixOSSkill(
            skill_id="nixos_modules",
            name="NixOS Module System",
            skill_type=SkillType.ARCHITECTURE,
            prerequisites=["nixos_configuration", "nix_expressions"],
            difficulty=0.9,
            learning_objectives=["Create custom modules", "Understand option types"],
            examples=["services.nginx.enable", "types.str", "mkOption"]
        ))
        
        # Error handling and debugging (crucial for learning)
        self.add_skill(NixOSSkill(
            skill_id="nix_debugging",
            name="Nix Debugging and Troubleshooting",
            skill_type=SkillType.CONCEPT,
            prerequisites=["nix_expressions"],
            difficulty=0.6,
            learning_objectives=["Debug build failures", "Understand error messages"],
            examples=["nix-build --show-trace", "Understanding infinite recursion errors"]
        ))
        
    def add_skill(self, skill: NixOSSkill):
        """Add a skill to the graph"""
        self.skills[skill.skill_id] = skill
        
        # Create edges for prerequisites
        if skill.skill_id not in self.edges:
            self.edges[skill.skill_id] = {}
            
        for prereq in skill.prerequisites:
            self.edges[skill.skill_id][prereq] = 1.0  # Full dependency by default
            
    def get_skill_dependencies(self, skill_id: str) -> List[str]:
        """Get all skills this skill depends on (transitive)"""
        if skill_id not in self.skills:
            return []
            
        visited = set()
        dependencies = []
        
        def dfs(current_skill):
            if current_skill in visited:
                return
            visited.add(current_skill)
            
            if current_skill in self.edges:
                for prereq in self.edges[current_skill]:
                    dependencies.append(prereq)
                    dfs(prereq)
                    
        dfs(skill_id)
        return dependencies
        
    def get_skills_depending_on(self, skill_id: str) -> List[str]:
        """Get all skills that depend on this skill"""
        dependents = []
        for skill, prereqs in self.edges.items():
            if skill_id in prereqs:
                dependents.append(skill)
        return dependents
        
    def suggest_next_skills(self, current_masteries: Dict[str, float], threshold: float = 0.7) -> List[str]:
        """Suggest skills user is ready to learn based on prerequisites"""
        suggestions = []
        
        for skill_id, skill in self.skills.items():
            # Skip if already mastered
            if current_masteries.get(skill_id, 0.0) >= threshold:
                continue
                
            # Check if prerequisites are met
            prerequisites_met = True
            for prereq in skill.prerequisites:
                if current_masteries.get(prereq, 0.0) < threshold:
                    prerequisites_met = False
                    break
                    
            if prerequisites_met:
                suggestions.append(skill_id)
                
        # Sort by difficulty (easier first)
        suggestions.sort(key=lambda s: self.skills[s].difficulty)
        return suggestions
        
    def identify_skill_from_command(self, command: str, intent: str) -> Optional[str]:
        """Identify which skill a command/intent represents"""
        command_lower = command.lower()
        intent_lower = intent.lower()
        
        # Direct command mapping
        if "nix-env" in command_lower or intent_lower == "install":
            return "nix_env"
        elif "nix-build" in command_lower:
            return "nix_build"
        elif "nix-shell" in command_lower:
            return "nix_shell"
        elif "nixos-rebuild" in command_lower or intent_lower == "rebuild":
            return "nixos_rebuild"
        elif "nix-collect-garbage" in command_lower or "garbage" in intent_lower:
            return "nix_store"
        elif "configuration.nix" in command_lower or "config" in intent_lower:
            return "nixos_configuration"
        elif "flake" in command_lower:
            return "flakes"
        elif "module" in command_lower:
            return "nixos_modules"
        elif "error" in command_lower or "debug" in command_lower:
            return "nix_debugging"
        
        # Fallback to basic nix usage
        return "nix_basics"


class BayesianKnowledgeTracer:
    """Revolutionary BKT implementation for NixOS skill mastery tracking"""
    
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path.home() / ".config" / "nix-for-humanity" / "bkt.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self.db_path = db_path
        self.skill_graph = NixOSSkillGraph()
        self.parameters: Dict[str, BKTParameters] = {}
        self._init_db()
        self._load_parameters()
        
    def _init_db(self):
        """Initialize BKT database schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # BKT parameters table
        c.execute('''
            CREATE TABLE IF NOT EXISTS bkt_parameters (
                skill_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                prior_knowledge REAL NOT NULL,
                learning_rate REAL NOT NULL,
                slip_probability REAL NOT NULL,
                guess_probability REAL NOT NULL,
                current_mastery REAL NOT NULL,
                confidence REAL NOT NULL,
                observation_count INTEGER NOT NULL,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (skill_id, user_id)
            )
        ''')
        
        # Skill observations table  
        c.execute('''
            CREATE TABLE IF NOT EXISTS skill_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                context TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence_self_report REAL
            )
        ''')
        
        # Skill definitions (cache of skill graph)
        c.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                skill_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                skill_type TEXT NOT NULL,
                prerequisites TEXT NOT NULL,
                difficulty REAL NOT NULL,
                learning_objectives TEXT NOT NULL,
                examples TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Cache skill graph in database
        self._cache_skill_graph()
        
    def _cache_skill_graph(self):
        """Cache the skill graph in the database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for skill_id, skill in self.skill_graph.skills.items():
            c.execute('''
                INSERT OR REPLACE INTO skills 
                (skill_id, name, skill_type, prerequisites, difficulty, learning_objectives, examples)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                skill.skill_id,
                skill.name,
                skill.skill_type.value,
                json.dumps(skill.prerequisites),
                skill.difficulty,
                json.dumps(skill.learning_objectives),
                json.dumps(skill.examples)
            ))
            
        conn.commit()
        conn.close()
        
    def _load_parameters(self):
        """Load BKT parameters from database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT * FROM bkt_parameters')
        for row in c.fetchall():
            skill_id, user_id, prior, learning, slip, guess, mastery, confidence, count, updated = row
            key = f"{user_id}:{skill_id}"
            self.parameters[key] = BKTParameters(
                skill_id=skill_id,
                prior_knowledge=prior,
                learning_rate=learning,
                slip_probability=slip,
                guess_probability=guess,
                current_mastery=mastery,
                confidence=confidence,
                observation_count=count,
                last_updated=updated
            )
            
        conn.close()
        
    def get_or_create_parameters(self, user_id: str, skill_id: str) -> BKTParameters:
        """Get BKT parameters for a user-skill pair, creating defaults if needed"""
        key = f"{user_id}:{skill_id}"
        
        if key not in self.parameters:
            # Create default parameters based on skill difficulty
            skill = self.skill_graph.skills.get(skill_id)
            if skill:
                # Adjust priors based on skill difficulty and prerequisites
                prior = max(0.05, 0.3 - skill.difficulty * 0.2)
                
                # Check prerequisite mastery to adjust prior
                # FIXED: Break circular dependency by getting prereq mastery directly
                prereq_mastery = 0.0
                if skill.prerequisites:
                    # Get existing parameters only, don't create new ones
                    prereq_scores = []
                    for prereq_skill_id in skill.prerequisites:
                        prereq_key = f"{user_id}:{prereq_skill_id}"
                        if prereq_key in self.parameters:
                            prereq_scores.append(self.parameters[prereq_key].current_mastery)
                        else:
                            # Use default mastery for missing prerequisites
                            prereq_scores.append(0.1)
                    
                    if prereq_scores:
                        prereq_mastery = sum(prereq_scores) / len(prereq_scores)
                    
                # Higher prior if prerequisites are well mastered
                adjusted_prior = min(0.8, prior + prereq_mastery * 0.2)
                
                self.parameters[key] = BKTParameters(
                    skill_id=skill_id,
                    prior_knowledge=adjusted_prior,
                    learning_rate=0.3,
                    slip_probability=0.1 + skill.difficulty * 0.1,  # Harder skills = more slips
                    guess_probability=max(0.05, 0.2 - skill.difficulty * 0.15),  # Harder skills = less guessing
                    current_mastery=adjusted_prior
                )
            else:
                # Default parameters for unknown skills
                self.parameters[key] = BKTParameters(skill_id=skill_id)
                
            # Save to database
            self._save_parameters(user_id, self.parameters[key])
            
        return self.parameters[key]
        
    def _save_parameters(self, user_id: str, params: BKTParameters):
        """Save BKT parameters to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO bkt_parameters
            (skill_id, user_id, prior_knowledge, learning_rate, slip_probability, 
             guess_probability, current_mastery, confidence, observation_count, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            params.skill_id, user_id, params.prior_knowledge, params.learning_rate,
            params.slip_probability, params.guess_probability, params.current_mastery,
            params.confidence, params.observation_count, params.last_updated
        ))
        
        conn.commit()
        conn.close()
        
    def update_mastery(self, observation: SkillObservation) -> BKTParameters:
        """Update skill mastery using Bayesian inference - THE CORE BKT ALGORITHM"""
        params = self.get_or_create_parameters(observation.user_id, observation.skill_id)
        
        # Current mastery belief
        current_mastery = params.current_mastery
        
        # Bayesian update based on observation
        if observation.success:
            # P(Learned | Correct) using Bayes' theorem
            # P(L|C) = P(C|L) * P(L) / P(C)
            # P(C|L) = 1 - slip_probability
            # P(C|¬L) = guess_probability
            # P(C) = P(C|L) * P(L) + P(C|¬L) * P(¬L)
            
            p_correct_given_learned = 1 - params.slip_probability
            p_correct_given_not_learned = params.guess_probability
            
            numerator = p_correct_given_learned * current_mastery
            denominator = (numerator + 
                          p_correct_given_not_learned * (1 - current_mastery))
            
            if denominator > 0:
                params.current_mastery = numerator / denominator
            else:
                params.current_mastery = current_mastery  # No change if denominator is 0
                
        else:
            # P(Learned | Incorrect)
            p_incorrect_given_learned = params.slip_probability
            p_incorrect_given_not_learned = 1 - params.guess_probability
            
            numerator = p_incorrect_given_learned * current_mastery
            denominator = (numerator + 
                          p_incorrect_given_not_learned * (1 - current_mastery))
            
            if denominator > 0:
                params.current_mastery = numerator / denominator
            else:
                params.current_mastery = current_mastery
        
        # Apply learning rate (opportunity to learn from this interaction)
        if not observation.success:
            # Learning opportunity from failure
            learn_probability = params.learning_rate
            params.current_mastery = (params.current_mastery + 
                                    learn_probability * (1 - params.current_mastery))
        
        # Update confidence based on number of observations
        # More observations = higher confidence (up to a limit)
        params.observation_count += 1
        params.confidence = min(0.95, 0.5 + (params.observation_count * 0.05))
        
        # Contextual adjustments based on observation context
        self._apply_contextual_adjustments(params, observation)
        
        # Update timestamp
        params.last_updated = datetime.now().isoformat()
        
        # Save to database
        self._save_parameters(observation.user_id, params)
        
        # Record the observation
        self._save_observation(observation)
        
        # Update the in-memory parameters
        key = f"{observation.user_id}:{observation.skill_id}"
        self.parameters[key] = params
        
        return params
        
    def _apply_contextual_adjustments(self, params: BKTParameters, observation: SkillObservation):
        """Apply contextual adjustments based on observation details"""
        context = observation.context
        
        # Adjust slip probability based on context
        if 'error_type' in context:
            error_type = context['error_type']
            if error_type == 'typo':
                # Typos don't indicate lack of knowledge
                params.slip_probability = min(1.0, params.slip_probability * 1.2)
            elif error_type == 'conceptual':
                # Conceptual errors indicate knowledge gaps
                params.slip_probability = max(0.05, params.slip_probability * 0.8)
                
        # Adjust learning rate based on help received
        if context.get('help_received', False):
            # Learning is more likely when help is provided
            params.learning_rate = min(1.0, params.learning_rate * 1.3)
            
        # Consider timing - quick responses might indicate mastery
        if 'response_time_ms' in context and context['response_time_ms'] is not None:
            response_time = context['response_time_ms']
            # Ensure response_time is numeric before comparison
            try:
                response_time_int = int(response_time)
                if response_time_int < 5000 and observation.success:  # Quick success
                    # Reduce slip probability - indicates true mastery
                    params.slip_probability = max(0.01, params.slip_probability * 0.9)
                elif response_time_int > 30000:  # Slow response
                    # Might indicate uncertainty
                    params.guess_probability = max(0.05, params.guess_probability * 1.1)
            except (ValueError, TypeError):
                # Skip timing adjustment if response_time is not convertible to int
                pass
                
    def _save_observation(self, observation: SkillObservation):
        """Save skill observation to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO skill_observations
            (skill_id, user_id, success, context, timestamp, confidence_self_report)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            observation.skill_id,
            observation.user_id,
            observation.success,
            json.dumps(observation.context),
            observation.timestamp,
            observation.confidence_self_report
        ))
        
        conn.commit()
        conn.close()
        
    def get_user_skill_masteries(self, user_id: str) -> Dict[str, float]:
        """Get current mastery estimates for all skills for a user"""
        masteries = {}
        
        for skill_id in self.skill_graph.skills.keys():
            key = f"{user_id}:{skill_id}"
            if key in self.parameters:
                # Use existing parameters
                masteries[skill_id] = self.parameters[key].current_mastery
            else:
                # Use default mastery for skills not yet encountered
                skill = self.skill_graph.skills.get(skill_id)
                if skill:
                    # Base default on skill difficulty
                    default_mastery = max(0.05, 0.3 - skill.difficulty * 0.2)
                else:
                    default_mastery = 0.1
                masteries[skill_id] = default_mastery
            
        return masteries
        
    def suggest_next_skills_for_user(self, user_id: str, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """Suggest next skills for user based on current mastery levels"""
        masteries = self.get_user_skill_masteries(user_id)
        suggestions = self.skill_graph.suggest_next_skills(masteries, threshold)
        
        # Return skill info with predicted difficulty
        result = []
        for skill_id in suggestions[:5]:  # Top 5 suggestions
            skill = self.skill_graph.skills[skill_id]
            result.append((skill_id, skill.name, skill.difficulty))
            
        return result
        
    def predict_success_probability(self, user_id: str, skill_id: str) -> float:
        """Predict probability of success for a user attempting a skill"""
        params = self.get_or_create_parameters(user_id, skill_id)
        
        # P(Success) = P(Success|Learned) * P(Learned) + P(Success|Not Learned) * P(Not Learned)
        p_success_learned = 1 - params.slip_probability
        p_success_not_learned = params.guess_probability
        
        predicted_success = (p_success_learned * params.current_mastery + 
                           p_success_not_learned * (1 - params.current_mastery))
        
        return predicted_success
        
    def identify_knowledge_gaps(self, user_id: str) -> List[Tuple[str, str, float]]:
        """Identify skills with low mastery that are prerequisites for desired skills"""
        masteries = self.get_user_skill_masteries(user_id)
        gaps = []
        
        # Find skills with low mastery
        for skill_id, mastery in masteries.items():
            if mastery < 0.5:  # Below 50% mastery
                skill = self.skill_graph.skills[skill_id]
                # Check if this skill is a prerequisite for other skills
                dependents = self.skill_graph.get_skills_depending_on(skill_id)
                if dependents:
                    gaps.append((skill_id, skill.name, mastery))
                    
        # Sort by most critical (lowest mastery, most dependents)
        gaps.sort(key=lambda x: x[2])  # Sort by mastery level
        return gaps[:10]  # Top 10 gaps
        
    def get_learning_progress_summary(self, user_id: str) -> Dict:
        """Get comprehensive learning progress for a user"""
        masteries = self.get_user_skill_masteries(user_id)
        
        # Calculate progress statistics
        total_skills = len(masteries)
        mastered_skills = sum(1 for m in masteries.values() if m >= 0.8)
        learning_skills = sum(1 for m in masteries.values() if 0.3 <= m < 0.8)
        beginning_skills = sum(1 for m in masteries.values() if m < 0.3)
        
        # Get suggestions and gaps
        suggestions = self.suggest_next_skills_for_user(user_id)
        gaps = self.identify_knowledge_gaps(user_id)
        
        # Calculate average mastery by skill type
        type_masteries = {}
        for skill_id, mastery in masteries.items():
            skill_type = self.skill_graph.skills[skill_id].skill_type.value
            if skill_type not in type_masteries:
                type_masteries[skill_type] = []
            type_masteries[skill_type].append(mastery)
            
        avg_by_type = {t: sum(scores)/len(scores) for t, scores in type_masteries.items()}
        
        return {
            'user_id': user_id,
            'total_skills': total_skills,
            'mastered_skills': mastered_skills,
            'learning_skills': learning_skills,
            'beginning_skills': beginning_skills,
            'overall_progress': mastered_skills / total_skills if total_skills > 0 else 0,
            'average_mastery_by_type': avg_by_type,
            'next_suggestions': suggestions,
            'knowledge_gaps': gaps,
            'generated_at': datetime.now().isoformat()
        }
        
    def record_interaction_with_bkt(self, user_id: str, command: str, intent: str, 
                                   success: bool, context: Dict = None) -> Optional[BKTParameters]:
        """Main interface: Record an interaction and update BKT model"""
        
        # Identify which skill this interaction represents
        skill_id = self.skill_graph.identify_skill_from_command(command, intent)
        if not skill_id:
            return None
            
        # Create observation
        observation = SkillObservation(
            skill_id=skill_id,
            user_id=user_id,
            success=success,
            context=context or {}
        )
        
        # Update mastery using BKT
        return self.update_mastery(observation)
        
    def export_bkt_data(self, user_id: str) -> Dict:
        """Export all BKT data for a user (privacy feature)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get parameters
        c.execute('SELECT * FROM bkt_parameters WHERE user_id = ?', (user_id,))
        parameters = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
        
        # Get observations
        c.execute('SELECT * FROM skill_observations WHERE user_id = ?', (user_id,))
        observations = [dict(zip([col[0] for col in c.description], row)) for row in c.fetchall()]
        
        conn.close()
        
        return {
            'user_id': user_id,
            'parameters': parameters,
            'observations': observations,
            'progress_summary': self.get_learning_progress_summary(user_id),
            'export_timestamp': datetime.now().isoformat()
        }
        
    def reset_user_bkt_data(self, user_id: str):
        """Reset all BKT data for a user (privacy feature)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM bkt_parameters WHERE user_id = ?', (user_id,))
        c.execute('DELETE FROM skill_observations WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        
        # Remove from memory
        keys_to_remove = [k for k in self.parameters.keys() if k.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self.parameters[key]