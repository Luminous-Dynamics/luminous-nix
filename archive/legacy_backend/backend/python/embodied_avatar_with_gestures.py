#!/usr/bin/env python3
"""
from typing import Tuple
Enhanced Embodied Avatar with Gesture System
Integrates gesture system with avatar visualization for complete expression
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import asyncio
import time
import math
import random

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
sys.path.insert(0, str(Path(__file__).parent))

# Import our modules
from nix_knowledge_engine import NixOSKnowledgeEngine
from emotion_system import EmotionSystem, EmotionNLPConnector, EmotionType
from gesture_system import GestureSystem, GestureNLPConnector, GestureType, GestureRenderer
from natural_language_executor import NaturalLanguageExecutor

# Import pygame for enhanced avatar
try:
    import pygame
    import pygame.gfxdraw
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Install with: pip install pygame")


class EnhancedAvatar:
    """Enhanced avatar with emotions and gestures"""
    
    def __init__(self, width=800, height=600):
        if not PYGAME_AVAILABLE:
            raise ImportError("pygame is required for avatar visualization")
            
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Nix - Your Embodied AI Partner")
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        
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
        self.pulse_rate = 1.0
        self.particle_rate = 0.5
        
        # Gesture offset
        self.gesture_offset_x = 0
        self.gesture_offset_y = 0
        
        # Initialize renderers
        self.gesture_renderer = GestureRenderer(width, height)
        
    def update_from_emotion(self, emotion_state: Dict):
        """Update avatar appearance based on emotion"""
        # Map emotions to colors
        emotion_colors = {
            EmotionType.HAPPY: (255, 200, 100),      # Warm yellow
            EmotionType.THINKING: (150, 150, 255),   # Thoughtful blue
            EmotionType.CONFUSED: (200, 150, 200),   # Purple
            EmotionType.EXCITED: (255, 150, 100),    # Orange
            EmotionType.CALM: (100, 150, 255),       # Calm blue
            EmotionType.CONCERNED: (255, 100, 100),  # Concerned red
            EmotionType.PROUD: (100, 255, 150),      # Proud green
            EmotionType.CURIOUS: (255, 255, 150)     # Curious yellow
        }
        
        emotion_type = EmotionType(emotion_state['emotion'])
        self.color = emotion_colors.get(emotion_type, (100, 150, 255))
        
        # Update animation parameters
        animation = emotion_state.get('animation', {})
        self.pulse_rate = animation.get('pulse_rate', 1.0)
        self.particle_rate = animation.get('particle_rate', 0.5)
        self.glow_intensity = animation.get('glow_intensity', 0.5)
        
    def update_from_gesture(self, gesture_offset: Tuple[float, float]):
        """Update avatar position offset from gesture"""
        self.gesture_offset_x, self.gesture_offset_y = gesture_offset
        
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
            particle['y'] -= particle['speed'] * dt
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def spawn_particle(self):
        """Create a new particle effect"""
        angle = random.uniform(0, 2 * math.pi)
        distance = self.radius + 10
        self.particles.append({
            'x': self.x + self.gesture_offset_x + distance * math.cos(angle),
            'y': self.y + self.gesture_offset_y + distance * math.sin(angle),
            'speed': random.uniform(20, 50),
            'life': 1.0,
            'size': random.randint(2, 5)
        })
    
    def draw(self, current_gesture=None):
        """Render the avatar with gestures"""
        self.screen.fill((20, 20, 30))  # Dark background
        
        # Calculate avatar position with gesture offset
        avatar_x = int(self.x + self.gesture_offset_x)
        avatar_y = int(self.y + self.gesture_offset_y)
        
        # Draw pointing indicator if pointing gesture
        if current_gesture and current_gesture.type == GestureType.POINTING and current_gesture.target_point:
            self.gesture_renderer.render_pointing_indicator(
                self.screen, 
                (avatar_x, avatar_y),
                current_gesture.target_point,
                current_gesture.progress
            )
        
        # Draw glow effect
        for i in range(3):
            glow_radius = self.radius + 20 - i * 5
            glow_alpha = int(50 * self.glow_intensity * (1 - i/3))
            glow_color = tuple(min(255, c + 50) for c in self.color)
            
            # Anti-aliased circle for smooth glow
            pygame.gfxdraw.filled_circle(
                self.screen, avatar_x, avatar_y, 
                glow_radius, glow_color + (glow_alpha,)
            )
            pygame.gfxdraw.aacircle(
                self.screen, avatar_x, avatar_y,
                glow_radius, glow_color
            )
        
        # Draw main orb
        pygame.gfxdraw.filled_circle(
            self.screen, avatar_x, avatar_y, 
            self.radius, self.color
        )
        pygame.gfxdraw.aacircle(
            self.screen, avatar_x, avatar_y,
            self.radius, self.color
        )
        
        # Draw inner highlight for depth
        highlight_x = avatar_x - self.radius // 3
        highlight_y = avatar_y - self.radius // 3
        highlight_radius = self.radius // 3
        highlight_color = tuple(min(255, c + 100) for c in self.color)
        
        pygame.gfxdraw.filled_circle(
            self.screen, highlight_x, highlight_y,
            highlight_radius, highlight_color + (100,)
        )
        
        # Draw particles
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            particle_color = tuple(min(255, c + 100) for c in self.color)
            
            pygame.gfxdraw.filled_circle(
                self.screen,
                int(particle['x']), int(particle['y']),
                particle['size'], particle_color + (alpha,)
            )
        
        # Draw gesture-specific particles
        if current_gesture:
            self.gesture_renderer.render_gesture_particles(
                self.screen, (avatar_x, avatar_y), current_gesture
            )
        
        # Draw UI hints for demo
        self.draw_ui_hints(current_gesture)
        
        pygame.display.flip()
    
    def draw_ui_hints(self, current_gesture):
        """Draw helpful UI hints"""
        font = pygame.font.Font(None, 24)
        
        # Draw emotion and gesture info
        y_pos = 10
        if hasattr(self, 'current_emotion'):
            emotion_text = font.render(
                f"Emotion: {self.current_emotion}", 
                True, (200, 200, 200)
            )
            self.screen.blit(emotion_text, (10, y_pos))
            y_pos += 30
            
        if current_gesture:
            gesture_text = font.render(
                f"Gesture: {current_gesture.type.value}", 
                True, (200, 200, 200)
            )
            self.screen.blit(gesture_text, (10, y_pos))
            y_pos += 30
        
        # Draw mock UI elements that can be pointed to
        self.draw_mock_ui_elements()
    
    def draw_mock_ui_elements(self):
        """Draw mock UI elements for pointing demonstrations"""
        font = pygame.font.Font(None, 20)
        
        # Mock windows/buttons
        elements = [
            {"x": 100, "y": 100, "w": 200, "h": 50, "label": "Firefox", "color": (100, 100, 150)},
            {"x": 400, "y": 200, "w": 150, "h": 40, "label": "Terminal", "color": (100, 150, 100)},
            {"x": 300, "y": 400, "w": 100, "h": 30, "label": "Settings", "color": (150, 100, 100)},
            {"x": 500, "y": 300, "w": 120, "h": 120, "label": "App Menu", "color": (150, 150, 100)},
        ]
        
        for elem in elements:
            # Draw rectangle
            pygame.draw.rect(
                self.screen, elem["color"],
                (elem["x"], elem["y"], elem["w"], elem["h"]),
                2
            )
            
            # Draw label
            label = font.render(elem["label"], True, (200, 200, 200))
            label_rect = label.get_rect(center=(
                elem["x"] + elem["w"] // 2,
                elem["y"] + elem["h"] // 2
            ))
            self.screen.blit(label, label_rect)


class EmbodiedNixWithGestures:
    """Complete embodied AI assistant with emotions and gestures"""
    
    def __init__(self):
        # Initialize all systems
        self.knowledge_engine = NixOSKnowledgeEngine()
        self.emotion_system = EmotionSystem()
        self.emotion_connector = EmotionNLPConnector(self.emotion_system)
        self.gesture_system = GestureSystem()
        self.gesture_connector = GestureNLPConnector(self.gesture_system)
        self.nlp_executor = NaturalLanguageExecutor()
        
        # Avatar (if pygame available)
        self.avatar = None
        if PYGAME_AVAILABLE:
            try:
                self.avatar = EnhancedAvatar()
            except Exception as e:
                print(f"Could not initialize avatar: {e}")
        
        # State tracking
        self.conversation_history = []
        self.current_gesture = None
        
    async def process_input(self, user_input: str) -> Dict:
        """Process user input through complete pipeline"""
        
        # Stage 1: Extract intent and confidence
        intent = self.knowledge_engine.extract_intent(user_input)
        confidence = self._calculate_confidence(intent)
        
        # Stage 2: Update emotions based on NLP results
        emotion_result = self.emotion_connector.process_nlp_result(
            intent=intent['action'],
            confidence=confidence,
            success=None
        )
        
        # Stage 3: Process gestures based on input
        gesture_type = self.gesture_connector.process_input(
            user_input, intent['action']
        )
        
        # Stage 4: Update avatar
        if self.avatar:
            self.avatar.update_from_emotion(emotion_result)
            if gesture_type:
                self.current_gesture = self.gesture_system.current_gesture
        
        # Stage 5: Get solution and format response
        solution = self.knowledge_engine.get_solution(intent)
        response = self.knowledge_engine.format_response(intent, solution)
        
        # Stage 6: Determine execution success
        success = solution.get('found', False)
        
        # Update emotion with final result
        final_emotion = self.emotion_connector.process_nlp_result(
            intent=intent['action'],
            confidence=confidence,
            success=success
        )
        
        # Store in history
        self.conversation_history.append({
            'input': user_input,
            'intent': intent,
            'confidence': confidence,
            'emotion': final_emotion,
            'gesture': gesture_type,
            'response': response,
            'timestamp': time.time()
        })
        
        return {
            'response': response,
            'emotion': final_emotion,
            'gesture': gesture_type,
            'confidence': confidence,
            'intent': intent['action']
        }
    
    def _calculate_confidence(self, intent: Dict) -> float:
        """Calculate confidence score based on intent extraction"""
        if intent['action'] == 'unknown':
            return 0.15
        elif intent.get('package'):
            if intent['package'] in self.knowledge_engine.package_aliases.values():
                return 0.95
            else:
                return 0.75
        else:
            return 0.85
    
    def run_interactive_demo(self):
        """Run interactive demo with full embodied avatar"""
        print("🤖 Embodied Nix Assistant with Gestures")
        print("=" * 50)
        print("Try commands like:")
        print("- 'Show me where Firefox is'")
        print("- 'Point to the terminal'")
        print("- 'Hello there!'")
        print("- 'I successfully installed it!'")
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
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                
                # Process input
                result = asyncio.run(self.process_input(user_input))
                
                # Display response with emotion and gesture info
                print(f"\nNix: {result['response']}")
                print(f"\n[Emotion: {result['emotion']['emotion']} "
                      f"(intensity: {result['emotion']['intensity']:.2f}), "
                      f"Gesture: {result['gesture'].value if result['gesture'] else 'None'}, "
                      f"Confidence: {result['confidence']:.0%}]")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye! 👋")
        if self.avatar and PYGAME_AVAILABLE:
            pygame.quit()
    
    def _avatar_loop(self):
        """Avatar animation loop with gesture integration"""
        running = True
        dt = 0
        
        while running:
            # Check for pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Demo: Click to point at mouse position
                    self.gesture_system.start_gesture(
                        GestureType.POINTING,
                        target=pygame.mouse.get_pos(),
                        duration=2.0
                    )
            
            # Update gesture system
            self.current_gesture = self.gesture_system.update()
            
            # Update avatar position from gesture
            if self.current_gesture:
                offset = self.gesture_system.get_gesture_offset(
                    self.current_gesture,
                    (self.avatar.x, self.avatar.y)
                )
                self.avatar.update_from_gesture(offset)
            else:
                self.avatar.update_from_gesture((0, 0))
            
            # Update avatar animations
            self.avatar.update(dt)
            
            # Update emotion display
            if hasattr(self.emotion_system, 'current_emotion'):
                self.avatar.current_emotion = self.emotion_system.current_emotion.emotion
            
            # Draw everything
            self.avatar.draw(self.current_gesture)
            
            # Control frame rate
            dt = self.avatar.clock.tick(60) / 1000.0  # 60 FPS
            
            # Check if emotion should return to calm
            if self.emotion_system.should_return_to_calm():
                self.emotion_system.return_to_calm()
                calm_emotion = self.emotion_connector.process_nlp_result(
                    intent="idle",
                    confidence=0.5,
                    success=True
                )
                self.avatar.update_from_emotion(calm_emotion)


# Demo script
if __name__ == "__main__":
    assistant = EmbodiedNixWithGestures()
    
    if len(sys.argv) > 1:
        # Process single command
        query = ' '.join(sys.argv[1:])
        result = asyncio.run(assistant.process_input(query))
        print(result['response'])
        print(f"\n[Emotion: {result['emotion']['emotion']}, "
              f"Gesture: {result['gesture'].value if result['gesture'] else 'None'}, "
              f"Confidence: {result['confidence']:.0%}]")
    else:
        # Run interactive demo
        assistant.run_interactive_demo()