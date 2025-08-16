#!/usr/bin/env python3
"""
Simplified Self-Healing Engine V2 for Luminous Nix.

This streamlined version reduces complexity from 1,150 lines to ~300 lines
while maintaining all essential functionality.

Key improvements:
- 3 action categories instead of 14 specific actions
- Simple threshold-based detection
- Pattern matching for resolution
- Clean separation of concerns
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path

from luminous_nix.environmental import get_system_monitor
from .permission_handler_v2 import execute_healing_action
from .friction_monitor import get_friction_monitor
from .notification_queue import get_notification_queue, Priority

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Simplified issue categories"""
    SERVICE = "service"      # Service not running, crashed, etc.
    RESOURCE = "resource"    # High CPU, memory, disk usage
    SYSTEM = "system"        # System-level issues (corruption, etc.)


class Severity(Enum):
    """Issue severity levels"""
    LOW = "low"          # Monitor only
    MEDIUM = "medium"    # Fix if easy
    HIGH = "high"        # Fix now
    CRITICAL = "critical"  # Emergency fix


@dataclass
class Issue:
    """Simplified issue representation"""
    type: IssueType
    severity: Severity
    description: str
    component: str  # What component is affected
    metric_value: float  # Current problematic value
    threshold: float  # What triggered the issue
    

@dataclass
class HealingResult:
    """Result of a healing action"""
    success: bool
    action_taken: str
    error: Optional[str] = None
    duration_ms: int = 0


class SimpleDetector:
    """
    Simple threshold-based issue detection.
    No complex state machines, just check and report.
    """
    
    def __init__(self):
        self.monitor = get_system_monitor()
        
        # Simple thresholds (configurable)
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'load_average': 4.0,
        }
    
    async def detect_issues(self) -> List[Issue]:
        """Check system and return list of issues"""
        issues = []
        
        try:
            # Get current metrics - adapt to SystemMonitor interface
            if hasattr(self.monitor, 'get_health_metrics'):
                metrics = await self.monitor.get_health_metrics()
            else:
                # Use SystemMonitor's actual interface
                await self.monitor.update_category('full')
                state = self.monitor.get_state()
                
                # Convert to expected format
                metrics = {
                    'cpu': {'percent': state.get('cpu', {}).percent if state.get('cpu') else 0},
                    'memory': {'percent': state.get('memory', {}).percent_used if state.get('memory') else 0},
                    'disk': {'percent': max([d.percent_used for d in state.get('disk', [])] + [0])},
                    'services': {s.name: {'running': s.active} for s in state.get('services', [])}
                }
            
            # CPU check
            cpu = metrics.get('cpu', {}).get('percent', 0)
            if cpu > self.thresholds['cpu_percent']:
                issues.append(Issue(
                    type=IssueType.RESOURCE,
                    severity=Severity.HIGH if cpu > 90 else Severity.MEDIUM,
                    description=f"High CPU usage: {cpu:.1f}%",
                    component="cpu",
                    metric_value=cpu,
                    threshold=self.thresholds['cpu_percent']
                ))
            
            # Memory check
            memory = metrics.get('memory', {}).get('percent', 0)
            if memory > self.thresholds['memory_percent']:
                issues.append(Issue(
                    type=IssueType.RESOURCE,
                    severity=Severity.HIGH if memory > 95 else Severity.MEDIUM,
                    description=f"High memory usage: {memory:.1f}%",
                    component="memory",
                    metric_value=memory,
                    threshold=self.thresholds['memory_percent']
                ))
            
            # Disk check
            disk = metrics.get('disk', {}).get('percent', 0)
            if disk > self.thresholds['disk_percent']:
                issues.append(Issue(
                    type=IssueType.RESOURCE,
                    severity=Severity.CRITICAL if disk > 95 else Severity.HIGH,
                    description=f"Low disk space: {disk:.1f}% used",
                    component="disk",
                    metric_value=disk,
                    threshold=self.thresholds['disk_percent']
                ))
            
            # Service checks (simplified)
            services = metrics.get('services', {})
            for service_name, status in services.items():
                if not status.get('running', True):
                    issues.append(Issue(
                        type=IssueType.SERVICE,
                        severity=Severity.HIGH,
                        description=f"Service {service_name} is not running",
                        component=service_name,
                        metric_value=0,
                        threshold=1
                    ))
            
        except Exception as e:
            logger.error(f"Error detecting issues: {e}")
        
        return issues


