# Persona-Adaptive TUI Styling and Accessibility
"""
Persona-aware styling system for the TUI that adapts visual appearance,
timing, language complexity, and accessibility features based on user persona.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from textual.css import Stylesheet
from textual.color import Color


class PersonaType(Enum):
    """The 10 core personas for Nix for Humanity."""
    GRANDMA_ROSE = "grandma_rose"      # 75, voice-first, zero technical terms
    MAYA = "maya"                      # 16, ADHD, fast-focused, minimal distractions  
    DAVID = "david"                    # 42, tired parent, stress-free, reliable
    DR_SARAH = "dr_sarah"              # 35, researcher, efficient, precise
    ALEX = "alex"                      # 28, blind developer, 100% accessible
    CARLOS = "carlos"                  # 52, career switcher, learning support
    PRIYA = "priya"                    # 34, single mom, quick, context-aware
    JAMIE = "jamie"                    # 19, privacy advocate, transparent
    VIKTOR = "viktor"                  # 67, ESL, clear communication  
    LUNA = "luna"                      # 14, autistic, predictable


@dataclass
class PersonaProfile:
    """Complete profile for persona-specific adaptations."""
    name: str
    age: int
    characteristics: List[str]
    
    # Visual styling preferences
    font_size: str  # "small", "medium", "large", "extra-large"
    contrast: str   # "normal", "high", "maximum"  
    colors: Dict[str, str]  # CSS color overrides
    animations: bool  # Enable/disable animations
    
    # Timing preferences
    max_response_time: float  # seconds
    typing_delay: float       # delay between characters for readability
    auto_advance: bool        # auto-advance through steps
    
    # Language preferences  
    complexity_level: str     # "simple", "standard", "technical"
    max_sentence_length: int  # words per sentence
    technical_terms_allowed: bool
    
    # Accessibility needs
    screen_reader_optimized: bool
    keyboard_only: bool
    high_contrast_required: bool
    audio_feedback: bool
    
    # UI behavior preferences
    minimal_ui: bool          # hide secondary elements
    auto_suggestions: bool    # show predictive suggestions
    confirmation_required: bool  # require confirmation for actions
    detailed_explanations: bool  # provide detailed explanations


# Define the 10 core personas with their complete profiles
PERSONA_PROFILES = {
    PersonaType.GRANDMA_ROSE: PersonaProfile(
        name="Grandma Rose",
        age=75,
        characteristics=["voice-first", "zero technical knowledge", "patient"],
        font_size="large",
        contrast="high", 
        colors={
            "background": "#f8f9fa",
            "text": "#212529", 
            "primary": "#0d6efd",
            "success": "#198754",
            "warning": "#fd7e14"
        },
        animations=False,
        max_response_time=2.0,
        typing_delay=0.05,
        auto_advance=False,
        complexity_level="simple",
        max_sentence_length=10,
        technical_terms_allowed=False,
        screen_reader_optimized=True,
        keyboard_only=False,
        high_contrast_required=True,
        audio_feedback=True,
        minimal_ui=False,
        auto_suggestions=True,
        confirmation_required=True,
        detailed_explanations=False
    ),
    
    PersonaType.MAYA: PersonaProfile(
        name="Maya",
        age=16,
        characteristics=["ADHD", "fast-paced", "minimal attention span"],
        font_size="medium",
        contrast="normal",
        colors={
            "background": "#000000",
            "text": "#ffffff",
            "primary": "#ff6b6b", 
            "success": "#51cf66",
            "warning": "#ffd43b"
        },
        animations=True,
        max_response_time=1.0,
        typing_delay=0.01,
        auto_advance=True,
        complexity_level="simple",
        max_sentence_length=8,
        technical_terms_allowed=False,
        screen_reader_optimized=False,
        keyboard_only=True,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=True,
        auto_suggestions=False,  # Distracting for ADHD
        confirmation_required=False,
        detailed_explanations=False
    ),
    
    PersonaType.DAVID: PersonaProfile(
        name="David",
        age=42,
        characteristics=["tired parent", "stressed", "needs reliability"],
        font_size="medium",
        contrast="normal",
        colors={
            "background": "#2d3748",
            "text": "#e2e8f0",
            "primary": "#4299e1",
            "success": "#68d391", 
            "warning": "#f6ad55"
        },
        animations=False,
        max_response_time=3.0,
        typing_delay=0.03,
        auto_advance=False,
        complexity_level="standard",
        max_sentence_length=12,
        technical_terms_allowed=True,
        screen_reader_optimized=False,
        keyboard_only=False,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=True,
        confirmation_required=True,
        detailed_explanations=False
    ),
    
    PersonaType.DR_SARAH: PersonaProfile(
        name="Dr. Sarah",
        age=35,
        characteristics=["researcher", "technical", "efficient"],
        font_size="small",
        contrast="normal",
        colors={
            "background": "#1a202c",
            "text": "#f7fafc",
            "primary": "#63b3ed",
            "success": "#68d391",
            "warning": "#fbb6ce"
        },
        animations=False,
        max_response_time=2.0,
        typing_delay=0.01,
        auto_advance=False,
        complexity_level="technical",
        max_sentence_length=20,
        technical_terms_allowed=True,
        screen_reader_optimized=False,
        keyboard_only=True,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=True,
        confirmation_required=False,
        detailed_explanations=True
    ),
    
    PersonaType.ALEX: PersonaProfile(
        name="Alex",
        age=28,
        characteristics=["blind developer", "screen reader", "keyboard only"],
        font_size="medium",
        contrast="maximum",
        colors={
            "background": "#000000",
            "text": "#ffffff",
            "primary": "#ffff00",  # High contrast yellow
            "success": "#00ff00",  # Bright green
            "warning": "#ff0000"   # Bright red
        },
        animations=False,
        max_response_time=2.0,
        typing_delay=0.02,
        auto_advance=False,
        complexity_level="technical",
        max_sentence_length=15,
        technical_terms_allowed=True,
        screen_reader_optimized=True,
        keyboard_only=True,
        high_contrast_required=True,
        audio_feedback=True,
        minimal_ui=False,
        auto_suggestions=False,  # Can be distracting for screen readers
        confirmation_required=True,
        detailed_explanations=True
    ),
    
    PersonaType.CARLOS: PersonaProfile(
        name="Carlos",
        age=52,
        characteristics=["career switcher", "learning tech", "needs encouragement"],
        font_size="medium",
        contrast="high",
        colors={
            "background": "#f7fafc",
            "text": "#2d3748",
            "primary": "#3182ce",
            "success": "#38a169",
            "warning": "#d69e2e"
        },
        animations=True,
        max_response_time=3.0,
        typing_delay=0.04,
        auto_advance=False,
        complexity_level="standard",
        max_sentence_length=12,
        technical_terms_allowed=False,
        screen_reader_optimized=False,
        keyboard_only=False,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=True,
        confirmation_required=True,
        detailed_explanations=True
    ),
    
    PersonaType.PRIYA: PersonaProfile(
        name="Priya",
        age=34,
        characteristics=["single mom", "time-constrained", "needs efficiency"],
        font_size="medium",
        contrast="normal",
        colors={
            "background": "#1a365d",
            "text": "#f7fafc",
            "primary": "#4299e1",
            "success": "#48bb78",
            "warning": "#ed8936"
        },
        animations=True,
        max_response_time=1.5,
        typing_delay=0.01,
        auto_advance=True,
        complexity_level="standard", 
        max_sentence_length=10,
        technical_terms_allowed=True,
        screen_reader_optimized=False,
        keyboard_only=False,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=True,
        auto_suggestions=True,
        confirmation_required=False,
        detailed_explanations=False
    ),
    
    PersonaType.JAMIE: PersonaProfile(
        name="Jamie",
        age=19,
        characteristics=["privacy advocate", "security conscious", "tech savvy"],
        font_size="small",
        contrast="normal",
        colors={
            "background": "#0d1117",
            "text": "#c9d1d9",
            "primary": "#58a6ff",
            "success": "#3fb950",
            "warning": "#f85149"
        },
        animations=False,
        max_response_time=2.0,
        typing_delay=0.02,
        auto_advance=False,
        complexity_level="technical",
        max_sentence_length=15,
        technical_terms_allowed=True,
        screen_reader_optimized=False,
        keyboard_only=True,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=False,  # Privacy-conscious
        confirmation_required=True,
        detailed_explanations=True
    ),
    
    PersonaType.VIKTOR: PersonaProfile(
        name="Viktor",
        age=67,
        characteristics=["ESL speaker", "careful with language", "patient"],
        font_size="large",
        contrast="high",
        colors={
            "background": "#faf5ff",
            "text": "#1a202c",
            "primary": "#805ad5",
            "success": "#38a169",
            "warning": "#d69e2e"
        },
        animations=False,
        max_response_time=4.0,
        typing_delay=0.06,
        auto_advance=False,
        complexity_level="simple",
        max_sentence_length=8,
        technical_terms_allowed=False,
        screen_reader_optimized=False,
        keyboard_only=False,
        high_contrast_required=True,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=True,
        confirmation_required=True,
        detailed_explanations=True
    ),
    
    PersonaType.LUNA: PersonaProfile(
        name="Luna",
        age=14,
        characteristics=["autistic", "needs predictability", "detail-oriented"],
        font_size="medium",
        contrast="normal",
        colors={
            "background": "#f0f4f8",
            "text": "#2d3748",
            "primary": "#4c51bf",
            "success": "#38a169",
            "warning": "#ed8936"
        },
        animations=False,  # Consistent, predictable
        max_response_time=3.0,
        typing_delay=0.03,
        auto_advance=False,
        complexity_level="standard",
        max_sentence_length=15,
        technical_terms_allowed=True,
        screen_reader_optimized=False,
        keyboard_only=False,
        high_contrast_required=False,
        audio_feedback=False,
        minimal_ui=False,
        auto_suggestions=False,  # Maintain predictability
        confirmation_required=True,
        detailed_explanations=True
    )
}


class PersonaStyleManager:
    """Manages persona-specific styling and behavior adaptations."""
    
    def __init__(self, current_persona: PersonaType = PersonaType.DAVID):
        self.current_persona = current_persona
        self.profile = PERSONA_PROFILES[current_persona]
    
    def set_persona(self, persona: PersonaType) -> None:
        """Switch to a different persona profile."""
        self.current_persona = persona
        self.profile = PERSONA_PROFILES[persona]
    
    def get_css_styles(self) -> str:
        """Generate CSS styles adapted for current persona."""
        profile = self.profile
        
        # Base font sizes
        font_sizes = {
            "small": "14px",
            "medium": "16px", 
            "large": "20px",
            "extra-large": "24px"
        }
        
        # Generate adaptive CSS
        css = f"""
        /* Persona-adaptive styles for {profile.name} */
        Screen {{
            background: {profile.colors['background']};
        }}
        
        .persona-text {{
            color: {profile.colors['text']};
            font-size: {font_sizes[profile.font_size]};
            line-height: 1.6;
        }}
        
        .persona-primary {{
            background: {profile.colors['primary']};
            color: {profile.colors['text']};
        }}
        
        .persona-success {{
            color: {profile.colors['success']};
        }}
        
        .persona-warning {{
            color: {profile.colors['warning']};
        }}
        
        /* High contrast adjustments */
        """
        
        if profile.high_contrast_required:
            css += """
            .high-contrast {
                border: 2px solid currentColor;
            }
            
            Button {
                border: 2px solid currentColor;
            }
            
            Input {
                border: 2px solid currentColor;
            }
            """
        
        # Accessibility-specific styles
        if profile.screen_reader_optimized:
            css += """
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
            
            .sr-focus:focus {
                position: static;
                width: auto;
                height: auto;
                padding: inherit;
                margin: inherit;
                overflow: visible;
                clip: auto;
                white-space: normal;
            }
            """
        
        # Animation control
        if not profile.animations:
            css += """
            * {
                animation-duration: 0s !important;
                transition-duration: 0s !important;
            }
            """
        
        return css
    
    def adapt_message(self, message: str) -> str:
        """Adapt message content for current persona."""
        profile = self.profile
        
        # Language complexity adaptation
        if profile.complexity_level == "simple":
            # Replace technical terms with simple alternatives
            technical_replacements = {
                "repository": "software source",
                "binary": "program file", 
                "compilation": "building",
                "dependency": "required software",
                "installation": "setup",
                "configuration": "settings",
                "authentication": "login",
                "initialization": "setup"
            }
            
            for tech_term, simple_term in technical_replacements.items():
                message = message.replace(tech_term, simple_term)
        
        # Sentence length control
        if profile.max_sentence_length < 15:
            # Break long sentences into shorter ones
            sentences = message.split('. ')
            adapted_sentences = []
            
            for sentence in sentences:
                words = sentence.split()
                if len(words) > profile.max_sentence_length:
                    # Break into smaller sentences 
                    mid_point = len(words) // 2
                    part1 = ' '.join(words[:mid_point])
                    part2 = ' '.join(words[mid_point:])
                    adapted_sentences.extend([part1, part2])
                else:
                    adapted_sentences.append(sentence)
            
            message = '. '.join(adapted_sentences)
        
        # Add encouraging language for Carlos
        if self.current_persona == PersonaType.CARLOS:
            if "error" in message.lower():
                message = "Don't worry, let's fix this together! " + message
            elif "success" in message.lower():
                message = "Great job! " + message
        
        # Add efficiency indicators for Priya
        if self.current_persona == PersonaType.PRIYA:
            if "install" in message.lower():
                message = "Quick install: " + message
            elif "update" in message.lower():
                message = "Fast update: " + message
        
        return message
    
    def get_accessibility_attributes(self) -> Dict[str, Any]:
        """Get accessibility attributes for UI elements."""
        profile = self.profile
        attrs = {}
        
        if profile.screen_reader_optimized:
            attrs.update({
                "aria-live": "polite",
                "aria-atomic": "true",
                "role": "status"
            })
        
        if profile.keyboard_only:
            attrs.update({
                "tabindex": "0",
                "aria-describedby": "keyboard-help"
            })
        
        return attrs
    
    def should_show_confirmation(self, action: str) -> bool:
        """Determine if confirmation is needed for an action."""
        if not self.profile.confirmation_required:
            return False
        
        # High-risk actions always need confirmation
        high_risk_actions = ["remove", "delete", "uninstall", "format", "reset"]
        return any(risk in action.lower() for risk in high_risk_actions)
    
    def get_typing_animation_delay(self) -> float:
        """Get typing delay for animated text display."""
        return self.profile.typing_delay
    
    def should_auto_advance(self) -> bool:
        """Check if UI should auto-advance through steps."""
        return self.profile.auto_advance
    
    def get_explanation_detail_level(self) -> str:
        """Get appropriate explanation detail level."""
        if self.profile.detailed_explanations:
            return "detailed"
        elif self.profile.complexity_level == "technical":
            return "technical" 
        else:
            return "simple"


# Utility functions for persona detection and switching
def detect_persona_from_input(user_input: str) -> Optional[PersonaType]:
    """Attempt to detect persona from user input patterns."""
    input_lower = user_input.lower()
    
    # Simple heuristics for persona detection
    if any(phrase in input_lower for phrase in ["please help", "i don't understand", "what is"]):
        return PersonaType.CARLOS  # Learning/help-seeking
    
    if len(user_input.split()) <= 3 and any(urgent in input_lower for urgent in ["fast", "quick", "now"]):
        return PersonaType.MAYA  # Quick/urgent requests
    
    if any(phrase in input_lower for phrase in ["privacy", "secure", "data", "track"]):
        return PersonaType.JAMIE  # Privacy-conscious
    
    if any(phrase in input_lower for phrase in ["screen reader", "accessibility", "speak"]):
        return PersonaType.ALEX  # Accessibility needs
    
    return None  # No clear persona detected


def get_persona_specific_help_text(persona: PersonaType) -> str:
    """Get help text adapted for specific persona."""
    profile = PERSONA_PROFILES[persona]
    
    if persona == PersonaType.GRANDMA_ROSE:
        return """
Welcome! I'm here to help you with your computer in simple terms.
You can ask me things like:
• "I need Firefox" 
• "Help me update my computer"
• "Make the text bigger"

Just speak naturally - I understand!
"""
    
    elif persona == PersonaType.MAYA:
        return """
Quick help:
• install [app] - Install software
• update - Update system  
• wifi - Fix network
• help - This menu

Fast responses, minimal text. Let's go! 🚀
"""
    
    elif persona == PersonaType.ALEX:
        return """
Accessibility-optimized help:

Main commands:
1. Install software: "install [program name]"
2. System update: "update system"
3. Network help: "wifi help"

All responses are screen reader optimized.
Tab to navigate, Enter to select.
"""
    
    elif persona == PersonaType.DR_SARAH:
        return """
Technical interface ready. Available operations:
• Package management: install, remove, search
• System operations: update, rollback, configure  
• Development tools: compiler setup, environment config
• Research tools: LaTeX, Jupyter, scientific computing

Full NixOS integration with detailed explanations.
"""
    
    else:
        return f"""
Hello {profile.name}! Here's what I can help you with:

• Installing and removing software
• Updating your system
• Fixing network issues  
• Managing files and settings

Just describe what you need in your own words!
"""