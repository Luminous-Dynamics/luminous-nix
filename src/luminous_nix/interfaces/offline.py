"""
Offline Voice Recognition and Synthesis Support.

Provides voice recognition using Whisper and text-to-speech using Piper,
both running completely offline for privacy and performance.

Since: v1.0.1
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try to import Whisper for speech recognition
try:
    import whisper

    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False
    logger.info("Whisper not available - install with: pip install openai-whisper")

# Check for Piper TTS (usually installed as a binary)
HAS_PIPER = subprocess.run(["which", "piper"], capture_output=True).returncode == 0


@dataclass
class OfflineModel:
    """
    Configuration for offline speech model.

    Since: v1.0.1
    """

    name: str
    language: str
    size_mb: int
    accuracy: str  # "low", "medium", "high"
    download_url: str | None
    local_path: Path | None


class OfflineVoiceInterface:
    """
    Offline voice recognition interface.

    Provides speech recognition without internet connection using
    lightweight models that run locally.

    Features:
    - No internet required
    - Privacy-preserving (all processing local)
    - Multiple model sizes (50MB to 1GB)
    - Support for multiple languages

    Since: v1.0.1
    """

    # Available models
    MODELS = {
        "vosk-small-en": OfflineModel(
            name="vosk-model-small-en-us-0.15",
            language="en-US",
            size_mb=40,
            accuracy="medium",
            download_url="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            local_path=None,
        ),
        "vosk-large-en": OfflineModel(
            name="vosk-model-en-us-0.22",
            language="en-US",
            size_mb=1800,
            accuracy="high",
            download_url="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
            local_path=None,
        ),
        "pocketsphinx-en": OfflineModel(
            name="pocketsphinx-en-us",
            language="en-US",
            size_mb=30,
            accuracy="low",
            download_url=None,  # Comes with pocketsphinx
            local_path=None,
        ),
    }

    def __init__(self, model_name: str = "vosk-small-en"):
        """
        Initialize offline voice interface.

        Args:
            model_name: Name of model to use

        Since: v1.0.1
        """
        self.model_name = model_name
        self.model_config = self.MODELS.get(model_name)

        if not self.model_config:
            raise ValueError(f"Unknown model: {model_name}")

        self.recognizer = None
        self.model = None

        # Initialize based on model type
        if model_name.startswith("vosk"):
            self._init_vosk()
        elif model_name.startswith("pocketsphinx"):
            self._init_pocketsphinx()

    def _init_vosk(self):
        """Initialize Vosk recognizer."""
        if not HAS_VOSK:
            raise ImportError("Vosk not installed. Run: pip install vosk")

        # Set up model path
        model_path = self._get_model_path()

        if not model_path or not model_path.exists():
            logger.warning(f"Model not found at {model_path}")
            logger.info(f"Download from: {self.model_config.download_url}")
            raise FileNotFoundError(f"Model {self.model_name} not found")

        # Load model
        try:
            self.model = vosk.Model(str(model_path))
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            logger.info(f"Loaded Vosk model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            raise

    def _init_pocketsphinx(self):
        """Initialize PocketSphinx recognizer."""
        if not HAS_POCKETSPHINX:
            raise ImportError(
                "PocketSphinx not installed. Run: pip install pocketsphinx"
            )

        try:
            # PocketSphinx setup is simpler - uses built-in models
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()
            logger.info("Initialized PocketSphinx")
        except Exception as e:
            logger.error(f"Failed to initialize PocketSphinx: {e}")
            raise

    def _get_model_path(self) -> Path | None:
        """Get path to model files."""
        # Check common locations
        possible_paths = [
            Path.home() / ".cache" / "vosk" / self.model_config.name,
            Path.home() / ".local" / "share" / "vosk" / self.model_config.name,
            Path("/usr/share/vosk-models") / self.model_config.name,
            Path.cwd() / "models" / self.model_config.name,
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def recognize(self, audio_data: bytes, sample_rate: int = 16000) -> str | None:
        """
        Recognize speech from audio data.

        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate

        Returns:
            Recognized text or None

        Since: v1.0.1
        """
        if self.model_name.startswith("vosk"):
            return self._recognize_vosk(audio_data)
        if self.model_name.startswith("pocketsphinx"):
            return self._recognize_pocketsphinx(audio_data)

        return None

    def _recognize_vosk(self, audio_data: bytes) -> str | None:
        """Recognize using Vosk."""
        if not self.recognizer:
            return None

        try:
            # Process audio in chunks
            chunk_size = 4000

            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i : i + chunk_size]
                self.recognizer.AcceptWaveform(chunk)

            # Get final result
            result = json.loads(self.recognizer.FinalResult())
            text = result.get("text", "")

            return text if text else None

        except Exception as e:
            logger.error(f"Vosk recognition failed: {e}")
            return None

    def _recognize_pocketsphinx(self, audio_data: bytes) -> str | None:
        """Recognize using PocketSphinx."""
        try:
            import speech_recognition as sr

            # Convert bytes to AudioData
            audio = sr.AudioData(audio_data, 16000, 2)

            # Recognize
            text = self.recognizer.recognize_sphinx(audio)
            return text if text else None

        except Exception as e:
            logger.error(f"PocketSphinx recognition failed: {e}")
            return None

    def download_model(self, model_name: str | None = None) -> bool:
        """
        Download model for offline use.

        Args:
            model_name: Model to download (or current model)

        Returns:
            True if successful

        Since: v1.0.1
        """
        model_name = model_name or self.model_name
        model_config = self.MODELS.get(model_name)

        if not model_config or not model_config.download_url:
            logger.error(f"No download URL for model: {model_name}")
            return False

        try:
            import urllib.request
            import zipfile

            # Download location
            cache_dir = Path.home() / ".cache" / "vosk"
            cache_dir.mkdir(parents=True, exist_ok=True)

            model_zip = cache_dir / f"{model_config.name}.zip"

            # Download if not exists
            if not model_zip.exists():
                logger.info(
                    f"Downloading {model_config.name} ({model_config.size_mb}MB)..."
                )
                urllib.request.urlretrieve(model_config.download_url, model_zip)

            # Extract
            model_dir = cache_dir / model_config.name
            if not model_dir.exists():
                logger.info("Extracting model...")
                with zipfile.ZipFile(model_zip, "r") as zip_ref:
                    zip_ref.extractall(cache_dir)

            logger.info(f"Model ready at: {model_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False

    def list_available_models(self) -> dict[str, dict[str, Any]]:
        """
        List available offline models.

        Returns:
            Dictionary of model information

        Since: v1.0.1
        """
        models = {}

        for name, config in self.MODELS.items():
            # Check if installed
            config.local_path = self._get_model_path()
            installed = config.local_path is not None

            models[name] = {
                "name": config.name,
                "language": config.language,
                "size_mb": config.size_mb,
                "accuracy": config.accuracy,
                "installed": installed,
                "download_url": config.download_url,
            }

        return models

    def test_microphone(self) -> bool:
        """
        Test if microphone works with offline recognition.

        Returns:
            True if working

        Since: v1.0.1
        """
        try:
            import pyaudio

            # Test audio input
            p = pyaudio.PyAudio()

            # Try to open stream
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000,
            )

            # Read a bit of audio
            data = stream.read(1000)

            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()

            return len(data) > 0

        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False

    def continuous_recognition(self, callback):
        """
        Continuous recognition mode.

        Args:
            callback: Function to call with recognized text

        Since: v1.0.1
        """
        if not HAS_VOSK or not self.recognizer:
            logger.error("Continuous recognition requires Vosk")
            return

        try:
            import pyaudio

            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8000,
            )
            stream.start_stream()

            logger.info("Listening... Press Ctrl+C to stop")

            while True:
                data = stream.read(4000, exception_on_overflow=False)

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")

                    if text:
                        callback(text)
                else:
                    # Partial result
                    partial = json.loads(self.recognizer.PartialResult())
                    # Could show partial results if desired

        except KeyboardInterrupt:
            logger.info("Stopping...")
        except Exception as e:
            logger.error(f"Continuous recognition error: {e}")
        finally:
            if "stream" in locals():
                stream.stop_stream()
                stream.close()
            if "p" in locals():
                p.terminate()


def setup_offline_voice() -> bool:
    """
    One-time setup for offline voice recognition.

    Downloads small model and tests functionality.

    Returns:
        True if setup successful

    Since: v1.0.1
    """
    try:
        # Install dependencies
        logger.info("Setting up offline voice recognition...")

        # Create interface
        voice = OfflineVoiceInterface("vosk-small-en")

        # Download model if needed
        if not voice._get_model_path():
            logger.info("Downloading offline model (40MB)...")
            if not voice.download_model():
                logger.error("Failed to download model")
                return False

        # Test microphone
        if not voice.test_microphone():
            logger.warning("Microphone test failed - check audio input")

        logger.info("Offline voice recognition ready!")
        return True

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        logger.info("Manual setup required:")
        logger.info("1. pip install vosk pyaudio")
        logger.info("2. Download model from https://alphacephei.com/vosk/models")
        return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Setup
    if setup_offline_voice():
        # Test recognition
        voice = OfflineVoiceInterface("vosk-small-en")

        # List models
        print("\nAvailable models:")
        for name, info in voice.list_available_models().items():
            status = "✓" if info["installed"] else "✗"
            print(
                f"  [{status}] {name}: {info['size_mb']}MB, {info['accuracy']} accuracy"
            )

        # Test continuous recognition
        def on_recognized(text):
            print(f"Heard: {text}")
            if "stop" in text.lower():
                return False
            return True

        print("\nStarting continuous recognition. Say 'stop' to end.")
        voice.continuous_recognition(on_recognized)
