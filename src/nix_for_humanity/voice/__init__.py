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
"""

from .interface import VoiceInterface
from .recognition import SpeechRecognizer
from .synthesis import SpeechSynthesizer
from .wake_word import WakeWordDetector

__all__ = [
    "VoiceInterface",
    "SpeechRecognizer",
    "SpeechSynthesizer",
    "WakeWordDetector",
]
