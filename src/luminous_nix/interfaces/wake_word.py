"""
Wake Word Detection for Voice Interface.

Listens for activation phrases like "Hey Nix" to trigger voice commands.

Since: v1.0.0
"""

import time
from dataclasses import dataclass

from ..core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class WakeWordConfig:
    """
    Wake word detection configuration.

    Since: v1.0.0
    """

    wake_words: list[str]
    sensitivity: float = 0.5
    timeout: float = 10.0
    cooldown: float = 2.0


class WakeWordDetector:
    """
    Detects wake words to activate voice interface.

    Provides always-listening capability with low CPU usage.
    Supports multiple wake words and custom sensitivity.

    Since: v1.0.0
    """

    def __init__(self, wake_word: str = "hey nix", sensitivity: float = 0.5):
        """
        Initialize wake word detector.

        Args:
            wake_word: Primary wake word
            sensitivity: Detection sensitivity (0-1)
        """
        self.wake_words = [wake_word.lower()]
        self.sensitivity = sensitivity
        self.last_detection = 0
        self.cooldown = 2.0  # Seconds between detections

        # Try to import recognition
        try:
            import speech_recognition as sr

            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.available = True
        except ImportError:
            self.recognizer = None
            self.microphone = None
            self.available = False
            logger.warning("Speech recognition not available for wake word")

    def detect(self, timeout: float = 1.0) -> bool:
        """
        Listen for wake word.

        Args:
            timeout: Maximum time to listen

        Returns:
            True if wake word detected
        """
        if not self.available:
            return False

        # Check cooldown
        if time.time() - self.last_detection < self.cooldown:
            return False

        try:
            # Quick listen for wake word
            with self.microphone as source:
                # Very short timeout for wake word detection
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=2
                )

            # Quick recognition
            text = self._quick_recognize(audio)

            if text and self._contains_wake_word(text):
                logger.info(f"Wake word detected: {text}")
                self.last_detection = time.time()
                return True

            return False

        except Exception:
            # Timeouts are expected and normal
            return False

    def _quick_recognize(self, audio) -> str | None:
        """
        Quick speech recognition for wake word.

        Args:
            audio: Audio data

        Returns:
            Recognized text
        """
        try:
            # Use Google for quick recognition
            text = self.recognizer.recognize_google(audio, language="en-US")
            return text.lower()
        except:
            return None

    def _contains_wake_word(self, text: str) -> bool:
        """
        Check if text contains wake word.

        Args:
            text: Recognized text

        Returns:
            True if wake word found
        """
        text_lower = text.lower()

        for wake_word in self.wake_words:
            # Exact match
            if wake_word in text_lower:
                return True

            # Fuzzy match for similar sounding words
            if self._fuzzy_match(wake_word, text_lower):
                return True

        return False

    def _fuzzy_match(self, wake_word: str, text: str) -> bool:
        """
        Fuzzy matching for wake words.

        Args:
            wake_word: Expected wake word
            text: Recognized text

        Returns:
            True if fuzzy match found
        """
        # Simple fuzzy matching
        wake_parts = wake_word.split()
        text_parts = text.split()

        matches = 0
        for wake_part in wake_parts:
            for text_part in text_parts:
                if self._similar(wake_part, text_part):
                    matches += 1
                    break

        # Require most parts to match
        required_matches = max(1, len(wake_parts) * self.sensitivity)
        return matches >= required_matches

    def _similar(self, word1: str, word2: str) -> bool:
        """
        Check if two words are similar.

        Args:
            word1: First word
            word2: Second word

        Returns:
            True if similar
        """
        # Simple similarity check
        if word1 == word2:
            return True

        # Check if one is substring of other
        if len(word1) > 2 and len(word2) > 2:
            if word1 in word2 or word2 in word1:
                return True

        # Levenshtein distance would be better but keeping it simple
        return False

    def set_wake_word(self, wake_word: str) -> None:
        """
        Change the wake word.

        Args:
            wake_word: New wake word
        """
        self.wake_words = [wake_word.lower()]
        logger.info(f"Wake word set to: {wake_word}")

    def add_wake_word(self, wake_word: str) -> None:
        """
        Add an additional wake word.

        Args:
            wake_word: Additional wake word
        """
        wake_word_lower = wake_word.lower()
        if wake_word_lower not in self.wake_words:
            self.wake_words.append(wake_word_lower)
            logger.info(f"Added wake word: {wake_word}")

    def set_sensitivity(self, sensitivity: float) -> None:
        """
        Adjust detection sensitivity.

        Args:
            sensitivity: Sensitivity level (0-1)
        """
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        logger.info(f"Sensitivity set to: {self.sensitivity}")
