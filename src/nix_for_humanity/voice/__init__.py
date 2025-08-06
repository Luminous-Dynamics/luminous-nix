"""
🗣️ Voice Interface for Nix for Humanity

Natural conversation interface using pipecat for low-latency, accessibility-first voice interaction.
This module enables Grandma Rose to say "I need that Firefox thing" and have it just work.
"""

from .pipecat_interface import PipecatVoiceInterface
from .voice_config import VoiceConfig, PersonaVoiceSettings

__all__ = [
    "PipecatVoiceInterface",
    "VoiceConfig",
    "PersonaVoiceSettings",
]