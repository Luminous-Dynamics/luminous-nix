#!/usr/bin/env python3
"""
from typing import List, Tuple, Dict, Optional
Emotion System for Embodied AI Partner
Connects NLP confidence to emotional states for avatar visualization
"""

import time
from dataclasses import dataclass
from enum import Enum


class EmotionType(Enum):
    """Core emotional states for the AI partner"""

    HAPPY = "happy"  # High confidence, successful operations
    THINKING = "thinking"  # Processing, medium confidence
    CONFUSED = "confused"  # Low confidence, unclear intent
    EXCITED = "excited"  # New discovery, learning moment
    CALM = "calm"  # Default state, idle
    CONCERNED = "concerned"  # Error states, warnings
    PROUD = "proud"  # Task completed successfully
    CURIOUS = "curious"  # Exploring new patterns


@dataclass
class EmotionState:
    """Current emotional state with intensity and context"""

    primary: EmotionType
    intensity: float  # 0.0 to 1.0
    secondary: EmotionType | None = None
    secondary_intensity: float = 0.0
    reason: str = ""
    duration: float = 2.0  # seconds to maintain emotion


class EmotionSystem:
    """Maps NLP confidence and system states to emotional expressions"""

    def __init__(self):
        self.current_emotion = EmotionState(EmotionType.CALM, 0.5)
        self.emotion_history = []
        self.last_update = time.time()

        # Confidence to emotion mapping
        self.confidence_thresholds = {
            0.95: EmotionType.HAPPY,  # Very high confidence
            0.80: EmotionType.CALM,  # Good confidence
            0.60: EmotionType.THINKING,  # Medium confidence
            0.40: EmotionType.CONFUSED,  # Low confidence
            0.0: EmotionType.CONCERNED,  # Very low/error
        }

        # Event-based emotions
        self.event_emotions = {
            "learning": EmotionType.EXCITED,
            "success": EmotionType.PROUD,
            "error": EmotionType.CONCERNED,
            "discovery": EmotionType.CURIOUS,
            "helping": EmotionType.HAPPY,
        }

    def update_from_nlp_confidence(
        self, confidence: float, intent: str = None
    ) -> EmotionState:
        """Update emotion based on NLP confidence score"""
        # Find appropriate emotion for confidence level
        emotion = EmotionType.CALM
        for threshold, emotion_type in sorted(
            self.confidence_thresholds.items(), reverse=True
        ):
            if confidence >= threshold:
                emotion = emotion_type
                break

        # Calculate intensity based on confidence
        if confidence >= 0.8:
            intensity = 0.5 + (confidence - 0.8) * 2.5  # 0.5-1.0 for high confidence
        elif confidence >= 0.4:
            intensity = 0.3 + (confidence - 0.4) * 0.5  # 0.3-0.5 for medium
        else:
            intensity = (
                0.7 + (0.4 - confidence) * 0.75
            )  # 0.7-1.0 for low (more intense confusion)

        # Add context-specific adjustments
        reason = f"Intent recognition confidence: {confidence:.0%}"
        if intent:
            reason += f" for '{intent}'"

            # Special emotions for certain intents
            if "help" in intent.lower():
                emotion = EmotionType.HAPPY
                reason = "I love helping!"
            elif "learn" in intent.lower():
                emotion = EmotionType.CURIOUS
                reason = "Learning something new!"

        # Create new emotion state
        new_emotion = EmotionState(
            primary=emotion, intensity=min(1.0, intensity), reason=reason
        )

        self._update_emotion(new_emotion)
        return self.current_emotion

    def update_from_event(self, event_type: str, details: dict = None) -> EmotionState:
        """Update emotion based on system events"""
        emotion = self.event_emotions.get(event_type, EmotionType.CALM)
        intensity = 0.7  # Default intensity for events

        # Event-specific handling
        if event_type == "learning":
            reason = "I learned something new!"
            if details and "pattern" in details:
                reason = f"I learned: {details['pattern']}"
                intensity = 0.8

        elif event_type == "success":
            reason = "Task completed successfully!"
            if details and "operation" in details:
                reason = f"Successfully {details['operation']}!"
                intensity = 0.9

        elif event_type == "error":
            emotion = EmotionType.CONCERNED
            reason = "Something went wrong"
            if details and "error" in details:
                reason = f"Error: {details['error']}"
                intensity = 0.8

        elif event_type == "discovery":
            reason = "I discovered something interesting!"
            intensity = 0.85

        else:
            reason = event_type

        new_emotion = EmotionState(primary=emotion, intensity=intensity, reason=reason)

        self._update_emotion(new_emotion)
        return self.current_emotion

    def blend_emotions(
        self, primary: EmotionType, secondary: EmotionType, blend_factor: float = 0.3
    ) -> EmotionState:
        """Create a blended emotion state"""
        new_emotion = EmotionState(
            primary=primary,
            intensity=0.7,
            secondary=secondary,
            secondary_intensity=blend_factor,
            reason="Complex emotional state",
        )

        self._update_emotion(new_emotion)
        return self.current_emotion

    def get_animation_params(self) -> dict:
        """Get parameters for avatar animation based on emotion"""
        params = {
            "emotion": self.current_emotion.primary.value,
            "intensity": self.current_emotion.intensity,
            "pulse_rate": 1.0,
            "color_shift": 0.0,
            "particle_rate": 0.5,
            "glow_intensity": 0.5,
        }

        # Emotion-specific parameters
        if self.current_emotion.primary == EmotionType.HAPPY:
            params["pulse_rate"] = 1.2
            params["particle_rate"] = 0.8
            params["glow_intensity"] = 0.7

        elif self.current_emotion.primary == EmotionType.THINKING:
            params["pulse_rate"] = 0.8
            params["color_shift"] = 0.1  # Slight color variation

        elif self.current_emotion.primary == EmotionType.CONFUSED:
            params["pulse_rate"] = 1.5
            params["color_shift"] = 0.3  # More color variation
            params["particle_rate"] = 0.3

        elif self.current_emotion.primary == EmotionType.EXCITED:
            params["pulse_rate"] = 2.0
            params["particle_rate"] = 1.0
            params["glow_intensity"] = 0.9

        elif self.current_emotion.primary == EmotionType.CONCERNED:
            params["pulse_rate"] = 0.5
            params["glow_intensity"] = 0.3
            params["particle_rate"] = 0.2

        # Apply intensity scaling
        params["pulse_rate"] = (
            1.0 + (params["pulse_rate"] - 1.0) * self.current_emotion.intensity
        )
        params["particle_rate"] *= self.current_emotion.intensity

        return params

    def get_color_for_emotion(self) -> tuple[int, int, int]:
        """Get RGB color for current emotion"""
        colors = {
            EmotionType.HAPPY: (100, 255, 150),  # Bright green
            EmotionType.THINKING: (150, 200, 255),  # Light blue
            EmotionType.CONFUSED: (255, 200, 100),  # Orange
            EmotionType.EXCITED: (255, 100, 255),  # Magenta
            EmotionType.CALM: (100, 150, 255),  # Calm blue
            EmotionType.CONCERNED: (255, 100, 100),  # Red
            EmotionType.PROUD: (255, 215, 0),  # Gold
            EmotionType.CURIOUS: (200, 150, 255),  # Purple
        }

        primary_color = colors.get(self.current_emotion.primary, (100, 150, 255))

        # Blend with secondary emotion if present
        if self.current_emotion.secondary:
            secondary_color = colors.get(self.current_emotion.secondary, primary_color)
            blend = self.current_emotion.secondary_intensity

            color = tuple(
                int(primary_color[i] * (1 - blend) + secondary_color[i] * blend)
                for i in range(3)
            )
            return color

        return primary_color

    def _update_emotion(self, new_emotion: EmotionState):
        """Internal method to update emotion and track history"""
        # Add to history
        self.emotion_history.append(
            {"emotion": self.current_emotion, "timestamp": time.time()}
        )

        # Keep only recent history (last 10 emotions)
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)

        # Update current emotion
        self.current_emotion = new_emotion
        self.last_update = time.time()

    def get_emotion_duration_remaining(self) -> float:
        """Get remaining time for current emotion display"""
        elapsed = time.time() - self.last_update
        remaining = max(0, self.current_emotion.duration - elapsed)
        return remaining

    def should_return_to_calm(self) -> bool:
        """Check if emotion should return to calm state"""
        return self.get_emotion_duration_remaining() <= 0

    def return_to_calm(self):
        """Gradually return to calm state"""
        if self.current_emotion.primary != EmotionType.CALM:
            # Reduce intensity first
            if self.current_emotion.intensity > 0.5:
                self.current_emotion.intensity *= 0.9
            else:
                # Then switch to calm
                self._update_emotion(
                    EmotionState(
                        primary=EmotionType.CALM,
                        intensity=0.5,
                        reason="Returning to rest",
                    )
                )


