"""
Speech Synthesis Module for Voice Interface.

Handles text-to-speech conversion with multiple voice engines.

Since: v1.0.0
"""

import queue
import threading
from enum import Enum

from ..core.logging_config import get_logger

logger = get_logger(__name__)

# Try to import TTS libraries
try:
    import pyttsx3

    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    logger.warning("pyttsx3 not available - TTS features limited")

try:
    import gtts

    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    logger.warning("gtts not available - Google TTS disabled")


class Voice(Enum):
    """Available voice types."""

    DEFAULT = "default"
    MALE = "male"
    FEMALE = "female"
    ROBOTIC = "robotic"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"


class TTSEngine(Enum):
    """Available TTS engines."""

    PYTTSX3 = "pyttsx3"  # Offline
    GTTS = "gtts"  # Google TTS (online)
    ESPEAK = "espeak"  # Linux espeak
    SYSTEM = "system"  # System default


class SpeechSynthesizer:
    """
    Text-to-speech synthesizer.

    Converts text to spoken audio using various TTS engines.
    Supports both online and offline synthesis.

    Since: v1.0.0
    """

    def __init__(
        self,
        engine: TTSEngine = TTSEngine.PYTTSX3,
        voice: Voice = Voice.DEFAULT,
        rate: int = 150,
        volume: float = 0.9,
    ):
        """
        Initialize speech synthesizer.

        Args:
            engine: TTS engine to use
            voice: Voice type
            rate: Speech rate (words per minute)
            volume: Volume level (0-1)
        """
        self.engine_type = engine
        self.voice_type = voice
        self.rate = rate
        self.volume = volume

        # Initialize engine
        self.engine = self._init_engine()

        # Speech queue for async speaking
        self.speech_queue: queue.Queue = queue.Queue()
        self.speaking = False
        self.stop_event = threading.Event()

    def _init_engine(self):
        """Initialize the TTS engine."""
        if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3:
            return self._init_pyttsx3()
        if self.engine_type == TTSEngine.GTTS and HAS_GTTS:
            return self._init_gtts()
        logger.warning(f"TTS engine {self.engine_type} not available")
        return None

    def _init_pyttsx3(self):
        """Initialize pyttsx3 engine."""
        try:
            engine = pyttsx3.init()

            # Set properties
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            # Set voice
            voices = engine.getProperty("voices")
            if voices:
                if self.voice_type == Voice.FEMALE and len(voices) > 1:
                    engine.setProperty("voice", voices[1].id)
                else:
                    engine.setProperty("voice", voices[0].id)

            return engine

        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            return None

    def _init_gtts(self):
        """Initialize gTTS engine."""
        # gTTS doesn't need initialization
        return "gtts"

    def test_speakers(self) -> bool:
        """
        Test if speakers are working.

        Returns:
            True if speakers work
        """
        try:
            self.speak("Testing audio output", wait=True)
            return True
        except Exception as e:
            logger.error(f"Speaker test failed: {e}")
            return False

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Speak the given text.

        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        if not text:
            return

        if not self.engine:
            logger.warning("No TTS engine available")
            # Fallback to console output
            print(f"🔊 {text}")
            return

        if wait:
            self._speak_blocking(text)
        else:
            self._speak_async(text)

    def _speak_blocking(self, text: str) -> None:
        """Speak text synchronously."""
        try:
            if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3:
                self.engine.say(text)
                self.engine.runAndWait()
            elif self.engine_type == TTSEngine.GTTS and HAS_GTTS:
                self._speak_gtts(text)
            else:
                # Fallback
                print(f"🔊 {text}")

        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"🔊 {text}")

    def _speak_async(self, text: str) -> None:
        """Speak text asynchronously."""
        self.speech_queue.put(text)

        if not self.speaking:
            thread = threading.Thread(target=self._speech_worker, daemon=True)
            thread.start()

    def _speech_worker(self) -> None:
        """Worker thread for async speech."""
        self.speaking = True

        while not self.stop_event.is_set():
            try:
                text = self.speech_queue.get(timeout=1)
                self._speak_blocking(text)
            except queue.Empty:
                if self.speech_queue.empty():
                    break
            except Exception as e:
                logger.error(f"Speech worker error: {e}")

        self.speaking = False

    def _speak_gtts(self, text: str) -> None:
        """Speak using Google TTS."""
        try:
            import os
            import tempfile

            from gtts import gTTS

            # Create TTS object
            tts = gTTS(text=text, lang="en", slow=False)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tmp_filename = tmp_file.name
                tts.save(tmp_filename)

            # Play the file (platform-specific)
            import platform

            system = platform.system()

            if system == "Darwin":  # macOS
                os.system(f"afplay {tmp_filename}")
            elif system == "Linux":
                os.system(
                    f"mpg123 -q {tmp_filename} 2>/dev/null || play -q {tmp_filename} 2>/dev/null"
                )
            elif system == "Windows":
                os.system(f"start {tmp_filename}")

            # Clean up
            os.unlink(tmp_filename)

        except Exception as e:
            logger.error(f"gTTS error: {e}")
            print(f"🔊 {text}")

    def play_sound(self, sound_type: str) -> None:
        """
        Play a notification sound.

        Args:
            sound_type: Type of sound (activate, success, error, etc.)
        """
        # Map sound types to text or system sounds
        sounds = {
            "activate": "Ready",
            "success": "Done",
            "error": "Error",
            "warning": "Warning",
        }

        if sound_type in sounds:
            self.speak(sounds[sound_type], wait=False)

    def set_voice(self, voice: Voice) -> None:
        """
        Change the voice type.

        Args:
            voice: New voice type
        """
        self.voice_type = voice

        if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3 and self.engine:
            voices = self.engine.getProperty("voices")
            if voices:
                if voice == Voice.FEMALE and len(voices) > 1:
                    self.engine.setProperty("voice", voices[1].id)
                else:
                    self.engine.setProperty("voice", voices[0].id)

    def set_rate(self, rate: int) -> None:
        """
        Change speech rate.

        Args:
            rate: Words per minute
        """
        self.rate = rate

        if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3 and self.engine:
            self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float) -> None:
        """
        Change volume.

        Args:
            volume: Volume level (0-1)
        """
        self.volume = max(0.0, min(1.0, volume))

        if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3 and self.engine:
            self.engine.setProperty("volume", self.volume)

    def stop(self) -> None:
        """Stop the synthesizer."""
        self.stop_event.set()

        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except:
                pass

        # Stop engine
        if self.engine_type == TTSEngine.PYTTSX3 and HAS_PYTTSX3 and self.engine:
            self.engine.stop()
