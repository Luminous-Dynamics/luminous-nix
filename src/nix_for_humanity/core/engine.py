# Core Engine
"""
The headless core engine that powers all Nix for Humanity interfaces
"""

import time
from typing import Optional, Dict, Any
from pathlib import Path

from .interface import Query, ExecutionMode
from .types import Response, Intent, Command
from .planning import Plan, ExecutionResult
from .intent_engine import IntentEngine
from .knowledge_base import KnowledgeBase
from .execution_engine import ExecutionEngine
from .personality_system import PersonalitySystem, PersonalityStyle
from .learning_system import LearningSystem, Interaction


class NixForHumanityCore:
    """
    The central brain of Nix for Humanity.
    Processes natural language queries and returns structured responses.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the core engine with all subsystems"""
        
        config = config or {}
        
        # Initialize subsystems
        self.intent_engine = IntentEngine()
        self.knowledge_base = KnowledgeBase(config.get('knowledge_db_path'))
        self.execution_engine = ExecutionEngine(dry_run=config.get('dry_run', True))
        self.personality_system = PersonalitySystem(
            PersonalityStyle(config.get('default_personality', 'friendly'))
        )
        self.learning_system = LearningSystem(config.get('learning_db_path'))
        
        # Configuration
        self.collect_feedback = config.get('collect_feedback', True)
        self.enable_learning = config.get('enable_learning', True)
        
    def plan(self, query: Query) -> Plan:
        """
        Create a plan for the query without executing it.
        This separates "thinking" from "doing".
        """
        
        # Step 1: Extract intent
        intent = self.intent_engine.recognize(query.text)
        
        # Step 2: Get knowledge
        solution = self.knowledge_base.get_solution(intent.type)
        
        # Step 3: Build response text
        response_text = self._build_response_text(intent, solution, query.text)
        
        # Step 4: Apply personality
        if query.personality:
            style = PersonalityStyle(query.personality)
        else:
            style = self.personality_system.current_style
            
        final_text = self.personality_system.adapt_response(
            response_text, 
            query.text,
            style
        )
        
        # Step 5: Build command if needed
        command = None
        requires_confirmation = False
        
        if solution['found']:
            # Build command
            action_map = {
                'install': 'install',
                'remove': 'remove',
                'update': 'update',
                'search': 'search',
                'rollback': 'rollback',
                'info': 'list'
            }
            
            action = action_map.get(intent.type.value)
            if action:
                # Some commands don't need a target (update, rollback, list)
                if intent.target or action in ['update', 'rollback', 'list']:
                    command = self.execution_engine.build_command(action, intent.target)
                
                # Determine if confirmation needed
                if action in ['remove', 'update', 'rollback']:
                    requires_confirmation = True
                    
        # Create plan
        plan = Plan(
            text=final_text,
            intent=intent,
            command=command,
            suggestions=self._get_suggestions(intent, solution),
            confidence=intent.confidence,
            requires_confirmation=requires_confirmation
        )
        
        return plan
        
    def execute_plan(self, plan: Plan, user_id: Optional[str] = None) -> ExecutionResult:
        """
        Execute a previously created plan.
        Returns the result of execution.
        """
        
        if not plan.command:
            return ExecutionResult(
                success=True,
                output="No action needed for this query."
            )
            
        # Execute the command
        result = self.execution_engine.execute(plan.command, ExecutionMode.EXECUTE)
        
        # Create execution result
        exec_result = ExecutionResult(
            success=result['success'],
            output=result.get('output', ''),
            error=result.get('error', ''),
            exit_code=result.get('exit_code', 0)
        )
        
        # Record for learning if enabled
        if self.enable_learning and user_id:
            interaction = Interaction(
                query=plan.intent.metadata.get('original_input', ''),
                intent=plan.intent.type.value,
                response=plan.text,
                success=exec_result.success,
                user_id=user_id
            )
            self.learning_system.record_interaction(interaction)
            
        return exec_result
        
    def process(self, query: Query) -> Response:
        """
        Main processing pipeline for queries.
        Convenience method that plans and optionally executes.
        This maintains backward compatibility.
        """
        
        start_time = time.time()
        
        # Create plan
        plan = self.plan(query)
        
        # Execute if requested
        executed = False
        success = None
        execution_output = None
        
        if plan.command and query.mode == ExecutionMode.EXECUTE:
            exec_result = self.execute_plan(plan, query.user_id)
            executed = True
            success = exec_result.success
            
            # Add execution results to response text
            if exec_result.success:
                execution_output = "\n\n✅ Command executed successfully!"
            else:
                execution_output = f"\n\n❌ Command failed: {exec_result.error}"
                
        # Build final response text
        final_text = plan.text
        if execution_output:
            final_text += execution_output
            
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build response (for backward compatibility)
        response = Response(
            text=final_text,
            intent=plan.intent,
            command=plan.command,
            executed=executed,
            success=success,
            suggestions=plan.suggestions,
            confidence=plan.confidence,
            feedback_requested=self.collect_feedback and query.personality == 'symbiotic',
            processing_time_ms=processing_time
        )
        
        return response
        
    def _build_response_text(self, intent: Intent, solution: Dict, query: str) -> str:
        """Build base response text from intent and solution"""
        
        if not solution['found']:
            return solution['suggestion']
            
        # Special handling for different intents
        if intent.type.value == 'install' and intent.target:
            methods = self.knowledge_base.get_install_methods(intent.target)
            response = f"I'll help you install {intent.target}! Here are your options:\n\n"
            
            for i, method in enumerate(methods, 1):
                response += f"{i}. **{method['name']}** - {method['description']}\n"
                response += f"   ```\n   {method['example']}\n   ```\n\n"
                
            response += f"\n💡 {solution['explanation']}"
            return response
            
        elif intent.type.value == 'search' and intent.target:
            # Perform search
            success, results, error = self.execution_engine.execute_safe_search(intent.target)
            
            if success and results:
                response = f"Found {len(results)} packages matching '{intent.target}':\n\n"
                for pkg in results[:5]:  # Show top 5
                    response += f"• **{pkg['name']}** ({pkg['version']})\n"
                    response += f"  {pkg['description']}\n\n"
                return response
            else:
                return f"No packages found matching '{intent.target}'. Try a different search term."
                
        else:
            # Generic response
            response = solution['solution']
            if solution.get('example'):
                response += f"\n\nExample:\n```\n{solution['example']}\n```"
            if solution.get('explanation'):
                response += f"\n\n💡 {solution['explanation']}"
            return response
            
    def _get_suggestions(self, intent: Intent, solution: Dict) -> list[str]:
        """Get relevant suggestions based on intent"""
        
        suggestions = []
        
        # Add related commands
        if solution.get('related'):
            for related in solution['related']:
                if related:
                    suggestions.append(f"Try: {related}")
                    
        # Add intent-specific suggestions
        if intent.type.value == 'install':
            suggestions.extend([
                "Search first if unsure: 'search <name>'",
                "Remove with: 'remove <package>'"
            ])
        elif intent.type.value == 'update':
            suggestions.extend([
                "Check generations: 'show generations'",
                "Rollback if needed: 'rollback'"
            ])
            
        return suggestions[:3]  # Limit to 3 suggestions
        
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get learned preferences for a user"""
        if self.enable_learning:
            return self.learning_system.get_user_preferences(user_id)
        return {}
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = {
            'personality': self.personality_system.current_style.value,
            'dry_run_mode': self.execution_engine.dry_run,
            'learning_enabled': self.enable_learning,
            'feedback_enabled': self.collect_feedback
        }
        
        if self.enable_learning:
            stats['learning_stats'] = self.learning_system.get_feedback_summary()
            
        return stats