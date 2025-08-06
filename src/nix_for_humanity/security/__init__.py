"""
🛡️ Nix for Humanity Security Framework

Consciousness-first security that protects without fragmenting user attention.
All security measures are designed to be invisible during normal use but
comprehensive in protection.

Sacred Security Principles:
1. Sanctuary First - Security creates safety, not friction
2. Transparent Protection - Users feel secure, not constrained  
3. Progressive Trust - Earned through vulnerability and honesty
4. Defensive Compassion - Protect all beings, including attackers from themselves
"""

from .input_validator import (
    InputValidator,
    ValidationError,
    SanitizedInput,
    SecurityLevel
)

from .command_sandbox import (
    CommandSandbox,
    SandboxError,
    ExecutionContext,
    SafetyLevel
)

from .threat_detection import (
    ThreatDetector,
    ThreatType,
    SecurityEvent,
    ThreatResponse
)

from .privacy_guardian import (
    PrivacyGuardian,
    PersonalDataType,
    PrivacyLevel,
    DataHandlingPolicy
)

from .security_monitor import (
    SecurityMonitor,
    SecurityMetrics,
    SecurityAlert,
    MonitoringLevel
)

__all__ = [
    # Core validation
    'InputValidator',
    'ValidationError', 
    'SanitizedInput',
    'SecurityLevel',
    
    # Command sandboxing
    'CommandSandbox',
    'SandboxError',
    'ExecutionContext',
    'SafetyLevel',
    
    # Threat detection
    'ThreatDetector',
    'ThreatType',
    'SecurityEvent',
    'ThreatResponse',
    
    # Privacy protection
    'PrivacyGuardian',
    'PersonalDataType',
    'PrivacyLevel',
    'DataHandlingPolicy',
    
    # Security monitoring
    'SecurityMonitor',
    'SecurityMetrics',
    'SecurityAlert',
    'MonitoringLevel'
]

# Sacred Mantras for Security
SECURITY_MANTRAS = {
    'sanctuary': "This system is a sanctuary. All who enter are protected.",
    'transparency': "Trust through vulnerability. Honesty through openness.",
    'compassion': "Protect without judgment. Guide without force.",
    'wisdom': "True security comes from understanding, not fear."
}