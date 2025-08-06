"""
🎛️ Voice Configuration for Consciousness-First Voice Interface

Configuration system that adapts to each of our 10 personas with specific
accessibility needs, response timing, and interaction patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from enum import Enum
import json
from pathlib import Path


class VoiceProvider(Enum):
    """Available voice synthesis providers."""
    PIPER_TTS = "piper"           # Local, fast, privacy-first
    ESPEAK_NG = "espeak-ng"       # Accessibility standard
    WHISPER_CPP = "whisper-cpp"   # High-quality STT
    VOSK = "vosk"                 # Lightweight STT


class EmotionTone(Enum):
    """Emotional tones for voice synthesis."""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    CALM = "calm"
    EXCITED = "excited"
    PATIENT = "patient"


@dataclass
class PersonaVoiceSettings:
    """Voice settings optimized for each persona's needs."""
    
    # Identity
    persona_name: str
    age: int
    accessibility_needs: List[str] = field(default_factory=list)
    
    # Speech Recognition
    stt_provider: VoiceProvider = VoiceProvider.WHISPER_CPP
    language: str = "en-US"
    vocabulary_context: List[str] = field(default_factory=list)  # Domain-specific words
    noise_tolerance: float = 0.3  # 0.0 = very quiet, 1.0 = very noisy
    
    # Response Timing (crucial for ADHD, elderly users)
    max_response_time_ms: int = 2000  # Max acceptable response delay
    silence_timeout_ms: int = 1500    # How long to wait for user speech
    interruption_allowed: bool = True  # Can AI interrupt user?
    
    # Voice Synthesis  
    tts_provider: VoiceProvider = VoiceProvider.PIPER_TTS
    voice_speed: float = 1.0      # Speech rate multiplier
    voice_pitch: float = 1.0      # Pitch adjustment
    default_emotion: EmotionTone = EmotionTone.FRIENDLY
    
    # Content Adaptation
    explanation_depth: Literal["minimal", "standard", "detailed"] = "standard"
    technical_terms: bool = True   # Use technical vocabulary?
    confirmation_style: Literal["explicit", "implicit", "none"] = "explicit"
    
    # Audio Processing
    volume_normalization: bool = True
    background_noise_suppression: bool = True
    voice_activity_detection: bool = True


