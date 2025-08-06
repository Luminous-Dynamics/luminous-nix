"""
Explanation formatting for different personas and contexts
Adapts XAI explanations to user preferences and understanding levels
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import textwrap
import json

from .causal_engine import (
    CausalExplanation,
    ExplanationLevel,
    ConfidenceLevel,
    DecisionNode
)


class PersonaType(Enum):
    """The 10 core personas of Nix for Humanity"""
    GRANDMA_ROSE = "grandma_rose"        # 75, voice-first, gentle
    MAYA_ADHD = "maya_adhd"              # 16, ADHD, fast responses
    DAVID_PARENT = "david_parent"        # 42, tired parent, stress-free
    DR_SARAH = "dr_sarah"                # 35, researcher, precise
    ALEX_BLIND = "alex_blind"            # 28, blind developer, screen reader
    CARLOS_LEARNER = "carlos_learner"    # 52, career switcher, educational
    PRIYA_MOM = "priya_mom"              # 34, single mom, quick & clear
    JAMIE_PRIVACY = "jamie_privacy"      # 19, privacy advocate, transparent
    VIKTOR_ESL = "viktor_esl"            # 67, ESL, simple language
    LUNA_AUTISTIC = "luna_autistic"      # 14, autistic, predictable


@dataclass
class FormattingPreferences:
    """User-specific formatting preferences"""
    max_length: int = 200
    use_emojis: bool = False
    use_technical_terms: bool = False
    prefer_examples: bool = True
    screen_reader_optimized: bool = False
    response_speed: str = "normal"  # "fast", "normal", "detailed"
    language_complexity: str = "medium"  # "simple", "medium", "complex"


class PersonaExplanationAdapter:
    """Adapts explanations to specific personas"""
    
    def __init__(self):
        self.persona_preferences = self._initialize_persona_preferences()
    
    def _initialize_persona_preferences(self) -> Dict[PersonaType, FormattingPreferences]:
        """Define formatting preferences for each persona"""
        return {
            PersonaType.GRANDMA_ROSE: FormattingPreferences(
                max_length=100,
                use_emojis=True,
                use_technical_terms=False,
                prefer_examples=True,
                language_complexity="simple"
            ),
            PersonaType.MAYA_ADHD: FormattingPreferences(
                max_length=50,
                use_emojis=False,
                response_speed="fast",
                language_complexity="simple"
            ),
            PersonaType.DR_SARAH: FormattingPreferences(
                max_length=500,
                use_technical_terms=True,
                prefer_examples=False,
                response_speed="detailed",
                language_complexity="complex"
            ),
            PersonaType.ALEX_BLIND: FormattingPreferences(
                screen_reader_optimized=True,
                use_emojis=False,
                prefer_examples=True,
                language_complexity="medium"
            ),
            PersonaType.CARLOS_LEARNER: FormattingPreferences(
                max_length=300,
                use_emojis=True,
                prefer_examples=True,
                language_complexity="medium",
                response_speed="detailed"
            ),
            PersonaType.VIKTOR_ESL: FormattingPreferences(
                max_length=150,
                use_technical_terms=False,
                language_complexity="simple",
                prefer_examples=True
            ),
            PersonaType.LUNA_AUTISTIC: FormattingPreferences(
                max_length=200,
                use_emojis=False,
                language_complexity="simple",
                response_speed="normal"
            ),
            PersonaType.DAVID_PARENT: FormattingPreferences(
                max_length=150,
                use_emojis=False,
                language_complexity="simple",
                response_speed="fast"
            ),
            PersonaType.PRIYA_MOM: FormattingPreferences(
                max_length=100,
                response_speed="fast",
                language_complexity="simple"
            ),
            PersonaType.JAMIE_PRIVACY: FormattingPreferences(
                max_length=300,
                use_technical_terms=True,
                language_complexity="medium",
                prefer_examples=True
            )
        }
    
    def adapt_for_persona(
        self, 
        explanation: CausalExplanation,
        persona: PersonaType
    ) -> Dict[str, Any]:
        """Adapt an explanation for a specific persona"""
        prefs = self.persona_preferences.get(persona, FormattingPreferences())
        
        # Format the main explanation
        formatted_text = self._format_text(explanation.primary_reason, prefs)
        
        # Build adapted response
        response = {
            "text": formatted_text,
            "confidence": self._format_confidence(explanation.confidence, prefs),
            "style": self._get_style_for_persona(persona)
        }
        
        # Add details based on persona preferences
        if prefs.response_speed == "detailed" and explanation.contributing_factors:
            response["details"] = self._format_factors(explanation.contributing_factors, prefs)
        
        if prefs.prefer_examples and explanation.alternative_paths:
            response["alternatives"] = self._format_alternatives(explanation.alternative_paths, prefs)
        
        if prefs.screen_reader_optimized:
            response["aria_label"] = self._create_aria_label(explanation)
            response["aria_live"] = "polite"
        
        return response
    
    def _format_text(self, text: str, prefs: FormattingPreferences) -> str:
        """Format text according to preferences"""
        # Simplify language if needed
        if prefs.language_complexity == "simple":
            text = self._simplify_language(text)
        
        # Truncate if too long
        if len(text) > prefs.max_length:
            text = textwrap.shorten(text, width=prefs.max_length, placeholder="...")
        
        # Add emoji if preferred
        if prefs.use_emojis:
            text = self._add_contextual_emoji(text)
        
        return text
    
    def _simplify_language(self, text: str) -> str:
        """Simplify complex language"""
        replacements = {
            "decided to": "will",
            "because": "since",
            "multiple factors": "several reasons",
            "contributing factors": "things that helped",
            "confidence": "sure",
            "alternative": "other way"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _add_contextual_emoji(self, text: str) -> str:
        """Add appropriate emoji based on context"""
        emoji_map = {
            "install": "📦",
            "update": "🔄",
            "fix": "🔧",
            "error": "⚠️",
            "success": "✅",
            "help": "💡"
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in text.lower():
                return f"{emoji} {text}"
        
        return text
    
    def _format_confidence(self, confidence: ConfidenceLevel, prefs: FormattingPreferences) -> str:
        """Format confidence level for persona"""
        if prefs.language_complexity == "simple":
            simple_map = {
                ConfidenceLevel.CERTAIN: "very sure",
                ConfidenceLevel.HIGH: "pretty sure",
                ConfidenceLevel.MEDIUM: "somewhat sure",
                ConfidenceLevel.LOW: "not very sure"
            }
            return simple_map.get(confidence, "unsure")
        else:
            return confidence.value
    
    def _format_factors(self, factors: List[DecisionNode], prefs: FormattingPreferences) -> List[str]:
        """Format contributing factors"""
        formatted = []
        for factor in factors[:3]:  # Limit to top 3
            text = factor.description
            if prefs.language_complexity == "simple":
                text = self._simplify_language(text)
            formatted.append(text)
        return formatted
    
    def _format_alternatives(self, alternatives: List[Dict[str, Any]], prefs: FormattingPreferences) -> List[Dict[str, str]]:
        """Format alternative approaches"""
        formatted = []
        for alt in alternatives[:2]:  # Limit to 2 alternatives
            formatted.append({
                "option": self._simplify_language(alt["decision"]) if prefs.language_complexity == "simple" else alt["decision"],
                "reason": self._simplify_language(alt["reason"]) if prefs.language_complexity == "simple" else alt["reason"]
            })
        return formatted
    
    def _create_aria_label(self, explanation: CausalExplanation) -> str:
        """Create screen reader optimized label"""
        label = f"AI decision: {explanation.decision}. "
        label += f"Reason: {explanation.primary_reason}. "
        label += f"Confidence: {explanation.confidence.value}."
        return label
    
    def _get_style_for_persona(self, persona: PersonaType) -> str:
        """Get response style for persona"""
        style_map = {
            PersonaType.GRANDMA_ROSE: "gentle",
            PersonaType.MAYA_ADHD: "minimal",
            PersonaType.DR_SARAH: "technical",
            PersonaType.ALEX_BLIND: "descriptive",
            PersonaType.CARLOS_LEARNER: "educational",
            PersonaType.VIKTOR_ESL: "clear",
            PersonaType.LUNA_AUTISTIC: "consistent",
            PersonaType.DAVID_PARENT: "efficient",
            PersonaType.PRIYA_MOM: "concise",
            PersonaType.JAMIE_PRIVACY: "transparent"
        }
        return style_map.get(persona, "balanced")


class ExplanationFormatter:
    """Main formatter for XAI explanations"""
    
    def __init__(self):
        self.persona_adapter = PersonaExplanationAdapter()
    
    def format_explanation(
        self,
        explanation: CausalExplanation,
        format_type: str = "text",
        persona: Optional[PersonaType] = None,
        **kwargs
    ) -> str:
        """Format explanation in requested format"""
        if format_type == "text":
            return self._format_as_text(explanation, persona)
        elif format_type == "json":
            return self._format_as_json(explanation, persona)
        elif format_type == "markdown":
            return self._format_as_markdown(explanation, persona)
        elif format_type == "tui":
            return self._format_for_tui(explanation, persona)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_as_text(self, explanation: CausalExplanation, persona: Optional[PersonaType]) -> str:
        """Format as plain text"""
        if persona:
            adapted = self.persona_adapter.adapt_for_persona(explanation, persona)
            return adapted["text"]
        
        # Default formatting
        lines = [
            f"Decision: {explanation.decision}",
            f"Reason: {explanation.primary_reason}",
            f"Confidence: {explanation.confidence.value} ({explanation.confidence_score:.1%})"
        ]
        
        if explanation.contributing_factors:
            lines.append("\nContributing factors:")
            for factor in explanation.contributing_factors:
                lines.append(f"  • {factor.description} ({factor.confidence:.1%} confidence)")
        
        return "\n".join(lines)
    
    def _format_as_json(self, explanation: CausalExplanation, persona: Optional[PersonaType]) -> str:
        """Format as JSON"""
        if persona:
            adapted = self.persona_adapter.adapt_for_persona(explanation, persona)
            return json.dumps(adapted, indent=2)
        
        return json.dumps(explanation.to_dict(), indent=2)
    
    def _format_as_markdown(self, explanation: CausalExplanation, persona: Optional[PersonaType]) -> str:
        """Format as Markdown"""
        if persona:
            adapted = self.persona_adapter.adapt_for_persona(explanation, persona)
            md = f"## {explanation.decision}\n\n"
            md += f"{adapted['text']}\n\n"
            md += f"**Confidence**: {adapted['confidence']}\n"
            return md
        
        # Default markdown
        md = f"## {explanation.decision}\n\n"
        md += f"{explanation.primary_reason}\n\n"
        md += f"**Confidence**: {explanation.confidence.value} ({explanation.confidence_score:.1%})\n\n"
        
        if explanation.contributing_factors:
            md += "### Contributing Factors\n\n"
            for factor in explanation.contributing_factors:
                md += f"- **{factor.description}** (confidence: {factor.confidence:.1%})\n"
        
        return md
    
    def _format_for_tui(self, explanation: CausalExplanation, persona: Optional[PersonaType]) -> Dict[str, Any]:
        """Format for Textual TUI display"""
        if persona:
            adapted = self.persona_adapter.adapt_for_persona(explanation, persona)
            return {
                "type": "explanation_panel",
                "title": "Why I made this decision",
                "content": adapted["text"],
                "confidence": adapted["confidence"],
                "style": adapted.get("style", "balanced"),
                "details": adapted.get("details", []),
                "alternatives": adapted.get("alternatives", [])
            }
        
        # Default TUI format
        return {
            "type": "explanation_panel",
            "title": "Decision Explanation",
            "content": explanation.primary_reason,
            "confidence": f"{explanation.confidence.value} ({explanation.confidence_score:.1%})",
            "factors": [
                {
                    "name": f.description,
                    "confidence": f"{f.confidence:.1%}",
                    "weight": f.weight
                }
                for f in explanation.contributing_factors
            ],
            "alternatives": explanation.alternative_paths
        }
    
    def create_progress_explanation(self, operation: str, step: int, total: int) -> str:
        """Create explanation for operation progress"""
        percentage = (step / total) * 100 if total > 0 else 0
        return f"Performing {operation}: Step {step}/{total} ({percentage:.0f}% complete)"