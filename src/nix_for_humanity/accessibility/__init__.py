"""
Accessibility utilities for Nix for Humanity
Ensuring all interfaces work properly with screen readers and assistive technologies
"""

from .screen_reader import (
    ScreenReaderSupport,
    AriaLiveRegion,
    FocusManager,
    KeyboardNavigator
)

from .wcag_compliance import (
    WCAGValidator,
    ColorContrastChecker,
    TextSpacingManager,
    MotionController
)

from .persona_accessibility import (
    PersonaAccessibilityAdapter,
    AccessibilityProfile,
    get_persona_accessibility_settings
)

__all__ = [
    # Screen reader support
    'ScreenReaderSupport',
    'AriaLiveRegion',
    'FocusManager',
    'KeyboardNavigator',
    
    # WCAG compliance
    'WCAGValidator',
    'ColorContrastChecker',
    'TextSpacingManager',
    'MotionController',
    
    # Persona-specific
    'PersonaAccessibilityAdapter',
    'AccessibilityProfile',
    'get_persona_accessibility_settings'
]