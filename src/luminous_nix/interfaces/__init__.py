"""
Voice Interface for Nix for Humanity.

Enables natural language control through speech recognition and synthesis.
Supports multiple speech engines and provides accessibility features.

Key Features:
    - Real-time speech recognition
    - Natural text-to-speech synthesis
    - Wake word detection
    - Continuous listening mode
    - Noise cancellation
    - Multi-language support

Since: v1.0.0
Updated: v1.3.0+ - Consolidated implementation
"""

# Import from consolidated module
from .consolidated_voice import (
    ConsolidatedVoice,
    SimpleVoiceInterface,
    VoiceConfig,
    create_voice_interface,
    test_voice_setup,
)

# Maintain backward compatibility
try:
    from .interface import VoiceInterface as _OldVoiceInterface
except ImportError:
    _OldVoiceInterface = ConsolidatedVoice

try:
    from .recognition import SpeechRecognizer as _OldSpeechRecognizer
except ImportError:
    _OldSpeechRecognizer = ConsolidatedVoice

try:
    from .synthesis import SpeechSynthesizer as _OldSpeechSynthesizer
except ImportError:
    _OldSpeechSynthesizer = ConsolidatedVoice

try:
    from .wake_word import WakeWordDetector as _OldWakeWordDetector
except ImportError:
    _OldWakeWordDetector = ConsolidatedVoice

# Use consolidated implementations
VoiceInterface = ConsolidatedVoice
SpeechRecognizer = ConsolidatedVoice
SpeechSynthesizer = ConsolidatedVoice
WakeWordDetector = ConsolidatedVoice

__all__ = [
    # New consolidated API
    "ConsolidatedVoice",
    "SimpleVoiceInterface",
    "VoiceConfig",
    "create_voice_interface",
    "test_voice_setup",
    # Backward compatibility
    "VoiceInterface",
    "SpeechRecognizer",
    "SpeechSynthesizer",
    "WakeWordDetector",
]
