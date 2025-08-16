"""
Environmental awareness package for Luminous Nix.

Provides system monitoring, predictive assistance, and context-aware
intent recognition for intelligent NixOS management.
"""

from .system_monitor import (
    SystemMonitor,
    SystemState,
    CPUState,
    MemoryState,
    DiskState,
    NetworkInterface,
    ServiceState,
    NixOSState,
    get_system_monitor
)

from .predictive_assistant import (
    PredictiveAssistant,
    Prediction,
    UserPattern,
    PatternDatabase,
    get_predictions
)

from .context_aware_intent import (
    ContextAwareIntentRecognizer,
    ContextualIntent,
    IntentType,
    process_query_with_context
)

__all__ = [
    # System monitoring
    'SystemMonitor',
    'SystemState',
    'CPUState', 
    'MemoryState',
    'DiskState',
    'NetworkInterface',
    'ServiceState',
    'NixOSState',
    'get_system_monitor',
    
    # Predictive assistance
    'PredictiveAssistant',
    'Prediction',
    'UserPattern',
    'PatternDatabase',
    'get_predictions',
    
    # Context-aware intent
    'ContextAwareIntentRecognizer',
    'ContextualIntent',
    'IntentType',
    'process_query_with_context'
]

__version__ = '0.1.0'