"""AI and NLP components for Nix for Humanity."""

from .nlp import (
    NLPPipeline,
    extract_package_name,
    get_explanation_for_user,
    process,
    record_interaction_feedback,
)

# Alias for backward compatibility
NLPEngine = NLPPipeline

__all__ = [
    "NLPEngine",
    "NLPPipeline",
    "process",
    "extract_package_name",
    "record_interaction_feedback",
    "get_explanation_for_user",
]
