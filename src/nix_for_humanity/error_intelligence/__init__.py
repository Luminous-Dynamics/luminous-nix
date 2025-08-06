"""
Enhanced Error Intelligence for Nix for Humanity

This module provides educational error handling with pattern recognition,
context-aware solutions, learning capabilities, and preventive suggestions.
Integrates with the XAI engine to explain why errors occurred.
"""

from .error_analyzer import ErrorAnalyzer, ErrorPattern, ErrorSolution
from .nixos_error_patterns import NixOSErrorPatterns
from .educational_formatter import EducationalErrorFormatter
from .error_learner import ErrorLearner
from .preventive_advisor import PreventiveAdvisor

__all__ = [
    'ErrorAnalyzer',
    'ErrorPattern',
    'ErrorSolution',
    'NixOSErrorPatterns',
    'EducationalErrorFormatter',
    'ErrorLearner',
    'PreventiveAdvisor'
]