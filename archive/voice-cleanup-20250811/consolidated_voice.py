"""
Consolidated Voice Module for Nix for Humanity v1.3.0+

This single module replaces all duplicate voice implementations:
- interface.py
- recognition.py
- synthesis.py
- offline.py
- whisper_piper.py
- pipecat_integration.py
- wake_word.py

Design Principles:
- One voice module to rule them all
- Graceful degradation when dependencies missing
- < 500ms initialization time
- Clean, maintainable code
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    sr = None

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    pyttsx3 = None

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    whisper = None


@dataclass
class VoiceConfig:
    """Configuration for unified voice interface."""
    enable_wake_word: bool = False
    wake_word: str = "hey nix"
    language: str = "en-US"
    speech_rate: int = 150
    volume: float = 0.9
    microphone_index: Optional[int] = None
    model_size: str = "tiny"  # For whisper
    use_offline: bool = True  # Prefer offline processing
    continuous_listening: bool = False
    timeout: float = 5.0
    phrase_time_limit: float = 10.0


class ConsolidatedVoice:
    """
    The ONE unified voice implementation.
    
    Features:
    - Speech recognition (multiple engines)
    - Text-to-speech synthesis
    - Wake word detection
    - Offline-first processing
    - Graceful fallbacks
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize the consolidated voice interface."""
        self.config = config or VoiceConfig()
        self.is_listening = False
        self._recognizer = None
        self._microphone = None
        self._tts_engine = None
        self._whisper_model = None
        self._callbacks: Dict[str, List[Callable]] = {}
        
        # Lazy initialization flags
        self._recognizer_initialized = False
        self._tts_initialized = False
        self._whisper_initialized = False
        
        # Check available features
        self.features = {
            "speech_recognition": SR_AVAILABLE,
            "text_to_speech": TTS_AVAILABLE,
            "whisper": WHISPER_AVAILABLE,
            "wake_word": SR_AVAILABLE and self.config.enable_wake_word,
        }
        
        logger.info(f"Voice features available: {self.features}")
    
    def _init_recognizer(self) -> bool:
        """Initialize speech recognizer lazily."""
        if self._recognizer_initialized:
            return True
        
        if not SR_AVAILABLE:
            logger.warning("Speech recognition not available (install speech_recognition)")
            return False
        
        try:
            self._recognizer = sr.Recognizer()
            self._microphone = sr.Microphone(
                device_index=self.config.microphone_index
            )
            
            # Adjust for ambient noise
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self._recognizer_initialized = True
            logger.info("Speech recognizer initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize recognizer: {e}")
            return False
    
    def _init_tts(self) -> bool:
        """Initialize text-to-speech engine lazily."""
        if self._tts_initialized:
            return True
        
        if not TTS_AVAILABLE:
            logger.warning("TTS not available (install pyttsx3)")
            return False
        
        try:
            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty('rate', self.config.speech_rate)
            self._tts_engine.setProperty('volume', self.config.volume)
            
            self._tts_initialized = True
            logger.info("TTS engine initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            return False
    
    def _init_whisper(self) -> bool:
        """Initialize Whisper model lazily."""
        if self._whisper_initialized:
            return True
        
        if not WHISPER_AVAILABLE:
            logger.warning("Whisper not available (install openai-whisper)")
            return False
        
        try:
            self._whisper_model = whisper.load_model(self.config.model_size)
            self._whisper_initialized = True
            logger.info(f"Whisper model '{self.config.model_size}' loaded")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return False
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Listen for speech and return transcribed text."""
        if not self._init_recognizer():
            return None
        
        timeout = timeout or self.config.timeout
        
        try:
            with self._microphone as source:
                logger.debug("Listening...")
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )
            
            # Try offline recognition first if configured
            if self.config.use_offline and self._init_whisper():
                return self._transcribe_with_whisper(audio)
            
            # Fallback to online recognition
            return self._transcribe_online(audio)
            
        except sr.WaitTimeoutError:
            logger.debug("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Error during listening: {e}")
            return None
    
    def _transcribe_with_whisper(self, audio) -> Optional[str]:
        """Transcribe audio using Whisper (offline)."""
        if not self._whisper_model:
            return None
        
        try:
            # Convert audio to wav format
            import io
            import wave
            
            wav_data = io.BytesIO(audio.get_wav_data())
            result = self._whisper_model.transcribe(wav_data)
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return None
    
    def _transcribe_online(self, audio) -> Optional[str]:
        """Transcribe using online services."""
        if not self._recognizer:
            return None
        
        try:
            # Try Google Speech Recognition (free, no API key)
            text = self._recognizer.recognize_google(
                audio,
                language=self.config.language
            )
            return text
        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Online recognition error: {e}")
            return None
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """Convert text to speech."""
        if not text:
            return False
        
        # Simple console fallback
        if not self._init_tts():
            print(f"🔊 {text}")
            return True
        
        try:
            self._tts_engine.say(text)
            if wait:
                self._tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            # Fallback to console
            print(f"🔊 {text}")
            return False
    
    async def listen_continuously(self, callback: Callable[[str], None]):
        """Listen continuously in the background."""
        if not self._init_recognizer():
            logger.error("Cannot start continuous listening")
            return
        
        self.is_listening = True
        logger.info("Started continuous listening")
        
        while self.is_listening:
            text = self.listen(timeout=1.0)
            if text:
                # Check for wake word if enabled
                if self.config.enable_wake_word:
                    if self.config.wake_word.lower() in text.lower():
                        self.speak("Yes?")
                        # Listen for actual command
                        command = self.listen(timeout=10.0)
                        if command:
                            callback(command)
                else:
                    callback(text)
            
            await asyncio.sleep(0.1)
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        logger.info("Stopped continuous listening")
    
    def set_wake_word(self, wake_word: str):
        """Update the wake word."""
        self.config.wake_word = wake_word
        logger.info(f"Wake word set to: {wake_word}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available TTS voices."""
        if not self._init_tts():
            return []
        
        voices = []
        for voice in self._tts_engine.getProperty('voices'):
            voices.append({
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, 'languages', []),
                "gender": getattr(voice, 'gender', 'unknown'),
            })
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """Set TTS voice by ID."""
        if not self._init_tts():
            return False
        
        try:
            self._tts_engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False
    
    def test_microphone(self) -> bool:
        """Test if microphone is working."""
        if not self._init_recognizer():
            return False
        
        try:
            with self._microphone as source:
                # Just try to read some audio
                self._recognizer.listen(source, timeout=0.5)
            logger.info("Microphone test successful")
            return True
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False
    
    def test_speaker(self) -> bool:
        """Test if speaker/TTS is working."""
        return self.speak("Voice interface test successful", wait=True)