class SimpleResolver:
    """
    Simple pattern matching to determine healing actions.
    No complex plan generation, just map issue to action.
    """
    
    def get_action(self, issue: Issue) -> Dict[str, Any]:
        """Determine what action to take for an issue"""
        
        # Pattern matching based on issue type and component
        if issue.type == IssueType.SERVICE:
            return {
                'action': 'restart_service',
                'parameters': {'service': issue.component}
            }
        
        elif issue.type == IssueType.RESOURCE:
            if issue.component == 'cpu':
                # For high CPU, we might kill resource-heavy processes
                # or adjust CPU governor
                return {
                    'action': 'set_cpu_governor',
                    'parameters': {'governor': 'powersave'}
                }
            
            elif issue.component == 'memory':
                # For high memory, clear caches
                return {
                    'action': 'clear_system_cache',
                    'parameters': {}
                }
            
            elif issue.component == 'disk':
                # For low disk, run garbage collection
                return {
                    'action': 'clean_nix_store',
                    'parameters': {}
                }
        
        elif issue.type == IssueType.SYSTEM:
            # For system issues, might need rollback
            return {
                'action': 'rollback_generation',
                'parameters': {}
            }
        
        # Default: no action
        return {'action': 'none', 'parameters': {}}


class SimplifiedHealingEngine:
    """
    Simplified self-healing engine with clear separation of concerns.
    
    This is 300 lines instead of 1,150 lines, but does the same job.
    """
    
    def __init__(self):
        self.detector = SimpleDetector()
        self.resolver = SimpleResolver()
        self.healing_enabled = True
        self.dry_run = False
        
        # Simple metrics (no complex Prometheus setup)
        self.metrics = {
            'issues_detected': 0,
            'issues_resolved': 0,
            'last_check': None,
        }
        
        # Friction monitoring for adaptive behavior
        self.friction_monitor = get_friction_monitor()
        
        # Flow-respecting notification queue
        self.notifications = get_notification_queue()
    
    async def detect_and_heal(self) -> List[HealingResult]:
        """
        Main healing cycle: detect issues and fix them.
        Simple, no complex state machine.
        """
        results = []
        
        # Detect issues
        issues = await self.detector.detect_issues()
        self.metrics['issues_detected'] += len(issues)
        self.metrics['last_check'] = datetime.now()
        
        if not issues:
            self.notifications.add("✅ No issues detected", Priority.LOW, "success")
            return results
        
        self.notifications.add(f"🔍 Found {len(issues)} issues", Priority.NORMAL, "info")
        
        # Process each issue
        for issue in issues:
            if not self.healing_enabled:
                self.notifications.add(
                    f"⚠️ Healing disabled, skipping: {issue.description}",
                    Priority.NORMAL,
                    "warning"
                )
                continue
            
            # Only fix high/critical issues automatically
            if issue.severity in [Severity.LOW, Severity.MEDIUM]:
                self.notifications.add(
                    f"ℹ️ Low priority, monitoring only: {issue.description}",
                    Priority.LOW,
                    "info"
                )
                continue
            
            # Get action
            action_spec = self.resolver.get_action(issue)
            
            if action_spec['action'] == 'none':
                self.notifications.add(
                    f"❓ No action defined for: {issue.description}",
                    Priority.NORMAL,
                    "warning"
                )
                # Track friction - no action available
                self.friction_monitor.track_action('no_action', False, issue.description)
                continue
            
            # Execute healing
            self.notifications.add(
                f"🔧 Healing: {issue.description} → {action_spec['action']}",
                Priority.HIGH if issue.severity == Severity.CRITICAL else Priority.NORMAL,
                "info"
            )
            
            # Check if user is confused and adapt
            if self.friction_monitor.is_user_confused():
                adaptations = self.friction_monitor.suggest_adaptation()
                if adaptations['verbose_mode']:
                    # High friction - provide verbose details immediately
                    verbose_msg = (
                        f"🤔 High friction detected - providing more details:\n"
                        f"   Issue type: {issue.type.value}\n"
                        f"   Severity: {issue.severity.value}\n"
                        f"   Component: {issue.component}\n"
                        f"   Current value: {issue.metric_value:.2f}\n"
                        f"   Threshold: {issue.threshold:.2f}"
                    )
                    # Show verbose info immediately for confused users
                    logger.info(verbose_msg)  # Direct log for immediate help
            
            if self.dry_run:
                results.append(HealingResult(
                    success=True,
                    action_taken=f"[DRY RUN] {action_spec['action']}",
                ))
                continue
            
            # Use the V2 permission handler
            start_time = datetime.now()
            result = await execute_healing_action(
                action_spec['action'],
                action_spec['parameters']
            )
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            healing_result = HealingResult(
                success=result.success,
                action_taken=action_spec['action'],
                error=result.error,
                duration_ms=duration_ms
            )
            
            # Track friction based on success
            self.friction_monitor.track_action(
                action_spec['action'],
                result.success,
                issue.description
            )
            
            if result.success:
                self.metrics['issues_resolved'] += 1
                self.notifications.add(
                    f"✅ Successfully healed: {issue.description}",
                    Priority.NORMAL,
                    "success"
                )
            else:
                # Failures are critical - show immediately
                logger.error(f"❌ Failed to heal: {result.error}")
                if result.suggestion:
                    self.notifications.add(
                        f"💡 Suggestion: {result.suggestion}",
                        Priority.HIGH,
                        "info"
                    )
                
                # High friction after failure - provide help immediately
                if self.friction_monitor.is_user_confused():
                    logger.info("📚 Need help? Try 'ask-nix healing help' for guidance")
            
            results.append(healing_result)
        
        return results
    
    def get_friction_metrics(self) -> Dict[str, Any]:
        """Get current friction metrics for monitoring"""
        metrics = self.friction_monitor.get_metrics()
        return {
            'friction_score': metrics.score,
            'error_rate': metrics.error_rate,
            'user_confused': self.friction_monitor.is_user_confused(),
            'adaptations': self.friction_monitor.suggest_adaptation()
        }
    
    async def start_monitoring(self, interval: int = 60):
        """
        Start continuous monitoring and healing.
        Simple loop, no complex orchestration.
        """
        logger.info("🚀 Starting simplified healing engine")
        logger.info(f"   Check interval: {interval}s")
        logger.info(f"   Dry run: {self.dry_run}")
        logger.info(f"   Notification batching: 2 minutes")
        
        while True:
            try:
                await self.detect_and_heal()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                logger.info("🛑 Monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get simple metrics (no Prometheus complexity)"""
        return {
            **self.metrics,
            'success_rate': (
                self.metrics['issues_resolved'] / self.metrics['issues_detected'] * 100
                if self.metrics['issues_detected'] > 0 else 0
            )
        }
    
    def set_threshold(self, metric: str, value: float):
        """Update detection threshold"""
        if hasattr(self.detector, 'thresholds'):
            self.detector.thresholds[metric] = value
            logger.info(f"Updated threshold: {metric} = {value}")
    
    def enter_flow_state(self):
        """Signal that user is entering deep work - hold notifications"""
        self.notifications.enter_flow_state()
        logger.info("🧘 Flow state activated - batching notifications")
    
    def exit_flow_state(self):
        """Signal that user is ready for notifications"""
        self.notifications.exit_flow_state()
        logger.info("📬 Flow state ended - delivering notifications")
    
    def get_notification_status(self) -> Dict[str, Any]:
        """Get current notification queue status"""
        return self.notifications.get_status()
    
    def flush_notifications(self):
        """Force immediate delivery of all queued notifications"""
        self.notifications.force_flush()


# Convenience functions for compatibility
def create_self_healing_engine() -> SimplifiedHealingEngine:
    """Create a simplified healing engine instance"""
    return SimplifiedHealingEngine()


async def quick_heal() -> List[HealingResult]:
    """Run a single healing cycle"""
    engine = SimplifiedHealingEngine()
    return await engine.detect_and_heal()


# For backward compatibility
SelfHealingEngine = SimplifiedHealingEngine  # Alias for compatibility