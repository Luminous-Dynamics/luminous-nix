"""
Whisper and Piper Voice Integration.

This module provides voice recognition using OpenAI's Whisper and
text-to-speech using Piper, as specified in the architecture documentation.

Features:
- Whisper for accurate speech-to-text
- Piper for natural text-to-speech
- Completely offline operation
- Privacy-preserving (all local)
- Multiple model sizes available

Since: v1.1.0
"""

import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Whisper
try:
    import whisper

    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    logger.info("Whisper not available - install with: pip install openai-whisper")

# Check for Piper TTS binary
HAS_PIPER = (
    subprocess.run(["which", "piper"], capture_output=True, text=True).returncode == 0
)

if not HAS_PIPER:
    logger.info("Piper not available - install from: https://github.com/rhasspy/piper")


@dataclass
class WhisperModel:
    """Configuration for Whisper speech recognition models."""

    name: str
    size_mb: int
    accuracy: str  # "low", "medium", "high", "very_high"
    speed: str  # "fast", "medium", "slow"
    languages: list[str]  # Supported languages


@dataclass
class PiperVoice:
    """Configuration for Piper TTS voices."""

    name: str
    language: str
    quality: str  # "low", "medium", "high"
    gender: str  # "male", "female", "neutral"
    model_path: Path | None