class EmotionNLPConnector:
    """Connects NLP system to emotion system"""

    def __init__(self, emotion_system: EmotionSystem):
        self.emotion_system = emotion_system
        self.last_confidence = 0.0

    def process_nlp_result(
        self, intent: str, confidence: float, success: bool = None, error: str = None
    ) -> dict[str, any]:
        """Process NLP result and update emotions accordingly"""

        # Update based on confidence
        emotion_state = self.emotion_system.update_from_nlp_confidence(
            confidence, intent
        )

        # Additional event-based updates
        if error:
            emotion_state = self.emotion_system.update_from_event(
                "error", {"error": error}
            )
        elif success is True:
            emotion_state = self.emotion_system.update_from_event(
                "success", {"operation": intent}
            )
        elif confidence > self.last_confidence + 0.2:
            # Significant confidence increase - learning!
            emotion_state = self.emotion_system.update_from_event(
                "learning", {"pattern": intent}
            )

        self.last_confidence = confidence

        # Get animation parameters
        animation = self.emotion_system.get_animation_params()
        color = self.emotion_system.get_color_for_emotion()

        return {
            "emotion": emotion_state.primary.value,
            "intensity": emotion_state.intensity,
            "reason": emotion_state.reason,
            "animation": animation,
            "color": color,
            "duration": emotion_state.duration,
        }

    def process_interaction_flow(self, interaction_stages: list[dict]) -> list[dict]:
        """Process a complete interaction flow with emotional journey"""
        emotional_journey = []

        for stage in interaction_stages:
            stage_emotion = self.process_nlp_result(
                intent=stage.get("intent", ""),
                confidence=stage.get("confidence", 0.5),
                success=stage.get("success"),
                error=stage.get("error"),
            )

            emotional_journey.append(
                {
                    "stage": stage.get("stage", "processing"),
                    "emotion": stage_emotion,
                    "timestamp": time.time(),
                }
            )

            # Small delay between stages for natural flow
            time.sleep(0.1)

        return emotional_journey


