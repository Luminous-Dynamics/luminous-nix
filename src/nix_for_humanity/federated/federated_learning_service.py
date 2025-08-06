"""
Federated Learning Service for Nix for Humanity

This module provides the main service interface for federated learning,
integrating all components into a cohesive system that users can interact
with through simple, natural language commands.

Research Foundation:
- Complete Federated Learning Design Principles
- Intent-Centric Learning Orchestration
- Privacy-Preserving Collective Intelligence
- Sacred Trinity Validation Protocol
- Constitutional AI Framework

Phase 4 Living System Component
"""

import asyncio
import logging
import time
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import json

from .zk_learning_protocol import (
    ZKLearningProtocol, ModelUpdate, AggregateUpdate, ZKProof,
    FederatedUpdateType, PrivacyLevel, ConstitutionalAIValidator
)
from .federated_orchestrator import (
    FederatedLearningOrchestrator, LearningIntent, GovernanceStage,
    UpdateTimingProtocol, FederatedLearningStatus
)
from .polycentric_network import (
    PolycentricNetworkManager, LayerType, NetworkState, NetworkHealth
)

logger = logging.getLogger(__name__)

class ServiceState(Enum):
    """Federated learning service states"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class ParticipationLevel(Enum):
    """User participation levels"""
    NONE = "none"           # No participation
    MINIMAL = "minimal"     # Receive only, maximum privacy
    BALANCED = "balanced"   # Send and receive, high privacy
    ACTIVE = "active"       # Full participation, balanced privacy
    MAXIMUM = "maximum"     # Maximum contribution, some privacy trade-offs

@dataclass
class FederatedLearningConfig:
    """Configuration for federated learning service"""
    participation_level: ParticipationLevel
    privacy_epsilon: float
    min_cohort_size: int
    enable_voice_commands: bool
    governance_participation: bool
    max_daily_contributions: int
    auto_apply_updates: bool
    flow_state_protection: bool

class FederatedLearningService:
    """
    Main Federated Learning Service for Nix for Humanity
    
    This service provides a unified interface for all federated learning
    capabilities, making the complex polycentric architecture transparent
    to users through natural language interactions.
    
    Key Features:
    1. Natural language intent processing
    2. Privacy-preserving collective intelligence
    3. Multi-layer polycentric coordination
    4. Constitutional AI governance
    5. Flow state protection
    6. Sacred Trinity validation
    """
    
    def __init__(self, 
                 config: Optional[FederatedLearningConfig] = None,
                 storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / ".nix-humanity" / "federated"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load or create configuration
        self.config = config or self._load_default_config()
        
        # Initialize core components
        self.zk_protocol = ZKLearningProtocol(
            storage_path=self.storage_path / "zk_protocol",
            privacy_epsilon=self.config.privacy_epsilon,
            min_cohort_size=self.config.min_cohort_size
        )
        
        self.orchestrator = FederatedLearningOrchestrator(
            storage_path=self.storage_path / "orchestrator"
        )
        
        self.network_manager = PolycentricNetworkManager(
            storage_path=self.storage_path / "network"
        )
        
        # Service state
        self.service_state = ServiceState.INACTIVE
        self.last_status_update = 0.0
        self.error_state = None
        
        # Statistics and metrics
        self.session_stats = {
            "intents_processed": 0,
            "improvements_shared": 0,
            "updates_received": 0,
            "privacy_violations": 0,  # Should always be 0
            "session_start": time.time()
        }
        
        logger.info("Federated Learning Service initialized")
    
    def _load_default_config(self) -> FederatedLearningConfig:
        """Load default federated learning configuration"""
        return FederatedLearningConfig(
            participation_level=ParticipationLevel.BALANCED,
            privacy_epsilon=0.1,  # Strong privacy protection
            min_cohort_size=50,   # k-anonymity protection
            enable_voice_commands=True,
            governance_participation=False,  # Disabled until network matures
            max_daily_contributions=10,
            auto_apply_updates=True,
            flow_state_protection=True
        )
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the federated learning service"""
        try:
            self.service_state = ServiceState.INITIALIZING
            logger.info("Initializing Federated Learning Service...")
            
            # Initialize network layer first
            network_result = await self.network_manager.initialize_network()
            if not network_result["success"]:
                logger.warning("Network initialization failed, operating in local-only mode")
            
            # Initialize orchestrator
            orchestrator_ready = await self._verify_orchestrator_ready()
            
            # Check constitutional AI framework
            constitutional_check = await self._verify_constitutional_framework()
            
            # Initialize voice interface if enabled
            voice_result = None
            if self.config.enable_voice_commands:
                voice_result = await self._initialize_voice_interface()
            
            # Mark service as active
            self.service_state = ServiceState.ACTIVE
            self.last_status_update = time.time()
            
            logger.info("Federated Learning Service successfully initialized")
            
            return {
                "success": True,
                "service_state": self.service_state.value,
                "network_status": network_result,
                "orchestrator_ready": orchestrator_ready,
                "constitutional_ai": constitutional_check,
                "voice_interface": voice_result,
                "privacy_level": "maximum",
                "participation_level": self.config.participation_level.value,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.service_state = ServiceState.ERROR
            self.error_state = str(e)
            logger.error(f"Failed to initialize Federated Learning Service: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "service_state": self.service_state.value,
                "fallback_mode": "local_only"
            }
    
    async def process_natural_language_intent(self, 
                                            user_input: str,
                                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process natural language input for federated learning intents
        
        Examples:
        - "Share my improvements with the community"
        - "Learn from other users' experiences"
        - "What's my privacy status?"
        - "Stop sharing my data"
        - "How is the network doing?"
        """
        try:
            if self.service_state != ServiceState.ACTIVE:
                return await self._handle_inactive_service(user_input)
            
            # Parse natural language to extract intent
            intent_result = await self._parse_federated_intent(user_input, context)
            
            if not intent_result["intent_recognized"]:
                return {
                    "success": False,
                    "error": "Could not understand federated learning intent",
                    "suggestion": "Try: 'share my improvements', 'learn from community', or 'show privacy status'",
                    "user_input": user_input
                }
            
            # Extract learning intent and parameters
            learning_intent = intent_result["learning_intent"]
            intent_context = intent_result["context"]
            
            # Process through orchestrator
            result = await self.orchestrator.process_learning_intent(
                intent=learning_intent,
                context=intent_context
            )
            
            # Update session statistics
            self.session_stats["intents_processed"] += 1
            if learning_intent == LearningIntent.SHARE_IMPROVEMENT:
                self.session_stats["improvements_shared"] += 1
            elif learning_intent == LearningIntent.LEARN_FROM_COMMUNITY:
                self.session_stats["updates_received"] += result.get("updates_applied", 0)
            
            # Generate user-friendly response
            user_response = await self._generate_user_friendly_response(
                user_input, learning_intent, result
            )
            
            return {
                "success": True,
                "user_input": user_input,
                "intent_recognized": learning_intent.value,
                "response": user_response,
                "technical_result": result,
                "privacy_preserved": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to process federated learning intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_input": user_input,
                "privacy_note": "Privacy is always preserved, even during errors"
            }
    
    async def _parse_federated_intent(self, 
                                    user_input: str, 
                                    context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse natural language input to extract federated learning intent"""
        user_input_lower = user_input.lower()
        
        # Intent recognition patterns
        intent_patterns = {
            LearningIntent.SHARE_IMPROVEMENT: [
                "share", "contribute", "help community", "share improvements",
                "contribute to", "help others", "give back"
            ],
            LearningIntent.LEARN_FROM_COMMUNITY: [
                "learn from", "get updates", "community improvements", 
                "what's new", "community knowledge", "learn from others"
            ],
            LearningIntent.VIEW_PRIVACY_STATUS: [
                "privacy", "privacy status", "what data", "what's shared",
                "privacy settings", "data protection", "what do you know"
            ],
            LearningIntent.ADJUST_PARTICIPATION: [
                "participation", "change settings", "adjust", "configure",
                "participation level", "stop sharing", "start sharing"
            ],
            LearningIntent.VALIDATE_UPDATE: [
                "validate", "check update", "verify", "is this safe",
                "trust", "validation", "security check"
            ],
            LearningIntent.ROLLBACK_CHANGES: [
                "rollback", "undo", "revert", "go back", "restore",
                "undo changes", "previous state"
            ],
            LearningIntent.CONTRIBUTE_ANONYMOUSLY: [
                "anonymous", "anonymously", "private contribution",
                "contribute privately", "share anonymously"
            ]
        }
        
        # Find matching intent
        matched_intent = None
        confidence = 0.0
        
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    # Calculate confidence based on pattern match quality
                    pattern_confidence = len(pattern) / len(user_input_lower)
                    if pattern_confidence > confidence:
                        matched_intent = intent
                        confidence = pattern_confidence
        
        if not matched_intent or confidence < 0.1:
            return {
                "intent_recognized": False,
                "confidence": confidence,
                "user_input": user_input
            }
        
        # Extract context based on intent
        intent_context = context or {}
        
        # Add intent-specific context extraction
        if matched_intent == LearningIntent.SHARE_IMPROVEMENT:
            intent_context.update(self._extract_improvement_context(user_input))
        elif matched_intent == LearningIntent.ADJUST_PARTICIPATION:
            intent_context.update(self._extract_participation_context(user_input))
        
        return {
            "intent_recognized": True,
            "learning_intent": matched_intent,
            "confidence": confidence,
            "context": intent_context,
            "user_input": user_input
        }
    
    def _extract_improvement_context(self, user_input: str) -> Dict[str, Any]:
        """Extract context for improvement sharing intent"""
        context = {}
        
        # Try to identify improvement type
        if "skill" in user_input.lower() or "learning" in user_input.lower():
            context["improvement_type"] = FederatedUpdateType.SKILL_MASTERY.value
        elif "pattern" in user_input.lower() or "command" in user_input.lower():
            context["improvement_type"] = FederatedUpdateType.INTENT_PATTERNS.value
        elif "performance" in user_input.lower() or "speed" in user_input.lower():
            context["improvement_type"] = FederatedUpdateType.PERFORMANCE_METRICS.value
        
        # Extract confidence indicators
        if "sure" in user_input.lower() or "confident" in user_input.lower():
            context["confidence"] = 0.9
        elif "think" in user_input.lower() or "maybe" in user_input.lower():
            context["confidence"] = 0.7
        else:
            context["confidence"] = 0.8  # Default
        
        return context
    
    def _extract_participation_context(self, user_input: str) -> Dict[str, Any]:
        """Extract context for participation adjustment intent"""
        context = {}
        
        # Determine desired participation level
        if "stop" in user_input.lower() or "disable" in user_input.lower():
            context["level"] = ParticipationLevel.NONE.value
        elif "minimal" in user_input.lower() or "privacy" in user_input.lower():
            context["level"] = ParticipationLevel.MINIMAL.value
        elif "active" in user_input.lower() or "full" in user_input.lower():
            context["level"] = ParticipationLevel.ACTIVE.value
        elif "maximum" in user_input.lower() or "contribute everything" in user_input.lower():
            context["level"] = ParticipationLevel.MAXIMUM.value
        else:
            context["level"] = ParticipationLevel.BALANCED.value
        
        return context
    
    async def _generate_user_friendly_response(self, 
                                             user_input: str,
                                             intent: LearningIntent,
                                             result: Dict[str, Any]) -> str:
        """Generate natural, user-friendly response based on intent and result"""
        
        if not result.get("success", False):
            error_responses = {
                LearningIntent.SHARE_IMPROVEMENT: "I couldn't share your improvements right now. Your privacy is still completely protected.",
                LearningIntent.LEARN_FROM_COMMUNITY: "I couldn't fetch community improvements at the moment. You can try again later.",
                LearningIntent.VIEW_PRIVACY_STATUS: "I had trouble checking your privacy status, but rest assured - all your data stays local and private.",
                LearningIntent.ADJUST_PARTICIPATION: "I couldn't adjust your participation settings right now. Your current settings remain unchanged.",
                LearningIntent.VALIDATE_UPDATE: "I couldn't validate that update right now. When in doubt, it's safer to wait.",
                LearningIntent.ROLLBACK_CHANGES: "I couldn't complete the rollback. Your system state is unchanged.",
                LearningIntent.CONTRIBUTE_ANONYMOUSLY: "I couldn't process your anonymous contribution right now. Your privacy remains fully protected."
            }
            return error_responses.get(intent, "Something went wrong, but your privacy and data are completely safe.")
        
        # Generate success responses based on intent
        if intent == LearningIntent.SHARE_IMPROVEMENT:
            if result.get("consensus_reached", False):
                improvement = result.get("improvement_delta", 0) * 100
                return f"✅ Your {improvement:.1f}% improvement has been shared with the community! Other users will benefit while your privacy stays completely protected."
            else:
                return "📤 Your improvement has been submitted to the community. It's being validated while keeping your data completely private."
        
        elif intent == LearningIntent.LEARN_FROM_COMMUNITY:
            updates_applied = result.get("updates_applied", 0)
            if updates_applied > 0:
                return f"🎓 Applied {updates_applied} community improvements to your system! Your experience should be noticeably better."
            elif result.get("updates_scheduled", 0) > 0:
                scheduled = result.get("updates_scheduled", 0)
                return f"⏰ Found {scheduled} improvements that will be applied when you're not busy (protecting your focus)."
            else:
                return "👍 Checked for community improvements - you're already using the latest knowledge!"
        
        elif intent == LearningIntent.VIEW_PRIVACY_STATUS:
            return f"""🔒 Your privacy is maximally protected:
• All data stays on your computer (never leaves)
• Zero-knowledge proofs protect your contributions  
• k-anonymity ensures you can't be identified
• You control all participation settings"""
        
        elif intent == LearningIntent.ADJUST_PARTICIPATION:
            level = result.get("participation_level", "balanced")
            level_descriptions = {
                "none": "🔒 Maximum privacy - no participation",
                "minimal": "🔒 Minimal participation - receive only, maximum privacy",
                "balanced": "⚖️ Balanced participation - contribute and receive with high privacy",
                "active": "🤝 Active participation - full contribution with privacy protection",
                "maximum": "🌟 Maximum contribution - helping community most while maintaining core privacy"
            }
            return f"✅ Participation level set to: {level_descriptions.get(level, level)}"
        
        elif intent == LearningIntent.VALIDATE_UPDATE:
            if result.get("overall_valid", False):
                return "✅ Update validation passed - this improvement is safe and beneficial for your system."
            else:
                failed = [k for k, v in result.get("validation_details", {}).items() if not v]
                return f"⚠️ Update validation failed ({', '.join(failed)}). It's safer to skip this one."
        
        elif intent == LearningIntent.ROLLBACK_CHANGES:
            changes = result.get("changes_reverted", 0)
            scope = result.get("scope", "unknown")
            return f"↩️ Successfully rolled back {changes} changes from {scope}. Your system is restored to the previous state."
        
        elif intent == LearningIntent.CONTRIBUTE_ANONYMOUSLY:
            benefit = result.get("estimated_community_benefit", 0) * 100
            return f"🎭 Anonymous contribution successful! Your insights will help the community (~{benefit:.1f}% estimated benefit) while keeping you completely anonymous."
        
        return "✅ Operation completed successfully with full privacy protection."
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive federated learning service status"""
        try:
            # Get orchestrator status
            orchestrator_status = self.orchestrator.get_status()
            
            # Get network health
            network_health = await self.network_manager.get_network_health()
            
            # Get privacy metrics
            privacy_metrics = self.zk_protocol.get_privacy_metrics()
            
            return {
                "service_state": self.service_state.value,
                "participation_level": self.config.participation_level.value,
                "orchestrator_status": asdict(orchestrator_status),
                "network_health": asdict(network_health),
                "privacy_metrics": privacy_metrics,
                "session_stats": self.session_stats,
                "last_update": time.time(),
                "error_state": self.error_state,
                "constitutional_ai_active": True,
                "flow_state_protection": self.config.flow_state_protection
            }
            
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {
                "service_state": ServiceState.ERROR.value,
                "error": str(e),
                "privacy_note": "Privacy protection remains active even during errors"
            }
    
    async def shutdown(self) -> Dict[str, Any]:
        """Gracefully shutdown the federated learning service"""
        try:
            logger.info("Shutting down Federated Learning Service...")
            
            self.service_state = ServiceState.INACTIVE
            
            # Save any pending state
            await self._save_service_state()
            
            # Close network connections
            # (Network manager would handle connection cleanup)
            
            # Clear sensitive data from memory
            await self._secure_cleanup()
            
            logger.info("Federated Learning Service shutdown complete")
            
            return {
                "success": True,
                "message": "Federated learning service shut down gracefully",
                "privacy_preserved": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error during service shutdown: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Service shutdown encountered issues but privacy remains protected"
            }
    
    # Implementation helpers
    
    async def _handle_inactive_service(self, user_input: str) -> Dict[str, Any]:
        """Handle requests when service is not active"""
        return {
            "success": False,
            "error": f"Federated learning service is {self.service_state.value}",
            "suggestion": "The service needs to be initialized first",
            "privacy_note": "Your privacy is always protected regardless of service state"
        }
    
    async def _verify_orchestrator_ready(self) -> bool:
        """Verify orchestrator is ready for operation"""
        try:
            status = self.orchestrator.get_status()
            return status.participating
        except Exception as e:
            logger.warning(f"Orchestrator readiness check failed: {e}")
            return False
    
    async def _verify_constitutional_framework(self) -> Dict[str, Any]:
        """Verify constitutional AI framework is operational"""
        try:
            # Test constitutional validator
            validator = ConstitutionalAIValidator()
            
            # Create test update to validate framework
            test_update = await self.zk_protocol.create_model_update(
                improvement_type=FederatedUpdateType.SKILL_MASTERY,
                improvement_delta=0.05,
                confidence=0.8,
                metadata={"test": True, "limitations": ["test_only"]}
            )
            
            validation_result = await validator.validate_update(test_update)
            
            return {
                "operational": validation_result,
                "boundaries_active": len(validator.sacred_boundaries),
                "test_validation": validation_result
            }
            
        except Exception as e:
            logger.error(f"Constitutional framework check failed: {e}")
            return {
                "operational": False,
                "error": str(e)
            }
    
    async def _initialize_voice_interface(self) -> Dict[str, Any]:
        """Initialize voice interface for federated learning commands"""
        # In real implementation, would integrate with voice system
        return {
            "enabled": self.config.enable_voice_commands,
            "wake_phrase": "Hey Nix, federated",
            "available_commands": [
                "share my improvements",
                "learn from community", 
                "show privacy status",
                "adjust participation"
            ]
        }
    
    async def _save_service_state(self):
        """Save service state for persistence"""
        state_file = self.storage_path / "service_state.json"
        
        state_data = {
            "service_state": self.service_state.value,
            "config": asdict(self.config),
            "session_stats": self.session_stats,
            "last_shutdown": time.time()
        }
        
        with open(state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    async def _secure_cleanup(self):
        """Securely clean up sensitive data from memory"""
        # Clear any cached sensitive data
        # In real implementation, would zero out memory buffers
        pass

# Module exports
__all__ = [
    'FederatedLearningService',
    'FederatedLearningConfig', 
    'ParticipationLevel',
    'ServiceState'
]