class WhisperPiperInterface:
    """
    Voice interface using Whisper and Piper as per architecture.

    This is the correct implementation according to our documentation,
    replacing the incorrect Vosk implementation.

    Since: v1.1.0
    """

    # Available Whisper models (from smallest to largest)
    WHISPER_MODELS = {
        "tiny": WhisperModel(
            name="tiny",
            size_mb=39,
            accuracy="low",
            speed="fast",
            languages=["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"],
        ),
        "base": WhisperModel(
            name="base",
            size_mb=74,
            accuracy="medium",
            speed="fast",
            languages=["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"],
        ),
        "small": WhisperModel(
            name="small",
            size_mb=244,
            accuracy="high",
            speed="medium",
            languages=["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"],
        ),
        "medium": WhisperModel(
            name="medium",
            size_mb=769,
            accuracy="very_high",
            speed="slow",
            languages=["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"],
        ),
        "large": WhisperModel(
            name="large",
            size_mb=1550,
            accuracy="very_high",
            speed="slow",
            languages=["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja"],
        ),
    }

    # Available Piper voices
    PIPER_VOICES = {
        "en_US-amy-low": PiperVoice(
            name="en_US-amy-low",
            language="en-US",
            quality="low",
            gender="female",
            model_path=None,
        ),
        "en_US-ryan-high": PiperVoice(
            name="en_US-ryan-high",
            language="en-US",
            quality="high",
            gender="male",
            model_path=None,
        ),
        "en_GB-jenny_dioco-medium": PiperVoice(
            name="en_GB-jenny_dioco-medium",
            language="en-GB",
            quality="medium",
            gender="female",
            model_path=None,
        ),
    }

    def __init__(
        self,
        whisper_model: str = "base",
        piper_voice: str = "en_US-amy-low",
        device: str | None = None,
    ):
        """
        Initialize Whisper/Piper voice interface.

        Args:
            whisper_model: Whisper model size to use
            piper_voice: Piper voice to use for TTS
            device: Device for Whisper ("cuda" or "cpu")

        Since: v1.1.0
        """
        self.whisper_model_name = whisper_model
        self.piper_voice_name = piper_voice
        self.device = device or "cpu"

        # Validate models exist
        if whisper_model not in self.WHISPER_MODELS:
            raise ValueError(f"Unknown Whisper model: {whisper_model}")
        if piper_voice not in self.PIPER_VOICES:
            raise ValueError(f"Unknown Piper voice: {piper_voice}")

        self.whisper_config = self.WHISPER_MODELS[whisper_model]
        self.piper_config = self.PIPER_VOICES[piper_voice]

        # Initialize models
        self.whisper_model = None
        self._init_whisper()

    def _init_whisper(self):
        """Initialize Whisper model for speech recognition."""
        if not HAS_WHISPER:
            raise ImportError(
                "Whisper not installed. Install with:\n" "pip install openai-whisper"
            )

        try:
            logger.info(f"Loading Whisper model: {self.whisper_model_name}")
            self.whisper_model = whisper.load_model(
                self.whisper_model_name, device=self.device
            )
            logger.info(f"Whisper model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def recognize_speech(
        self, audio_file: Path, language: str | None = None
    ) -> dict[str, Any]:
        """
        Recognize speech from audio file using Whisper.

        Args:
            audio_file: Path to audio file
            language: Optional language code (e.g., "en")

        Returns:
            Dictionary with transcript and metadata

        Since: v1.1.0
        """
        if not self.whisper_model:
            raise RuntimeError("Whisper model not initialized")

        try:
            # Transcribe audio
            result = self.whisper_model.transcribe(
                str(audio_file),
                language=language,
                fp16=False,  # Disable for CPU compatibility
            )

            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "segments": result.get("segments", []),
                "confidence": self._calculate_confidence(result),
            }

        except Exception as e:
            logger.error(f"Speech recognition failed: {e}")
            return {"success": False, "error": str(e), "text": ""}

    def synthesize_speech(
        self, text: str, output_file: Path | None = None, speed: float = 1.0
    ) -> Path:
        """
        Synthesize speech from text using Piper.

        Args:
            text: Text to synthesize
            output_file: Optional output file path
            speed: Speech speed multiplier

        Returns:
            Path to generated audio file

        Since: v1.1.0
        """
        if not HAS_PIPER:
            raise RuntimeError(
                "Piper not installed. Install from:\n"
                "https://github.com/rhasspy/piper"
            )

        # Create output file if not specified
        if output_file is None:
            output_file = Path(tempfile.mktemp(suffix=".wav"))

        try:
            # Run Piper TTS
            cmd = [
                "piper",
                "--model",
                self.piper_voice_name,
                "--output_file",
                str(output_file),
            ]

            # Add speed control if not default
            if speed != 1.0:
                cmd.extend(["--length-scale", str(1.0 / speed)])

            # Run synthesis
            result = subprocess.run(
                cmd, input=text, text=True, capture_output=True, check=True
            )

            if output_file.exists():
                logger.info(f"Speech synthesized to: {output_file}")
                return output_file
            raise RuntimeError("Piper failed to generate audio")

        except subprocess.CalledProcessError as e:
            logger.error(f"Piper TTS failed: {e.stderr}")
            raise RuntimeError(f"Speech synthesis failed: {e.stderr}")

    def _calculate_confidence(self, whisper_result: dict) -> float:
        """
        Calculate confidence score from Whisper result.

        Args:
            whisper_result: Result from Whisper transcribe

        Returns:
            Confidence score between 0 and 1

        Since: v1.1.0
        """
        # Whisper doesn't provide direct confidence scores,
        # but we can estimate based on model size and processing
        base_confidence = {
            "tiny": 0.7,
            "base": 0.8,
            "small": 0.85,
            "medium": 0.9,
            "large": 0.95,
        }.get(self.whisper_model_name, 0.8)

        # Adjust based on result quality indicators
        if whisper_result.get("language", "") == "en":
            base_confidence += 0.05  # English typically more accurate

        return min(base_confidence, 1.0)

    def stream_recognition(self, callback=None):
        """
        Stream audio recognition (future implementation).

        This will integrate with pipecat for real-time streaming
        as specified in the architecture.

        Since: v1.2.0 (planned)
        """
        raise NotImplementedError(
            "Streaming recognition will be implemented with pipecat integration"
        )

    @classmethod
    def get_available_models(cls) -> dict[str, Any]:
        """
        Get information about available models.

        Returns:
            Dictionary with Whisper models and Piper voices

        Since: v1.1.0
        """
        return {
            "whisper_models": {
                name: {
                    "size_mb": model.size_mb,
                    "accuracy": model.accuracy,
                    "speed": model.speed,
                }
                for name, model in cls.WHISPER_MODELS.items()
            },
            "piper_voices": {
                name: {
                    "language": voice.language,
                    "quality": voice.quality,
                    "gender": voice.gender,
                }
                for name, voice in cls.PIPER_VOICES.items()
            },
        }

    def test_setup(self) -> dict[str, bool]:
        """
        Test if voice components are properly set up.

        Returns:
            Dictionary with component status

        Since: v1.1.0
        """
        return {
            "whisper_available": HAS_WHISPER,
            "whisper_model_loaded": self.whisper_model is not None,
            "piper_available": HAS_PIPER,
            "device": self.device,
            "ready": HAS_WHISPER and HAS_PIPER and self.whisper_model is not None,
        }


# Convenience function for quick testing
def test_voice_setup():
    """Test if Whisper and Piper are properly installed."""
    print("🎤 Testing Voice Setup")
    print("-" * 40)

    # Check Whisper
    if HAS_WHISPER:
        print("✅ Whisper: Installed")
        try:
            model = whisper.load_model("tiny")
            print("✅ Whisper: Can load models")
        except Exception as e:
            print(f"⚠️ Whisper: Model loading failed - {e}")
    else:
        print("❌ Whisper: Not installed")
        print("   Install with: pip install openai-whisper")

    # Check Piper
    if HAS_PIPER:
        print("✅ Piper: Installed")
    else:
        print("❌ Piper: Not installed")
        print("   Install from: https://github.com/rhasspy/piper")

    print("-" * 40)

    if HAS_WHISPER and HAS_PIPER:
        print("🎉 Voice system ready!")
        return True
    print("⚠️ Some components missing")
    return False


if __name__ == "__main__":
    # Run setup test
    test_voice_setup()
