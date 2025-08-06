"""
Security Configuration Loader
Loads and manages security settings from configuration files
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging


class SecurityConfig:
    """Manages security configuration settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize security configuration
        
        Args:
            config_path: Path to security config file. If None, uses default locations.
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load security configuration from file
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Configuration dictionary
        """
        # Default search paths
        search_paths = [
            config_path,
            os.path.expanduser("~/.config/nix-humanity/security.yaml"),
            "/etc/nix-humanity/security.yaml",
            os.path.join(os.path.dirname(__file__), "../../../config/security_config.yaml"),
        ]
        
        # Find first existing config file
        for path in search_paths:
            if path and os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f)
                        self.logger.info(f"Loaded security config from: {path}")
                        return config
                except Exception as e:
                    self.logger.error(f"Failed to load config from {path}: {e}")
                    
        # Return default configuration if no file found
        self.logger.warning("No security config found, using defaults")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default security configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            'security': {
                'level': 'balanced',
                'rate_limiting': {
                    'enabled': True,
                    'requests_per_minute': 60,
                    'requests_per_hour': 600,
                    'burst_size': 10,
                    'whitelist': ['127.0.0.1', '::1']
                },
                'validation': {
                    'max_input_length': 1000,
                    'enhanced_detection': True,
                    'behavioral_analysis': {
                        'enabled': True,
                        'history_window': 20,
                        'anomaly_threshold': 0.7
                    }
                },
                'execution': {
                    'require_confirmation': True,
                    'always_confirm': ['remove', 'update_system', 'rollback_system'],
                    'max_execution_time': 300,
                    'default_dry_run': True
                },
                'trust': {
                    'initial_level': 0.3,
                    'increase_per_success': 0.01,
                    'decrease_per_violation': 0.1,
                    'min_commands_for_increase': 5,
                    'thresholds': {
                        'low_trust': 0.3,
                        'high_trust': 0.7,
                        'trusted': 0.9
                    }
                },
                'privacy': {
                    'anonymize_logs': True,
                    'retention_days': 30,
                    'enable_learning': True,
                    'share_statistics': False
                }
            },
            'features': {
                'use_enhanced_validator': True,
                'behavioral_analysis': True,
                'explain_security_decisions': True
            }
        }
    
    def get_security_level(self) -> str:
        """Get the global security level
        
        Returns:
            Security level: 'strict', 'balanced', or 'permissive'
        """
        return self.config.get('security', {}).get('level', 'balanced')
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Get rate limiting configuration
        
        Returns:
            Rate limiting configuration dictionary
        """
        return self.config.get('security', {}).get('rate_limiting', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get input validation configuration
        
        Returns:
            Validation configuration dictionary
        """
        return self.config.get('security', {}).get('validation', {})
    
    def get_trust_config(self) -> Dict[str, Any]:
        """Get trust level configuration
        
        Returns:
            Trust configuration dictionary
        """
        return self.config.get('security', {}).get('trust', {})
    
    def get_persona_config(self, persona: str) -> Dict[str, Any]:
        """Get security configuration for a specific persona
        
        Args:
            persona: Persona identifier
            
        Returns:
            Persona-specific configuration or empty dict
        """
        personas = self.config.get('security', {}).get('personas', {})
        return personas.get(persona, {})
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a security feature is enabled
        
        Args:
            feature: Feature name
            
        Returns:
            True if feature is enabled
        """
        features = self.config.get('features', {})
        return features.get(feature, False)
    
    def should_require_confirmation(self, command: str) -> bool:
        """Check if a command requires confirmation
        
        Args:
            command: Command name
            
        Returns:
            True if confirmation required
        """
        exec_config = self.config.get('security', {}).get('execution', {})
        if not exec_config.get('require_confirmation', True):
            return False
            
        always_confirm = exec_config.get('always_confirm', [])
        return command in always_confirm
    
    def get_threat_patterns(self) -> list:
        """Get custom threat detection patterns
        
        Returns:
            List of threat pattern configurations
        """
        threats = self.config.get('security', {}).get('threats', {})
        return threats.get('custom_patterns', [])
    
    def update_trust_level(self, user_id: str, current_trust: float, 
                          success: bool) -> float:
        """Calculate updated trust level based on command outcome
        
        Args:
            user_id: User identifier
            current_trust: Current trust level
            success: Whether the command was successful
            
        Returns:
            Updated trust level
        """
        trust_config = self.get_trust_config()
        
        if success:
            # Increase trust on success
            increase = trust_config.get('increase_per_success', 0.01)
            new_trust = min(1.0, current_trust + increase)
        else:
            # Decrease trust on failure/violation
            decrease = trust_config.get('decrease_per_violation', 0.1)
            new_trust = max(0.0, current_trust - decrease)
            
        return new_trust
    
    def get_trust_level_name(self, trust_level: float) -> str:
        """Get human-readable trust level name
        
        Args:
            trust_level: Numeric trust level (0.0-1.0)
            
        Returns:
            Trust level name
        """
        thresholds = self.get_trust_config().get('thresholds', {})
        
        if trust_level >= thresholds.get('trusted', 0.9):
            return 'trusted'
        elif trust_level >= thresholds.get('high_trust', 0.7):
            return 'high_trust'
        elif trust_level >= thresholds.get('low_trust', 0.3):
            return 'medium_trust'
        else:
            return 'low_trust'
    
    def save_config(self, config_path: Optional[str] = None):
        """Save current configuration to file
        
        Args:
            config_path: Path to save config to
        """
        if not config_path:
            config_path = os.path.expanduser("~/.config/nix-humanity/security.yaml")
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Saved security config to: {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            raise


# Singleton instance for easy access
_security_config = None


def get_security_config(config_path: Optional[str] = None) -> SecurityConfig:
    """Get or create the global security configuration instance
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        SecurityConfig instance
    """
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig(config_path)
    return _security_config