"""
Voice Interface with Environmental Awareness Integration.

This combines voice control with system monitoring for intelligent,
context-aware voice assistance.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum

from luminous_nix.interfaces.voice import (
    VoiceInterface,
    VoiceConfig,
    VoiceState
)
from luminous_nix.service_with_awareness import AwareNixService
from luminous_nix.environmental import (
    get_system_monitor,
    PredictiveAssistant
)

logger = logging.getLogger(__name__)


class AwareVoiceMode(Enum):
    """Voice assistant personality modes based on system state"""
    NORMAL = "normal"       # Everything is fine
    CONCERNED = "concerned"  # Some issues detected
    URGENT = "urgent"       # Critical issues need attention
    HELPER = "helper"       # Proactive assistance mode


@dataclass
class AwareVoiceResponse:
    """Enhanced voice response with system context"""
    text: str
    mode: AwareVoiceMode
    alerts: List[str]
    suggestions: List[str]
    system_status: Optional[Dict[str, Any]] = None


class EnvironmentallyAwareVoiceInterface(VoiceInterface):
    """
    Voice interface that understands system context.
    
    Features:
    - Proactive alerts when system needs attention
    - Context-aware responses based on system state
    - Predictive suggestions during conversation
    - Adaptive speech based on urgency
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        super().__init__(config)
        
        # Initialize aware service
        self.service = AwareNixService()
        self.monitor = get_system_monitor()
        self.assistant = PredictiveAssistant(self.monitor)
        
        # Voice personality settings
        self.voice_modes = {
            AwareVoiceMode.NORMAL: {
                'rate': 150,
                'pitch': 100,
                'prefix': ""
            },
            AwareVoiceMode.CONCERNED: {
                'rate': 140,
                'pitch': 95,
                'prefix': "I noticed something: "
            },
            AwareVoiceMode.URGENT: {
                'rate': 160,
                'pitch': 105,
                'prefix': "Attention needed: "
            },
            AwareVoiceMode.HELPER: {
                'rate': 145,
                'pitch': 102,
                'prefix': "I can help with that: "
            }
        }
        
        # Start background monitoring
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background system monitoring"""
        loop = asyncio.new_event_loop()
        asyncio.run_coroutine_threadsafe(
            self.monitor.start_monitoring(),
            loop
        )
    
    def _determine_voice_mode(self) -> AwareVoiceMode:
        """Determine voice mode based on system state"""
        status = self.monitor.get_quick_status()
        
        # Check for critical issues
        if status['memory_percent'] > 90 or any(
            p > 95 for p in status.get('disk_usage', {}).values()
        ):
            return AwareVoiceMode.URGENT
        
        # Check for concerns
        if status['memory_percent'] > 80 or status['cpu_percent'] > 80:
            return AwareVoiceMode.CONCERNED
        
        # Check if we have helpful suggestions
        predictions = self.assistant.analyze_system()
        if predictions and any(p.priority in ['high', 'medium'] for p in predictions):
            return AwareVoiceMode.HELPER
        
        return AwareVoiceMode.NORMAL
    
    def _check_for_proactive_alerts(self) -> List[str]:
        """Check if we should proactively alert the user"""
        alerts = []
        status = self.monitor.get_quick_status()
        
        # Critical memory
        if status['memory_percent'] > 95:
            alerts.append(f"Your memory is critically low at {status['memory_percent']:.0f}%")
        
        # Critical disk
        for mount, percent in status.get('disk_usage', {}).items():
            if percent > 95:
                alerts.append(f"Your {mount} disk is almost full at {percent:.0f}%")
        
        # Failed services
        services = self.monitor.get_state().get('services', [])
        failed = [s for s in services if hasattr(s, 'status') and s.status == 'failed']
        if failed:
            alerts.append(f"{len(failed)} system services have failed")
        
        return alerts
    
    async def process_voice_command(self, text: str) -> AwareVoiceResponse:
        """Process voice command with environmental context"""
        
        # Get current system context
        mode = self._determine_voice_mode()
        alerts = self._check_for_proactive_alerts()
        
        # Process through aware service
        response = await self.service.process_natural_language(text)
        
        # Build suggestions based on context
        suggestions = []
        if response.get('suggestions'):
            suggestions.extend(response['suggestions'][:2])
        
        # Add predictive suggestions if relevant
        if 'slow' in text.lower() or 'problem' in text.lower():
            predictions = self.assistant.analyze_system()
            for pred in predictions[:2]:
                if pred.priority in ['critical', 'high']:
                    suggestions.append(pred.action)
        
        # Format response text
        response_text = response.get('explanation', '')
        
        # Add system context if relevant
        if response.get('system_status'):
            status = response['system_status']
            if status['memory_percent'] > 80:
                response_text += f" Your memory is at {status['memory_percent']:.0f}%. "
            if status['cpu_percent'] > 80:
                response_text += f" CPU usage is {status['cpu_percent']:.0f}%. "
        
        return AwareVoiceResponse(
            text=response_text,
            mode=mode,
            alerts=alerts,
            suggestions=suggestions,
            system_status=response.get('system_status')
        )
    
    def speak_with_awareness(self, response: AwareVoiceResponse):
        """Speak response with appropriate voice settings"""
        mode_settings = self.voice_modes[response.mode]
        
        # Adjust TTS settings
        self.engine.setProperty('rate', mode_settings['rate'])
        
        # Build full text
        full_text = mode_settings['prefix'] + response.text
        
        # Add alerts if urgent
        if response.alerts and response.mode == AwareVoiceMode.URGENT:
            full_text = ". ".join(response.alerts) + ". " + full_text
        
        # Speak
        self.speak(full_text)
        
        # Offer suggestions if any
        if response.suggestions:
            self.speak("Would you like me to " + response.suggestions[0] + "?")
    
    async def continuous_conversation_with_awareness(self):
        """
        Continuous conversation mode with proactive assistance.
        
        The assistant will:
        - Alert you to problems before you ask
        - Provide context-aware responses
        - Suggest optimizations proactively
        """
        
        logger.info("Starting environmentally aware voice assistant")
        
        # Initial greeting with system status
        status = self.monitor.get_quick_status()
        greeting = "Hello! I'm your NixOS assistant. "
        
        if status['memory_percent'] > 80:
            greeting += f"I notice your memory usage is high at {status['memory_percent']:.0f}%. "
        elif status['cpu_percent'] > 80:
            greeting += f"Your CPU is working hard at {status['cpu_percent']:.0f}%. "
        else:
            greeting += "Your system is running smoothly. "
        
        greeting += "How can I help you today?"
        self.speak(greeting)
        
        last_alert_time = 0
        alert_interval = 300  # 5 minutes
        
        while True:
            try:
                # Check for proactive alerts periodically
                import time
                current_time = time.time()
                if current_time - last_alert_time > alert_interval:
                    alerts = self._check_for_proactive_alerts()
                    if alerts:
                        self.speak("Excuse me, I have something important to tell you.")
                        for alert in alerts[:1]:  # Just the most important
                            self.speak(alert)
                        last_alert_time = current_time
                
                # Listen for commands
                text = self.listen()
                if not text:
                    continue
                
                # Check for exit commands
                if any(word in text.lower() for word in ['exit', 'quit', 'goodbye']):
                    # Give final system summary
                    health = self.service.get_system_insights()
                    farewell = f"Goodbye! Your system health score is {health['health_score']}/100. "
                    if health['health_score'] < 70:
                        farewell += "Please address the issues we discussed. "
                    self.speak(farewell + "Take care!")
                    break
                
                # Process with awareness
                response = await self.process_voice_command(text)
                
                # Speak response with appropriate urgency
                self.speak_with_awareness(response)
                
                # Wait a moment
                await asyncio.sleep(0.5)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in conversation: {e}")
                self.speak("I had a small problem, but I'm ready to continue.")
    
    def shutdown(self):
        """Clean shutdown with monitoring cleanup"""
        # Stop monitoring
        asyncio.run_coroutine_threadsafe(
            self.monitor.stop_monitoring(),
            asyncio.get_event_loop()
        )
        
        # Save system snapshot
        self.monitor.save_snapshot()
        
        # Cleanup service
        self.service.shutdown()
        
        # Parent cleanup
        super().stop()


class SmartVoiceAssistant:
    """
    High-level voice assistant with full environmental awareness.
    
    This is the main entry point for voice + awareness integration.
    """
    
    def __init__(self):
        self.config = VoiceConfig(
            wake_word="hey nix",
            confirmation_required=False,  # For smoother conversation
            audio_feedback=True
        )
        self.interface = EnvironmentallyAwareVoiceInterface(self.config)
    
    async def start(self):
        """Start the smart voice assistant"""
        print("🎤 Luminous Nix Smart Voice Assistant")
        print("=" * 50)
        print("I understand your system state and can help proactively!")
        print("Say 'Hey Nix' to wake me, or 'exit' to quit.")
        print()
        
        # Start conversation
        await self.interface.continuous_conversation_with_awareness()
    
    def demo_system_awareness(self):
        """Demonstrate system awareness capabilities"""
        print("\n🔍 Current System Awareness:")
        print("-" * 40)
        
        status = self.interface.monitor.get_quick_status()
        print(f"CPU: {status['cpu_percent']:.1f}%")
        print(f"Memory: {status['memory_percent']:.1f}% ({status['memory_available_gb']:.1f}GB free)")
        
        for mount, percent in status.get('disk_usage', {}).items():
            icon = "🟢" if percent < 80 else "🟡" if percent < 90 else "🔴"
            print(f"Disk {mount}: {percent:.1f}% {icon}")
        
        # Get predictions
        predictions = self.interface.assistant.analyze_system()
        if predictions:
            print("\n🔮 Predictive Suggestions:")
            for pred in predictions[:3]:
                print(f"  • {pred.action} ({pred.priority})")
        
        print("\n✨ I'll consider all of this when responding to you!")


# Convenience function
def create_smart_voice_assistant() -> SmartVoiceAssistant:
    """Create a voice assistant with full environmental awareness"""
    return SmartVoiceAssistant()


# Demo script
async def demo():
    """Demonstrate voice with environmental awareness"""
    assistant = create_smart_voice_assistant()
    
    # Show system awareness
    assistant.demo_system_awareness()
    
    # Start interactive session
    await assistant.start()


if __name__ == "__main__":
    asyncio.run(demo())