"""
Enhanced Backend with Error Intelligence Integration

This backend implementation integrates the Enhanced Error Intelligence module
to provide educational, helpful, and persona-adaptive error handling.
"""

import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List
import logging

from ..interfaces.backend_interface import BackendInterface
from ..core.types import (
    Request, Response, Intent, IntentType, Plan, ExecutionResult,
    PersonalityStyle, Command, ExecutionMode
)
from ..core.intent_engine import IntentEngine
from ..core.execution_engine import ExecutionEngine
# SafeExecutor is in the backend directory, not src structure
from ..ai.xai_engine import XAIEngine, ExplanationLevel
from ..xai.causal_engine import CausalXAI
from ..xai.confidence_calculator import ConfidenceCalculator

# Import Error Intelligence components
from ..error_intelligence import (
    ErrorAnalyzer, ErrorCategory, ErrorSeverity,
    EducationalFormatter, ErrorLearner, PreventiveAdvisor,
    ResolutionOutcome
)


logger = logging.getLogger(__name__)


class EnhancedBackend(BackendInterface):
    """
    Enhanced backend with integrated Error Intelligence.
    
    This backend provides:
    - Educational error handling
    - XAI-powered error explanations
    - Learning from error resolutions
    - Preventive suggestions
    - Persona-adaptive error messages
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced backend with error intelligence."""
        self.config = config or {}
        
        # Core components
        self.intent_engine = IntentEngine()
        self.execution_engine = ExecutionEngine()
        # Use execution_engine as executor for unified execution
        self.xai_engine = XAIEngine()
        self.causal_xai = CausalXAI()
        self.confidence_calculator = ConfidenceCalculator()
        
        # Error Intelligence components
        self.error_analyzer = ErrorAnalyzer()
        self.error_formatter = EducationalFormatter()
        self.error_learner = ErrorLearner()
        self.preventive_advisor = PreventiveAdvisor()
        
        # Configuration
        self.progress_callback = config.get('progress_callback')
        self.personality = config.get('personality', PersonalityStyle.FRIENDLY)
        self.learning_enabled = config.get('learning_enabled', True)
        self.native_api = config.get('native_api', True)
        
        # State
        self.last_error = None
        self.error_context = {}
        
    def process(self, request: Request) -> Response:
        """Process request with enhanced error handling."""
        try:
            # Check for preventive suggestions first
            preventive_suggestions = self._check_preventive_suggestions(request)
            
            # Extract intent
            intent = self.get_intent(request.query)
            
            if intent.type == IntentType.UNKNOWN:
                return self._handle_unknown_intent(request, intent)
            
            # Build plan
            plan = self.execution_engine.build_command(intent.type.value, intent.target)
            
            # Execute if requested
            if request.execute and not request.dry_run:
                result = self._execute_with_error_intelligence(plan, intent, request)
                
                # Learn from execution
                if self.learning_enabled and result.error:
                    self._learn_from_error(result, request)
                    
                return self._build_response(
                    intent, plan, result, 
                    preventive_suggestions=preventive_suggestions
                )
            else:
                # Dry run or preview only
                return self._build_response(
                    intent, plan, None,
                    preventive_suggestions=preventive_suggestions
                )
                
        except Exception as e:
            logger.error(f"Backend error: {e}", exc_info=True)
            return self._handle_unexpected_error(str(e), request)
    
    async def process_async(self, request: Request) -> Response:
        """Async version of process."""
        return await asyncio.to_thread(self.process, request)
    
    def get_intent(self, query: str) -> Intent:
        """Extract intent with error context awareness."""
        # Check if this is an error-related query
        if self._is_error_query(query):
            return self._handle_error_query(query)
            
        return self.intent_engine.recognize(query)
    
    def explain(self, intent: Intent) -> str:
        """Generate explanation with error context."""
        base_explanation = self.xai_engine.explain_intent(intent, ExplanationLevel.SIMPLE)
        
        # Add error context if relevant
        if self.last_error and intent.type in [IntentType.HELP, IntentType.EXPLAIN]:
            error_explanation = self._explain_last_error()
            return f"{base_explanation}\n\n{error_explanation}"
            
        return base_explanation
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        """Set progress callback."""
        self.progress_callback = callback
        # ExecutionEngine doesn't have set_progress_callback method
        # Progress callback handled through execution_engine
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get enhanced capabilities including error intelligence."""
        return {
            "native_api": self.native_api,
            "learning_enabled": self.learning_enabled,
            "personalities": [p.value for p in PersonalityStyle],
            "features": [
                "natural_language",
                "xai_explanations",
                "error_intelligence",
                "preventive_suggestions",
                "educational_errors",
                "persona_adaptation"
            ],
            "version": "0.9.0",
            "error_intelligence": {
                "pattern_recognition": True,
                "educational_formatting": True,
                "learning_from_resolutions": True,
                "preventive_suggestions": True,
                "xai_integration": True
            }
        }
    
    def shutdown(self) -> None:
        """Graceful shutdown."""
        # Save error learning data
        if hasattr(self.error_learner, 'save'):
            self.error_learner.save()
            
        logger.info("Enhanced backend shutdown complete")
    
    # Error Intelligence Methods
    
    def _execute_with_error_intelligence(self, plan: Plan, intent: Intent, 
                                       request: Request) -> ExecutionResult:
        """Execute with intelligent error handling."""
        try:
            # Execute command
            # Use execution_engine for command execution
            result = self.execution_engine.execute_plan(plan, intent)
            
            if result.error:
                # Analyze error intelligently
                analyzed_error = self.error_analyzer.analyze_error(
                    result.error,
                    context={
                        'command': plan.commands[0] if plan.commands else None,
                        'intent': intent,
                        'system_state': self._get_system_state()
                    }
                )
                
                # Get XAI explanation for why it failed
                if self.causal_xai:
                    xai_explanation = self.causal_xai.explain_error_causality(
                        analyzed_error, self.error_context
                    )
                    analyzed_error.xai_explanation = xai_explanation.explanation
                
                # Format educational error
                educational_error = self.error_formatter.format_educational_error(
                    analyzed_error,
                    self._detect_persona(request)
                )
                
                # Store for learning
                self.last_error = analyzed_error
                self.error_context = {
                    'timestamp': datetime.now(),
                    'request': request,
                    'plan': plan,
                    'educational_error': educational_error
                }
                
                # Update result with educational error
                result.educational_error = educational_error
                result.analyzed_error = analyzed_error
                
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1,
                duration=0.0
            )
    
    def _check_preventive_suggestions(self, request: Request) -> List[Any]:
        """Check for preventive suggestions before execution."""
        suggestions = []
        
        # Get system health suggestions
        health_suggestions = self.preventive_advisor.get_system_health_suggestions()
        suggestions.extend(health_suggestions)
        
        # Get context-based suggestions
        if request.context:
            context_suggestions = self.preventive_advisor.get_contextual_suggestions(
                request.context,
                self._detect_persona(request)
            )
            suggestions.extend(context_suggestions)
        
        return suggestions
    
    def _handle_unknown_intent(self, request: Request, intent: Intent) -> Response:
        """Handle unknown intent with educational error."""
        error_msg = f"I don't understand '{request.query}'"
        
        # Create educational error
        analyzed_error = self.error_analyzer.create_error(
            error_msg,
            ErrorCategory.USER_INPUT,
            ErrorSeverity.LOW
        )
        
        educational_error = self.error_formatter.format_educational_error(
            analyzed_error,
            self._detect_persona(request)
        )
        
        return Response(
            success=False,
            intent=intent,
            plan=None,
            result=None,
            message=educational_error.headline,
            educational_error=educational_error,
            suggestions=educational_error.solutions
        )
    
    def _handle_unexpected_error(self, error: str, request: Request) -> Response:
        """Handle unexpected errors educationally."""
        analyzed_error = self.error_analyzer.analyze_error(
            error,
            context={'request': request}
        )
        
        educational_error = self.error_formatter.format_educational_error(
            analyzed_error,
            self._detect_persona(request)
        )
        
        return Response(
            success=False,
            intent=Intent(type=IntentType.UNKNOWN),
            plan=None,
            result=None,
            message=educational_error.headline,
            educational_error=educational_error,
            error=error
        )
    
    def _is_error_query(self, query: str) -> bool:
        """Check if query is about an error."""
        error_keywords = [
            'error', 'failed', 'problem', 'issue', 'wrong',
            'help', 'why', "didn't work", 'broken'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in error_keywords)
    
    def _handle_error_query(self, query: str) -> Intent:
        """Handle queries about errors."""
        if self.last_error:
            return Intent(
                type=IntentType.EXPLAIN,
                entities={'target': 'last_error'},
                confidence=0.9,
                raw_input=query
            )
        return self.intent_engine.recognize(query)
    
    def _explain_last_error(self) -> str:
        """Explain the last error that occurred."""
        if not self.last_error:
            return "No recent errors to explain."
            
        explanation = ["**About your last error:**"]
        
        if self.last_error.xai_explanation:
            explanation.append(f"\n{self.last_error.xai_explanation}")
            
        if self.last_error.solutions:
            explanation.append("\n**Suggested solutions:**")
            for i, solution in enumerate(self.last_error.solutions[:3], 1):
                explanation.append(f"{i}. {solution.description}")
                
        return "\n".join(explanation)
    
    def _learn_from_error(self, result: ExecutionResult, request: Request) -> None:
        """Learn from error resolution."""
        if not self.last_error or not self.learning_enabled:
            return
            
        # Track the error occurrence
        self.error_learner.record_error(
            self.last_error,
            context={
                'request': request,
                'result': result
            }
        )
    
    def _build_response(self, intent: Intent, plan: Plan, 
                       result: Optional[ExecutionResult],
                       preventive_suggestions: Optional[List] = None) -> Response:
        """Build response with error intelligence enhancements."""
        response = Response(
            success=result.success if result else True,
            intent=intent,
            plan=plan,
            result=result,
            message=self._generate_message(intent, plan, result),
            timestamp=datetime.now()
        )
        
        # Add educational error if present
        if result and hasattr(result, 'educational_error'):
            response.educational_error = result.educational_error
            response.analyzed_error = result.analyzed_error
            
        # Add preventive suggestions
        if preventive_suggestions:
            response.preventive_suggestions = preventive_suggestions
            
        # Add XAI explanation
        if self.xai_engine:
            response.explanation = self.xai_engine.explain_intent(
                intent, 
                ExplanationLevel.SIMPLE
            )
            
        return response
    
    def _detect_persona(self, request: Request) -> str:
        """Detect persona from request context."""
        if request.context and 'persona' in request.context:
            return request.context['persona']
            
        # Default persona detection logic
        return 'default'
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Get current system state for error analysis."""
        # This would gather real system state in production
        return {
            'disk_free': '50GB',
            'memory_free': '4GB',
            'network_status': 'connected',
            'nixos_generation': '42'
        }
    
    def _generate_message(self, intent: Intent, plan: Plan, 
                         result: Optional[ExecutionResult]) -> str:
        """Generate user-friendly message."""
        if result and result.error:
            return "I encountered an issue. Let me help you understand and fix it."
        elif result and result.success:
            return f"Successfully completed: {intent.type.value}"
        else:
            return f"Ready to: {intent.type.value}"