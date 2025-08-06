"""
🛡️ Enhanced Input Validation Framework

Builds upon the existing input_validator.py with additional security layers:
- Advanced threat detection patterns
- Rate limiting and abuse prevention
- Context-aware validation
- Multi-stage validation pipeline
- Comprehensive logging and monitoring

Sacred Security Principles:
- Defense in depth
- Fail secure by default
- Validate early and often
- Trust but verify
"""

import re
import time
import hashlib
import ipaddress
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
import json
import base64

from .input_validator import (
    InputValidator, SecurityLevel, ThreatType, 
    ValidationError, SanitizedInput
)


class ValidationStage(Enum):
    """Stages of validation pipeline"""
    RATE_LIMIT = "rate_limit"
    FORMAT = "format"
    CONTENT = "content" 
    CONTEXT = "context"
    BEHAVIOR = "behavior"
    

@dataclass
class ValidationContext:
    """Context for validation decisions"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    command_history: List[str] = field(default_factory=list)
    trust_score: float = 0.5
    is_authenticated: bool = False
    previous_violations: int = 0
    

@dataclass
class ThreatIndicator:
    """Represents a detected threat indicator"""
    indicator_type: str
    severity: float  # 0.0 - 1.0
    description: str
    evidence: str
    mitigation: Optional[str] = None


class EnhancedInputValidator(InputValidator):
    """
    Enhanced input validator with advanced security features
    
    Adds rate limiting, behavioral analysis, and deeper threat detection
    to the base InputValidator.
    """
    
    def __init__(
        self, 
        security_level: SecurityLevel = SecurityLevel.BALANCED,
        enable_rate_limiting: bool = True,
        enable_behavioral_analysis: bool = True
    ):
        super().__init__(security_level)
        
        # Rate limiting
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limits = self._init_rate_limits()
        self.request_history = defaultdict(deque)
        self.blocked_users = {}  # user_id -> unblock_time
        
        # Behavioral analysis
        self.enable_behavioral_analysis = enable_behavioral_analysis
        self.behavior_patterns = defaultdict(lambda: {
            'commands': deque(maxlen=100),
            'violations': deque(maxlen=50),
            'trust_score': 0.5
        })
        
        # Enhanced patterns
        self.setup_enhanced_patterns()
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring
        self.threat_log = deque(maxlen=1000)
        
    def _init_rate_limits(self) -> Dict[str, Dict[str, Any]]:
        """Initialize rate limiting configuration"""
        return {
            'global': {
                'requests_per_minute': 60,
                'requests_per_hour': 600,
                'burst_size': 10
            },
            'per_user': {
                'requests_per_minute': 30,
                'requests_per_hour': 300,
                'burst_size': 5
            },
            'command_specific': {
                'install': {'per_minute': 5, 'per_hour': 20},
                'remove': {'per_minute': 3, 'per_hour': 10},
                'update': {'per_minute': 2, 'per_hour': 5},
                'config': {'per_minute': 10, 'per_hour': 50}
            }
        }
        
    def setup_enhanced_patterns(self):
        """Set up additional threat detection patterns"""
        
        # Advanced command injection patterns
        self.advanced_injection_patterns = [
            # Process substitution
            r'<\([^)]+\)',
            r'>\([^)]+\)',
            
            # Here documents with command execution
            r'<<.*\$\(',
            r'<<.*`',
            
            # Bash specific exploits
            r'\${.*##.*}',  # Parameter expansion tricks
            r'\${.*//.*}',   # Pattern substitution
            r'\${!.*}',      # Indirect expansion
            
            # Advanced piping
            r'\|&',          # Pipe both stdout and stderr
            r'>&',           # File descriptor manipulation
            r'<&',
            
            # Process control
            r'&\s*$',        # Background execution
            r'nohup',        # Persistent processes
            r'disown',
            r'trap',         # Signal handling
            
            # Time-based attacks
            r'sleep\s+\d+',  # Delays
            r'timeout',
        ]
        
        # Obfuscation detection
        self.obfuscation_patterns = [
            # Base64 encoded commands
            r'base64\s+-[de]',
            r'echo\s+[A-Za-z0-9+/]{20,}=*\s*\|',
            
            # Hex encoding
            r'\\x[0-9a-fA-F]{2}',
            r'printf\s+[\'"]?\\x',
            
            # URL encoding
            r'%[0-9a-fA-F]{2}',
            
            # Character manipulation
            r'tr\s+.*\s+.*',
            r'sed\s+s/.*/.*/g',
            
            # Compression/encoding
            r'gzip\s+-[dc]',
            r'bzip2\s+-[dc]',
            r'openssl\s+enc',
        ]
        
        # Data exfiltration patterns
        self.exfiltration_patterns = [
            # Network tools
            r'curl\s+.*(-d|--data)',
            r'wget\s+.*--post-',
            r'nc\s+.*-[lp]',
            r'socat',
            r'ssh\s+.*-[oR]',
            
            # DNS exfiltration
            r'nslookup.*\$',
            r'dig.*\$',
            r'host.*\$',
            
            # File transfer
            r'scp\s+',
            r'rsync\s+.*@',
            r'ftp\s+',
            
            # Encoding for transfer
            r'xxd\s+-[pr]',
            r'od\s+-',
        ]
        
        # Persistence mechanisms
        self.persistence_patterns = [
            # Cron jobs
            r'crontab\s+-[el]',
            r'at\s+',
            
            # Startup files
            r'~/\.(bash|zsh)rc',
            r'/etc/rc\.local',
            r'systemctl\s+enable',
            
            # SSH keys
            r'authorized_keys',
            r'ssh-keygen',
            r'~/.ssh/',
        ]
        
        # Resource exhaustion
        self.resource_exhaustion_patterns = [
            # Fork bombs
            r':\(\)\{:\|:&\};:',
            r'while.*true.*do',
            r'for.*in.*\$\(seq',
            
            # Memory exhaustion
            r'/dev/zero.*dd',
            r'yes\s*\|',
            r'tail\s+-f.*&',
            
            # Disk exhaustion
            r'dd.*of=/.*count=',
            r'fallocate\s+-l',
        ]
        
    def validate_enhanced(
        self, 
        input_data: Union[str, Dict, List],
        context: ValidationContext,
        command_type: Optional[str] = None
    ) -> SanitizedInput:
        """
        Enhanced validation with multi-stage pipeline
        
        Args:
            input_data: Data to validate
            context: Validation context with user info
            command_type: Type of command being executed
            
        Returns:
            SanitizedInput with enhanced validation results
        """
        
        with self._lock:
            # Stage 1: Rate limiting
            if self.enable_rate_limiting:
                self._check_rate_limits(context)
                
            # Stage 2: Basic validation (parent class)
            result = self.validate(input_data, command_type or "general")
            
            # Stage 3: Enhanced threat detection
            threat_indicators = self._detect_advanced_threats(result.sanitized)
            
            # Stage 4: Behavioral analysis
            if self.enable_behavioral_analysis:
                behavioral_risk = self._analyze_behavior(
                    result.sanitized, 
                    context,
                    threat_indicators
                )
                result.threat_level = max(result.threat_level, behavioral_risk)
                
            # Stage 5: Context-aware validation
            context_risk = self._validate_context(
                result.sanitized,
                context,
                command_type
            )
            result.threat_level = max(result.threat_level, context_risk)
            
            # Log threats
            if threat_indicators:
                self._log_threats(threat_indicators, context)
                
            # Update behavioral profile
            self._update_behavior_profile(context, result)
            
            # Add threat indicators to warnings
            for indicator in threat_indicators:
                if indicator.severity > 0.5:
                    result.warnings.append(
                        f"⚠️ {indicator.description}: {indicator.mitigation or 'Exercise caution'}"
                    )
                    
            return result
            
    def _check_rate_limits(self, context: ValidationContext):
        """Check and enforce rate limits"""
        
        user_id = context.user_id or "anonymous"
        current_time = time.time()
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            if current_time < self.blocked_users[user_id]:
                raise ValidationError(
                    "Rate limit exceeded - please wait before trying again",
                    ThreatType.RESOURCE_EXHAUSTION,
                    "",
                    f"Blocked until {datetime.fromtimestamp(self.blocked_users[user_id]).strftime('%H:%M:%S')}"
                )
            else:
                del self.blocked_users[user_id]
                
        # Track request
        self.request_history[user_id].append(current_time)
        
        # Clean old entries
        cutoff_time = current_time - 3600  # 1 hour
        while self.request_history[user_id] and self.request_history[user_id][0] < cutoff_time:
            self.request_history[user_id].popleft()
            
        # Check limits
        user_requests = self.request_history[user_id]
        
        # Per minute check
        minute_cutoff = current_time - 60
        minute_requests = sum(1 for t in user_requests if t > minute_cutoff)
        
        if minute_requests > self.rate_limits['per_user']['requests_per_minute']:
            # Block user for 5 minutes
            self.blocked_users[user_id] = current_time + 300
            raise ValidationError(
                "Rate limit exceeded - too many requests",
                ThreatType.RESOURCE_EXHAUSTION,
                "",
                "Please wait 5 minutes before trying again"
            )
            
        # Burst check
        if len(user_requests) >= 3:
            recent_times = list(user_requests)[-3:]
            if recent_times[-1] - recent_times[0] < 1:  # 3 requests in 1 second
                result.warnings.append("⚡ Slow down - detecting rapid requests")
                
    def _detect_advanced_threats(self, input_text: str) -> List[ThreatIndicator]:
        """Detect advanced threat patterns"""
        
        threats = []
        
        # Check for advanced injection
        for pattern in self.advanced_injection_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="advanced_injection",
                    severity=0.8,
                    description="Advanced command injection technique detected",
                    evidence=pattern,
                    mitigation="Use simple commands without special shell features"
                ))
                
        # Check for obfuscation
        for pattern in self.obfuscation_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="obfuscation",
                    severity=0.9,
                    description="Command obfuscation detected",
                    evidence=pattern,
                    mitigation="Use clear, unencoded commands"
                ))
                
        # Check for exfiltration
        for pattern in self.exfiltration_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="exfiltration",
                    severity=0.95,
                    description="Potential data exfiltration attempt",
                    evidence=pattern,
                    mitigation="Network operations are restricted"
                ))
                
        # Check for persistence
        for pattern in self.persistence_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="persistence",
                    severity=0.85,
                    description="Persistence mechanism detected",
                    evidence=pattern,
                    mitigation="System modifications require explicit permission"
                ))
                
        # Check for resource exhaustion
        for pattern in self.resource_exhaustion_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                threats.append(ThreatIndicator(
                    indicator_type="resource_exhaustion",
                    severity=0.9,
                    description="Resource exhaustion attempt detected",
                    evidence=pattern,
                    mitigation="Resource-intensive operations are blocked"
                ))
                
        # Check for suspicious character sequences
        if self._has_suspicious_characters(input_text):
            threats.append(ThreatIndicator(
                indicator_type="suspicious_characters",
                severity=0.6,
                description="Suspicious character sequences detected",
                evidence="Non-standard character combinations",
                mitigation="Use standard ASCII characters"
            ))
            
        return threats
        
    def _has_suspicious_characters(self, text: str) -> bool:
        """Check for suspicious character patterns"""
        
        # Excessive special characters
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\-_.]', text)) / max(len(text), 1)
        if special_char_ratio > 0.3:
            return True
            
        # Repeated special characters
        if re.search(r'([^a-zA-Z0-9])\1{3,}', text):
            return True
            
        # Mix of different quote types (possible injection)
        if "'" in text and '"' in text and '`' in text:
            return True
            
        # Unusual Unicode characters
        for char in text:
            if ord(char) > 127 and ord(char) not in range(0x00C0, 0x024F):
                return True
                
        return False
        
    def _analyze_behavior(
        self, 
        input_text: str,
        context: ValidationContext,
        threats: List[ThreatIndicator]
    ) -> float:
        """Analyze user behavior for anomalies"""
        
        user_id = context.user_id or "anonymous"
        profile = self.behavior_patterns[user_id]
        
        risk_score = 0.0
        
        # Check command frequency
        profile['commands'].append({
            'text': input_text,
            'time': time.time(),
            'threats': len(threats)
        })
        
        # Rapid command changes (possible automation)
        if len(profile['commands']) >= 5:
            recent_commands = list(profile['commands'])[-5:]
            unique_commands = len(set(cmd['text'] for cmd in recent_commands))
            if unique_commands == 5:  # All different
                time_span = recent_commands[-1]['time'] - recent_commands[0]['time']
                if time_span < 10:  # 5 different commands in 10 seconds
                    risk_score += 0.3
                    
        # Escalating threat patterns
        recent_threats = [cmd['threats'] for cmd in list(profile['commands'])[-10:]]
        if len(recent_threats) >= 3 and all(t > 0 for t in recent_threats[-3:]):
            risk_score += 0.4
            
        # Trust score adjustment
        if threats:
            profile['trust_score'] = max(0, profile['trust_score'] - 0.1)
        else:
            profile['trust_score'] = min(1, profile['trust_score'] + 0.01)
            
        # Adjust risk based on trust
        risk_score *= (1 - profile['trust_score'])
        
        return min(risk_score, 0.9)
        
    def _validate_context(
        self,
        input_text: str,
        context: ValidationContext,
        command_type: Optional[str]
    ) -> float:
        """Context-aware validation"""
        
        risk = 0.0
        
        # Unauthenticated users have restrictions
        if not context.is_authenticated:
            if command_type in ['install', 'remove', 'config']:
                risk += 0.2
                
        # Previous violations increase scrutiny
        if context.previous_violations > 0:
            risk += min(context.previous_violations * 0.1, 0.5)
            
        # Check command consistency with history
        if context.command_history:
            # Sudden change in command patterns
            if command_type and all(
                cmd_type != command_type 
                for cmd_type in context.command_history[-5:]
            ):
                risk += 0.1
                
        return risk
        
    def _update_behavior_profile(
        self,
        context: ValidationContext,
        result: SanitizedInput
    ):
        """Update user behavior profile"""
        
        user_id = context.user_id or "anonymous"
        profile = self.behavior_patterns[user_id]
        
        # Track violations
        if result.threat_level > 0.7:
            profile['violations'].append({
                'time': time.time(),
                'threat_level': result.threat_level,
                'input': result.original[:50]  # First 50 chars only
            })
            
    def _log_threats(
        self,
        threats: List[ThreatIndicator],
        context: ValidationContext
    ):
        """Log detected threats for monitoring"""
        
        for threat in threats:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': context.user_id or "anonymous",
                'session_id': context.session_id,
                'threat_type': threat.indicator_type,
                'severity': threat.severity,
                'description': threat.description,
                'evidence': threat.evidence[:100]  # Limit evidence length
            }
            
            self.threat_log.append(log_entry)
            
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary of recent threats"""
        
        if not self.threat_log:
            return {'total_threats': 0, 'threat_types': {}}
            
        threat_types = defaultdict(int)
        severity_sum = 0
        
        for entry in self.threat_log:
            threat_types[entry['threat_type']] += 1
            severity_sum += entry['severity']
            
        return {
            'total_threats': len(self.threat_log),
            'average_severity': severity_sum / len(self.threat_log),
            'threat_types': dict(threat_types),
            'most_recent': self.threat_log[-1]['timestamp'] if self.threat_log else None
        }
        
    def validate_file_upload(
        self,
        filename: str,
        file_size: int,
        content_type: Optional[str] = None
    ) -> SanitizedInput:
        """Validate file uploads"""
        
        # Check filename
        if not re.match(r'^[\w\-. ]+$', filename):
            raise ValidationError(
                "Invalid filename characters",
                ThreatType.INJECTION,
                filename,
                "Use only letters, numbers, dots, dashes and underscores"
            )
            
        # Check extension
        allowed_extensions = ['.txt', '.json', '.nix', '.conf', '.yaml', '.yml']
        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError(
                "File type not allowed",
                ThreatType.INJECTION,
                filename,
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )
            
        # Check file size (10MB limit)
        if file_size > 10 * 1024 * 1024:
            raise ValidationError(
                "File too large",
                ThreatType.RESOURCE_EXHAUSTION,
                filename,
                "Maximum file size is 10MB"
            )
            
        return SanitizedInput(
            original=filename,
            sanitized=filename,
            warnings=[],
            threat_level=0.0,
            modifications=[]
        )


def create_enhanced_validator(
    security_level: SecurityLevel = SecurityLevel.BALANCED
) -> EnhancedInputValidator:
    """Factory function to create enhanced validator"""
    return EnhancedInputValidator(
        security_level=security_level,
        enable_rate_limiting=True,
        enable_behavioral_analysis=True
    )