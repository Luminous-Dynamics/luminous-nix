"""
from typing import List, Dict
Privacy Guard - Ensuring user privacy in all perception activities

This module provides comprehensive privacy protection for all behavioral
awareness features, giving users complete control over their data.
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


class PrivacyLevel(Enum):
    """Privacy protection levels"""
    PARANOID = "paranoid"  # Maximum privacy, minimal functionality
    STRICT = "strict"      # High privacy, reduced insights
    BALANCED = "balanced"  # Default, good privacy with useful insights
    RELAXED = "relaxed"    # More insights, still private
    TRUSTING = "trusting"  # Maximum insights, trust-based


class DataSensitivity(Enum):
    """Data sensitivity classifications"""
    PUBLIC = "public"          # App names, general activity
    PRIVATE = "private"        # Window titles, URLs
    SENSITIVE = "sensitive"    # Passwords, personal info
    CONFIDENTIAL = "confidential"  # Financial, medical
    

@dataclass
class PrivacyPolicy:
    """User's privacy preferences"""
    level: PrivacyLevel
    excluded_apps: Set[str]
    excluded_patterns: Set[str]
    allowed_domains: Set[str]
    data_retention_days: int
    anonymize_after_days: int
    share_analytics: bool
    allow_pattern_learning: bool
    

@dataclass 
class PrivacyViolation:
    """Record of potential privacy concern"""
    timestamp: datetime
    violation_type: str
    data_involved: str
    action_taken: str
    severity: str


