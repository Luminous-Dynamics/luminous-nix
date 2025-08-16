"""
Theory of Mind Trust Modeling System

Implements a sophisticated trust modeling system based on Theory of Mind (ToM)
research, enabling the AI to model user mental states and build trust through
vulnerability, repair, and mutual understanding.
"""

from .mental_state_model import MentalStateModel
from .repair_mechanism import RepairMechanism
from .trust_engine import TrustEngine
from .vulnerability_tracker import VulnerabilityTracker

try:
    from .trust_metrics import TrustMetrics
except ImportError:
    from .trust_metrics_mock import TrustMetrics

__all__ = [
    "TrustEngine",
    "MentalStateModel",
    "VulnerabilityTracker",
    "RepairMechanism",
    "TrustMetrics",
]