@dataclass
class VoiceConfig:
    """Main voice interface configuration."""
    
    # Current active persona
    active_persona: str = "default"
    
    # Audio hardware settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    audio_device_input: Optional[str] = None
    audio_device_output: Optional[str] = None
    
    # Performance settings
    enable_gpu_acceleration: bool = False
    concurrent_processing: bool = True
    cache_models: bool = True
    
    # Privacy settings
    save_audio_history: bool = False
    anonymize_logs: bool = True
    local_processing_only: bool = True
    
    # Interaction behavior
    wake_word_enabled: bool = False
    wake_word: str = "hey nix"
    continuous_listening: bool = False
    
    # Persona configurations
    personas: Dict[str, PersonaVoiceSettings] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize with default persona configurations."""
        if not self.personas:
            self.personas = self._create_default_personas()
    
    def _create_default_personas(self) -> Dict[str, PersonaVoiceSettings]:
        """Create voice settings for all 10 core personas."""
        return {
            # Grandma Rose (75) - Voice-first, zero technical terms
            "grandma_rose": PersonaVoiceSettings(
                persona_name="Grandma Rose",
                age=75,
                accessibility_needs=["large_text", "clear_speech", "patient_responses"],
                stt_provider=VoiceProvider.WHISPER_CPP,  # Most accurate
                language="en-US",
                vocabulary_context=["family", "photos", "internet", "programs"],
                noise_tolerance=0.5,  # May have hearing aids
                max_response_time_ms=3000,  # Extra time is OK
                silence_timeout_ms=3000,    # Don't rush
                interruption_allowed=False,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=0.8,  # Slower speech
                voice_pitch=1.1,  # Slightly higher, clearer
                default_emotion=EmotionTone.PATIENT,
                explanation_depth="detailed",
                technical_terms=False,
                confirmation_style="explicit",
            ),
            
            # Maya (16, ADHD) - Fast, focused, minimal distractions
            "maya_adhd": PersonaVoiceSettings(
                persona_name="Maya",
                age=16,
                accessibility_needs=["fast_responses", "minimal_distractions", "clear_focus"],
                stt_provider=VoiceProvider.VOSK,  # Faster for quick commands
                language="en-US",
                vocabulary_context=["games", "discord", "streaming", "mods"],
                noise_tolerance=0.2,  # Likely in quiet room
                max_response_time_ms=800,   # MUST be fast
                silence_timeout_ms=800,
                interruption_allowed=True,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.3,  # Faster speech
                voice_pitch=1.0,
                default_emotion=EmotionTone.NEUTRAL,
                explanation_depth="minimal",
                technical_terms=True,
                confirmation_style="implicit",
            ),
            
            # David (42, Tired Parent) - Stress-free, reliable
            "david_parent": PersonaVoiceSettings(
                persona_name="David",
                age=42,
                accessibility_needs=["stress_reduction", "reliable_operation", "quick_help"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US", 
                vocabulary_context=["work", "family", "schedule", "productivity"],
                noise_tolerance=0.6,  # Kids in background
                max_response_time_ms=2000,
                silence_timeout_ms=2000,
                interruption_allowed=False,  # Don't add to stress
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.0,
                voice_pitch=0.9,  # Calming lower pitch
                default_emotion=EmotionTone.CALM,
                explanation_depth="standard",
                technical_terms=False,
                confirmation_style="explicit",
            ),
            
            # Dr. Sarah (35, Researcher) - Efficient, precise  
            "dr_sarah": PersonaVoiceSettings(
                persona_name="Dr. Sarah",
                age=35,
                accessibility_needs=["precision", "efficiency", "technical_depth"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["research", "analysis", "data", "computation"],
                noise_tolerance=0.3,
                max_response_time_ms=1500,
                silence_timeout_ms=1000,
                interruption_allowed=True,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.1,
                voice_pitch=1.0,
                default_emotion=EmotionTone.NEUTRAL,
                explanation_depth="detailed",
                technical_terms=True,
                confirmation_style="implicit",
            ),
            
            # Alex (28, Blind Developer) - 100% accessible
            "alex_blind": PersonaVoiceSettings(
                persona_name="Alex",
                age=28,
                accessibility_needs=["screen_reader", "audio_first", "detailed_feedback"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["development", "accessibility", "programming", "unix"],
                noise_tolerance=0.2,
                max_response_time_ms=1000,
                silence_timeout_ms=1200,
                interruption_allowed=True,
                tts_provider=VoiceProvider.ESPEAK_NG,  # Screen reader compatible
                voice_speed=1.4,  # Experienced screen reader users prefer speed
                voice_pitch=1.0,
                default_emotion=EmotionTone.NEUTRAL,
                explanation_depth="detailed",
                technical_terms=True,
                confirmation_style="explicit",
                volume_normalization=True,
                background_noise_suppression=True,
            ),
            
            # Carlos (52, Career Switcher) - Learning support
            "carlos_learner": PersonaVoiceSettings(
                persona_name="Carlos",
                age=52,
                accessibility_needs=["learning_support", "encouragement", "patience"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["learning", "career", "development", "basics"],
                noise_tolerance=0.4,
                max_response_time_ms=2500,
                silence_timeout_ms=2500,
                interruption_allowed=False,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=0.9,
                voice_pitch=1.0,
                default_emotion=EmotionTone.ENCOURAGING,
                explanation_depth="detailed",
                technical_terms=False,
                confirmation_style="explicit",
            ),
            
            # Priya (34, Single Mom) - Quick, context-aware
            "priya_mom": PersonaVoiceSettings(
                persona_name="Priya",
                age=34,
                accessibility_needs=["time_efficiency", "context_awareness", "multitasking"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["family", "work", "productivity", "organization"],
                noise_tolerance=0.7,  # Busy household
                max_response_time_ms=1800,
                silence_timeout_ms=1500,
                interruption_allowed=True,  # Needs to multitask
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.1,
                voice_pitch=1.0,
                default_emotion=EmotionTone.FRIENDLY,
                explanation_depth="standard",
                technical_terms=False,
                confirmation_style="implicit",
            ),
            
            # Jamie (19, Privacy Advocate) - Transparent
            "jamie_privacy": PersonaVoiceSettings(
                persona_name="Jamie",
                age=19,
                accessibility_needs=["privacy_transparency", "security_awareness", "control"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["privacy", "security", "opensource", "freedom"],
                noise_tolerance=0.3,
                max_response_time_ms=1500,
                silence_timeout_ms=1200,
                interruption_allowed=True,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.2,
                voice_pitch=1.0,
                default_emotion=EmotionTone.NEUTRAL,
                explanation_depth="detailed",
                technical_terms=True,
                confirmation_style="explicit",
            ),
            
            # Viktor (67, ESL) - Clear communication
            "viktor_esl": PersonaVoiceSettings(
                persona_name="Viktor",
                age=67,
                accessibility_needs=["clear_speech", "simple_language", "patience"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",  # Could support multiple languages
                vocabulary_context=["basic", "simple", "clear", "helpful"],
                noise_tolerance=0.4,
                max_response_time_ms=3000,
                silence_timeout_ms=3000,
                interruption_allowed=False,
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=0.8,  # Slower for comprehension
                voice_pitch=1.0,
                default_emotion=EmotionTone.PATIENT,
                explanation_depth="standard",
                technical_terms=False,
                confirmation_style="explicit",
            ),
            
            # Luna (14, Autistic) - Predictable
            "luna_autistic": PersonaVoiceSettings(
                persona_name="Luna",
                age=14,
                accessibility_needs=["predictability", "routine", "clear_patterns", "sensory_friendly"],
                stt_provider=VoiceProvider.WHISPER_CPP,
                language="en-US",
                vocabulary_context=["patterns", "systems", "logic", "precision"],
                noise_tolerance=0.2,  # Sensory sensitivity
                max_response_time_ms=2000,
                silence_timeout_ms=2000,
                interruption_allowed=False,  # Avoid sensory overload
                tts_provider=VoiceProvider.PIPER_TTS,
                voice_speed=1.0,
                voice_pitch=1.0,  # Consistent, neutral
                default_emotion=EmotionTone.NEUTRAL,
                explanation_depth="detailed",
                technical_terms=True,
                confirmation_style="explicit",
                background_noise_suppression=True,  # Reduce sensory load
            ),
        }
    
    def get_persona_settings(self, persona_name: str = None) -> PersonaVoiceSettings:
        """Get voice settings for specified persona or active persona."""
        target_persona = persona_name or self.active_persona
        
        if target_persona in self.personas:
            return self.personas[target_persona]
        
        # Fallback to default
        if "default" not in self.personas:
            # Create basic default settings
            self.personas["default"] = PersonaVoiceSettings(
                persona_name="Default User",
                age=30,
            )
        
        return self.personas["default"]
    
    def set_active_persona(self, persona_name: str) -> bool:
        """Set the active persona for voice interactions."""
        if persona_name in self.personas:
            self.active_persona = persona_name
            return True
        return False
    
    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            # Update configuration from file
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    
        except FileNotFoundError:
            # Create default config file
            self.save_to_file(config_path)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save current configuration to JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        data = {
            "active_persona": self.active_persona,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "chunk_size": self.chunk_size,
            "audio_device_input": self.audio_device_input,
            "audio_device_output": self.audio_device_output,
            "enable_gpu_acceleration": self.enable_gpu_acceleration,
            "concurrent_processing": self.concurrent_processing,
            "cache_models": self.cache_models,
            "save_audio_history": self.save_audio_history,
            "anonymize_logs": self.anonymize_logs,
            "local_processing_only": self.local_processing_only,
            "wake_word_enabled": self.wake_word_enabled,
            "wake_word": self.wake_word,
            "continuous_listening": self.continuous_listening,
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_optimal_settings_for_hardware(self) -> Dict[str, any]:
        """Determine optimal settings based on available hardware."""
        import psutil
        
        # Get system capabilities
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        settings = {
            "concurrent_processing": cpu_count > 2,
            "enable_gpu_acceleration": False,  # Detect GPU in real implementation
            "cache_models": memory_gb > 4,
            "chunk_size": 1024 if memory_gb > 8 else 512,
        }
        
        return settings


# Default global voice configuration
DEFAULT_VOICE_CONFIG = VoiceConfig()