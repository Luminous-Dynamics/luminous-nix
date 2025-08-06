"""
Consciousness-first test backend that provides real behavior with deterministic outcomes.

This backend uses the real NLP engine for authentic language understanding while
providing predictable execution results for reliable testing.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.nix_for_humanity.backend.core_engine import CoreEngine
from src.nix_for_humanity.core.interface import (
    Query, Response, Intent, IntentType, ExecutionResult,
    ExecutionMode, Config, Context
)
from src.nix_for_humanity.nlp.nlp_engine import NLPEngine
from src.nix_for_humanity.core.types import Command
from src.nix_for_humanity.core.planning import Plan


@dataclass
class InteractionMemory:
    """Stores interaction history for learning simulation."""
    query: Query
    intent: Intent
    response: Response
    timestamp: datetime = field(default_factory=datetime.now)
    persona_state: Dict[str, Any] = field(default_factory=dict)


class ConsciousnessTestBackend(CoreEngine):
    """
    A consciousness-first test backend that learns and adapts like the real one.
    
    This backend provides:
    - Real NLP processing for authentic language understanding
    - Deterministic execution results for reliable testing
    - Simulated learning and adaptation
    - Persona-aware responses
    """
    
    def __init__(self, persona: str = "test_user", test_mode: bool = True):
        """Initialize with minimal dependencies for fast tests."""
        # Initialize parent with test mode
        self.test_mode = test_mode
        self.config = Config(test_mode=True)
        
        # Initialize components we need
        self.nlp_engine = NLPEngine(config=self.config)
        self.persona = persona
        self.interaction_memory: List[InteractionMemory] = []
        self.learning_enabled = True
        self.learned_patterns: Dict[str, Dict[str, Any]] = {
            persona: {}
        }
        
        # Deterministic test data
        self.test_packages = {
            "firefox": {"type": "browser", "description": "Web browser"},
            "chrome": {"type": "browser", "description": "Google Chrome"},
            "vim": {"type": "editor", "description": "Text editor"},
            "neovim": {"type": "editor", "description": "Modern Vim"},
            "python": {"type": "language", "description": "Python interpreter"},
        }
        
        # Simulated system state
        self.installed_packages = set()
        self.system_generations = [1, 2, 3]  # Simulated NixOS generations
        
        # Context tracking
        self.context = Context()
        self.conversation_depth = 0
    
    async def process_query(self, query: Query) -> Response:
        """Process with real NLP but predictable outcomes."""
        self.conversation_depth += 1
        
        # Use the REAL NLP engine for authentic behavior
        intent = await self.nlp_engine.extract_intent(query.text)
        
        # Track the interaction
        memory = InteractionMemory(
            query=query,
            intent=intent,
            response=None,  # Will be set below
            persona_state=self._get_persona_state()
        )
        
        # Create response based on intent type
        if intent.type == IntentType.INSTALL:
            response = await self._create_test_install_response(intent, query)
        elif intent.type == IntentType.SEARCH:
            response = await self._create_test_search_response(intent, query)
        elif intent.type == IntentType.UPDATE:
            response = await self._create_test_update_response(intent, query)
        elif intent.type == IntentType.EXPLAIN:
            response = await self._create_test_explain_response(intent, query)
        else:
            response = await self._create_test_unknown_response(intent, query)
        
        # Complete memory record
        memory.response = response
        
        # Real learning still happens
        if self.learning_enabled:
            self.interaction_memory.append(memory)
            self._simulate_learning(memory)
        
        return response
    
    async def _create_test_install_response(self, intent: Intent, query: Query) -> Response:
        """Create deterministic install response."""
        package = intent.target or self._extract_package_name(query.text)
        
        if package and package in self.test_packages:
            # Simulate installation
            self.installed_packages.add(package)
            
            # Persona-aware response
            if self.persona == "grandma_rose":
                natural_response = f"I'll install {package.title()} for you! It's a {self.test_packages[package]['description']}. This will just take a moment..."
            elif self.persona == "maya_adhd":
                natural_response = f"Installing {package}..."
            else:
                natural_response = f"Installing {package} ({self.test_packages[package]['description']})"
            
            return Response(
                query_id=query.id,
                intent=intent,
                natural_response=natural_response,
                command=Command(
                    nix_command=f"nix-env -iA nixos.{package}",
                    description=f"Install {package}",
                    requires_sudo=False
                ),
                execution_result=ExecutionResult(
                    success=True,
                    output=f"Package {package} installed successfully",
                    exit_code=0
                ),
                success=True,
                confidence=0.95
            )
        else:
            return Response(
                query_id=query.id,
                intent=intent,
                natural_response=f"I couldn't find a package called '{package or 'that'}'. Would you like me to search for similar packages?",
                success=False,
                confidence=0.3
            )
    
    async def _create_test_search_response(self, intent: Intent, query: Query) -> Response:
        """Create deterministic search response."""
        search_term = intent.target or self._extract_search_term(query.text)
        
        # Find matching packages
        matches = [
            (name, info) for name, info in self.test_packages.items()
            if search_term and (search_term in name or search_term in info['type'])
        ]
        
        if matches:
            suggestions = "\n".join([f"- {name}: {info['description']}" for name, info in matches])
            natural_response = f"I found these packages:\n{suggestions}"
        else:
            natural_response = f"No packages found matching '{search_term}'"
        
        return Response(
            query_id=query.id,
            intent=intent,
            natural_response=natural_response,
            suggestions=[name for name, _ in matches],
            success=bool(matches),
            confidence=0.9
        )
    
    async def _create_test_update_response(self, intent: Intent, query: Query) -> Response:
        """Create deterministic update response."""
        return Response(
            query_id=query.id,
            intent=intent,
            natural_response="System is up to date! No updates available.",
            command=Command(
                nix_command="sudo nixos-rebuild switch",
                description="Update NixOS system",
                requires_sudo=True
            ),
            execution_result=ExecutionResult(
                success=True,
                output="System updated successfully",
                exit_code=0
            ),
            success=True,
            confidence=0.95
        )
    
    async def _create_test_explain_response(self, intent: Intent, query: Query) -> Response:
        """Create test explanation response."""
        topic = intent.target or "NixOS"
        
        explanations = {
            "generations": "NixOS generations are snapshots of your system configuration. You can roll back to any previous generation if something goes wrong.",
            "firefox": "Firefox is a free and open-source web browser. It's known for privacy features and customization options.",
            "nix": "Nix is a purely functional package manager that ensures reproducible builds and installations."
        }
        
        explanation = explanations.get(topic.lower(), f"Let me explain {topic} for you...")
        
        return Response(
            query_id=query.id,
            intent=intent,
            natural_response=explanation,
            success=True,
            confidence=0.85
        )
    
    async def _create_test_unknown_response(self, intent: Intent, query: Query) -> Response:
        """Create response for unknown intents."""
        return Response(
            query_id=query.id,
            intent=intent,
            natural_response="I'm not sure what you'd like to do. Could you rephrase that?",
            suggestions=["install <package>", "search <term>", "update system", "explain <topic>"],
            success=False,
            confidence=0.2
        )
    
    def _extract_package_name(self, text: str) -> Optional[str]:
        """Extract package name from query text."""
        words = text.lower().split()
        for word in words:
            if word in self.test_packages:
                return word
        return None
    
    def _extract_search_term(self, text: str) -> Optional[str]:
        """Extract search term from query text."""
        # Simple extraction - in real implementation this would be smarter
        keywords = ["search", "find", "look for"]
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                return words[i + 1]
        
        return words[-1] if words else None
    
    def _get_persona_state(self) -> Dict[str, Any]:
        """Get current state for the persona."""
        return {
            "conversation_depth": self.conversation_depth,
            "packages_installed": len(self.installed_packages),
            "learning_interactions": len(self.interaction_memory),
            "context_switches": 0,  # Could track topic changes
            "time_in_session": 0,  # Could track session duration
        }
    
    def _simulate_learning(self, memory: InteractionMemory):
        """Simulate learning from the interaction."""
        # Learn vocabulary patterns
        if memory.intent.type == IntentType.INSTALL and memory.response.success:
            # User successfully installed something
            words_used = memory.query.text.lower().split()
            if "need" in words_used or "want" in words_used:
                self.learned_patterns[self.persona]["prefers_natural_language"] = True
            if len(words_used) <= 3:
                self.learned_patterns[self.persona]["prefers_brief_commands"] = True
        
        # Learn from corrections
        if not memory.response.success and memory.intent.confidence < 0.5:
            self.learned_patterns[self.persona]["needs_clarification_often"] = True
        
        # Persona-specific learning
        if self.persona == "grandma_rose":
            if "please" in memory.query.text.lower() or "thank" in memory.query.text.lower():
                self.learned_patterns[self.persona]["polite_user"] = True
            self.learned_patterns[self.persona]["prefers_simple"] = True
        
        elif self.persona == "maya_adhd":
            if len(memory.query.text) < 20:
                self.learned_patterns[self.persona]["prefers_brief"] = True
            if memory.persona_state["conversation_depth"] == 1:
                self.learned_patterns[self.persona]["gets_to_point_quickly"] = True
    
    def has_learned_pattern(self, pattern_name: str) -> bool:
        """Check if a specific pattern has been learned."""
        return pattern_name in self.learned_patterns.get(self.persona, {})
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of what the system has learned."""
        return {
            "persona": self.persona,
            "interactions": len(self.interaction_memory),
            "learned_patterns": self.learned_patterns[self.persona],
            "successful_installs": len(self.installed_packages),
            "conversation_depth": self.conversation_depth,
        }
    
    def reset_learning(self):
        """Reset learning state for fresh test runs."""
        self.interaction_memory.clear()
        self.learned_patterns[self.persona].clear()
        self.conversation_depth = 0
    
    @property
    def understanding_depth(self) -> float:
        """Measure how well the system understands the user."""
        if not self.interaction_memory:
            return 0.0
        
        # Calculate based on successful interactions and patterns learned
        success_rate = sum(1 for m in self.interaction_memory if m.response.success) / len(self.interaction_memory)
        pattern_count = len(self.learned_patterns[self.persona])
        
        # Weighted score
        return (success_rate * 0.7) + (min(pattern_count / 5, 1.0) * 0.3)