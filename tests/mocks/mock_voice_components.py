"""
Mock components for voice interface testing.

Provides mocks for audio devices, speech recognition, and TTS.
"""

# REMOVED MOCK IMPORT: Mock, AsyncMock, MagicMock
from typing import Any

import numpy as np


class MockAudioDevice:
    """Mock audio input/output device."""

    def __init__(self, device_name: str = "Mock Audio Device"):
        self.device_name = device_name
        self.is_recording = False
        self.is_playing = False
        self.sample_rate = 16000
        self.channels = 1

    def start_recording(self):
        """Start recording audio."""
        self.is_recording = True

    def stop_recording(self):
        """Stop recording audio."""
        self.is_recording = False

    def get_audio_data(self, duration: float = 1.0) -> np.ndarray:
        """Generate mock audio data."""
        samples = int(self.sample_rate * duration)
        # Generate a simple sine wave
        t = np.linspace(0, duration, samples)
        audio = np.sin(2 * np.pi * 440 * t) * 0.5
        return audio.astype(np.float32)


class MockWhisperModel:
    """Mock Whisper speech recognition model."""

    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self.language = "en"

    def transcribe(
        self, audio: np.ndarray, language: str | None = None
    ) -> dict[str, Any]:
        """Mock transcription."""
        # Return different text based on audio length
        duration = len(audio) / 16000  # Assuming 16kHz

        if duration < 1:
            text = "test"
        elif duration < 3:
            text = "install firefox"
        else:
            text = "please help me set up a development environment for python"

        return {
            "text": text,
            "language": language or self.language,
            "segments": [{"text": text, "start": 0.0, "end": duration}],
            "duration": duration,
        }


class MockPiperTTS:
    """Mock Piper text-to-speech engine."""

    def __init__(self, voice: str = "en_US-amy-low"):
        self.voice = voice
        self.rate = 1.0

    def synthesize(self, text: str) -> np.ndarray:
        """Mock TTS synthesis."""
        # Generate audio based on text length
        words = len(text.split())
        duration = words * 0.5  # Rough estimate: 0.5 seconds per word

        samples = int(16000 * duration)
        # Generate a simple audio pattern
        audio = np.random.randn(samples) * 0.1
        return audio.astype(np.float32)


class MockWakeWordDetector:
    """Mock wake word detector."""

    def __init__(self, wake_word: str = "hey nix"):
        self.wake_word = wake_word
        self.sensitivity = 0.5
        self.detection_count = 0

    def detect(self, audio: np.ndarray) -> bool:
        """Mock wake word detection."""
        # Simulate detection based on audio energy
        energy = np.mean(np.abs(audio))

        # Simulate some randomness but mostly detect on higher energy
        if energy > 0.1:
            self.detection_count += 1
            return self.detection_count % 3 == 1  # Detect every 3rd time
        return False


class MockVoiceActivityDetector:
    """Mock voice activity detection."""

    def __init__(self):
        self.energy_threshold = 0.05
        self.speech_detected = False

    def is_speech(self, audio: np.ndarray) -> bool:
        """Detect if audio contains speech."""
        energy = np.mean(np.abs(audio))
        self.speech_detected = energy > self.energy_threshold
        return self.speech_detected

    def get_speech_segments(self, audio: np.ndarray) -> list:
        """Get speech segments from audio."""
        # Simple mock: return one segment if speech detected
        if self.is_speech(audio):
            duration = len(audio) / 16000
            return [(0.0, duration)]
        return []


def create_mock_voice_components():
    """Create a complete set of mock voice components."""
    return {
        "audio_device": MockAudioDevice(),
        "whisper_model": MockWhisperModel(),
        "piper_tts": MockPiperTTS(),
        "wake_word_detector": MockWakeWordDetector(),
        "vad": MockVoiceActivityDetector(),
    }


def mock_sounddevice():
    """Create mock for sounddevice module."""
    mock_sd = MagicMock()

    # Mock query_devices
    mock_sd.query_devices.return_value = [
        {
            "name": "Built-in Microphone",
            "max_input_channels": 1,
            "max_output_channels": 0,
            "default_samplerate": 44100.0,
        },
        {
            "name": "Built-in Output",
            "max_input_channels": 0,
            "max_output_channels": 2,
            "default_samplerate": 44100.0,
        },
    ]

    # Mock InputStream
    class MockInputStream:
        def __init__(self, callback=None, **kwargs):
            self.callback = callback
            self.is_active = False

        def start(self):
            self.is_active = True

        def stop(self):
            self.is_active = False

        def close(self):
            self.is_active = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    mock_sd.InputStream = MockInputStream

    # Mock play function
    def mock_play(data, samplerate=44100, **kwargs):
        pass

    mock_sd.play = mock_play
    mock_sd.wait = Mock()

    return mock_sd
