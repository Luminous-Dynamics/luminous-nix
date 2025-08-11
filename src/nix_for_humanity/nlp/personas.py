"""Persona management for different user types"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Persona:
    """Represents a user persona"""

    name: str
    level: str  # beginner, intermediate, expert
    style: str  # technical, friendly, encouraging
    preferences: dict[str, Any]


class PersonaManager:
    """Manages different user personas for tailored responses"""

    def __init__(self):
        self.personas = {
            "default": Persona(
                name="default",
                level="intermediate",
                style="helpful",
                preferences={"verbose": False, "examples": True},
            ),
            "beginner": Persona(
                name="beginner",
                level="beginner",
                style="encouraging",
                preferences={"verbose": True, "examples": True, "explanations": True},
            ),
            "expert": Persona(
                name="expert",
                level="expert",
                style="technical",
                preferences={"verbose": False, "examples": False, "technical": True},
            ),
            "grandma_rose": Persona(
                name="grandma_rose",
                level="beginner",
                style="gentle",
                preferences={
                    "verbose": True,
                    "examples": True,
                    "simple_language": True,
                },
            ),
        }

        self.current_persona = self.personas["default"]

    def get_persona(self, name: str = "default") -> Persona:
        """Get a specific persona by name"""
        return self.personas.get(name, self.personas["default"])

    def set_persona(self, name: str) -> None:
        """Set the current active persona"""
        self.current_persona = self.get_persona(name)

    def get_response_style(self) -> dict[str, Any]:
        """Get the response style for the current persona"""
        return {
            "level": self.current_persona.level,
            "style": self.current_persona.style,
            "preferences": self.current_persona.preferences,
        }

    def format_response(
        self,
        response: str,
        context: dict[str, Any] | None = None,
        persona_name: str | None = None,
    ) -> str:
        """Format a response according to persona preferences

        Args:
            response: The base response message
            context: Optional context dict with action details (not used currently but accepted for compatibility)
            persona_name: Optional specific persona to use
        """
        # If context is passed as second arg and it's a string, it's actually persona_name
        if isinstance(context, str):
            persona_name = context
            context = None

        persona = (
            self.get_persona(persona_name) if persona_name else self.current_persona
        )

        if persona.level == "beginner":
            # Add more explanation for beginners
            response = f"Let me explain: {response}"
            if persona.preferences.get("simple_language"):
                # Could add simple language processing here
                response = response.replace("configure", "set up")
                response = response.replace("package", "program")
                response = response.replace("repository", "software collection")

        elif persona.level == "expert":
            # Keep it concise for experts
            response = response.replace("Let me explain: ", "")

        return response
