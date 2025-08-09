#!/usr/bin/env python3
"""
from typing import Tuple, Union, List, Optional
Gesture System for Embodied AI Avatar
Implements pointing and other gestures for natural communication
"""

import math
import time
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict
from enum import Enum
import random

# Try to import pygame for screen element detection
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class GestureType(Enum):
    """Types of gestures the avatar can perform"""
    IDLE = "idle"
    POINTING = "pointing"
    WAVING = "waving"
    THINKING = "thinking"
    CELEBRATING = "celebrating"
    CONFUSED = "confused"
    NODDING = "nodding"
    SHAKING = "shaking"


@dataclass
class ScreenElement:
    """Represents an element on screen that can be pointed to"""
    x: int
    y: int
    width: int
    height: int
    name: str
    type: str  # 'window', 'button', 'text', 'icon', etc.
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center point of element"""
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass
class Gesture:
    """Represents a gesture animation"""
    type: GestureType
    target_point: Optional[Tuple[int, int]] = None
    duration: float = 1.0
    intensity: float = 1.0
    start_time: float = 0.0
    
    @property
    def progress(self) -> float:
        """Get animation progress (0.0 to 1.0)"""
        if self.start_time == 0:
            return 0.0
        elapsed = time.time() - self.start_time
        return min(1.0, elapsed / self.duration)
    
    @property
    def is_complete(self) -> bool:
        """Check if gesture animation is done"""
        return self.progress >= 1.0


class GestureSystem:
    """Manages gesture recognition and animation"""
    
    def __init__(self):
        self.current_gesture: Optional[Gesture] = None
        self.gesture_queue: List[Gesture] = []
        self.screen_elements: List[ScreenElement] = []
        
        # Animation parameters
        self.pointing_offset = 20  # Distance from avatar center when pointing
        self.animation_speed = 1.0
        
        # Initialize with some mock screen elements for testing
        self._initialize_mock_elements()
    
    def _initialize_mock_elements(self):
        """Create mock screen elements for testing"""
        self.screen_elements = [
            ScreenElement(100, 100, 200, 50, "Firefox", "window"),
            ScreenElement(400, 200, 150, 40, "Terminal", "window"),
            ScreenElement(300, 400, 100, 30, "Settings", "button"),
            ScreenElement(500, 300, 120, 120, "App Menu", "icon"),
        ]
    
    def find_element_by_name(self, name: str) -> Optional[ScreenElement]:
        """Find screen element by partial name match"""
        name_lower = name.lower()
        for element in self.screen_elements:
            if name_lower in element.name.lower():
                return element
        return None
    
    def find_element_at_position(self, x: int, y: int) -> Optional[ScreenElement]:
        """Find screen element at given position"""
        for element in self.screen_elements:
            if (element.x <= x <= element.x + element.width and
                element.y <= y <= element.y + element.height):
                return element
        return None
    
    def start_gesture(self, gesture_type: GestureType, 
                     target: Optional[Union[str, Tuple[int, int]]] = None,
                     duration: float = 1.0,
                     intensity: float = 1.0):
        """Start a new gesture animation"""
        
        target_point = None
        
        # Handle different target types
        if gesture_type == GestureType.POINTING and target:
            if isinstance(target, str):
                # Find element by name
                element = self.find_element_by_name(target)
                if element:
                    target_point = element.center
            elif isinstance(target, tuple) and len(target) == 2:
                # Direct coordinates
                target_point = target
        
        # Create gesture
        gesture = Gesture(
            type=gesture_type,
            target_point=target_point,
            duration=duration,
            intensity=intensity,
            start_time=time.time()
        )
        
        # Set as current or queue it
        if self.current_gesture is None or self.current_gesture.is_complete:
            self.current_gesture = gesture
        else:
            self.gesture_queue.append(gesture)
    
    def update(self) -> Optional[Gesture]:
        """Update gesture system and return current gesture"""
        # Check if current gesture is complete
        if self.current_gesture and self.current_gesture.is_complete:
            # Move to next gesture in queue
            if self.gesture_queue:
                self.current_gesture = self.gesture_queue.pop(0)
                self.current_gesture.start_time = time.time()
            else:
                self.current_gesture = None
        
        return self.current_gesture
    
    def get_pointing_angle(self, avatar_pos: Tuple[int, int], 
                          target_pos: Tuple[int, int]) -> float:
        """Calculate angle for pointing gesture"""
        dx = target_pos[0] - avatar_pos[0]
        dy = target_pos[1] - avatar_pos[1]
        return math.atan2(dy, dx)
    
    def get_gesture_offset(self, gesture: Gesture, 
                          avatar_pos: Tuple[int, int]) -> Tuple[float, float]:
        """Get position offset for current gesture"""
        if not gesture:
            return (0, 0)
        
        progress = gesture.progress
        
        if gesture.type == GestureType.POINTING and gesture.target_point:
            # Calculate pointing direction
            angle = self.get_pointing_angle(avatar_pos, gesture.target_point)
            
            # Ease in-out animation
            ease_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            
            # Move slightly toward target
            offset_x = math.cos(angle) * self.pointing_offset * ease_progress
            offset_y = math.sin(angle) * self.pointing_offset * ease_progress
            
            return (offset_x, offset_y)
        
        elif gesture.type == GestureType.WAVING:
            # Side to side motion
            wave_angle = math.sin(progress * math.pi * 4) * 0.3
            offset_x = math.cos(wave_angle) * 15
            offset_y = -abs(math.sin(progress * math.pi)) * 10
            return (offset_x, offset_y)
        
        elif gesture.type == GestureType.NODDING:
            # Up and down motion
            offset_y = math.sin(progress * math.pi * 3) * 10
            return (0, offset_y)
        
        elif gesture.type == GestureType.THINKING:
            # Small circular motion
            angle = progress * math.pi * 2
            offset_x = math.cos(angle) * 5
            offset_y = math.sin(angle) * 5
            return (offset_x, offset_y)
        
        return (0, 0)


class GestureNLPConnector:
    """Connects NLP understanding to gesture system"""
    
    def __init__(self, gesture_system: GestureSystem):
        self.gesture_system = gesture_system
        
        # Gesture triggers based on intent and keywords
        self.gesture_triggers = {
            'pointing': ['that', 'there', 'this', 'click', 'select', 'open'],
            'waving': ['hello', 'hi', 'bye', 'goodbye', 'welcome'],
            'thinking': ['hmm', 'let me think', 'processing', 'calculating'],
            'celebrating': ['success', 'done', 'complete', 'installed', 'fixed'],
            'confused': ['error', 'problem', 'unclear', "don't understand"],
            'nodding': ['yes', 'correct', 'right', 'exactly', 'understood'],
            'shaking': ['no', 'wrong', 'incorrect', 'not']
        }
    
    def process_input(self, text: str, intent: str) -> Optional[GestureType]:
        """Determine gesture based on user input"""
        text_lower = text.lower()
        
        # Check for pointing indicators
        if any(word in text_lower for word in self.gesture_triggers['pointing']):
            # Look for references to UI elements
            if 'firefox' in text_lower:
                self.gesture_system.start_gesture(
                    GestureType.POINTING, 
                    target="Firefox",
                    duration=1.5
                )
                return GestureType.POINTING
            elif 'terminal' in text_lower:
                self.gesture_system.start_gesture(
                    GestureType.POINTING,
                    target="Terminal",
                    duration=1.5
                )
                return GestureType.POINTING
            elif 'settings' in text_lower:
                self.gesture_system.start_gesture(
                    GestureType.POINTING,
                    target="Settings",
                    duration=1.5
                )
                return GestureType.POINTING
        
        # Check other gesture triggers
        for gesture_name, triggers in self.gesture_triggers.items():
            if gesture_name != 'pointing' and any(word in text_lower for word in triggers):
                gesture_type = GestureType[gesture_name.upper()]
                self.gesture_system.start_gesture(gesture_type, duration=1.0)
                return gesture_type
        
        # Intent-based gestures
        if intent == 'greeting':
            self.gesture_system.start_gesture(GestureType.WAVING)
            return GestureType.WAVING
        elif intent == 'install_package' and 'success' in text_lower:
            self.gesture_system.start_gesture(GestureType.CELEBRATING)
            return GestureType.CELEBRATING
        
        return None


# Integration with avatar visualization
class GestureRenderer:
    """Renders gestures on avatar"""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def render_pointing_indicator(self, screen, avatar_pos: Tuple[int, int], 
                                 target_pos: Tuple[int, int], progress: float):
        """Draw pointing indicator from avatar to target"""
        if not PYGAME_AVAILABLE:
            return
        
        # Calculate line from avatar toward target
        angle = math.atan2(
            target_pos[1] - avatar_pos[1],
            target_pos[0] - avatar_pos[0]
        )
        
        # Start point (edge of avatar)
        start_x = avatar_pos[0] + math.cos(angle) * 60
        start_y = avatar_pos[1] + math.sin(angle) * 60
        
        # End point (toward target, animated)
        distance = min(200, math.sqrt(
            (target_pos[0] - avatar_pos[0])**2 + 
            (target_pos[1] - avatar_pos[1])**2
        ) * 0.8)
        
        end_x = start_x + math.cos(angle) * distance * progress
        end_y = start_y + math.sin(angle) * distance * progress
        
        # Draw dotted line
        num_dots = int(distance * progress / 20)
        for i in range(num_dots):
            t = i / max(1, num_dots - 1)
            dot_x = start_x + (end_x - start_x) * t
            dot_y = start_y + (end_y - start_y) * t
            
            # Pulsing effect
            radius = 3 + math.sin((time.time() * 5 + i * 0.5)) * 1
            alpha = int(255 * (1 - t * 0.3))  # Fade toward target
            
            pygame.draw.circle(screen, (255, 255, 100, alpha), 
                             (int(dot_x), int(dot_y)), int(radius))
        
        # Draw arrow head at end
        if progress > 0.5:
            arrow_size = 15 * (progress - 0.5) * 2
            arrow_angle1 = angle + math.pi * 0.8
            arrow_angle2 = angle - math.pi * 0.8
            
            arrow_points = [
                (int(end_x), int(end_y)),
                (int(end_x + math.cos(arrow_angle1) * arrow_size),
                 int(end_y + math.sin(arrow_angle1) * arrow_size)),
                (int(end_x + math.cos(arrow_angle2) * arrow_size),
                 int(end_y + math.sin(arrow_angle2) * arrow_size))
            ]
            
            pygame.draw.polygon(screen, (255, 255, 100), arrow_points)
    
    def render_gesture_particles(self, screen, avatar_pos: Tuple[int, int],
                               gesture: Gesture):
        """Render particle effects for gestures"""
        if not PYGAME_AVAILABLE or not gesture:
            return
        
        progress = gesture.progress
        
        if gesture.type == GestureType.CELEBRATING:
            # Confetti particles
            num_particles = int(20 * progress)
            for i in range(num_particles):
                angle = random.random() * math.pi * 2
                distance = random.random() * 100 * progress
                x = avatar_pos[0] + math.cos(angle) * distance
                y = avatar_pos[1] + math.sin(angle) * distance - progress * 50
                
                color = random.choice([
                    (255, 100, 100),  # Red
                    (100, 255, 100),  # Green
                    (100, 100, 255),  # Blue
                    (255, 255, 100),  # Yellow
                ])
                
                pygame.draw.circle(screen, color, (int(x), int(y)), 3)
        
        elif gesture.type == GestureType.THINKING:
            # Thought bubbles
            for i in range(3):
                offset = i * 30
                bubble_y = avatar_pos[1] - 80 - offset
                bubble_x = avatar_pos[0] + math.sin(time.time() * 2 + i) * 10
                radius = 10 + i * 3
                
                alpha = int(200 * (1 - progress * 0.5))
                pygame.draw.circle(screen, (200, 200, 255, alpha),
                                 (int(bubble_x), int(bubble_y)), radius, 2)


# Demo and testing
if __name__ == "__main__":
    gesture_system = GestureSystem()
    gesture_nlp = GestureNLPConnector(gesture_system)
    
    # Test gesture recognition
    test_inputs = [
        ("Can you show me where Firefox is?", "help"),
        ("Click on that terminal window", "command"),
        ("Hello there!", "greeting"),
        ("I successfully installed the package!", "confirmation"),
        ("Hmm, let me think about that", "processing"),
        ("No, that's not right", "correction"),
    ]
    
    print("🎯 Gesture System Test")
    print("=" * 50)
    
    for text, intent in test_inputs:
        print(f"\nInput: '{text}'")
        gesture = gesture_nlp.process_input(text, intent)
        if gesture:
            print(f"Triggered: {gesture.value} gesture")
            current = gesture_system.current_gesture
            if current:
                print(f"Duration: {current.duration}s")
                if current.target_point:
                    print(f"Target: {current.target_point}")
        else:
            print("No gesture triggered")
    
    # Simulate gesture animation
    print("\n\n🎬 Simulating Pointing Animation")
    print("=" * 50)
    
    gesture_system.start_gesture(
        GestureType.POINTING,
        target="Firefox",
        duration=2.0
    )
    
    avatar_pos = (400, 300)
    for i in range(20):
        gesture = gesture_system.update()
        if gesture:
            offset = gesture_system.get_gesture_offset(gesture, avatar_pos)
            print(f"Frame {i+1}: Progress={gesture.progress:.2f}, "
                  f"Offset=({offset[0]:.1f}, {offset[1]:.1f})")
        time.sleep(0.1)