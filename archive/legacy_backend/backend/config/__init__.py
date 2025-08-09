"""
Configuration module for Nix for Humanity
"""

from .research_config import (
    ResearchConfig,
    get_research_config,
    update_research_config,
    research_config
)

__all__ = [
    'ResearchConfig',
    'get_research_config', 
    'update_research_config',
    'research_config'
]