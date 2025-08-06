"""
🛡️ Input Validation Framework

Consciousness-first input validation that protects while preserving natural expression.
Designed to catch genuine threats without flagging creative or emotional language.

Sacred Principles:
- Validate with compassion
- Sanitize without censorship  
- Protect without paranoia
- Guide without judgment
"""

import re
import html
import unicodedata
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path


class SecurityLevel(Enum):
    """Security validation levels"""
    PERMISSIVE = "permissive"    # Basic safety only
    BALANCED = "balanced"        # Standard security
    STRICT = "strict"            # High security
    PARANOID = "paranoid"        # Maximum security


class ThreatType(Enum):
    """Types of security threats"""
    INJECTION = "injection"              # Command/SQL injection
    XSS = "xss"                         # Cross-site scripting
    PATH_TRAVERSAL = "path_traversal"   # Directory traversal  
    PROTOTYPE_POLLUTION = "prototype_pollution"
    BUFFER_OVERFLOW = "buffer_overflow"
    SOCIAL_ENGINEERING = "social_engineering"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


@dataclass
class ValidationError(Exception):
    """Raised when input validation fails"""
    message: str
    threat_type: ThreatType
    original_input: str
    suggested_fix: Optional[str] = None
    
    def __str__(self):
        return f"Security validation failed: {self.message}"


@dataclass 
class SanitizedInput:
    """Container for validated and sanitized input"""
    original: str
    sanitized: str
    warnings: List[str]
    threat_level: float  # 0.0 = safe, 1.0 = dangerous
    modifications: List[str]  # List of changes made


