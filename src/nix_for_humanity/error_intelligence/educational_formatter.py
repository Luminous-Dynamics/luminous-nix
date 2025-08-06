"""
Educational Error Formatter - Makes errors helpful and persona-adaptive

This module transforms technical errors into educational opportunities,
adapting explanations to each persona's needs and learning style.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
import logging

from .error_analyzer import AnalyzedError, ErrorSolution, ErrorSeverity
from ..core.types import Context
from ..xai.explanation_formatter import PersonaExplanationAdapter, ExplanationLevel

logger = logging.getLogger(__name__)


class LearningStyle(Enum):
    """Different learning styles for error explanations"""
    VISUAL = "visual"          # Prefers diagrams and examples
    TEXTUAL = "textual"        # Prefers detailed text
    PRACTICAL = "practical"    # Prefers hands-on solutions
    CONCEPTUAL = "conceptual"  # Prefers understanding why


@dataclass
class EducationalError:
    """An error formatted for learning"""
    headline: str                    # Brief, friendly summary
    explanation: str                 # What went wrong in simple terms
    learning_point: str              # What to remember for next time
    solutions: List[str]             # Step-by-step solutions
    examples: Optional[List[str]] = None  # Concrete examples
    diagram: Optional[str] = None    # ASCII diagram if helpful
    confidence_message: str = ""     # Encouragement based on severity
    related_concepts: List[str] = None  # Links to learn more


class EducationalErrorFormatter:
    """
    Transforms technical errors into educational opportunities,
    adapting to each persona's learning style and needs.
    """
    
    def __init__(self):
        self.persona_adapter = PersonaExplanationAdapter()
        self._init_persona_styles()
        self._init_encouragement_templates()
    
    def _init_persona_styles(self):
        """Initialize learning styles for each persona"""
        self.persona_learning_styles = {
            "grandma_rose": LearningStyle.PRACTICAL,
            "maya_adhd": LearningStyle.VISUAL,
            "david_tired": LearningStyle.PRACTICAL,
            "dr_sarah": LearningStyle.CONCEPTUAL,
            "alex_blind": LearningStyle.TEXTUAL,
            "carlos_learner": LearningStyle.PRACTICAL,
            "priya_busy": LearningStyle.PRACTICAL,
            "jamie_privacy": LearningStyle.CONCEPTUAL,
            "viktor_esl": LearningStyle.VISUAL,
            "luna_autistic": LearningStyle.TEXTUAL
        }
    
    def _init_encouragement_templates(self):
        """Initialize encouragement messages by severity"""
        self.encouragement = {
            ErrorSeverity.INFO: [
                "No worries! This is just informational.",
                "Good to know for next time!",
                "You're doing great - this is just a tip."
            ],
            ErrorSeverity.WARNING: [
                "This is common - you're not alone!",
                "Many users encounter this. Here's how to fix it:",
                "Don't worry, this is easily resolved."
            ],
            ErrorSeverity.ERROR: [
                "Errors happen to everyone. Let's fix this together!",
                "You're learning! This error will help you understand NixOS better.",
                "Every expert was once a beginner. Here's what to do:"
            ],
            ErrorSeverity.CRITICAL: [
                "This is important, but we can handle it step by step.",
                "Take a deep breath. We'll work through this carefully.",
                "Critical doesn't mean impossible. Follow these steps:"
            ]
        }
    
    def format_error(
        self,
        analyzed_error: AnalyzedError,
        context: Optional[Context] = None,
        explanation_level: ExplanationLevel = ExplanationLevel.SIMPLE
    ) -> EducationalError:
        """
        Format an analyzed error into an educational opportunity
        
        Args:
            analyzed_error: The analyzed error with solutions
            context: User context including persona
            explanation_level: How detailed the explanation should be
        
        Returns:
            Educational error formatted for the user's persona
        """
        persona = self._get_persona(context)
        learning_style = self.persona_learning_styles.get(
            persona, LearningStyle.PRACTICAL
        )
        
        # Create base educational error
        educational_error = EducationalError(
            headline=self._create_headline(analyzed_error, persona),
            explanation=self._create_explanation(
                analyzed_error, persona, explanation_level
            ),
            learning_point=self._create_learning_point(analyzed_error, persona),
            solutions=self._format_solutions(analyzed_error.solutions, persona),
            confidence_message=self._get_encouragement(analyzed_error.severity),
            related_concepts=self._get_related_concepts(analyzed_error)
        )
        
        # Add persona-specific enhancements
        if learning_style == LearningStyle.VISUAL and persona != "alex_blind":
            educational_error.diagram = self._create_diagram(analyzed_error)
            educational_error.examples = self._create_visual_examples(analyzed_error)
        elif learning_style == LearningStyle.PRACTICAL:
            educational_error.examples = self._create_practical_examples(analyzed_error)
        elif learning_style == LearningStyle.CONCEPTUAL:
            educational_error.explanation = self._add_conceptual_depth(
                educational_error.explanation, analyzed_error
            )
        
        # Apply persona-specific formatting
        educational_error = self._apply_persona_formatting(
            educational_error, persona, analyzed_error
        )
        
        return educational_error
    
    def _get_persona(self, context: Optional[Context]) -> str:
        """Extract persona from context"""
        if not context or not hasattr(context, 'user_preferences'):
            return "friendly"  # Default
        
        return context.user_preferences.get('persona', 'friendly')
    
    def _create_headline(self, error: AnalyzedError, persona: str) -> str:
        """Create a friendly, persona-appropriate headline"""
        if persona == "grandma_rose":
            if error.category.value == "not_found":
                return "Oh dear, I couldn't find that program!"
            elif error.category.value == "permission":
                return "We need special permission for this, dear."
            else:
                return "Something didn't work quite right."
        
        elif persona == "maya_adhd":
            if error.category.value == "not_found":
                return "❌ Package not found"
            elif error.category.value == "permission":
                return "🔒 Need sudo"
            else:
                return "⚠️ Error occurred"
        
        elif persona == "dr_sarah":
            if error.pattern:
                return f"Error: {error.pattern.description}"
            else:
                return f"Error: {error.category.value.replace('_', ' ').title()}"
        
        # Default friendly headline
        if error.category.value == "not_found":
            return "I couldn't find that package"
        elif error.category.value == "permission":
            return "This needs administrator privileges"
        else:
            return "Something went wrong"
    
    def _create_explanation(
        self,
        error: AnalyzedError,
        persona: str,
        level: ExplanationLevel
    ) -> str:
        """Create an educational explanation of what went wrong"""
        base_explanation = error.pattern.description if error.pattern else \
                          "An unexpected error occurred"
        
        if persona == "grandma_rose":
            # Very simple, relatable explanation
            if "not found" in base_explanation.lower():
                return "The computer couldn't find a program with that exact name. Sometimes programs have different names than we expect!"
            elif "permission" in base_explanation.lower():
                return "This is like trying to change something important - we need the administrator's key (password) first."
            return "The computer ran into a small problem. Don't worry, we can fix it!"
        
        elif persona == "maya_adhd":
            # Ultra-concise explanation
            return base_explanation.split('.')[0] + "."
        
        elif persona == "dr_sarah" and level == ExplanationLevel.TECHNICAL:
            # Add technical details
            technical_details = []
            if error.pattern and error.pattern.common_causes:
                technical_details.append(
                    f"Common causes: {', '.join(error.pattern.common_causes[:2])}"
                )
            if error.xai_explanation:
                technical_details.append(f"Analysis: {error.xai_explanation}")
            
            return f"{base_explanation} {' '.join(technical_details)}"
        
        # Default explanation with appropriate detail level
        if level == ExplanationLevel.SIMPLE:
            return base_explanation.split('.')[0] + "."
        elif level == ExplanationLevel.DETAILED:
            return base_explanation
        else:  # TECHNICAL
            causes = error.pattern.common_causes[:3] if error.pattern else []
            if causes:
                return f"{base_explanation} This typically happens because: {', '.join(causes)}"
            return base_explanation
    
    def _create_learning_point(self, error: AnalyzedError, persona: str) -> str:
        """Create a memorable learning point from this error"""
        if persona == "grandma_rose":
            if error.category.value == "not_found":
                return "Remember: Programs sometimes have technical names. We can always search first!"
            elif error.category.value == "permission":
                return "Remember: Some changes need the administrator password, just like a locked cabinet needs a key."
            return "Remember: Computers are very particular about exact names and spelling."
        
        elif persona == "maya_adhd":
            if error.category.value == "not_found":
                return "💡 Use search first"
            elif error.category.value == "permission":
                return "💡 Add sudo"
            return "💡 Check spelling"
        
        elif persona == "carlos_learner":
            # Educational focus
            if error.category.value == "not_found":
                return "Learning tip: NixOS packages often have different names than other Linux distributions. Use 'nix search' to find the right name!"
            elif error.category.value == "permission":
                return "Learning tip: NixOS separates user and system packages. System-wide changes need sudo, but user packages don't!"
            return f"Learning tip: This error teaches us about {error.category.value.replace('_', ' ')}"
        
        # Default learning point
        if error.preventive_suggestions:
            return f"For next time: {error.preventive_suggestions[0]}"
        return "This helps us learn how NixOS works!"
    
    def _format_solutions(
        self,
        solutions: List[ErrorSolution],
        persona: str
    ) -> List[str]:
        """Format solutions for the persona's needs"""
        formatted_solutions = []
        
        for i, solution in enumerate(solutions[:3]):  # Top 3 solutions
            if persona == "grandma_rose":
                # Very gentle, step-by-step
                steps = []
                steps.append(f"Option {i+1}: {solution.title}")
                for j, step in enumerate(solution.steps[:2]):
                    steps.append(f"   {j+1}. {self._simplify_technical_terms(step)}")
                if solution.warnings:
                    steps.append(f"   Note: {solution.warnings[0]}")
                formatted_solutions.extend(steps)
            
            elif persona == "maya_adhd":
                # Just the command
                if solution.commands:
                    formatted_solutions.append(f"{i+1}. `{solution.commands[0]}`")
                else:
                    formatted_solutions.append(f"{i+1}. {solution.title}")
            
            elif persona == "dr_sarah":
                # Full technical solution
                formatted_solutions.append(f"\n{i+1}. {solution.title}")
                formatted_solutions.append(f"   Confidence: {solution.confidence:.1%}")
                for step in solution.steps:
                    formatted_solutions.append(f"   - {step}")
                for cmd in solution.commands:
                    formatted_solutions.append(f"   $ {cmd}")
                if solution.explanation:
                    formatted_solutions.append(f"   Rationale: {solution.explanation}")
            
            else:
                # Default balanced format
                formatted_solutions.append(f"{i+1}. {solution.title}")
                for step in solution.steps[:2]:
                    formatted_solutions.append(f"   • {step}")
                if solution.commands:
                    formatted_solutions.append(f"   Run: {solution.commands[0]}")
        
        return formatted_solutions
    
    def _create_diagram(self, error: AnalyzedError) -> Optional[str]:
        """Create an ASCII diagram for visual learners"""
        if error.category.value == "not_found":
            return """
    You asked for: "firefox"
           ↓
    🔍 Searching nixpkgs...
           ↓
    ❌ Not found exactly
           ↓
    💡 Did you mean: firefox, firefox-esr, firefox-bin?
    """
        
        elif error.category.value == "permission":
            return """
    Your request → System files
         ↓            ↓
    Regular user   🔒 Protected
         ↓            ↓
    ❌ Denied     Need sudo! → ✅ Allowed
    """
        
        return None
    
    def _create_visual_examples(self, error: AnalyzedError) -> List[str]:
        """Create visual examples for learning"""
        if error.category.value == "not_found":
            return [
                "❌ install fierfix  →  ✅ install firefox",
                "❌ install vscode   →  ✅ install vscode or vscodium",
                "❌ install java     →  ✅ install openjdk or jdk"
            ]
        return []
    
    def _create_practical_examples(self, error: AnalyzedError) -> List[str]:
        """Create practical examples for hands-on learners"""
        if error.category.value == "not_found":
            return [
                "First, search: nix search firefox",
                "Then install: nix-env -iA nixos.firefox",
                "Or add to config: environment.systemPackages = [ pkgs.firefox ];"
            ]
        elif error.category.value == "permission":
            return [
                "For system: sudo nixos-rebuild switch",
                "For user only: nix-env -iA nixos.firefox",
                "Check permissions: ls -la /etc/nixos/"
            ]
        return []
    
    def _add_conceptual_depth(self, explanation: str, error: AnalyzedError) -> str:
        """Add conceptual understanding for analytical learners"""
        conceptual_additions = []
        
        if error.category.value == "not_found":
            conceptual_additions.append(
                "This illustrates NixOS's declarative package management: every package must be explicitly defined in the Nix expression language."
            )
        elif error.category.value == "permission":
            conceptual_additions.append(
                "NixOS's security model separates user and system environments, preventing accidental system damage."
            )
        
        if conceptual_additions:
            return f"{explanation} {' '.join(conceptual_additions)}"
        return explanation
    
    def _apply_persona_formatting(
        self,
        educational_error: EducationalError,
        persona: str,
        analyzed_error: AnalyzedError
    ) -> EducationalError:
        """Apply final persona-specific formatting touches"""
        if persona == "luna_autistic":
            # Consistent, predictable formatting
            educational_error.solutions = [
                f"Step {i+1}: {sol}" for i, sol in enumerate(educational_error.solutions)
            ]
        
        elif persona == "jamie_privacy":
            # Add privacy-related notes
            if analyzed_error.category.value == "network":
                educational_error.explanation += " Note: All operations happen locally. No data is sent externally."
        
        elif persona == "viktor_esl":
            # Simplify language
            educational_error.explanation = self._simplify_language(educational_error.explanation)
            educational_error.learning_point = self._simplify_language(educational_error.learning_point)
        
        return educational_error
    
    def _get_encouragement(self, severity: ErrorSeverity) -> str:
        """Get an encouraging message based on error severity"""
        import random
        messages = self.encouragement.get(severity, ["We can fix this!"])
        return random.choice(messages)
    
    def _get_related_concepts(self, error: AnalyzedError) -> List[str]:
        """Get related concepts for further learning"""
        concepts = []
        
        if error.category.value == "not_found":
            concepts.extend([
                "Package naming in NixOS",
                "Using nix search effectively",
                "Understanding Nix channels"
            ])
        elif error.category.value == "permission":
            concepts.extend([
                "User vs system packages",
                "NixOS security model",
                "Declarative configuration"
            ])
        
        return concepts[:3]  # Top 3 concepts
    
    def _simplify_technical_terms(self, text: str) -> str:
        """Simplify technical terms for non-technical users"""
        replacements = {
            "sudo": "administrator permission",
            "package": "program",
            "nixpkgs": "the program library",
            "derivation": "installation recipe",
            "channel": "software source",
            "configuration.nix": "system settings file"
        }
        
        result = text
        for tech, simple in replacements.items():
            result = result.replace(tech, simple)
        
        return result
    
    def _simplify_language(self, text: str) -> str:
        """Simplify language for ESL users"""
        # Use shorter sentences
        sentences = text.split('. ')
        simplified = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 15:
                # Break long sentences
                mid = len(words) // 2
                simplified.append(' '.join(words[:mid]) + '.')
                simplified.append(' '.join(words[mid:]) + '.')
            else:
                simplified.append(sentence + '.')
        
        return ' '.join(simplified).replace('..', '.')
    
    def format_for_tui(
        self,
        educational_error: EducationalError,
        width: int = 80
    ) -> str:
        """Format educational error for TUI display"""
        lines = []
        
        # Headline with emoji
        lines.append(f"❗ {educational_error.headline}")
        lines.append("")
        
        # Explanation
        lines.append("What happened:")
        lines.append(self._wrap_text(educational_error.explanation, width - 2))
        lines.append("")
        
        # Learning point with lightbulb
        lines.append(f"💡 {educational_error.learning_point}")
        lines.append("")
        
        # Solutions
        lines.append("How to fix:")
        for solution in educational_error.solutions:
            lines.append(solution)
        lines.append("")
        
        # Diagram if present
        if educational_error.diagram:
            lines.append("Visual explanation:")
            lines.append(educational_error.diagram)
            lines.append("")
        
        # Examples if present
        if educational_error.examples:
            lines.append("Examples:")
            for example in educational_error.examples:
                lines.append(f"  {example}")
            lines.append("")
        
        # Encouragement
        lines.append(f"✨ {educational_error.confidence_message}")
        
        # Related concepts
        if educational_error.related_concepts:
            lines.append("")
            lines.append("Learn more about:")
            for concept in educational_error.related_concepts:
                lines.append(f"  • {concept}")
        
        return '\n'.join(lines)
    
    def _wrap_text(self, text: str, width: int) -> str:
        """Wrap text to specified width"""
        import textwrap
        return '\n'.join(textwrap.wrap(text, width))