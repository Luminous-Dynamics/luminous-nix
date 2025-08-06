# Personality System
"""
Adaptive response personality system for different user needs
"""

from typing import Dict, Optional
from enum import Enum


class PersonalityStyle(Enum):
    """Available personality styles"""
    MINIMAL = "minimal"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    TECHNICAL = "technical"
    SYMBIOTIC = "symbiotic"
    ADAPTIVE = "adaptive"


class PersonalitySystem:
    """Manages response personality and adaptation"""
    
    def __init__(self, default_style: PersonalityStyle = PersonalityStyle.FRIENDLY):
        self.current_style = default_style
        self.user_preferences = {}
        
    def adapt_response(self, base_response: str, query: str, style: Optional[PersonalityStyle] = None) -> str:
        """Adapt response based on personality style"""
        
        style = style or self.current_style
        
        if style == PersonalityStyle.MINIMAL:
            # Just return the facts
            return base_response
            
        elif style == PersonalityStyle.FRIENDLY:
            # Add warm greeting and closing
            enhanced = f"Hi there! {base_response}"
            if "?" not in base_response:
                enhanced += "\n\nLet me know if you need any clarification! 😊"
            return enhanced
            
        elif style == PersonalityStyle.ENCOURAGING:
            # Add encouragement for learning
            enhanced = f"Great question! {base_response}"
            
            # Add context-specific encouragement
            if any(word in query.lower() for word in ['first', 'new', 'beginner', 'start']):
                enhanced += "\n\nYou're doing great getting started with NixOS! 🌟"
            elif 'error' in query.lower() or 'problem' in query.lower():
                enhanced += "\n\nDon't worry, everyone encounters this! You're learning! 💪"
            else:
                enhanced += "\n\nYou're doing awesome learning NixOS! Keep it up! 🌟"
                
            return enhanced
            
        elif style == PersonalityStyle.TECHNICAL:
            # Add technical depth
            enhanced = base_response
            
            # Add technical notes based on content
            if 'nix profile' in base_response:
                enhanced += "\n\nTechnical note: nix profile uses the new Nix 2.0 CLI with improved UX over nix-env."
            elif 'nixos-rebuild' in base_response:
                enhanced += "\n\nNote: This follows NixOS's declarative configuration paradigm."
            elif 'declarative' in base_response.lower():
                enhanced += "\n\nTechnical detail: Declarative configuration ensures reproducibility and rollback capability."
                
            return enhanced
            
        elif style == PersonalityStyle.SYMBIOTIC:
            # Admit uncertainty and invite partnership
            enhanced = base_response
            enhanced += "\n\n🤝 I'm still learning! Was this helpful? Your feedback helps me improve."
            
            # Add learning context
            if 'error' in query.lower():
                enhanced += "\n\nIf you found a solution, I'd love to learn it for next time!"
            
            return enhanced
            
        elif style == PersonalityStyle.ADAPTIVE:
            # Detect user needs and adapt automatically
            return self._adaptive_response(base_response, query)
            
        return base_response
        
    def _adaptive_response(self, base_response: str, query: str) -> str:
        """Automatically adapt based on query analysis"""
        
        query_lower = query.lower()
        
        # Detect user expertise level
        if any(word in query_lower for word in ['help', 'how', 'what', 'new', 'first']):
            # Beginner - use encouraging
            return self.adapt_response(base_response, query, PersonalityStyle.ENCOURAGING)
            
        elif any(word in query_lower for word in ['config', 'flake', 'overlay', 'derivation']):
            # Advanced - use technical
            return self.adapt_response(base_response, query, PersonalityStyle.TECHNICAL)
            
        elif any(word in query_lower for word in ['please', 'thanks', 'hi', 'hello']):
            # Polite - use friendly
            return self.adapt_response(base_response, query, PersonalityStyle.FRIENDLY)
            
        elif len(query.split()) <= 3:
            # Terse query - use minimal
            return self.adapt_response(base_response, query, PersonalityStyle.MINIMAL)
            
        else:
            # Default to friendly
            return self.adapt_response(base_response, query, PersonalityStyle.FRIENDLY)
            
    def set_style(self, style: PersonalityStyle):
        """Set the current personality style"""
        self.current_style = style
        
    def learn_preference(self, user_id: str, preferred_style: PersonalityStyle):
        """Learn user's preferred style"""
        self.user_preferences[user_id] = preferred_style
        
    def get_user_style(self, user_id: str) -> PersonalityStyle:
        """Get user's preferred style or default"""
        return self.user_preferences.get(user_id, self.current_style)
        
    def get_style_description(self, style: PersonalityStyle) -> str:
        """Get description of a personality style"""
        
        descriptions = {
            PersonalityStyle.MINIMAL: "Just the facts, no extra text",
            PersonalityStyle.FRIENDLY: "Warm and helpful with emojis",
            PersonalityStyle.ENCOURAGING: "Supportive for beginners",
            PersonalityStyle.TECHNICAL: "Detailed technical explanations",
            PersonalityStyle.SYMBIOTIC: "Learning together as partners",
            PersonalityStyle.ADAPTIVE: "Automatically adjusts to your needs"
        }
        
        return descriptions.get(style, "Unknown style")