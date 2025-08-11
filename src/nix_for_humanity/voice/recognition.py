"""
Speech Recognition Module for Voice Interface.

Handles converting speech to text using multiple recognition engines.

Since: v1.0.0
"""

import time
from dataclasses import dataclass
from enum import Enum

from ..core.logging_config import get_logger

logger = get_logger(__name__)

# Try to import speech recognition
try:
    import speech_recognition as sr

    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    logger.warning("speech_recognition not available - voice features disabled")


class RecognitionEngine(Enum):
    """Available speech recognition engines."""

    GOOGLE = "google"  # Online fallback
    SPHINX = "sphinx"  # Offline fallback
    WHISPER = "whisper"  # PRIMARY: OpenAI Whisper (as per architecture)
    PIPER = "piper"  # PRIMARY: For TTS (as per architecture)


@dataclass
class RecognitionResult:
    """
    Result from speech recognition.

    Since: v1.0.0
    """

    text: str
    confidence: float
    language: str
    duration: float
    engine: str


class SpeechRecognizer:
    """
    Speech recognition handler.

    Converts audio input to text using various recognition engines.
    Supports both online and offline recognition.

    Since: v1.0.0
    """

    def __init__(
        self,
        engine: RecognitionEngine = RecognitionEngine.WHISPER,  # Changed to Whisper as primary
        language: str = "en-US",
        noise_threshold: float = 0.3,
    ):
        """
        Initialize speech recognizer.

        Args:
            engine: Recognition engine to use
            language: Language code
            noise_threshold: Noise threshold for detection
        """
        self.engine = engine
        self.language = language
        self.noise_threshold = noise_threshold

        if HAS_SPEECH_RECOGNITION:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

            # Adjust for ambient noise
            self._calibrate()
        else:
            self.recognizer = None
            self.microphone = None

    def _calibrate(self) -> None:
        """Calibrate for ambient noise."""
        if not HAS_SPEECH_RECOGNITION:
            return

        try:
            with self.microphone as source:
                logger.info("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Calibration complete")
        except Exception as e:
            logger.error(f"Calibration failed: {e}")

    def test_microphone(self) -> bool:
        """
        Test if microphone is working.

        Returns:
            True if microphone works
        """
        if not HAS_SPEECH_RECOGNITION:
            return False

        try:
            with self.microphone as source:
                # Try to get audio
                self.recognizer.listen(source, timeout=0.5)
            return True
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False

    def listen(
        self, timeout: float | None = None, phrase_time_limit: float | None = None
    ) -> RecognitionResult | None:
        """
        Listen for speech and convert to text.

        Args:
            timeout: Maximum time to wait for speech
            phrase_time_limit: Maximum time for a phrase

        Returns:
            Recognition result if successful
        """
        if not HAS_SPEECH_RECOGNITION:
            logger.warning("Speech recognition not available")
            return None

        start_time = time.time()

        try:
            # Listen for audio
            with self.microphone as source:
                logger.debug("Listening...")

                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

            # Recognize speech
            result = self._recognize(audio)

            if result:
                result.duration = time.time() - start_time

            return result

        except sr.WaitTimeoutError:
            logger.debug("Listening timeout")
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}")
            return None

    def _recognize(self, audio) -> RecognitionResult | None:
        """
        Recognize speech from audio.

        Args:
            audio: Audio data

        Returns:
            Recognition result
        """
        try:
            if self.engine == RecognitionEngine.GOOGLE:
                return self._recognize_google(audio)
            if self.engine == RecognitionEngine.SPHINX:
                return self._recognize_sphinx(audio)
            if self.engine == RecognitionEngine.WHISPER:
                return self._recognize_whisper(audio)
            if self.engine == RecognitionEngine.VOSK:
                return self._recognize_vosk(audio)
            logger.error(f"Unknown engine: {self.engine}")
            return None

        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return None

    def _recognize_google(self, audio) -> RecognitionResult | None:
        """Recognize using Google Speech API."""
        try:
            # Get result with confidence scores
            result = self.recognizer.recognize_google(
                audio, language=self.language, show_all=True
            )

            if result and result.get("alternative"):
                best = result["alternative"][0]
                text = best.get("transcript", "")
                confidence = best.get("confidence", 0.5)

                return RecognitionResult(
                    text=text,
                    confidence=confidence,
                    language=self.language,
                    duration=0,
                    engine="google",
                )

            return None

        except sr.UnknownValueError:
            logger.debug("Google could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google API error: {e}")
            return None

    def _recognize_sphinx(self, audio) -> RecognitionResult | None:
        """Recognize using PocketSphinx (offline)."""
        try:
            text = self.recognizer.recognize_sphinx(audio)

            return RecognitionResult(
                text=text,
                confidence=0.7,  # Sphinx doesn't provide confidence
                language=self.language,
                duration=0,
                engine="sphinx",
            )

        except sr.UnknownValueError:
            logger.debug("Sphinx could not understand audio")
            return None
        except Exception as e:
            logger.error(f"Sphinx error: {e}")
            return None

    def _recognize_whisper(self, audio) -> RecognitionResult | None:
        """Recognize using OpenAI Whisper."""
        # TODO: Implement Whisper recognition
        logger.warning("Whisper recognition not yet implemented")
        return None

    def _recognize_vosk(self, audio) -> RecognitionResult | None:
        """Recognize using Vosk (offline)."""
        # TODO: Implement Vosk recognition
        logger.warning("Vosk recognition not yet implemented")
        return None

    def stop(self) -> None:
        """Stop the recognizer."""
        # Cleanup if needed
        pass