class InputValidator:
    """
    Consciousness-first input validator
    
    Protects against genuine threats while preserving user expression.
    Uses multiple layers of validation with escalating responses.
    """
    
    def __init__(self, security_level: SecurityLevel = SecurityLevel.BALANCED):
        self.security_level = security_level
        self.setup_patterns()
        
    def setup_patterns(self):
        """Initialize threat detection patterns"""
        
        # Command injection patterns (high precision)
        self.command_injection_patterns = [
            r';\s*\w+',                    # Command chaining
            r'\|\s*\w+',                   # Piping
            r'&&\s*\w+',                   # AND chaining  
            r'\$\([^)]+\)',               # Command substitution
            r'`[^`]+`',                   # Backtick execution
            r'>\s*/dev/',                  # Device file redirect
            r'<\s*/dev/',                  # Device file input
            r'\|\s*nc\s+',                # Netcat piping
            r'\|\s*bash',                 # Bash piping
            r'\|\s*sh',                   # Shell piping
            r'rm\s+-rf\s+/',              # Dangerous deletion
            r'sudo\s+rm',                 # Privileged deletion
            r'chmod\s+777',               # Dangerous permissions
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./',                     # Directory traversal
            r'\.\.\.',                    # Multiple dots
            r'/etc/passwd',               # System files
            r'/etc/shadow',               # Password files
            r'/root/',                    # Root directory
            r'C:\\Windows\\',             # Windows system
            r'file://',                   # File protocol
            r'\\\\',                      # UNC paths
        ]
        
        # XSS patterns (for any web content)
        self.xss_patterns = [
            r'<script[^>]*>',             # Script tags
            r'javascript:',               # JavaScript protocol
            r'onload\s*=',                # Event handlers
            r'onerror\s*=',               # Error handlers
            r'<iframe[^>]*>',             # Iframe injection
            r'<object[^>]*>',             # Object embedding
        ]
        
        # Prototype pollution (for JSON/object inputs)
        self.pollution_patterns = [
            r'__proto__',
            r'constructor\.prototype',
            r'prototype\.constructor',
        ]
        
        # Social engineering keywords (contextual)
        self.social_engineering_keywords = [
            'urgent', 'immediately', 'expire', 'suspend',
            'verify account', 'click here', 'download now',
            'free money', 'winner', 'congratulations'
        ]
        
    def validate(self, 
                 input_data: Union[str, Dict, List], 
                 context: str = "general") -> SanitizedInput:
        """
        Main validation method
        
        Args:
            input_data: Data to validate
            context: Context of input (command, search, config, etc.)
            
        Returns:
            SanitizedInput with validation results
            
        Raises:
            ValidationError: If input poses genuine security threat
        """
        
        # Convert to string for processing
        if isinstance(input_data, (dict, list)):
            input_str = str(input_data)
        else:
            input_str = str(input_data)
            
        original_input = input_str
        
        # Initialize results
        warnings = []
        modifications = []
        threat_level = 0.0
        
        # 1. Basic sanitization
        sanitized = self._basic_sanitize(input_str)
        if sanitized != input_str:
            modifications.append("Basic character sanitization")
            
        # 2. Check for injection patterns
        injection_threat = self._check_injection(sanitized, context)
        if injection_threat > 0:
            threat_level = max(threat_level, injection_threat)
            if injection_threat > 0.8:
                raise ValidationError(
                    "Potential command injection detected",
                    ThreatType.INJECTION,
                    original_input,
                    "Try rephrasing without special shell characters"
                )
            elif injection_threat > 0.5:
                warnings.append("Input contains shell-like patterns")
                
        # 3. Check path traversal
        traversal_threat = self._check_path_traversal(sanitized)
        if traversal_threat > 0:
            threat_level = max(threat_level, traversal_threat)
            if traversal_threat > 0.7:
                raise ValidationError(
                    "Path traversal attempt detected", 
                    ThreatType.PATH_TRAVERSAL,
                    original_input,
                    "Use relative paths or specify full allowed paths"
                )
                
        # 4. Check XSS patterns
        xss_threat = self._check_xss(sanitized)
        if xss_threat > 0:
            threat_level = max(threat_level, xss_threat)
            sanitized = html.escape(sanitized)
            modifications.append("HTML escaped for XSS protection")
            
        # 5. Length validation
        if len(sanitized) > self._get_max_length(context):
            if self.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                raise ValidationError(
                    f"Input too long for context '{context}'",
                    ThreatType.RESOURCE_EXHAUSTION,
                    original_input,
                    f"Please limit input to {self._get_max_length(context)} characters"
                )
            else:
                warnings.append(f"Input is longer than recommended for {context}")
                
        # 6. Unicode normalization
        normalized = unicodedata.normalize('NFKC', sanitized)
        if normalized != sanitized:
            sanitized = normalized
            modifications.append("Unicode normalized")
            
        return SanitizedInput(
            original=original_input,
            sanitized=sanitized,
            warnings=warnings,
            threat_level=threat_level,
            modifications=modifications
        )
        
    def _basic_sanitize(self, input_str: str) -> str:
        """Basic string sanitization"""
        
        # Remove null bytes
        cleaned = input_str.replace('\x00', '')
        
        # Remove other control characters (except common whitespace)
        cleaned = ''.join(
            char for char in cleaned 
            if ord(char) >= 32 or char in '\t\n\r'
        )
        
        return cleaned.strip()
        
    def _check_injection(self, input_str: str, context: str) -> float:
        """Check for command injection patterns"""
        
        threat_score = 0.0
        input_lower = input_str.lower()
        
        # Context-specific checking
        if context in ['command', 'system', 'execute']:
            # More strict for command contexts
            multiplier = 1.5
        else:
            # Less strict for search, chat contexts
            multiplier = 1.0
            
        for pattern in self.command_injection_patterns:
            if re.search(pattern, input_lower):
                threat_score += 0.3 * multiplier
                
        # Check for dangerous commands
        dangerous_commands = [
            'rm ', 'del ', 'format', 'fdisk', 'dd if=', 
            'curl', 'wget', 'nc ', 'netcat', 'telnet'
        ]
        
        for cmd in dangerous_commands:
            if cmd in input_lower:
                threat_score += 0.4 * multiplier
                
        return min(threat_score, 1.0)
        
    def _check_path_traversal(self, input_str: str) -> float:
        """Check for path traversal patterns"""
        
        threat_score = 0.0
        input_lower = input_str.lower()
        
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, input_lower):
                threat_score += 0.4
                
        # Check for sensitive file patterns
        sensitive_files = [
            '/etc/', '/root/', '/home/', 'c:\\windows\\',
            'passwd', 'shadow', 'hosts', 'config'
        ]
        
        for file_pattern in sensitive_files:
            if file_pattern in input_lower:
                threat_score += 0.3
                
        return min(threat_score, 1.0)
        
    def _check_xss(self, input_str: str) -> float:
        """Check for XSS patterns"""
        
        threat_score = 0.0
        input_lower = input_str.lower()
        
        for pattern in self.xss_patterns:
            if re.search(pattern, input_lower):
                threat_score += 0.5
                
        return min(threat_score, 1.0)
        
    def _get_max_length(self, context: str) -> int:
        """Get maximum allowed length for context"""
        
        limits = {
            'command': 500,
            'search': 200,
            'chat': 2000,
            'config': 1000,
            'file_path': 255,
            'general': 1000
        }
        
        base_limit = limits.get(context, 1000)
        
        # Adjust based on security level
        if self.security_level == SecurityLevel.STRICT:
            return int(base_limit * 0.8)
        elif self.security_level == SecurityLevel.PARANOID:
            return int(base_limit * 0.6)
        else:
            return base_limit
            
    def validate_file_path(self, path: str) -> SanitizedInput:
        """Specialized validation for file paths"""
        
        try:
            # Use pathlib for safe path handling
            safe_path = Path(path).resolve()
            
            # Check if path escapes allowed directories
            allowed_prefixes = [
                Path.home(),
                Path('/nix/store'),
                Path('/etc/nixos'),
                Path('/tmp')
            ]
            
            is_allowed = any(
                str(safe_path).startswith(str(prefix)) 
                for prefix in allowed_prefixes
            )
            
            if not is_allowed and self.security_level in [SecurityLevel.STRICT, SecurityLevel.PARANOID]:
                raise ValidationError(
                    "Path outside allowed directories",
                    ThreatType.PATH_TRAVERSAL,
                    path,
                    "Use paths within home, /nix/store, /etc/nixos, or /tmp"
                )
                
            return SanitizedInput(
                original=path,
                sanitized=str(safe_path),
                warnings=[] if is_allowed else ["Path outside typical safe directories"],
                threat_level=0.0 if is_allowed else 0.3,
                modifications=["Resolved to absolute path"]
            )
            
        except (OSError, ValueError) as e:
            raise ValidationError(
                f"Invalid file path: {e}",
                ThreatType.PATH_TRAVERSAL,
                path,
                "Use a valid file path"
            )
            
    def validate_command_args(self, args: List[str]) -> List[SanitizedInput]:
        """Validate command arguments"""
        
        validated_args = []
        
        for arg in args:
            # Each argument gets validation
            validated = self.validate(arg, context="command")
            validated_args.append(validated)
            
        return validated_args
        
    def is_safe_for_context(self, input_data: str, context: str) -> bool:
        """Quick safety check for a given context"""
        
        try:
            result = self.validate(input_data, context)
            return result.threat_level < 0.5
        except ValidationError:
            return False


# Pre-configured validators for common use cases
def create_permissive_validator() -> InputValidator:
    """Create validator for creative/expressive content"""
    return InputValidator(SecurityLevel.PERMISSIVE)


def create_standard_validator() -> InputValidator:
    """Create validator for normal operations"""
    return InputValidator(SecurityLevel.BALANCED)


def create_strict_validator() -> InputValidator:
    """Create validator for system operations"""
    return InputValidator(SecurityLevel.STRICT)


def create_paranoid_validator() -> InputValidator:
    """Create validator for maximum security"""
    return InputValidator(SecurityLevel.PARANOID)