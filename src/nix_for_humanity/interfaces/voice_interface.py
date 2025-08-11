"""
Voice Interface for Nix for Humanity

Revolutionary natural language voice control for NixOS.
Makes system management accessible to everyone through speech.

Features:
    - Real-time speech recognition
    - Natural language processing
    - Voice feedback
    - Multi-language support (future)
"""

import asyncio
import logging
import queue
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Any

import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3

from ..core import NixForHumanityCore, Query, Response


logger = logging.getLogger(__name__)


class VoiceState(Enum):
    """Voice interface states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceConfig:
    """Configuration for voice interface"""
    
    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    
    # Voice activity detection
    energy_threshold: float = 300.0
    pause_threshold: float = 0.8
    phrase_time_limit: Optional[float] = None
    
    # Speech settings
    language: str = "en-US"
    speech_rate: int = 150
    speech_volume: float = 0.9
    
    # Behavior
    wake_word: Optional[str] = "hey nix"
    confirmation_required: bool = True
    audio_feedback: bool = True


class VoiceActivityDetector:
    """Detect voice activity in audio stream"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.energy_buffer = []
        self.buffer_size = 50
        
    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """Check if audio chunk contains speech"""
        # Calculate RMS energy
        energy = np.sqrt(np.mean(audio_chunk**2))
        
        # Add to buffer
        self.energy_buffer.append(energy)
        if len(self.energy_buffer) > self.buffer_size:
            self.energy_buffer.pop(0)
        
        # Check if energy exceeds threshold
        if len(self.energy_buffer) >= 10:
            avg_energy = np.mean(self.energy_buffer[-10:])
            return avg_energy > self.config.energy_threshold / 10000
        
        return False


