"""
Error Learner - Learns from error resolutions to improve future suggestions

This module tracks how users resolve errors and uses that knowledge to
provide better solutions in the future. All learning is local and private.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path
import sqlite3

from .error_analyzer import AnalyzedError, ErrorSolution, ErrorCategory
from ..core.types import Context

logger = logging.getLogger(__name__)


class ResolutionOutcome(Enum):
    """How an error resolution attempt ended"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ABANDONED = "abandoned"


@dataclass
class ErrorResolution:
    """A record of how an error was resolved"""
    error_id: str
    error_pattern_id: Optional[str]
    error_category: ErrorCategory
    attempted_solution: ErrorSolution
    outcome: ResolutionOutcome
    time_to_resolve: float  # seconds
    user_feedback: Optional[str] = None
    additional_steps: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningPattern:
    """A pattern learned from multiple resolutions"""
    pattern_id: str
    error_category: ErrorCategory
    successful_solutions: List[str]  # Solution IDs
    failure_indicators: List[str]
    average_resolution_time: float
    success_rate: float
    confidence: float
    usage_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


class ErrorLearner:
    """
    Learns from error resolutions to improve future suggestions.
    
    Features:
    - Tracks which solutions work for which errors
    - Learns user-specific resolution patterns
    - Identifies common failure patterns
    - Suggests preventive measures based on history
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".local/share/nix-humanity/learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "error_learning.db"
        self._init_database()
        
        # In-memory caches
        self.resolution_cache: Dict[str, List[ErrorResolution]] = {}
        self.pattern_cache: Dict[str, LearningPattern] = {}
        self._load_patterns()
    
    def _init_database(self):
        """Initialize the learning database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_resolutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_id TEXT NOT NULL,
                    error_pattern_id TEXT,
                    error_category TEXT NOT NULL,
                    solution_id TEXT NOT NULL,
                    solution_title TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    time_to_resolve REAL NOT NULL,
                    user_feedback TEXT,
                    additional_steps TEXT,
                    context TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    error_category TEXT NOT NULL,
                    successful_solutions TEXT NOT NULL,
                    failure_indicators TEXT,
                    avg_resolution_time REAL NOT NULL,
                    success_rate REAL NOT NULL,
                    confidence REAL NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indices for fast lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_pattern 
                ON error_resolutions(error_pattern_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_category 
                ON error_resolutions(error_category)
            """)
    
    def record_resolution(
        self,
        error: AnalyzedError,
        solution: ErrorSolution,
        outcome: ResolutionOutcome,
        time_to_resolve: float,
        context: Optional[Context] = None,
        user_feedback: Optional[str] = None,
        additional_steps: Optional[List[str]] = None
    ) -> ErrorResolution:
        """
        Record how an error was resolved
        
        Args:
            error: The analyzed error
            solution: The solution that was attempted
            outcome: How the resolution attempt ended
            time_to_resolve: Time taken to resolve in seconds
            context: User context
            user_feedback: Optional feedback from user
            additional_steps: Any extra steps the user took
        
        Returns:
            The recorded resolution
        """
        resolution = ErrorResolution(
            error_id=self._generate_error_id(error),
            error_pattern_id=error.pattern.id if error.pattern else None,
            error_category=error.category,
            attempted_solution=solution,
            outcome=outcome,
            time_to_resolve=time_to_resolve,
            user_feedback=user_feedback,
            additional_steps=additional_steps or [],
            context=self._extract_context(context)
        )
        
        # Store in database
        self._save_resolution(resolution)
        
        # Update caches
        error_id = resolution.error_id
        if error_id not in self.resolution_cache:
            self.resolution_cache[error_id] = []
        self.resolution_cache[error_id].append(resolution)
        
        # Update learning patterns if successful
        if outcome == ResolutionOutcome.SUCCESS:
            self._update_patterns(resolution)
        
        return resolution
    
    def get_enhanced_solutions(
        self,
        error: AnalyzedError,
        base_solutions: List[ErrorSolution]
    ) -> List[ErrorSolution]:
        """
        Enhance solutions based on learned patterns
        
        Args:
            error: The current error
            base_solutions: Initial solutions from error analyzer
        
        Returns:
            Enhanced and reordered solutions based on learning
        """
        enhanced_solutions = []
        
        # Get relevant patterns
        patterns = self._get_relevant_patterns(error)
        
        # Get historical success rates
        success_rates = self._calculate_success_rates(error)
        
        for solution in base_solutions:
            # Create enhanced solution
            enhanced = ErrorSolution(
                id=solution.id,
                title=solution.title,
                steps=solution.steps,
                commands=solution.commands,
                confidence=self._adjust_confidence(
                    solution, patterns, success_rates
                ),
                explanation=self._enhance_explanation(
                    solution, patterns, success_rates
                ),
                warnings=self._add_learned_warnings(solution, patterns),
                estimated_time=self._estimate_time(solution, patterns),
                success_probability=success_rates.get(solution.id, 0.5)
            )
            
            enhanced_solutions.append(enhanced)
        
        # Sort by adjusted confidence
        enhanced_solutions.sort(key=lambda s: s.confidence, reverse=True)
        
        # Add learned solutions not in base set
        learned_solutions = self._get_learned_solutions(error, patterns)
        for learned in learned_solutions:
            if not any(s.id == learned.id for s in enhanced_solutions):
                enhanced_solutions.append(learned)
        
        return enhanced_solutions[:5]  # Top 5 solutions
    
    def get_failure_warnings(
        self,
        error: AnalyzedError
    ) -> List[str]:
        """
        Get warnings about common failure patterns
        
        Args:
            error: The current error
        
        Returns:
            List of warnings based on past failures
        """
        warnings = []
        
        # Query past failures
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT solution_title, COUNT(*) as fail_count,
                       GROUP_CONCAT(user_feedback) as feedback
                FROM error_resolutions
                WHERE error_category = ? AND outcome = 'failure'
                GROUP BY solution_title
                ORDER BY fail_count DESC
                LIMIT 3
            """, (error.category.value,))
            
            for row in cursor:
                solution_title, fail_count, feedback = row
                if fail_count > 2:
                    warnings.append(
                        f"⚠️ '{solution_title}' has failed {fail_count} times before"
                    )
                    if feedback:
                        # Extract common feedback themes
                        feedbacks = [f for f in feedback.split(',') if f]
                        if feedbacks:
                            warnings.append(f"   Common issue: {feedbacks[0]}")
        
        return warnings
    
    def get_success_stories(
        self,
        error: AnalyzedError,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get successful resolution stories for similar errors
        
        Args:
            error: The current error
            limit: Maximum number of stories
        
        Returns:
            List of success stories with details
        """
        stories = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT solution_title, time_to_resolve, user_feedback,
                       additional_steps, timestamp
                FROM error_resolutions
                WHERE error_category = ? AND outcome = 'success'
                      AND user_feedback IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (error.category.value, limit))
            
            for row in cursor:
                solution_title, time, feedback, steps, timestamp = row
                stories.append({
                    "solution": solution_title,
                    "time": f"{int(time)}s" if time < 60 else f"{int(time/60)}m",
                    "feedback": feedback,
                    "extra_steps": json.loads(steps) if steps else [],
                    "when": self._format_relative_time(timestamp)
                })
        
        return stories
    
    def _save_resolution(self, resolution: ErrorResolution):
        """Save resolution to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO error_resolutions
                (error_id, error_pattern_id, error_category, solution_id,
                 solution_title, outcome, time_to_resolve, user_feedback,
                 additional_steps, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resolution.error_id,
                resolution.error_pattern_id,
                resolution.error_category.value,
                resolution.attempted_solution.id,
                resolution.attempted_solution.title,
                resolution.outcome.value,
                resolution.time_to_resolve,
                resolution.user_feedback,
                json.dumps(resolution.additional_steps),
                json.dumps(resolution.context)
            ))
    
    def _update_patterns(self, resolution: ErrorResolution):
        """Update learning patterns based on successful resolution"""
        pattern_id = f"{resolution.error_category.value}_{resolution.error_pattern_id or 'generic'}"
        
        if pattern_id in self.pattern_cache:
            pattern = self.pattern_cache[pattern_id]
            # Update existing pattern
            pattern.successful_solutions.append(resolution.attempted_solution.id)
            pattern.usage_count += 1
            pattern.last_updated = datetime.now()
            
            # Recalculate success rate and confidence
            self._recalculate_pattern_metrics(pattern)
        else:
            # Create new pattern
            pattern = LearningPattern(
                pattern_id=pattern_id,
                error_category=resolution.error_category,
                successful_solutions=[resolution.attempted_solution.id],
                failure_indicators=[],
                average_resolution_time=resolution.time_to_resolve,
                success_rate=1.0,
                confidence=0.5,  # Start with medium confidence
                usage_count=1
            )
            self.pattern_cache[pattern_id] = pattern
        
        # Save to database
        self._save_pattern(pattern)
    
    def _save_pattern(self, pattern: LearningPattern):
        """Save learning pattern to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO learning_patterns
                (pattern_id, error_category, successful_solutions,
                 failure_indicators, avg_resolution_time, success_rate,
                 confidence, usage_count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id,
                pattern.error_category.value,
                json.dumps(pattern.successful_solutions),
                json.dumps(pattern.failure_indicators),
                pattern.average_resolution_time,
                pattern.success_rate,
                pattern.confidence,
                pattern.usage_count,
                pattern.last_updated
            ))
    
    def _load_patterns(self):
        """Load patterns from database into cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM learning_patterns")
            
            for row in cursor:
                pattern = LearningPattern(
                    pattern_id=row[0],
                    error_category=ErrorCategory(row[1]),
                    successful_solutions=json.loads(row[2]),
                    failure_indicators=json.loads(row[3]),
                    average_resolution_time=row[4],
                    success_rate=row[5],
                    confidence=row[6],
                    usage_count=row[7],
                    last_updated=datetime.fromisoformat(row[8])
                )
                self.pattern_cache[pattern.pattern_id] = pattern
    
    def _get_relevant_patterns(
        self,
        error: AnalyzedError
    ) -> List[LearningPattern]:
        """Get patterns relevant to the current error"""
        relevant = []
        
        # Direct pattern match
        if error.pattern:
            pattern_id = f"{error.category.value}_{error.pattern.id}"
            if pattern_id in self.pattern_cache:
                relevant.append(self.pattern_cache[pattern_id])
        
        # Category-level patterns
        generic_id = f"{error.category.value}_generic"
        if generic_id in self.pattern_cache:
            relevant.append(self.pattern_cache[generic_id])
        
        # Sort by confidence and recency
        relevant.sort(
            key=lambda p: (p.confidence, p.last_updated),
            reverse=True
        )
        
        return relevant
    
    def _calculate_success_rates(
        self,
        error: AnalyzedError
    ) -> Dict[str, float]:
        """Calculate success rates for solutions"""
        rates = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT solution_id, 
                       SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) as successes,
                       COUNT(*) as total
                FROM error_resolutions
                WHERE error_category = ?
                GROUP BY solution_id
            """, (error.category.value,))
            
            for row in cursor:
                solution_id, successes, total = row
                rates[solution_id] = successes / total if total > 0 else 0.5
        
        return rates
    
    def _adjust_confidence(
        self,
        solution: ErrorSolution,
        patterns: List[LearningPattern],
        success_rates: Dict[str, float]
    ) -> float:
        """Adjust solution confidence based on learning"""
        base_confidence = solution.confidence
        
        # Adjust based on historical success rate
        if solution.id in success_rates:
            historical_factor = success_rates[solution.id]
            base_confidence = base_confidence * 0.7 + historical_factor * 0.3
        
        # Boost if solution appears in successful patterns
        for pattern in patterns:
            if solution.id in pattern.successful_solutions:
                base_confidence *= 1.1  # 10% boost
                base_confidence = min(base_confidence, 0.95)
        
        return base_confidence
    
    def _enhance_explanation(
        self,
        solution: ErrorSolution,
        patterns: List[LearningPattern],
        success_rates: Dict[str, float]
    ) -> str:
        """Enhance solution explanation with learned insights"""
        explanation = solution.explanation or ""
        
        # Add success rate info
        if solution.id in success_rates:
            rate = success_rates[solution.id]
            if rate > 0.8:
                explanation += " This solution works well for most users."
            elif rate < 0.3:
                explanation += " This solution has mixed results."
        
        # Add pattern insights
        for pattern in patterns:
            if solution.id in pattern.successful_solutions:
                avg_time = int(pattern.average_resolution_time)
                if avg_time < 60:
                    explanation += f" Usually resolves in {avg_time} seconds."
                else:
                    explanation += f" Usually takes about {avg_time//60} minutes."
        
        return explanation
    
    def _add_learned_warnings(
        self,
        solution: ErrorSolution,
        patterns: List[LearningPattern]
    ) -> List[str]:
        """Add warnings based on learned failure patterns"""
        warnings = solution.warnings.copy() if solution.warnings else []
        
        # Check failure indicators in patterns
        for pattern in patterns:
            for indicator in pattern.failure_indicators:
                if indicator in solution.id:
                    warnings.append(f"Note: {indicator}")
        
        return warnings
    
    def _estimate_time(
        self,
        solution: ErrorSolution,
        patterns: List[LearningPattern]
    ) -> Optional[float]:
        """Estimate resolution time based on patterns"""
        times = []
        
        for pattern in patterns:
            if solution.id in pattern.successful_solutions:
                times.append(pattern.average_resolution_time)
        
        if times:
            return sum(times) / len(times)
        
        return None
    
    def _get_learned_solutions(
        self,
        error: AnalyzedError,
        patterns: List[LearningPattern]
    ) -> List[ErrorSolution]:
        """Get additional solutions learned from experience"""
        learned_solutions = []
        
        # Aggregate successful solutions from patterns
        solution_counts = {}
        for pattern in patterns:
            for sol_id in pattern.successful_solutions:
                solution_counts[sol_id] = solution_counts.get(sol_id, 0) + 1
        
        # Create solutions for frequently successful ones
        for sol_id, count in solution_counts.items():
            if count >= 2:  # Used successfully at least twice
                # Retrieve solution details from database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT DISTINCT solution_title, additional_steps
                        FROM error_resolutions
                        WHERE solution_id = ? AND outcome = 'success'
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """, (sol_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        title, steps = row
                        learned_solutions.append(ErrorSolution(
                            id=sol_id,
                            title=f"{title} (Community Validated)",
                            steps=json.loads(steps) if steps else ["Follow standard procedure"],
                            confidence=0.7 + (count * 0.05),  # Higher with more uses
                            explanation="This solution has worked for multiple users"
                        ))
        
        return learned_solutions
    
    def _generate_error_id(self, error: AnalyzedError) -> str:
        """Generate a unique ID for an error"""
        import hashlib
        
        # Create ID from error characteristics
        components = [
            error.category.value,
            error.pattern.id if error.pattern else "unknown",
            error.original_error[:100]  # First 100 chars
        ]
        
        id_string = "|".join(components)
        return hashlib.md5(id_string.encode()).hexdigest()[:16]
    
    def _extract_context(self, context: Optional[Context]) -> Dict[str, Any]:
        """Extract relevant context for learning"""
        if not context:
            return {}
        
        extracted = {}
        
        if hasattr(context, 'user_preferences'):
            extracted['persona'] = context.user_preferences.get('persona', 'unknown')
            
        if hasattr(context, 'system_state'):
            extracted['nixos_version'] = context.system_state.get('version', 'unknown')
            
        return extracted
    
    def _recalculate_pattern_metrics(self, pattern: LearningPattern):
        """Recalculate success rate and confidence for a pattern"""
        with sqlite3.connect(self.db_path) as conn:
            # Get success/failure counts
            cursor = conn.execute("""
                SELECT outcome, COUNT(*) as count, AVG(time_to_resolve) as avg_time
                FROM error_resolutions
                WHERE error_pattern_id = ? OR 
                      (error_category = ? AND error_pattern_id IS NULL)
                GROUP BY outcome
            """, (
                pattern.pattern_id.split('_')[1],
                pattern.error_category.value
            ))
            
            total = 0
            successes = 0
            total_time = 0
            time_count = 0
            
            for row in cursor:
                outcome, count, avg_time = row
                total += count
                if outcome == 'success':
                    successes = count
                    if avg_time:
                        total_time += avg_time * count
                        time_count += count
            
            if total > 0:
                pattern.success_rate = successes / total
                # Confidence based on sample size and success rate
                pattern.confidence = min(
                    pattern.success_rate * (1 - 1 / (total + 1)),
                    0.95
                )
            
            if time_count > 0:
                pattern.average_resolution_time = total_time / time_count
    
    def _format_relative_time(self, timestamp: str) -> str:
        """Format timestamp as relative time"""
        try:
            dt = datetime.fromisoformat(timestamp)
            delta = datetime.now() - dt
            
            if delta.days > 7:
                return dt.strftime("%Y-%m-%d")
            elif delta.days > 0:
                return f"{delta.days} days ago"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hours ago"
            elif delta.seconds > 60:
                return f"{delta.seconds // 60} minutes ago"
            else:
                return "just now"
        except:
            return timestamp
    
    def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for backup or analysis"""
        data = {
            "patterns": {},
            "resolutions_summary": {},
            "export_date": datetime.now().isoformat()
        }
        
        # Export patterns
        for pattern_id, pattern in self.pattern_cache.items():
            data["patterns"][pattern_id] = {
                "category": pattern.error_category.value,
                "success_rate": pattern.success_rate,
                "confidence": pattern.confidence,
                "usage_count": pattern.usage_count,
                "avg_resolution_time": pattern.average_resolution_time
            }
        
        # Export resolution summary
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT error_category, outcome, COUNT(*) as count
                FROM error_resolutions
                GROUP BY error_category, outcome
            """)
            
            for row in cursor:
                category, outcome, count = row
                if category not in data["resolutions_summary"]:
                    data["resolutions_summary"][category] = {}
                data["resolutions_summary"][category][outcome] = count
        
        return data
    
    def clear_old_data(self, days: int = 90):
        """Clear learning data older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM error_resolutions
                WHERE timestamp < datetime(?, 'unixepoch')
            """, (cutoff_date,))
            
            logger.info(f"Cleared error resolutions older than {days} days")