class SimpleVoiceInterface:
    """
    Simple voice interface for environments without audio support.
    
    This provides a text-based simulation of voice interaction.
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize simple voice interface."""
        self.config = config or VoiceConfig()
        self.is_listening = False
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Simulate listening by prompting for input."""
        try:
            return input("🎤 Speak (type your command): ").strip()
        except (KeyboardInterrupt, EOFError):
            return None
    
    def speak(self, text: str, wait: bool = True) -> bool:
        """Simulate speaking by printing."""
        print(f"🔊 {text}")
        return True
    
    async def listen_continuously(self, callback: Callable[[str], None]):
        """Simulate continuous listening."""
        self.is_listening = True
        print("🎧 Continuous listening mode (type 'stop' to end)")
        
        while self.is_listening:
            text = self.listen()
            if text:
                if text.lower() == 'stop':
                    self.stop_listening()
                else:
                    callback(text)
            await asyncio.sleep(0.1)
    
    def stop_listening(self):
        """Stop listening."""
        self.is_listening = False
        print("🔇 Stopped listening")
    
    def test_microphone(self) -> bool:
        """Always returns True for text interface."""
        return True
    
    def test_speaker(self) -> bool:
        """Always returns True for text interface."""
        self.speak("Voice interface test (simulated)")
        return True


def create_voice_interface(config: Optional[VoiceConfig] = None) -> Any:
    """
    Factory function to create appropriate voice interface.
    
    Returns ConsolidatedVoice if audio libraries available,
    otherwise returns SimpleVoiceInterface.
    """
    # Check if we have any audio capabilities
    if SR_AVAILABLE or TTS_AVAILABLE:
        return ConsolidatedVoice(config)
    else:
        logger.info("No audio libraries available, using text simulation")
        return SimpleVoiceInterface(config)


def test_voice_setup() -> bool:
    """
    Test voice setup and provide diagnostic information.
    """
    print("Voice Interface Diagnostics")
    print("=" * 40)
    
    print(f"Speech Recognition: {'✅' if SR_AVAILABLE else '❌ (pip install SpeechRecognition)'}")
    print(f"Text-to-Speech: {'✅' if TTS_AVAILABLE else '❌ (pip install pyttsx3)'}")
    print(f"Whisper: {'✅' if WHISPER_AVAILABLE else '❌ (pip install openai-whisper)'}")
    
    voice = create_voice_interface()
    
    print("\nTesting components...")
    mic_ok = voice.test_microphone()
    print(f"Microphone: {'✅' if mic_ok else '❌'}")
    
    speaker_ok = voice.test_speaker()
    print(f"Speaker: {'✅' if speaker_ok else '❌'}")
    
    return mic_ok and speaker_ok


# Compatibility exports for old imports
VoiceInterface = ConsolidatedVoice
SpeechRecognizer = ConsolidatedVoice
SpeechSynthesizer = ConsolidatedVoice


__all__ = [
    "ConsolidatedVoice",
    "SimpleVoiceInterface",
    "VoiceConfig",
    "create_voice_interface",
    "test_voice_setup",
    # Compatibility
    "VoiceInterface",
    "SpeechRecognizer",
    "SpeechSynthesizer",
]