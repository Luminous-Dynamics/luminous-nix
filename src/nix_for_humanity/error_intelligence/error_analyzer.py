"""
Error Analyzer - Core component for understanding and analyzing errors

Provides pattern matching, context analysis, and integration with XAI
to explain why errors occurred and how to fix them.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import logging

from ..xai.causal_engine import CausalXAI, ExplanationLevel
from ..core.types import ExecutionResult, Context

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    INFO = "info"           # Informational, not really an error
    WARNING = "warning"     # Something to be aware of
    ERROR = "error"         # Actual error that needs fixing
    CRITICAL = "critical"   # System-breaking error


class ErrorCategory(Enum):
    """Categories of errors for different handling"""
    USER_INPUT = "user_input"          # Typos, wrong syntax
    SYSTEM = "system"                  # Disk full, network down
    PERMISSION = "permission"          # Needs sudo, locked file
    NOT_FOUND = "not_found"           # Package/file doesn't exist
    DEPENDENCY = "dependency"          # Missing dependencies
    CONFIGURATION = "configuration"    # Config file issues
    NETWORK = "network"               # Network-related errors
    SAFETY = "safety"                 # Dangerous operation blocked


@dataclass
class ErrorPattern:
    """Pattern definition for recognizing specific errors"""
    id: str
    category: ErrorCategory
    severity: ErrorSeverity
    patterns: List[re.Pattern]         # Regex patterns to match
    keywords: List[str]               # Keywords that indicate this error
    description: str                  # What this error means
    common_causes: List[str]          # Why this typically happens
    
    def matches(self, error_text: str) -> bool:
        """Check if error text matches this pattern"""
        error_lower = error_text.lower()
        
        # Check regex patterns
        for pattern in self.patterns:
            if pattern.search(error_text):
                return True
        
        # Check keywords
        for keyword in self.keywords:
            if keyword.lower() in error_lower:
                return True
        
        return False


@dataclass
class ErrorSolution:
    """A solution for an error with context"""
    id: str
    title: str                        # Brief solution title
    steps: List[str]                  # Step-by-step instructions
    commands: List[str]               # Exact commands to run
    explanation: str                  # Why this solution works
    confidence: float                 # How confident we are (0-1)
    prerequisites: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    learn_more_url: Optional[str] = None


@dataclass
class AnalyzedError:
    """Complete analysis of an error"""
    original_error: str
    pattern: Optional[ErrorPattern]
    category: ErrorCategory
    severity: ErrorSeverity
    solutions: List[ErrorSolution]
    context_factors: Dict[str, Any]
    xai_explanation: Optional[str] = None
    preventive_suggestions: List[str] = field(default_factory=list)
    similar_past_errors: List[Dict[str, Any]] = field(default_factory=list)


class ErrorAnalyzer:
    """
    Main error analysis engine that recognizes patterns,
    provides solutions, and learns from resolutions
    """
    
    def __init__(self, xai_engine: Optional[CausalXAI] = None):
        self.xai_engine = xai_engine or CausalXAI()
        self.patterns: List[ErrorPattern] = []
        self.solution_history: List[Dict[str, Any]] = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load error patterns (will be populated by NixOSErrorPatterns)"""
        # Patterns are registered dynamically
        pass
    
    def register_pattern(self, pattern: ErrorPattern):
        """Register a new error pattern"""
        self.patterns.append(pattern)
        logger.debug(f"Registered error pattern: {pattern.id}")
    
    def analyze_error(
        self,
        error_text: str,
        context: Optional[Context] = None,
        execution_result: Optional[ExecutionResult] = None,
        system_state: Optional[Dict[str, Any]] = None
    ) -> AnalyzedError:
        """
        Analyze an error and provide educational information
        
        Args:
            error_text: The error message text
            context: Request context
            execution_result: Full execution result if available
            system_state: Current system state (disk space, network, etc.)
        
        Returns:
            Complete error analysis with solutions
        """
        # Find matching pattern
        pattern = self._find_matching_pattern(error_text)
        
        # Determine category and severity
        if pattern:
            category = pattern.category
            severity = pattern.severity
        else:
            category, severity = self._infer_category_severity(error_text)
        
        # Gather context factors
        context_factors = self._analyze_context(
            error_text, context, execution_result, system_state
        )
        
        # Generate solutions
        solutions = self._generate_solutions(
            error_text, pattern, category, context_factors
        )
        
        # Get XAI explanation if available
        xai_explanation = None
        if self.xai_engine and pattern:
            xai_explanation = self._get_xai_explanation(
                pattern, context_factors, solutions
            )
        
        # Find similar past errors
        similar_errors = self._find_similar_errors(error_text, pattern)
        
        # Generate preventive suggestions
        preventive_suggestions = self._generate_preventive_suggestions(
            pattern, category, context_factors
        )
        
        return AnalyzedError(
            original_error=error_text,
            pattern=pattern,
            category=category,
            severity=severity,
            solutions=solutions,
            context_factors=context_factors,
            xai_explanation=xai_explanation,
            preventive_suggestions=preventive_suggestions,
            similar_past_errors=similar_errors
        )
    
    def _find_matching_pattern(self, error_text: str) -> Optional[ErrorPattern]:
        """Find the best matching error pattern"""
        for pattern in self.patterns:
            if pattern.matches(error_text):
                logger.debug(f"Matched error pattern: {pattern.id}")
                return pattern
        return None
    
    def _infer_category_severity(
        self, error_text: str
    ) -> Tuple[ErrorCategory, ErrorSeverity]:
        """Infer category and severity when no pattern matches"""
        error_lower = error_text.lower()
        
        # Permission errors
        if any(word in error_lower for word in ["permission", "denied", "sudo"]):
            return ErrorCategory.PERMISSION, ErrorSeverity.ERROR
        
        # Not found errors
        if any(word in error_lower for word in ["not found", "404", "missing"]):
            return ErrorCategory.NOT_FOUND, ErrorSeverity.ERROR
        
        # Network errors
        if any(word in error_lower for word in ["network", "connection", "timeout"]):
            return ErrorCategory.NETWORK, ErrorSeverity.ERROR
        
        # System errors
        if any(word in error_lower for word in ["disk", "memory", "space"]):
            return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL
        
        # Default
        return ErrorCategory.USER_INPUT, ErrorSeverity.ERROR
    
    def _analyze_context(
        self,
        error_text: str,
        context: Optional[Context],
        execution_result: Optional[ExecutionResult],
        system_state: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze all context factors that might affect the error"""
        factors = {
            "error_text": error_text,
            "has_context": context is not None,
            "has_execution_result": execution_result is not None,
            "has_system_state": system_state is not None
        }
        
        if context:
            factors.update({
                "frontend": context.frontend,
                "personality": context.personality,
                "dry_run": context.dry_run
            })
        
        if execution_result:
            factors.update({
                "exit_code": execution_result.exit_code,
                "duration": execution_result.duration,
                "output_length": len(execution_result.output)
            })
        
        if system_state:
            factors.update({
                "disk_space_low": system_state.get("disk_space_gb", 100) < 10,
                "network_available": system_state.get("network_up", True),
                "nixos_version": system_state.get("nixos_version", "unknown")
            })
        
        return factors
    
    def _generate_solutions(
        self,
        error_text: str,
        pattern: Optional[ErrorPattern],
        category: ErrorCategory,
        context_factors: Dict[str, Any]
    ) -> List[ErrorSolution]:
        """Generate solutions based on error analysis"""
        solutions = []
        
        # Pattern-specific solutions
        if pattern:
            solutions.extend(self._get_pattern_solutions(pattern, context_factors))
        
        # Category-specific solutions
        solutions.extend(self._get_category_solutions(category, error_text))
        
        # Context-aware solutions
        if context_factors.get("disk_space_low"):
            solutions.append(ErrorSolution(
                id="free_disk_space",
                title="Free up disk space",
                steps=[
                    "Check disk usage with 'df -h'",
                    "Run garbage collection: 'nix-collect-garbage -d'",
                    "Remove old generations: 'nix-env --delete-generations old'"
                ],
                commands=[
                    "df -h",
                    "sudo nix-collect-garbage -d",
                    "nix-env --delete-generations old"
                ],
                explanation="Low disk space can cause many NixOS operations to fail",
                confidence=0.9
            ))
        
        # Sort by confidence
        solutions.sort(key=lambda s: s.confidence, reverse=True)
        
        return solutions[:5]  # Return top 5 solutions
    
    def _get_pattern_solutions(
        self,
        pattern: ErrorPattern,
        context_factors: Dict[str, Any]
    ) -> List[ErrorSolution]:
        """Get solutions specific to an error pattern"""
        # This will be implemented with specific solutions for each pattern
        # For now, return a generic solution based on the pattern
        return [
            ErrorSolution(
                id=f"pattern_{pattern.id}",
                title=f"Fix {pattern.description}",
                steps=[
                    f"This error typically happens because: {cause}"
                    for cause in pattern.common_causes[:2]
                ],
                commands=[],
                explanation=pattern.description,
                confidence=0.8
            )
        ]
    
    def _get_category_solutions(
        self,
        category: ErrorCategory,
        error_text: str
    ) -> List[ErrorSolution]:
        """Get generic solutions for error categories"""
        solutions = []
        
        if category == ErrorCategory.PERMISSION:
            solutions.append(ErrorSolution(
                id="use_sudo",
                title="Try with administrator privileges",
                steps=["Prepend 'sudo' to your command"],
                commands=["sudo <your-command>"],
                explanation="Some operations require administrator privileges",
                confidence=0.7
            ))
        
        elif category == ErrorCategory.NOT_FOUND:
            solutions.append(ErrorSolution(
                id="search_package",
                title="Search for the correct package name",
                steps=[
                    "Search available packages",
                    "Check for typos in the package name"
                ],
                commands=["nix search nixpkgs <package-name>"],
                explanation="The package name might be different than expected",
                confidence=0.8
            ))
        
        return solutions
    
    def _get_xai_explanation(
        self,
        pattern: ErrorPattern,
        context_factors: Dict[str, Any],
        solutions: List[ErrorSolution]
    ) -> str:
        """Generate XAI explanation for why the error occurred"""
        factors = [
            ("error_pattern", 0.9, f"Matched known pattern: {pattern.id}"),
            ("context", 0.7, "System context indicates potential issues"),
            ("solutions_available", 0.8, f"Found {len(solutions)} potential solutions")
        ]
        
        explanation = self.xai_engine.explain_decision(
            decision_type="error_diagnosis",
            decision_value=pattern.description,
            context=context_factors,
            factors=factors,
            level=ExplanationLevel.DETAILED
        )
        
        return explanation.explanation
    
    def _find_similar_errors(
        self,
        error_text: str,
        pattern: Optional[ErrorPattern]
    ) -> List[Dict[str, Any]]:
        """Find similar errors from history"""
        similar = []
        
        # Search through solution history
        for past_error in self.solution_history[-10:]:  # Last 10 errors
            if pattern and past_error.get("pattern_id") == pattern.id:
                similar.append({
                    "error": past_error["error_text"][:100] + "...",
                    "solution_used": past_error["solution_id"],
                    "success": past_error["success"],
                    "timestamp": past_error["timestamp"]
                })
        
        return similar[:3]  # Return top 3
    
    def _generate_preventive_suggestions(
        self,
        pattern: Optional[ErrorPattern],
        category: ErrorCategory,
        context_factors: Dict[str, Any]
    ) -> List[str]:
        """Generate suggestions to prevent this error in the future"""
        suggestions = []
        
        if category == ErrorCategory.PERMISSION:
            suggestions.append("Consider using declarative configuration in /etc/nixos/configuration.nix instead of imperative commands")
        
        if category == ErrorCategory.NOT_FOUND:
            suggestions.append("Use 'nix search' before installing to verify package names")
            suggestions.append("Enable tab completion for package names")
        
        if context_factors.get("disk_space_low"):
            suggestions.append("Set up automatic garbage collection in your NixOS configuration")
            suggestions.append("Monitor disk space regularly with 'df -h'")
        
        if pattern and pattern.severity == ErrorSeverity.CRITICAL:
            suggestions.append("Create system backups before major operations")
            suggestions.append("Test changes in a VM first")
        
        return suggestions
    
    def record_solution_outcome(
        self,
        error_text: str,
        pattern_id: Optional[str],
        solution_id: str,
        success: bool,
        user_feedback: Optional[str] = None
    ):
        """Record the outcome of applying a solution for learning"""
        self.solution_history.append({
            "error_text": error_text,
            "pattern_id": pattern_id,
            "solution_id": solution_id,
            "success": success,
            "user_feedback": user_feedback,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Recorded solution outcome: {solution_id} - {'Success' if success else 'Failed'}")