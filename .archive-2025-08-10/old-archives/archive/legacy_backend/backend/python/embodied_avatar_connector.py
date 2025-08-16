#!/usr/bin/env python3
"""
Embodied Avatar Connector
Bridges NLP system, emotion system, and avatar visualization
"""

import asyncio
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from emotion_system import EmotionNLPConnector, EmotionSystem
from natural_language_executor import NaturalLanguageExecutor
from nix_knowledge_engine import NixOSKnowledgeEngine

# Import pygame for avatar
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Install with: pip install pygame")


class MinimalAvatar:
    """Basic 2D avatar visualization with emotions"""

    def __init__(self, width=400, height=400):
        if not PYGAME_AVAILABLE:
            raise ImportError("pygame is required for avatar visualization")

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Nix - Your AI Partner")
        self.clock = pygame.time.Clock()

        # Avatar properties
        self.x = width // 2
        self.y = height // 2
        self.base_radius = 50
        self.radius = self.base_radius
        self.color = (100, 150, 255)  # Calm blue
        self.particles = []

        # Animation properties
        self.pulse_phase = 0
        self.rotation = 0
        self.glow_intensity = 0.5

    def update_from_emotion(self, emotion_state: dict):
        """Update avatar appearance based on emotion"""
        # Update color
        self.color = emotion_state.get("color", (100, 150, 255))

        # Update animation parameters
        animation = emotion_state.get("animation", {})
        self.pulse_rate = animation.get("pulse_rate", 1.0)
        self.particle_rate = animation.get("particle_rate", 0.5)
        self.glow_intensity = animation.get("glow_intensity", 0.5)

    def update(self, dt):
        """Update avatar animations"""
        # Pulse animation
        self.pulse_phase += dt * self.pulse_rate
        pulse = 1.0 + 0.1 * math.sin(self.pulse_phase * 2 * math.pi)
        self.radius = int(self.base_radius * pulse)

        # Rotation
        self.rotation += dt * 0.5

        # Update particles
        if random.random() < self.particle_rate * dt:
            self.spawn_particle()

        # Update existing particles
        for particle in self.particles[:]:
            particle["y"] -= particle["speed"] * dt
            particle["life"] -= dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def spawn_particle(self):
        """Create a new particle effect"""
        angle = random.uniform(0, 2 * math.pi)
        distance = self.radius + 10
        self.particles.append(
            {
                "x": self.x + distance * math.cos(angle),
                "y": self.y + distance * math.sin(angle),
                "speed": random.uniform(20, 50),
                "life": 1.0,
                "size": random.randint(2, 5),
            }
        )

    def draw(self):
        """Render the avatar"""
        self.screen.fill((20, 20, 30))  # Dark background

        # Draw glow effect
        for i in range(3):
            glow_radius = self.radius + 20 - i * 5
            glow_alpha = int(50 * self.glow_intensity * (1 - i / 3))
            glow_color = tuple(min(255, c + 50) for c in self.color)
            pygame.draw.circle(
                self.screen, glow_color + (glow_alpha,), (self.x, self.y), glow_radius
            )

        # Draw main orb
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

        # Draw particles
        for particle in self.particles:
            alpha = int(255 * particle["life"])
            particle_color = tuple(min(255, c + 100) for c in self.color)
            pygame.draw.circle(
                self.screen,
                particle_color + (alpha,),
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

        pygame.display.flip()


class EmbodiedNixAssistant:
    """Complete integration of NLP, emotions, and avatar"""

    def __init__(self):
        # Initialize components
        self.knowledge_engine = NixOSKnowledgeEngine()
        self.emotion_system = EmotionSystem()
        self.emotion_connector = EmotionNLPConnector(self.emotion_system)
        self.nlp_executor = NaturalLanguageExecutor()

        # Avatar (if pygame available)
        self.avatar = None
        if PYGAME_AVAILABLE:
            try:
                self.avatar = MinimalAvatar()
            except Exception as e:
                print(f"Could not initialize avatar: {e}")

        # Interaction state
        self.conversation_history = []
        self.last_confidence = 0.0

    async def process_input(self, user_input: str) -> dict:
        """Process user input through complete pipeline"""

        # Stage 1: Extract intent and confidence
        intent = self.knowledge_engine.extract_intent(user_input)

        # Simulate confidence score based on intent recognition
        confidence = self._calculate_confidence(intent)

        # Stage 2: Update emotions based on NLP results
        emotion_result = self.emotion_connector.process_nlp_result(
            intent=intent["action"],
            confidence=confidence,
            success=None,  # Will update after execution
        )

        # Stage 3: Update avatar if available
        if self.avatar:
            self.avatar.update_from_emotion(emotion_result)

        # Stage 4: Get solution and format response
        solution = self.knowledge_engine.get_solution(intent)
        response = self.knowledge_engine.format_response(intent, solution)

        # Stage 5: Determine execution success
        success = solution.get("found", False)

        # Update emotion with final result
        final_emotion = self.emotion_connector.process_nlp_result(
            intent=intent["action"], confidence=confidence, success=success
        )

        # Store in history
        self.conversation_history.append(
            {
                "input": user_input,
                "intent": intent,
                "confidence": confidence,
                "emotion": final_emotion,
                "response": response,
                "timestamp": time.time(),
            }
        )

        return {
            "response": response,
            "emotion": final_emotion,
            "confidence": confidence,
            "intent": intent["action"],
        }

    def _calculate_confidence(self, intent: dict) -> float:
        """Calculate confidence score based on intent extraction"""
        if intent["action"] == "unknown":
            return 0.15
        if intent.get("package"):
            # Higher confidence when package is recognized
            if intent["package"] in self.knowledge_engine.package_aliases.values():
                return 0.95
            return 0.75
        # Medium confidence for other recognized intents
        return 0.85

    def run_interactive_demo(self):
        """Run interactive demo with avatar visualization"""
        print("🤖 Embodied Nix Assistant Demo")
        print("=" * 50)
        print("Type 'quit' to exit")
        print()

        # Start avatar animation loop if available
        if self.avatar:
            import threading

            avatar_thread = threading.Thread(target=self._avatar_loop)
            avatar_thread.daemon = True
            avatar_thread.start()

        # Main interaction loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["quit", "exit"]:
                    break

                # Process input
                result = asyncio.run(self.process_input(user_input))

                # Display response with emotion info
                print(f"\nNix: {result['response']}")
                print(
                    f"\n[Emotion: {result['emotion']['emotion']} "
                    f"(intensity: {result['emotion']['intensity']:.2f}), "
                    f"Confidence: {result['confidence']:.0%}]"
                )

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nGoodbye! 👋")
        if self.avatar and PYGAME_AVAILABLE:
            pygame.quit()

    def _avatar_loop(self):
        """Avatar animation loop (runs in separate thread)"""

        running = True
        dt = 0

        while running:
            # Check for pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update avatar
            self.avatar.update(dt)
            self.avatar.draw()

            # Control frame rate
            dt = self.avatar.clock.tick(60) / 1000.0  # 60 FPS

            # Check if emotion should return to calm
            if self.emotion_system.should_return_to_calm():
                self.emotion_system.return_to_calm()
                calm_emotion = self.emotion_connector.process_nlp_result(
                    intent="idle", confidence=0.5, success=True
                )
                self.avatar.update_from_emotion(calm_emotion)


# Demo script
if __name__ == "__main__":
    import math
    import random
    import time

    assistant = EmbodiedNixAssistant()

    if len(sys.argv) > 1:
        # Process single command
        query = " ".join(sys.argv[1:])
        result = asyncio.run(assistant.process_input(query))
        print(result["response"])
        print(
            f"\n[Emotion: {result['emotion']['emotion']}, "
            f"Confidence: {result['confidence']:.0%}]"
        )
    else:
        # Run interactive demo
        assistant.run_interactive_demo()