class PrivacyGuard:
    """
    Comprehensive privacy protection for perception system
    
    Core principles:
    1. Privacy by default - opt-in for everything
    2. Data minimization - collect only what's needed
    3. User control - easy to understand and modify
    4. Transparency - clear about what and why
    5. Local first - nothing leaves without permission
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph):
        self.skg = skg
        self.logger = logging.getLogger(__name__)
        
        # Load or create privacy policy
        self.policy = self._load_privacy_policy()
        
        # Sensitive patterns to detect
        self.sensitive_patterns = [
            r'password',
            r'passwd',
            r'secret',
            r'private',
            r'confidential',
            r'ssn',
            r'credit.*card',
            r'bank.*account',
            r'medical',
            r'health.*record'
        ]
        
        # Privacy violations log
        self.violations = []
        
        # Anonymization salt (changes periodically)
        self.anonymization_salt = self._generate_salt()
        
    def _load_privacy_policy(self) -> PrivacyPolicy:
        """Load user's privacy policy from storage"""
        cursor = self.skg.conn.cursor()
        
        policy_data = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'metacognitive'
            AND type = 'privacy_policy'
            ORDER BY created_at DESC
            LIMIT 1
        """).fetchone()
        
        if policy_data:
            data = json.loads(policy_data[0])
            return PrivacyPolicy(
                level=PrivacyLevel(data['level']),
                excluded_apps=set(data['excluded_apps']),
                excluded_patterns=set(data['excluded_patterns']),
                allowed_domains=set(data.get('allowed_domains', [])),
                data_retention_days=data.get('data_retention_days', 30),
                anonymize_after_days=data.get('anonymize_after_days', 7),
                share_analytics=data.get('share_analytics', False),
                allow_pattern_learning=data.get('allow_pattern_learning', True)
            )
        
        # Default privacy policy (balanced)
        return PrivacyPolicy(
            level=PrivacyLevel.BALANCED,
            excluded_apps={'1password', 'bitwarden', 'keychain', 'banking'},
            excluded_patterns={'password', 'private', 'incognito'},
            allowed_domains=set(),
            data_retention_days=30,
            anonymize_after_days=7,
            share_analytics=False,
            allow_pattern_learning=True
        )
        
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize data according to privacy policy
        
        Returns cleaned data safe for storage/processing
        """
        if self.policy.level == PrivacyLevel.PARANOID:
            # Maximum privacy - almost everything redacted
            return self._paranoid_sanitization(data)
            
        # Check for excluded apps
        app_name = data.get('app_name', '').lower()
        if any(excluded in app_name for excluded in self.policy.excluded_apps):
            return self._redact_all(data, reason="excluded_app")
            
        # Check window title
        window_title = data.get('window_title', '')
        if window_title:
            data['window_title'] = self._sanitize_window_title(window_title)
            
        # Check URLs
        if 'url' in data:
            data['url'] = self._sanitize_url(data['url'])
            
        # Remove any detected sensitive information
        data = self._remove_sensitive_data(data)
        
        return data
        
    def _paranoid_sanitization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Maximum privacy mode - minimal data"""
        return {
            'timestamp': data.get('timestamp'),
            'activity_type': 'active' if data.get('active') else 'idle',
            'anonymized': True
        }
        
    def _redact_all(self, data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Completely redact sensitive data"""
        return {
            'timestamp': data.get('timestamp'),
            'redacted': True,
            'redaction_reason': reason
        }
        
    def _sanitize_window_title(self, title: str) -> str:
        """Clean window titles of sensitive information"""
        # Check against excluded patterns
        for pattern in self.policy.excluded_patterns:
            if pattern.lower() in title.lower():
                return "[PRIVATE]"
                
        # Remove sensitive patterns
        for pattern in self.sensitive_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                self._log_violation("sensitive_pattern_detected", pattern)
                return "[SENSITIVE]"
                
        # Level-based sanitization
        if self.policy.level == PrivacyLevel.STRICT:
            # Remove all specifics
            return self._generalize_title(title)
        elif self.policy.level == PrivacyLevel.BALANCED:
            # Remove personal identifiers
            title = self._remove_identifiers(title)
            
        return title
        
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URLs based on privacy level"""
        if self.policy.level in [PrivacyLevel.PARANOID, PrivacyLevel.STRICT]:
            # Only keep domain
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}"
            
        # Check if domain is allowed
        domain = urllib.parse.urlparse(url).netloc
        if self.policy.allowed_domains and domain not in self.policy.allowed_domains:
            return f"[EXTERNAL_DOMAIN]"
            
        # Remove query parameters that might contain personal data
        parsed = urllib.parse.urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
    def _remove_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively remove sensitive information"""
        cleaned = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # Check for sensitive patterns
                is_sensitive = any(
                    re.search(pattern, value, re.IGNORECASE)
                    for pattern in self.sensitive_patterns
                )
                
                if is_sensitive:
                    cleaned[key] = "[REDACTED]"
                    self._log_violation("sensitive_data_removed", key)
                else:
                    cleaned[key] = value
                    
            elif isinstance(value, dict):
                cleaned[key] = self._remove_sensitive_data(value)
            else:
                cleaned[key] = value
                
        return cleaned
        
    def _generalize_title(self, title: str) -> str:
        """Generalize window title to category"""
        # Common application patterns
        if any(browser in title.lower() for browser in ['firefox', 'chrome', 'safari', 'edge']):
            return "Web Browser"
        elif any(editor in title.lower() for editor in ['code', 'vim', 'emacs', 'sublime']):
            return "Code Editor"
        elif any(term in title.lower() for term in ['terminal', 'console', 'shell']):
            return "Terminal"
        elif any(chat in title.lower() for chat in ['slack', 'discord', 'teams']):
            return "Communication"
        else:
            return "Application"
            
    def _remove_identifiers(self, text: str) -> str:
        """Remove potential personal identifiers"""
        # Email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', text)
        
        # Phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        
        # Social Security Numbers
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Credit card numbers
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
        
        # File paths with usernames
        text = re.sub(r'/home/[^/]+/', '/home/[USER]/', text)
        text = re.sub(r'C:\\Users\\[^\\]+\\', 'C:\\Users\\[USER]\\', text)
        
        return text
        
    def _generate_salt(self) -> str:
        """Generate anonymization salt"""
        # Changes weekly for better anonymization
        week_number = datetime.now().isocalendar()[1]
        return hashlib.sha256(f"privacy_salt_{week_number}".encode()).hexdigest()[:16]
        
    def anonymize_identifier(self, identifier: str) -> str:
        """Anonymize an identifier (e.g., user ID, session ID)"""
        if self.policy.level == PrivacyLevel.PARANOID:
            return "ANONYMOUS"
            
        # One-way hash with salt
        combined = f"{identifier}{self.anonymization_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:12]
        
    def check_data_retention(self) -> Dict[str, int]:
        """Check and enforce data retention policies"""
        cursor = self.skg.conn.cursor()
        
        # Count data older than retention period
        retention_cutoff = datetime.now() - timedelta(days=self.policy.data_retention_days)
        anonymize_cutoff = datetime.now() - timedelta(days=self.policy.anonymize_after_days)
        
        # Data to be deleted
        delete_count = cursor.execute("""
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'phenomenological'
            AND created_at < ?
        """, (retention_cutoff.isoformat(),)).fetchone()[0]
        
        # Data to be anonymized
        anonymize_count = cursor.execute("""
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'phenomenological'
            AND created_at < ?
            AND created_at > ?
            AND json_extract(properties, '$.anonymized') IS NULL
        """, (anonymize_cutoff.isoformat(), retention_cutoff.isoformat())).fetchone()[0]
        
        return {
            'to_delete': delete_count,
            'to_anonymize': anonymize_count,
            'retention_days': self.policy.data_retention_days,
            'anonymize_after_days': self.policy.anonymize_after_days
        }
        
    def enforce_data_retention(self) -> Dict[str, int]:
        """Actually enforce retention policies"""
        stats = self.check_data_retention()
        cursor = self.skg.conn.cursor()
        
        retention_cutoff = datetime.now() - timedelta(days=self.policy.data_retention_days)
        anonymize_cutoff = datetime.now() - timedelta(days=self.policy.anonymize_after_days)
        
        # Delete old data
        cursor.execute("""
            DELETE FROM nodes
            WHERE layer = 'phenomenological'
            AND created_at < ?
        """, (retention_cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        
        # Anonymize recent data
        nodes_to_anonymize = cursor.execute("""
            SELECT id, properties
            FROM nodes
            WHERE layer = 'phenomenological'
            AND created_at < ?
            AND created_at > ?
            AND json_extract(properties, '$.anonymized') IS NULL
        """, (anonymize_cutoff.isoformat(), retention_cutoff.isoformat())).fetchall()
        
        anonymized = 0
        for node_id, properties in nodes_to_anonymize:
            props = json.loads(properties)
            props = self._anonymize_properties(props)
            props['anonymized'] = True
            props['anonymized_date'] = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE nodes
                SET properties = ?
                WHERE id = ?
            """, (json.dumps(props), node_id))
            
            anonymized += 1
            
        self.skg.conn.commit()
        
        self.logger.info(f"Data retention enforced: {deleted} deleted, {anonymized} anonymized")
        
        return {
            'deleted': deleted,
            'anonymized': anonymized
        }
        
    def _anonymize_properties(self, props: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize properties while preserving structure"""
        anonymized = {}
        
        for key, value in props.items():
            if key in ['timestamp', 'type', 'pattern_type', 'anonymized']:
                # Preserve these fields
                anonymized[key] = value
            elif isinstance(value, str):
                # Anonymize strings
                if len(value) > 20:
                    anonymized[key] = "[ANONYMIZED_TEXT]"
                else:
                    anonymized[key] = "[ANONYMIZED]"
            elif isinstance(value, (int, float)):
                # Preserve numeric patterns but add noise
                import random
                noise = random.uniform(0.9, 1.1)
                anonymized[key] = round(value * noise, 2)
            elif isinstance(value, dict):
                anonymized[key] = self._anonymize_properties(value)
            else:
                anonymized[key] = "[ANONYMIZED]"
                
        return anonymized
        
    def _log_violation(self, violation_type: str, details: str):
        """Log a privacy violation or concern"""
        violation = PrivacyViolation(
            timestamp=datetime.now(),
            violation_type=violation_type,
            data_involved=details,
            action_taken="data_sanitized",
            severity="medium"
        )
        
        self.violations.append(violation)
        
        # Log to knowledge graph
        violation_id = f"privacy_violation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'privacy_violation', ?)
        """, (
            violation_id,
            json.dumps({
                'timestamp': violation.timestamp.isoformat(),
                'type': violation.violation_type,
                'data_involved': violation.data_involved,
                'action_taken': violation.action_taken,
                'severity': violation.severity
            })
        ))
        
        self.skg.conn.commit()
        
    def get_privacy_report(self) -> Dict[str, Any]:
        """Generate comprehensive privacy report"""
        # Recent violations
        recent_violations = [
            {
                'timestamp': v.timestamp.isoformat(),
                'type': v.violation_type,
                'action': v.action_taken
            }
            for v in self.violations[-10:]
        ]
        
        # Data statistics
        cursor = self.skg.conn.cursor()
        total_nodes = cursor.execute("""
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'phenomenological'
        """).fetchone()[0]
        
        anonymized_nodes = cursor.execute("""
            SELECT COUNT(*)
            FROM nodes
            WHERE layer = 'phenomenological'
            AND json_extract(properties, '$.anonymized') = true
        """).fetchone()[0]
        
        # Retention status
        retention_status = self.check_data_retention()
        
        return {
            'privacy_level': self.policy.level.value,
            'policy': {
                'excluded_apps': list(self.policy.excluded_apps),
                'data_retention_days': self.policy.data_retention_days,
                'share_analytics': self.policy.share_analytics,
                'allow_pattern_learning': self.policy.allow_pattern_learning
            },
            'statistics': {
                'total_data_points': total_nodes,
                'anonymized_data_points': anonymized_nodes,
                'anonymization_rate': anonymized_nodes / max(total_nodes, 1)
            },
            'recent_violations': recent_violations,
            'retention_status': retention_status,
            'privacy_health': self._calculate_privacy_health()
        }
        
    def _calculate_privacy_health(self) -> Dict[str, Any]:
        """Calculate overall privacy health score"""
        # Factors contributing to privacy health
        factors = {
            'policy_strictness': self._score_policy_strictness(),
            'violation_rate': self._score_violation_rate(),
            'data_minimization': self._score_data_minimization(),
            'retention_compliance': self._score_retention_compliance()
        }
        
        # Overall health score
        health_score = sum(factors.values()) / len(factors)
        
        # Determine health status
        if health_score > 0.8:
            status = "excellent"
        elif health_score > 0.6:
            status = "good"
        elif health_score > 0.4:
            status = "fair"
        else:
            status = "needs_attention"
            
        return {
            'score': health_score,
            'status': status,
            'factors': factors,
            'recommendations': self._generate_privacy_recommendations(factors)
        }
        
    def _score_policy_strictness(self) -> float:
        """Score based on privacy policy strictness"""
        level_scores = {
            PrivacyLevel.PARANOID: 1.0,
            PrivacyLevel.STRICT: 0.8,
            PrivacyLevel.BALANCED: 0.6,
            PrivacyLevel.RELAXED: 0.4,
            PrivacyLevel.TRUSTING: 0.2
        }
        return level_scores.get(self.policy.level, 0.5)
        
    def _score_violation_rate(self) -> float:
        """Score based on privacy violation rate"""
        if not self.violations:
            return 1.0
            
        recent_violations = len([
            v for v in self.violations
            if v.timestamp > datetime.now() - timedelta(days=7)
        ])
        
        # Lower violations = higher score
        if recent_violations == 0:
            return 1.0
        elif recent_violations < 5:
            return 0.8
        elif recent_violations < 10:
            return 0.6
        else:
            return 0.3
            
    def _score_data_minimization(self) -> float:
        """Score based on data minimization practices"""
        cursor = self.skg.conn.cursor()
        
        # Check ratio of anonymized to total data
        total = cursor.execute(
            "SELECT COUNT(*) FROM nodes WHERE layer = 'phenomenological'"
        ).fetchone()[0]
        
        anonymized = cursor.execute("""
            SELECT COUNT(*) FROM nodes 
            WHERE layer = 'phenomenological'
            AND json_extract(properties, '$.anonymized') = true
        """).fetchone()[0]
        
        if total == 0:
            return 1.0
            
        return anonymized / total
        
    def _score_retention_compliance(self) -> float:
        """Score based on retention policy compliance"""
        retention_status = self.check_data_retention()
        
        # Perfect score if no data needs action
        if retention_status['to_delete'] == 0 and retention_status['to_anonymize'] == 0:
            return 1.0
            
        # Reduce score based on pending actions
        total_pending = retention_status['to_delete'] + retention_status['to_anonymize']
        if total_pending < 10:
            return 0.8
        elif total_pending < 50:
            return 0.6
        else:
            return 0.3
            
    def _generate_privacy_recommendations(self, factors: Dict[str, float]) -> List[str]:
        """Generate privacy improvement recommendations"""
        recommendations = []
        
        if factors['policy_strictness'] < 0.6:
            recommendations.append("Consider increasing privacy level for better protection")
            
        if factors['violation_rate'] < 0.8:
            recommendations.append("Review recent privacy violations and adjust filters")
            
        if factors['data_minimization'] < 0.5:
            recommendations.append("Enable more aggressive data anonymization")
            
        if factors['retention_compliance'] < 0.8:
            recommendations.append("Run data retention enforcement to clean old data")
            
        if not recommendations:
            recommendations.append("Privacy health is excellent - keep up the good practices!")
            
        return recommendations
        
    def update_privacy_policy(self, updates: Dict[str, Any]) -> bool:
        """
        Update privacy policy with user preferences
        """
        # Apply updates
        if 'level' in updates:
            self.policy.level = PrivacyLevel(updates['level'])
            
        if 'excluded_apps' in updates:
            self.policy.excluded_apps.update(updates['excluded_apps'])
            
        if 'data_retention_days' in updates:
            self.policy.data_retention_days = updates['data_retention_days']
            
        # Save to knowledge graph
        policy_id = f"privacy_policy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'privacy_policy', ?)
        """, (
            policy_id,
            json.dumps({
                'level': self.policy.level.value,
                'excluded_apps': list(self.policy.excluded_apps),
                'excluded_patterns': list(self.policy.excluded_patterns),
                'allowed_domains': list(self.policy.allowed_domains),
                'data_retention_days': self.policy.data_retention_days,
                'anonymize_after_days': self.policy.anonymize_after_days,
                'share_analytics': self.policy.share_analytics,
                'allow_pattern_learning': self.policy.allow_pattern_learning,
                'updated_at': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
        self.logger.info(f"Privacy policy updated: {updates}")
        return True