# Example usage and testing
if __name__ == "__main__":
    # Create emotion system
    emotion_system = EmotionSystem()
    connector = EmotionNLPConnector(emotion_system)

    print("🎭 Emotion System Test\n" + "=" * 50)

    # Test different confidence levels
    test_cases = [
        {"intent": "install firefox", "confidence": 0.98, "success": True},
        {"intent": "fix network", "confidence": 0.45, "success": None},
        {"intent": "help me learn", "confidence": 0.75, "success": None},
        {
            "intent": "unknown command",
            "confidence": 0.15,
            "error": "Intent not recognized",
        },
        {"intent": "update system", "confidence": 0.92, "success": True},
    ]

    for test in test_cases:
        result = connector.process_nlp_result(**test)
        print(f"\nIntent: {test['intent']}")
        print(f"Confidence: {test['confidence']:.0%}")
        print(f"Emotion: {result['emotion']} (intensity: {result['intensity']:.2f})")
        print(f"Reason: {result['reason']}")
        print(f"Color: RGB{result['color']}")
        print(
            f"Animation: pulse={result['animation']['pulse_rate']:.1f}, "
            f"particles={result['animation']['particle_rate']:.1f}"
        )

        time.sleep(0.5)

    # Test interaction flow
    print("\n" + "=" * 50)
    print("Testing interaction flow...")

    interaction = [
        {"stage": "greeting", "intent": "hello", "confidence": 0.95},
        {"stage": "understanding", "intent": "install vscode", "confidence": 0.7},
        {"stage": "processing", "intent": "install vscode", "confidence": 0.85},
        {
            "stage": "complete",
            "intent": "install vscode",
            "confidence": 0.98,
            "success": True,
        },
    ]

    journey = connector.process_interaction_flow(interaction)

    print("\nEmotional Journey:")
    for step in journey:
        print(
            f"  {step['stage']}: {step['emotion']['emotion']} "
            f"({step['emotion']['intensity']:.2f})"
        )
