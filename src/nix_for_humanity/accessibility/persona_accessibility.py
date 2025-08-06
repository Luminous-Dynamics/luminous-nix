"""
Persona-Specific Accessibility Settings
Tailored accessibility configurations for each of the 10 core personas
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .screen_reader import AriaLivePriority
from .wcag_compliance import TextSpacingRequirements


class PersonaType(Enum):
    """The 10 core personas"""
    GRANDMA_ROSE = "grandma_rose"
    MAYA_ADHD = "maya_adhd"
    DAVID_TIRED_PARENT = "david_tired_parent"
    DR_SARAH = "dr_sarah"
    ALEX_BLIND = "alex_blind"
    CARLOS_CAREER_SWITCHER = "carlos_career_switcher"
    PRIYA_SINGLE_MOM = "priya_single_mom"
    JAMIE_PRIVACY = "jamie_privacy"
    VIKTOR_ESL = "viktor_esl"
    LUNA_AUTISTIC = "luna_autistic"


@dataclass
class AccessibilityProfile:
    """Accessibility settings for a persona"""
    # Screen reader settings
    screen_reader_enabled: bool = False
    screen_reader_verbosity: str = "medium"  # low, medium, high
    announcement_priority: AriaLivePriority = AriaLivePriority.POLITE
    
    # Visual settings
    high_contrast: bool = False
    large_text: bool = False
    reduced_motion: bool = False
    focus_highlight_strength: str = "normal"  # normal, strong, extra-strong
    
    # Interaction settings
    keyboard_only: bool = False
    simplified_interface: bool = False
    confirmation_required: bool = True
    response_time_limit: Optional[float] = None  # seconds, None = no limit
    
    # Cognitive support
    clear_language: bool = False
    step_by_step_guidance: bool = False
    error_prevention: bool = True
    predictable_navigation: bool = True
    
    # Audio settings
    audio_cues: bool = False
    voice_feedback: bool = False
    
    # Timing and pacing
    extended_timeouts: bool = False
    no_time_limits: bool = False
    pause_animations: bool = False
    
    # Custom text spacing
    custom_text_spacing: Optional[TextSpacingRequirements] = None


class PersonaAccessibilityAdapter:
    """
    Adapts accessibility settings based on persona needs
    """
    
    # Persona-specific configurations
    PERSONA_PROFILES: Dict[PersonaType, AccessibilityProfile] = {
        PersonaType.GRANDMA_ROSE: AccessibilityProfile(
            large_text=True,
            simplified_interface=True,
            confirmation_required=True,
            clear_language=True,
            step_by_step_guidance=True,
            extended_timeouts=True,
            voice_feedback=True,
            audio_cues=True,
            focus_highlight_strength="extra-strong",
            reduced_motion=True,
            error_prevention=True,
        ),
        
        PersonaType.MAYA_ADHD: AccessibilityProfile(
            reduced_motion=False,  # Quick responses preferred
            simplified_interface=True,
            confirmation_required=False,  # Speed over safety
            response_time_limit=1.0,  # 1 second max
            focus_highlight_strength="strong",
            clear_language=True,
            predictable_navigation=True,
            no_time_limits=False,  # Keep focused
        ),
        
        PersonaType.DAVID_TIRED_PARENT: AccessibilityProfile(
            simplified_interface=True,
            confirmation_required=True,
            error_prevention=True,
            clear_language=True,
            extended_timeouts=True,
            step_by_step_guidance=True,
            reduced_motion=True,  # Calm interface
        ),
        
        PersonaType.DR_SARAH: AccessibilityProfile(
            # Power user - minimal assistance
            screen_reader_enabled=False,
            simplified_interface=False,
            confirmation_required=False,
            keyboard_only=False,
            response_time_limit=2.0,
        ),
        
        PersonaType.ALEX_BLIND: AccessibilityProfile(
            screen_reader_enabled=True,
            screen_reader_verbosity="high",
            announcement_priority=AriaLivePriority.ASSERTIVE,
            keyboard_only=True,
            audio_cues=True,
            voice_feedback=True,
            no_time_limits=True,
            focus_highlight_strength="extra-strong",  # For partial sight
        ),
        
        PersonaType.CARLOS_CAREER_SWITCHER: AccessibilityProfile(
            clear_language=True,
            step_by_step_guidance=True,
            error_prevention=True,
            confirmation_required=True,
            extended_timeouts=True,
            predictable_navigation=True,
        ),
        
        PersonaType.PRIYA_SINGLE_MOM: AccessibilityProfile(
            simplified_interface=True,
            clear_language=True,
            response_time_limit=3.0,  # Quick but not rushed
            error_prevention=True,
            extended_timeouts=True,
        ),
        
        PersonaType.JAMIE_PRIVACY: AccessibilityProfile(
            # Standard accessibility, focus on privacy
            confirmation_required=True,
            clear_language=True,
            predictable_navigation=True,
        ),
        
        PersonaType.VIKTOR_ESL: AccessibilityProfile(
            clear_language=True,  # Extra important
            simplified_interface=True,
            step_by_step_guidance=True,
            extended_timeouts=True,
            error_prevention=True,
            confirmation_required=True,
            large_text=True,  # Easier reading
        ),
        
        PersonaType.LUNA_AUTISTIC: AccessibilityProfile(
            predictable_navigation=True,  # Critical
            reduced_motion=True,
            simplified_interface=True,
            clear_language=True,
            no_time_limits=True,
            confirmation_required=True,
            error_prevention=True,
            focus_highlight_strength="strong",
            pause_animations=True,
        ),
    }
    
    def __init__(self):
        self.current_persona: Optional[PersonaType] = None
        self.current_profile: Optional[AccessibilityProfile] = None
        self.custom_overrides: Dict[str, Any] = {}
        
    def set_persona(self, persona: PersonaType):
        """Set the current persona and load their profile"""
        self.current_persona = persona
        self.current_profile = self.PERSONA_PROFILES.get(
            persona, 
            AccessibilityProfile()  # Default if not found
        )
        
    def get_current_profile(self) -> AccessibilityProfile:
        """Get the current accessibility profile"""
        if self.current_profile is None:
            return AccessibilityProfile()  # Default profile
        
        # Apply any custom overrides
        if self.custom_overrides:
            profile_dict = self.current_profile.__dict__.copy()
            profile_dict.update(self.custom_overrides)
            return AccessibilityProfile(**profile_dict)
            
        return self.current_profile
        
    def override_setting(self, setting: str, value: Any):
        """Override a specific accessibility setting"""
        self.custom_overrides[setting] = value
        
    def clear_overrides(self):
        """Clear all custom overrides"""
        self.custom_overrides.clear()
        
    def get_response_requirements(self) -> Dict[str, Any]:
        """Get response requirements for current persona"""
        profile = self.get_current_profile()
        
        return {
            'max_response_time': profile.response_time_limit,
            'requires_confirmation': profile.confirmation_required,
            'simplified_language': profile.clear_language,
            'step_by_step': profile.step_by_step_guidance,
            'announce_priority': profile.announcement_priority,
        }
        
    def get_interface_requirements(self) -> Dict[str, Any]:
        """Get interface requirements for current persona"""
        profile = self.get_current_profile()
        
        return {
            'simplified': profile.simplified_interface,
            'high_contrast': profile.high_contrast,
            'large_text': profile.large_text,
            'reduced_motion': profile.reduced_motion,
            'keyboard_only': profile.keyboard_only,
            'focus_strength': profile.focus_highlight_strength,
        }
        
    def should_announce(self, content_type: str) -> bool:
        """Check if content should be announced to screen reader"""
        profile = self.get_current_profile()
        
        if not profile.screen_reader_enabled:
            return False
            
        # Always announce based on verbosity level
        verbosity_map = {
            'low': ['errors', 'critical'],
            'medium': ['errors', 'critical', 'success', 'warnings'],
            'high': ['errors', 'critical', 'success', 'warnings', 'info', 'progress']
        }
        
        allowed_types = verbosity_map.get(profile.screen_reader_verbosity, [])
        return content_type in allowed_types


def get_persona_accessibility_settings(persona_name: str) -> AccessibilityProfile:
    """
    Get accessibility settings for a persona by name
    
    Args:
        persona_name: Name of the persona (case insensitive)
        
    Returns:
        AccessibilityProfile for the persona
    """
    # Convert name to enum
    persona_map = {
        'grandma rose': PersonaType.GRANDMA_ROSE,
        'maya': PersonaType.MAYA_ADHD,
        'david': PersonaType.DAVID_TIRED_PARENT,
        'dr sarah': PersonaType.DR_SARAH,
        'dr. sarah': PersonaType.DR_SARAH,
        'alex': PersonaType.ALEX_BLIND,
        'carlos': PersonaType.CARLOS_CAREER_SWITCHER,
        'priya': PersonaType.PRIYA_SINGLE_MOM,
        'jamie': PersonaType.JAMIE_PRIVACY,
        'viktor': PersonaType.VIKTOR_ESL,
        'luna': PersonaType.LUNA_AUTISTIC,
    }
    
    normalized_name = persona_name.lower().strip()
    persona_type = persona_map.get(normalized_name)
    
    if persona_type:
        adapter = PersonaAccessibilityAdapter()
        return adapter.PERSONA_PROFILES.get(persona_type, AccessibilityProfile())
    
    return AccessibilityProfile()  # Default profile if not found