"""
Example Implementation - Demonstrating Interface Usage

This file shows how to implement the interfaces with a simple,
minimal backend that can be used for testing or as a starting point.
"""

from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
import asyncio

from .backend_interface import BackendInterface
from .intent_interface import IntentRecognizerInterface
from .executor_interface import ExecutorInterface
from .knowledge_interface import KnowledgeInterface
from .learning_interface import LearningInterface
from .personality_interface import PersonalityInterface

from ..core.types import (
    Request, Response, Intent, IntentType, 
    Command, ExecutionResult, Plan, Package, FeedbackItem
)


class SimpleIntentRecognizer(IntentRecognizerInterface):
    """Simple pattern-based intent recognizer"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.patterns = {
            IntentType.INSTALL: ["install", "add", "get"],
            IntentType.REMOVE: ["remove", "uninstall", "delete"],
            IntentType.UPDATE: ["update", "upgrade"],
            IntentType.SEARCH: ["search", "find", "look for"],
        }
    
    def recognize(self, query: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        query_lower = query.lower()
        
        for intent_type, keywords in self.patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    # Extract package name if present
                    entities = {}
                    words = query_lower.split()
                    if keyword in words:
                        idx = words.index(keyword)
                        if idx + 1 < len(words):
                            entities['package'] = words[idx + 1]
                    
                    return Intent(
                        type=intent_type,
                        entities=entities,
                        confidence=0.9,
                        raw_input=query
                    )
        
        return Intent(
            type=IntentType.UNKNOWN,
            entities={},
            confidence=0.0,
            raw_input=query
        )
    
    def get_supported_intents(self) -> List[IntentType]:
        return list(self.patterns.keys())
    
    def get_confidence_threshold(self) -> float:
        return self.confidence_threshold
    
    def set_confidence_threshold(self, threshold: float) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
        self.confidence_threshold = threshold
    
    def get_entity_extractors(self) -> Dict[str, Any]:
        return {
            "package": "simple word after keyword",
            "version": "not implemented",
        }
    
    def train_on_correction(self, query: str, correct_intent: Intent) -> None:
        # Simple implementation: just log it
        print(f"Learning: '{query}' should be {correct_intent.type}")
    
    def get_debug_info(self, query: str) -> Dict[str, Any]:
        intent = self.recognize(query)
        return {
            "query": query,
            "recognized_intent": intent.type.value,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "matched_patterns": [k for k in self.patterns if any(p in query.lower() for p in self.patterns[k])]
        }


class SimpleExecutor(ExecutorInterface):
    """Simple executor that only simulates"""
    
    def __init__(self):
        self.progress_callback = None
        self.sudo_handler = None
        self.history = []
        self.safety_rules = [
            {
                "name": "no-rm-rf",
                "description": "Prevent dangerous deletions",
                "pattern": r"rm\s+-rf\s+/",
                "severity": "critical"
            }
        ]
    
    def execute(self, plan: Plan, intent: Intent, dry_run: bool = True) -> ExecutionResult:
        start_time = datetime.now()
        
        if self.progress_callback:
            self.progress_callback("Starting execution...", 0.0)
        
        # For this example, we always simulate
        output_lines = [
            f"[DRY RUN] Would execute {len(plan.commands)} commands:",
            ""
        ]
        
        for i, cmd in enumerate(plan.commands):
            output_lines.append(f"{i+1}. {cmd.get('command', 'Unknown command')}")
            if self.progress_callback:
                self.progress_callback(f"Step {i+1}/{len(plan.commands)}", (i+1)/len(plan.commands))
        
        duration = (datetime.now() - start_time).total_seconds()
        
        result = ExecutionResult(
            success=True,
            output="\n".join(output_lines),
            error="",
            exit_code=0,
            duration=duration
        )
        
        # Record in history
        self.history.append({
            "timestamp": datetime.now(),
            "command": plan.commands[0] if plan.commands else {},
            "success": True,
            "dry_run": dry_run,
            "duration": duration
        })
        
        return result
    
    async def execute_async(self, plan: Plan, intent: Intent, dry_run: bool = True) -> ExecutionResult:
        # Simple async wrapper
        await asyncio.sleep(0.1)  # Simulate async work
        return self.execute(plan, intent, dry_run)
    
    def validate_command(self, command: Command) -> tuple[bool, Optional[str]]:
        cmd_str = f"{command.command} {' '.join(command.args)}"
        
        for rule in self.safety_rules:
            import re
            if re.search(rule["pattern"], cmd_str):
                return False, f"Command violates safety rule: {rule['name']}"
        
        return True, None
    
    def set_sudo_handler(self, handler: Callable[[str], bool]) -> None:
        self.sudo_handler = handler
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        self.progress_callback = callback
    
    def get_safety_rules(self) -> List[Dict[str, Any]]:
        return self.safety_rules.copy()
    
    def add_safety_rule(self, rule: Dict[str, Any]) -> None:
        self.safety_rules.append(rule)
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.history[-limit:]
    
    def can_execute_native(self) -> bool:
        return False  # This simple executor doesn't support native API


class SimpleBackend(BackendInterface):
    """Simple backend implementation combining all components"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.intent_recognizer = SimpleIntentRecognizer()
        self.executor = SimpleExecutor()
        self.progress_callback = None
        
        # Set progress callback if provided
        if 'progress_callback' in self.config:
            self.set_progress_callback(self.config['progress_callback'])
    
    def process(self, request: Request) -> Response:
        try:
            # Recognize intent
            intent = self.get_intent(request.query)
            
            # Create a simple plan
            plan = self._create_plan(intent)
            
            # Execute if requested
            result = None
            if request.context.get('execute', False):
                result = self.executor.execute(
                    plan, 
                    intent, 
                    request.context.get('dry_run', True)
                )
            
            # Build response
            return Response(
                success=True,
                text=self.explain(intent),
                intent=intent,
                plan=plan,
                result=result,
                commands=self._extract_commands(plan),
                suggestions=self._get_suggestions(intent),
                explanation=f"I understood you want to {intent.type.value}"
            )
            
        except Exception as e:
            return Response(
                success=False,
                text=f"Error: {str(e)}",
                error=str(e)
            )
    
    async def process_async(self, request: Request) -> Response:
        # Simple async wrapper
        await asyncio.sleep(0.1)
        return self.process(request)
    
    def get_intent(self, query: str) -> Intent:
        return self.intent_recognizer.recognize(query)
    
    def explain(self, intent: Intent) -> str:
        explanations = {
            IntentType.INSTALL: f"I'll help you install {intent.entities.get('package', 'that package')}",
            IntentType.REMOVE: f"I'll help you remove {intent.entities.get('package', 'that package')}",
            IntentType.UPDATE: "I'll help you update your system",
            IntentType.SEARCH: f"I'll search for {intent.entities.get('query', 'packages')}",
            IntentType.UNKNOWN: "I'm not sure what you're asking for"
        }
        return explanations.get(intent.type, "I'll help with that")
    
    def set_progress_callback(self, callback: Callable[[str, float], None]) -> None:
        self.progress_callback = callback
        self.executor.set_progress_callback(callback)
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "native_api": False,
            "learning_enabled": False,
            "personalities": ["minimal"],
            "features": ["dry-run", "basic-intents"],
            "version": "1.0.0-example"
        }
    
    def shutdown(self) -> None:
        # Clean shutdown
        print("SimpleBackend shutting down...")
    
    def _create_plan(self, intent: Intent) -> Plan:
        """Create a simple execution plan"""
        commands = []
        
        if intent.type == IntentType.INSTALL:
            package = intent.entities.get('package', 'unknown')
            commands.append({
                'command': f'nix profile install nixpkgs#{package}',
                'description': f'Install {package}'
            })
        elif intent.type == IntentType.UPDATE:
            commands.append({
                'command': 'sudo nix-channel --update',
                'description': 'Update channels'
            })
            commands.append({
                'command': 'sudo nixos-rebuild switch',
                'description': 'Rebuild system'
            })
        
        return Plan(
            steps=[f"Step {i+1}: {cmd['description']}" for i, cmd in enumerate(commands)],
            commands=commands,
            requires_sudo=any('sudo' in cmd['command'] for cmd in commands),
            is_destructive=False,
            estimated_duration=len(commands) * 5.0
        )
    
    def _extract_commands(self, plan: Plan) -> List[Dict[str, Any]]:
        return plan.commands
    
    def _get_suggestions(self, intent: Intent) -> List[str]:
        suggestions = {
            IntentType.INSTALL: [
                "To make this permanent, add it to configuration.nix",
                "You can search for similar packages with 'search <term>'"
            ],
            IntentType.UPDATE: [
                "Check what changed with 'nixos-rebuild dry-build'",
                "View generations with 'nixos-rebuild list-generations'"
            ],
            IntentType.UNKNOWN: [
                "Try asking about installing packages",
                "Ask me to update your system",
                "Search for packages with 'search <term>'"
            ]
        }
        return suggestions.get(intent.type, [])


# Example usage
if __name__ == "__main__":
    # Create a simple backend
    backend = SimpleBackend()
    
    # Process a request
    request = Request(
        query="install firefox",
        context={
            'personality': 'minimal',
            'execute': True,
            'dry_run': True
        }
    )
    
    response = backend.process(request)
    
    print(f"Success: {response.success}")
    print(f"Response: {response.text}")
    print(f"Intent: {response.intent.type if response.intent else 'None'}")
    print(f"Commands: {response.commands}")
    print(f"Suggestions: {response.suggestions}")