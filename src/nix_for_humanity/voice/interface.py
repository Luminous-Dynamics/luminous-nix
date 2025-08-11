"""
Main Voice Interface for Nix for Humanity.

Coordinates speech recognition, processing, and synthesis for a complete
voice-controlled experience.

Since: v1.0.0
"""

import asyncio
import queue
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..constants import DEFAULT_TIMEOUT
from ..core import NixForHumanityBackend
from ..core.logging_config import get_logger
from ..types import ExecutionContext
from .recognition import RecognitionResult, SpeechRecognizer
from .synthesis import SpeechSynthesizer, Voice
from .wake_word import WakeWordDetector

logger = get_logger(__name__)


class VoiceState(Enum):
    """Voice interface states."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class VoiceConfig:
    """
    Voice interface configuration.

    Since: v1.0.0
    """

    wake_word: str = "nix"
    language: str = "en-US"
    voice: Voice = Voice.DEFAULT
    continuous_mode: bool = False
    noise_threshold: float = 0.3
    silence_timeout: float = 2.0
    confirmation_required: bool = True
    audio_feedback: bool = True
    verbose_responses: bool = True


class VoiceInterface:
    """
    Main voice interface for natural language control.

    Provides a complete voice interaction system with wake word detection,
    speech recognition, command processing, and speech synthesis.

    Features:
        - Wake word activation ("Hey Nix")
        - Continuous listening mode
        - Real-time feedback
        - Confirmation for dangerous operations
        - Accessibility-focused design

    Since: v1.0.0
    """

    def __init__(self, config: VoiceConfig | None = None):
        """
        Initialize voice interface.

        Args:
            config: Voice configuration
        """
        self.config = config or VoiceConfig()
        self.state = VoiceState.IDLE

        # Initialize components
        self.recognizer = SpeechRecognizer(
            language=self.config.language, noise_threshold=self.config.noise_threshold
        )
        self.synthesizer = SpeechSynthesizer(voice=self.config.voice)
        self.wake_detector = WakeWordDetector(wake_word=self.config.wake_word)

        # Backend for processing
        self.backend = NixForHumanityBackend()
        self.context = ExecutionContext()

        # Threading for continuous listening
        self.listening_thread: threading.Thread | None = None
        self.command_queue: queue.Queue = queue.Queue()
        self.stop_event = threading.Event()

        # Callbacks
        self.on_wake: Callable[[], None] | None = None
        self.on_command: Callable[[str], None] | None = None
        self.on_result: Callable[[Any], None] | None = None
        self.on_error: Callable[[str], None] | None = None

    def start(self) -> bool:
        """
        Start the voice interface.

        Returns:
            True if successfully started
        """
        try:
            logger.info("Starting voice interface...")

            # Test audio systems
            if not self._test_audio():
                logger.error("Audio system test failed")
                return False

            # Start listening thread
            self.stop_event.clear()
            self.listening_thread = threading.Thread(
                target=self._listening_loop, daemon=True
            )
            self.listening_thread.start()

            # Start command processor
            asyncio.create_task(self._process_commands())

            # Welcome message
            if self.config.audio_feedback:
                self.speak("Voice interface ready. Say 'Hey Nix' to begin.")

            logger.info("Voice interface started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start voice interface: {e}")
            self.state = VoiceState.ERROR
            return False

    def stop(self) -> None:
        """Stop the voice interface."""
        logger.info("Stopping voice interface...")

        self.stop_event.set()

        if self.listening_thread:
            self.listening_thread.join(timeout=2)

        self.recognizer.stop()
        self.synthesizer.stop()

        logger.info("Voice interface stopped")

    def _test_audio(self) -> bool:
        """
        Test audio input and output.

        Returns:
            True if audio systems working
        """
        try:
            # Test microphone
            if not self.recognizer.test_microphone():
                logger.error("Microphone test failed")
                return False

            # Test speakers
            if not self.synthesizer.test_speakers():
                logger.error("Speaker test failed")
                return False

            return True

        except Exception as e:
            logger.error(f"Audio test failed: {e}")
            return False

    def _listening_loop(self) -> None:
        """Main listening loop (runs in thread)."""
        logger.debug("Listening loop started")

        while not self.stop_event.is_set():
            try:
                if self.config.continuous_mode or self.state == VoiceState.LISTENING:
                    # Listen for audio
                    result = self.recognizer.listen(timeout=self.config.silence_timeout)

                    if result and result.text:
                        self._handle_speech(result)
                else:
                    # Wait for wake word
                    if self.wake_detector.detect():
                        self._handle_wake()

                # Small delay to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Listening loop error: {e}")
                time.sleep(1)

    def _handle_wake(self) -> None:
        """Handle wake word detection."""
        logger.info("Wake word detected")

        self.state = VoiceState.LISTENING

        # Audio feedback
        if self.config.audio_feedback:
            self.synthesizer.play_sound("activate")

        # Callback
        if self.on_wake:
            self.on_wake()

        # Voice prompt
        self.speak("Yes? How can I help?", wait=False)

    def _handle_speech(self, result: RecognitionResult) -> None:
        """
        Handle recognized speech.

        Args:
            result: Recognition result
        """
        text = result.text.strip()
        confidence = result.confidence

        logger.info(f"Recognized: '{text}' (confidence: {confidence:.2f})")

        # Check confidence threshold
        if confidence < 0.5:
            self.speak("Sorry, I didn't quite catch that. Could you repeat?")
            return

        # Check for cancel commands
        if text.lower() in ["cancel", "never mind", "stop"]:
            self.state = VoiceState.IDLE
            self.speak("Cancelled.")
            return

        # Add to command queue
        self.command_queue.put(text)

        # Callback
        if self.on_command:
            self.on_command(text)

    async def _process_commands(self) -> None:
        """Process commands from queue (async)."""
        while not self.stop_event.is_set():
            try:
                # Get command from queue
                command = self.command_queue.get(timeout=1)

                # Update state
                self.state = VoiceState.PROCESSING

                # Confirmation for dangerous operations
                if self._requires_confirmation(command):
                    if not await self._get_confirmation(command):
                        continue

                # Process command
                result = await self._execute_command(command)

                # Speak result
                self._speak_result(result)

                # Callback
                if self.on_result:
                    self.on_result(result)

                # Return to listening or idle
                if self.config.continuous_mode:
                    self.state = VoiceState.LISTENING
                else:
                    self.state = VoiceState.IDLE

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Command processing error: {e}")
                self.speak(f"Sorry, there was an error: {e}")
                if self.on_error:
                    self.on_error(str(e))

    async def _execute_command(self, command: str) -> dict[str, Any]:
        """
        Execute a voice command.

        Args:
            command: Natural language command

        Returns:
            Execution result
        """
        logger.info(f"Executing command: {command}")

        try:
            # Execute through backend
            result = await self.backend.execute(command, self.context)

            return {
                "success": result.success,
                "output": result.output,
                "command": command,
                "data": result.data,
            }

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "success": False,
                "output": str(e),
                "command": command,
            }

    def _requires_confirmation(self, command: str) -> bool:
        """
        Check if command requires confirmation.

        Args:
            command: Command text

        Returns:
            True if confirmation needed
        """
        if not self.config.confirmation_required:
            return False

        dangerous_keywords = [
            "remove",
            "delete",
            "uninstall",
            "rollback",
            "switch",
            "rebuild",
            "format",
            "wipe",
            "clean",
        ]

        command_lower = command.lower()
        return any(keyword in command_lower for keyword in dangerous_keywords)

    async def _get_confirmation(self, command: str) -> bool:
        """
        Get user confirmation for command.

        Args:
            command: Command to confirm

        Returns:
            True if confirmed
        """
        self.speak(
            f"You want to: {command}. " "Please say 'yes' to confirm or 'no' to cancel."
        )

        # Listen for response
        self.state = VoiceState.LISTENING

        # Wait for response (with timeout)
        start_time = time.time()
        while time.time() - start_time < DEFAULT_TIMEOUT:
            if not self.command_queue.empty():
                response = self.command_queue.get()
                response_lower = response.lower()

                if "yes" in response_lower or "confirm" in response_lower:
                    self.speak("Confirmed.")
                    return True
                if "no" in response_lower or "cancel" in response_lower:
                    self.speak("Cancelled.")
                    return False

            await asyncio.sleep(0.1)

        self.speak("No response received. Cancelling.")
        return False

    def _speak_result(self, result: dict[str, Any]) -> None:
        """
        Speak command result.

        Args:
            result: Command result
        """
        if result["success"]:
            if self.config.verbose_responses:
                message = f"Success. {result['output']}"
            else:
                message = "Done."
        else:
            message = f"Failed. {result['output']}"

        self.speak(message)

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Speak text using synthesizer.

        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        self.state = VoiceState.SPEAKING

        try:
            self.synthesizer.speak(text, wait=wait)
        finally:
            if self.state == VoiceState.SPEAKING:
                self.state = VoiceState.IDLE

    def process_text(self, text: str) -> None:
        """
        Process text as if it was spoken.

        Useful for testing or text-based fallback.

        Args:
            text: Text to process
        """
        self.command_queue.put(text)

    def set_wake_word(self, wake_word: str) -> None:
        """
        Change the wake word.

        Args:
            wake_word: New wake word
        """
        self.config.wake_word = wake_word
        self.wake_detector.set_wake_word(wake_word)
        logger.info(f"Wake word changed to: {wake_word}")

    def toggle_continuous_mode(self) -> bool:
        """
        Toggle continuous listening mode.

        Returns:
            New continuous mode state
        """
        self.config.continuous_mode = not self.config.continuous_mode

        if self.config.continuous_mode:
            self.state = VoiceState.LISTENING
            self.speak("Continuous mode enabled.")
        else:
            self.state = VoiceState.IDLE
            self.speak("Continuous mode disabled. Say wake word to activate.")

        return self.config.continuous_mode