class VoiceInterface:
    """
    Main voice interface for natural language NixOS control.
    
    This makes NixOS accessible to everyone through speech,
    serving all 10 personas from Grandma Rose to power users.
    """
    
    def __init__(
        self,
        core: Optional[NixForHumanityCore] = None,
        config: Optional[VoiceConfig] = None,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        """
        Initialize voice interface.
        
        Args:
            core: NixForHumanityCore instance
            config: Voice configuration
            progress_callback: Callback for progress updates
        """
        self.core = core or NixForHumanityCore()
        self.config = config or VoiceConfig()
        self.progress_callback = progress_callback
        
        # State management
        self.state = VoiceState.IDLE
        self.is_running = False
        
        # Audio components
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.config.energy_threshold
        self.recognizer.pause_threshold = self.config.pause_threshold
        
        # Text-to-speech
        self.tts_engine = pyttsx3.init()
        self._configure_tts()
        
        # Voice activity detection
        self.vad = VoiceActivityDetector(self.config)
        
        # Audio queue for streaming
        self.audio_queue = queue.Queue()
        
        # Callbacks
        self.on_state_change: Optional[Callable[[VoiceState], None]] = None
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[Response], None]] = None
        
    def _configure_tts(self):
        """Configure text-to-speech engine"""
        # Set voice properties
        self.tts_engine.setProperty('rate', self.config.speech_rate)
        self.tts_engine.setProperty('volume', self.config.speech_volume)
        
        # Try to select a nice voice
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Prefer female voice for friendliness
            for voice in voices:
                if 'female' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
    
    def _update_state(self, new_state: VoiceState):
        """Update state and notify callback"""
        self.state = new_state
        if self.on_state_change:
            self.on_state_change(new_state)
        logger.info(f"Voice state: {new_state.value}")
    
    def _update_progress(self, message: str, progress: float):
        """Update progress callback"""
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    def speak(self, text: str):
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
        """
        self._update_state(VoiceState.SPEAKING)
        
        # Clean up text for speech
        text = text.replace("NixOS", "nix O S")
        text = text.replace("sudo", "pseudo")
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
        finally:
            self._update_state(VoiceState.IDLE)
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout: Maximum time to listen
            
        Returns:
            Transcribed text or None
        """
        self._update_state(VoiceState.LISTENING)
        self._update_progress("Listening...", 0.0)
        
        try:
            # Use microphone
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self._update_progress("Listening...", 0.3)
                
                # Listen for audio
                if timeout:
                    audio = self.recognizer.listen(source, timeout=timeout)
                else:
                    audio = self.recognizer.listen(source)
                
                self._update_progress("Processing speech...", 0.6)
            
            # Convert to text
            self._update_state(VoiceState.PROCESSING)
            
            # Try Google Speech Recognition (online)
            try:
                text = self.recognizer.recognize_google(audio)
                self._update_progress("Recognized!", 1.0)
                
                if self.on_transcription:
                    self.on_transcription(text)
                
                return text
                
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Recognition error: {e}")
                # Could fall back to offline recognition here
                return None
                
        except sr.WaitTimeoutError:
            logger.info("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            self._update_state(VoiceState.ERROR)
            return None
        finally:
            if self.state != VoiceState.ERROR:
                self._update_state(VoiceState.IDLE)
    
    def process_voice_command(self, text: str) -> Response:
        """
        Process voice command through NixForHumanity core.
        
        Args:
            text: Transcribed voice command
            
        Returns:
            Response from the system
        """
        self._update_state(VoiceState.PROCESSING)
        
        # Create query
        query = Query(text=text, context={"interface": "voice"})
        
        # Process through core
        response = self.core.process(query)
        
        if self.on_response:
            self.on_response(response)
        
        self._update_state(VoiceState.IDLE)
        return response
    
    async def start_continuous_listening(self):
        """
        Start continuous listening mode.
        
        Listens for wake word, then processes commands.
        """
        self.is_running = True
        logger.info("Starting continuous voice interface")
        
        while self.is_running:
            try:
                # Listen for input
                text = self.listen(timeout=5.0)
                
                if text:
                    logger.info(f"Heard: {text}")
                    
                    # Check for wake word if configured
                    if self.config.wake_word:
                        if self.config.wake_word.lower() in text.lower():
                            # Remove wake word and process
                            command = text.lower().replace(
                                self.config.wake_word.lower(), ""
                            ).strip()
                            
                            if command:
                                # Process command
                                response = self.process_voice_command(command)
                                
                                # Speak response
                                if response.success:
                                    self.speak(response.message)
                                else:
                                    self.speak(f"Sorry, {response.message}")
                    else:
                        # No wake word, process directly
                        response = self.process_voice_command(text)
                        
                        # Speak response
                        if response.success:
                            self.speak(response.message)
                        else:
                            self.speak(f"I had trouble with that: {response.message}")
                
                # Small delay between listens
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Continuous listening error: {e}")
                await asyncio.sleep(1.0)
        
        logger.info("Stopped continuous listening")
    
    def stop(self):
        """Stop the voice interface"""
        self.is_running = False
        self._update_state(VoiceState.IDLE)
    
    def test_audio(self) -> bool:
        """
        Test audio input/output.
        
        Returns:
            True if audio works
        """
        try:
            # Test TTS
            self.speak("Testing audio output")
            
            # Test microphone
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio test failed: {e}")
            return False


class VoiceCommands:
    """
    Predefined voice command patterns for better recognition.
    
    Maps natural speech patterns to NixOS operations.
    """
    
    INSTALL_PATTERNS = [
        "install {package}",
        "get me {package}",
        "i need {package}",
        "download {package}",
        "add {package} to my system",
    ]
    
    UPDATE_PATTERNS = [
        "update my system",
        "update everything",
        "get the latest updates",
        "upgrade the system",
        "check for updates",
    ]
    
    ROLLBACK_PATTERNS = [
        "roll back",
        "go back to previous",
        "undo the last change",
        "revert the system",
        "restore previous version",
    ]
    
    SEARCH_PATTERNS = [
        "search for {package}",
        "find {package}",
        "look for {package}",
        "what packages have {term}",
        "show me {term} packages",
    ]
    
    HELP_PATTERNS = [
        "help",
        "what can you do",
        "show me commands",
        "how do i",
        "explain",
    ]
    
    @classmethod
    def enhance_recognition(cls, text: str) -> str:
        """
        Enhance voice recognition with common corrections.
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Enhanced text
        """
        # Common mishearings
        replacements = {
            "firefox": ["fire fox", "firefocks", "fair fox"],
            "nixos": ["nix os", "nix o s", "nicksos", "nexos"],
            "install": ["in stall", "in store"],
            "update": ["up date", "up grade"],
        }
        
        text_lower = text.lower()
        
        for correct, variants in replacements.items():
            for variant in variants:
                if variant in text_lower:
                    text_lower = text_lower.replace(variant, correct)
        
        return text_lower


def create_voice_interface() -> VoiceInterface:
    """
    Factory function to create configured voice interface.
    
    Returns:
        Configured VoiceInterface instance
    """
    config = VoiceConfig(
        wake_word="hey nix",
        confirmation_required=True,
        audio_feedback=True,
        speech_rate=150,
    )
    
    interface = VoiceInterface(config=config)
    
    # Add command enhancement
    original_process = interface.process_voice_command
    
    def enhanced_process(text: str) -> Response:
        enhanced_text = VoiceCommands.enhance_recognition(text)
        return original_process(enhanced_text)
    
    interface.process_voice_command = enhanced_process
    
    return interface