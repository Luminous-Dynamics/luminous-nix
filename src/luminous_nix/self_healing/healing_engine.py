"""
Self-Healing Engine for Luminous Nix.

This revolutionary system automatically detects, diagnoses, and repairs
system issues without human intervention, learning from each fix to
improve future responses.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import hashlib

# New monitoring dependencies
try:
    from prometheus_client import Counter, Gauge, Histogram, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    
try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False
    
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from luminous_nix.environmental import (
    get_system_monitor,
    PredictiveAssistant,
    Prediction
)
from luminous_nix.service_with_awareness import AwareNixService
from luminous_nix.environmental.historical_trending import HistoricalHealthTracker
from luminous_nix.environmental.file_monitor import FileSystemMonitor

# Import healing-specific modules
try:
    from .healing_plans import HealingPlans
    from .backup_restore import BackupRestoreManager
    from .permission_handler import PermissionHandler, GracefulHealingAdapter
    HEALING_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Healing modules not available: {e}")
    HEALING_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class HealingAction(Enum):
    """Types of healing actions the system can take"""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    GARBAGE_COLLECT = "garbage_collect"
    KILL_PROCESS = "kill_process"
    FREE_MEMORY = "free_memory"
    CLEAN_DISK = "clean_disk"
    OPTIMIZE_STORE = "optimize_store"
    ROLLBACK_GENERATION = "rollback_generation"
    REPAIR_SERVICE = "repair_service"
    REINDEX_DATABASE = "reindex_database"
    ADJUST_LIMITS = "adjust_limits"
    CUSTOM_SCRIPT = "custom_script"
    RESTORE_FILE = "restore_file"
    FIX_PERMISSIONS = "fix_permissions"
    REPAIR_CORRUPTED_FILE = "repair_corrupted_file"


class Severity(Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Issue:
    """Detected system issue"""
    id: str
    timestamp: datetime
    type: str
    severity: Severity
    description: str
    metrics: Dict[str, Any]
    affected_components: List[str]
    
    def fingerprint(self) -> str:
        """Generate unique fingerprint for this issue type"""
        key = f"{self.type}:{':'.join(sorted(self.affected_components))}"
        return hashlib.md5(key.encode()).hexdigest()[:8]


@dataclass
class HealingPlan:
    """Plan for fixing an issue"""
    issue_id: str
    actions: List[HealingAction]
    estimated_impact: Dict[str, Any]
    confidence: float
    requires_confirmation: bool
    rollback_possible: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_id': self.issue_id,
            'actions': [a.value for a in self.actions],
            'estimated_impact': self.estimated_impact,
            'confidence': self.confidence,
            'requires_confirmation': self.requires_confirmation,
            'rollback_possible': self.rollback_possible
        }


@dataclass
class HealingResult:
    """Result of a healing action"""
    issue_id: str
    success: bool
    actions_taken: List[str]
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    duration_seconds: float
    rolled_back: bool = False
    error: Optional[str] = None


class HealingKnowledgeBase:
    """
    Knowledge base that learns from successful fixes.
    Stores patterns of issues and their effective remedies.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / '.local' / 'share' / 'luminous-nix' / 'healing_knowledge.json'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.knowledge = self._load_knowledge()
        
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from disk"""
        if self.db_path.exists():
            try:
                with open(self.db_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load healing knowledge: {e}")
        
        return {
            'fixes': {},  # issue_fingerprint -> successful fixes
            'failures': {},  # issue_fingerprint -> failed attempts
            'patterns': {},  # pattern -> issue fingerprints
            'statistics': {
                'total_heals': 0,
                'successful_heals': 0,
                'prevented_issues': 0
            }
        }
    
    def save_knowledge(self):
        """Persist knowledge to disk"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save healing knowledge: {e}")
    
    def record_healing(self, issue: Issue, result: HealingResult):
        """Record the result of a healing attempt"""
        fingerprint = issue.fingerprint()
        
        if result.success:
            if fingerprint not in self.knowledge['fixes']:
                self.knowledge['fixes'][fingerprint] = []
            
            self.knowledge['fixes'][fingerprint].append({
                'timestamp': datetime.now().isoformat(),
                'actions': result.actions_taken,
                'impact': {
                    'duration': result.duration_seconds,
                    'metrics_improvement': self._calculate_improvement(
                        result.metrics_before,
                        result.metrics_after
                    )
                }
            })
            
            self.knowledge['statistics']['successful_heals'] += 1
        else:
            if fingerprint not in self.knowledge['failures']:
                self.knowledge['failures'][fingerprint] = []
            
            self.knowledge['failures'][fingerprint].append({
                'timestamp': datetime.now().isoformat(),
                'actions': result.actions_taken,
                'error': result.error
            })
        
        self.knowledge['statistics']['total_heals'] += 1
        self.save_knowledge()
    
    def _calculate_improvement(self, before: Dict, after: Dict) -> Dict[str, float]:
        """Calculate improvement in metrics"""
        improvement = {}
        
        for key in before:
            if key in after and isinstance(before[key], (int, float)):
                if before[key] > 0:
                    improvement[key] = (before[key] - after[key]) / before[key] * 100
        
        return improvement
    
    def get_successful_fixes(self, issue: Issue) -> List[Dict[str, Any]]:
        """Get previously successful fixes for this issue type"""
        fingerprint = issue.fingerprint()
        return self.knowledge['fixes'].get(fingerprint, [])
    
    def get_confidence(self, issue: Issue, actions: List[HealingAction]) -> float:
        """Calculate confidence based on past success"""
        fixes = self.get_successful_fixes(issue)
        
        if not fixes:
            return 0.5  # No history, medium confidence
        
        # Check how many times these actions worked
        action_strings = [a.value for a in actions]
        successes = sum(1 for fix in fixes if fix['actions'] == action_strings)
        
        if successes == 0:
            return 0.3  # Never tried this combination
        
        # Calculate success rate
        fingerprint = issue.fingerprint()
        total_attempts = len(self.knowledge['fixes'].get(fingerprint, [])) + \
                        len(self.knowledge['failures'].get(fingerprint, []))
        
        if total_attempts > 0:
            return min(0.95, successes / total_attempts)
        
        return 0.5


class SelfHealingEngine:
    """
    Main self-healing engine that coordinates detection, diagnosis,
    and repair of system issues.
    """
    
    def __init__(self):
        self.monitor = get_system_monitor()
        self.assistant = PredictiveAssistant(self.monitor)
        self.service = AwareNixService()
        self.health_tracker = HistoricalHealthTracker()
        self.knowledge = HealingKnowledgeBase()
        
        # Initialize file system monitor with healing callback
        self.file_monitor = FileSystemMonitor(healing_callback=self._handle_file_issue)
        
        # Initialize backup/restore manager
        if HEALING_MODULES_AVAILABLE:
            self.backup_manager = BackupRestoreManager(healing_engine=self)
            self.healing_plans = HealingPlans()
            self.permission_handler = PermissionHandler()
            self.healing_adapter = GracefulHealingAdapter(self.permission_handler)
        else:
            self.backup_manager = None
            self.healing_plans = None
            self.permission_handler = None
            self.healing_adapter = None
        
        # Metrics server (initialized separately)
        self.metrics_server = None
        
        self._running = False
        self._healing_task = None
        
        # Set up Prometheus metrics if available
        if PROMETHEUS_AVAILABLE:
            self._setup_prometheus_metrics()
        
        # Set up disk cache if available
        if DISKCACHE_AVAILABLE:
            cache_dir = Path.home() / '.cache' / 'luminous-nix' / 'healing'
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache = diskcache.Cache(str(cache_dir))
        else:
            self.cache = None
        
        # Healing strategies
        self.strategies = {
            'memory_high': self._heal_high_memory,
            'disk_full': self._heal_disk_full,
            'cpu_high': self._heal_high_cpu,
            'temperature_high': self._heal_high_temperature,
            'service_failed': self._heal_failed_service,
            'system_slow': self._heal_slow_system,
            'generation_broken': self._heal_broken_generation,
            'file_system_issue': self._heal_file_issue,
            'file_deleted': self._heal_deleted_file,
            'file_corrupted': self._heal_corrupted_file,
            'permission_denied': self._heal_permission_issue,
            'network_issues': self._heal_network_issues
        }
        
        # Safety limits
        self.limits = {
            'max_heals_per_hour': 10,
            'max_rollbacks_per_day': 3,
            'min_health_for_auto': 30,  # Don't auto-heal below this
            'cooldown_minutes': 5
        }
        
        self.recent_heals = []
    
    def _setup_prometheus_metrics(self):
        """Set up Prometheus metrics for monitoring healing activities"""
        # Counters
        self.metrics_issues_detected = Counter(
            'luminous_nix_healing_issues_detected_total',
            'Total number of issues detected',
            ['issue_type', 'severity']
        )
        self.metrics_heals_attempted = Counter(
            'luminous_nix_healing_attempts_total',
            'Total number of healing attempts',
            ['issue_type', 'action']
        )
        self.metrics_heals_successful = Counter(
            'luminous_nix_healing_successes_total',
            'Total number of successful heals',
            ['issue_type', 'action']
        )
        
        # Gauges
        self.metrics_system_health = Gauge(
            'luminous_nix_system_health_score',
            'Current system health score (0-100)'
        )
        self.metrics_active_issues = Gauge(
            'luminous_nix_active_issues',
            'Number of currently active issues',
            ['severity']
        )
        
        # Histograms
        self.metrics_healing_duration = Histogram(
            'luminous_nix_healing_duration_seconds',
            'Time taken to heal issues',
            ['issue_type'],
            buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        # Summary
        self.metrics_confidence_score = Summary(
            'luminous_nix_healing_confidence',
            'Confidence scores for healing plans',
            ['issue_type']
        )
        
        logger.info("✅ Prometheus metrics initialized for healing engine")
    
    async def start(self):
        """Start the self-healing engine"""
        if self._running:
            return
        
        self._running = True
        logger.info("🔧 Self-healing engine started")
        
        # Start system monitoring
        await self.monitor.start_monitoring()
        
        # Start file system monitoring
        if self.file_monitor.is_available():
            self.file_monitor.start()
            logger.info("🔍 File system monitoring activated")
        
        # Start healing loop
        self._healing_task = asyncio.create_task(self._healing_loop())
    
    async def stop(self):
        """Stop the self-healing engine"""
        self._running = False
        
        if self._healing_task:
            self._healing_task.cancel()
            try:
                await self._healing_task
            except asyncio.CancelledError:
                pass
        
        # Stop file system monitoring
        if self.file_monitor.is_available():
            self.file_monitor.stop()
        
        await self.monitor.stop_monitoring()
        logger.info("🔧 Self-healing engine stopped")
    
    async def _healing_loop(self):
        """Main healing loop"""
        while self._running:
            try:
                # Detect issues
                issues = await self.detect_issues()
                
                # Process each issue
                for issue in issues:
                    if self._should_heal(issue):
                        await self.heal_issue(issue)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in healing loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def detect_issues(self) -> List[Issue]:
        """Detect current system issues"""
        issues = []
        
        # Get current state
        state = self.monitor.get_state()
        status = self.monitor.get_quick_status()
        
        # Check memory
        if status['memory_percent'] > 90:
            issues.append(Issue(
                id=f"mem_{datetime.now().timestamp():.0f}",
                timestamp=datetime.now(),
                type='memory_high',
                severity=Severity.CRITICAL if status['memory_percent'] > 95 else Severity.HIGH,
                description=f"Memory usage critical at {status['memory_percent']:.1f}%",
                metrics={'memory_percent': status['memory_percent']},
                affected_components=['system.memory']
            ))
        
        # Check disk
        for mount, percent in status.get('disk_usage', {}).items():
            if percent > 90:
                issues.append(Issue(
                    id=f"disk_{mount}_{datetime.now().timestamp():.0f}",
                    timestamp=datetime.now(),
                    type='disk_full',
                    severity=Severity.CRITICAL if percent > 95 else Severity.HIGH,
                    description=f"Disk {mount} is {percent:.1f}% full",
                    metrics={'disk_percent': percent, 'mount': mount},
                    affected_components=[f'disk.{mount}']
                ))
        
        # Check CPU
        if status['cpu_percent'] > 90:
            issues.append(Issue(
                id=f"cpu_{datetime.now().timestamp():.0f}",
                timestamp=datetime.now(),
                type='cpu_high',
                severity=Severity.HIGH,
                description=f"CPU usage high at {status['cpu_percent']:.1f}%",
                metrics={'cpu_percent': status['cpu_percent']},
                affected_components=['system.cpu']
            ))
        
        # Check temperature
        if 'cpu_temp' in status and status['cpu_temp'] > 80:
            temp = status['cpu_temp']
            issues.append(Issue(
                id=f"temp_{datetime.now().timestamp():.0f}",
                timestamp=datetime.now(),
                type='temperature_high',
                severity=Severity.CRITICAL if temp > 90 else Severity.HIGH,
                description=f"CPU temperature high at {temp:.1f}°C",
                metrics={'temperature': temp},
                affected_components=['system.temperature']
            ))
        
        # Check services
        if 'services' in state:
            for service in state['services']:
                if hasattr(service, 'status') and service.status == 'failed':
                    issues.append(Issue(
                        id=f"svc_{service.name}_{datetime.now().timestamp():.0f}",
                        timestamp=datetime.now(),
                        type='service_failed',
                        severity=Severity.HIGH,
                        description=f"Service {service.name} has failed",
                        metrics={'service': service.name},
                        affected_components=[f'service.{service.name}']
                    ))
        
        # Check overall health
        health_score = self._calculate_health_score(state)
        if health_score < 50:
            issues.append(Issue(
                id=f"health_{datetime.now().timestamp():.0f}",
                timestamp=datetime.now(),
                type='system_slow',
                severity=Severity.MEDIUM,
                description=f"System health poor at {health_score}/100",
                metrics={'health_score': health_score},
                affected_components=['system.overall']
            ))
        
        return issues
    
    def _calculate_health_score(self, state: Dict) -> float:
        """Calculate system health score"""
        # Simplified calculation
        score = 100
        
        if 'cpu' in state and hasattr(state['cpu'], 'percent'):
            score -= min(20, state['cpu'].percent / 5)
        
        if 'memory' in state and hasattr(state['memory'], 'percent'):
            score -= min(30, state['memory'].percent / 3)
        
        return max(0, score)
    
    def _should_heal(self, issue: Issue) -> bool:
        """Determine if we should attempt to heal this issue"""
        # Check safety limits
        recent_count = sum(1 for h in self.recent_heals 
                          if (datetime.now() - h['timestamp']).seconds < 3600)
        
        if recent_count >= self.limits['max_heals_per_hour']:
            logger.warning("Healing rate limit reached")
            return False
        
        # Check cooldown
        for heal in self.recent_heals:
            if heal['issue_type'] == issue.type:
                if (datetime.now() - heal['timestamp']).seconds < self.limits['cooldown_minutes'] * 60:
                    logger.debug(f"Issue {issue.type} in cooldown")
                    return False
        
        # Check severity
        if issue.severity == Severity.CRITICAL:
            return True  # Always try to heal critical issues
        
        # Check confidence from knowledge base
        fixes = self.knowledge.get_successful_fixes(issue)
        if fixes and len(fixes) > 2:
            return True  # We've fixed this successfully before
        
        # For other issues, check if health is above minimum
        health = self._calculate_health_score(self.monitor.get_state())
        return health >= self.limits['min_health_for_auto']
    
    async def heal_issue(self, issue: Issue) -> Optional[HealingResult]:
        """Attempt to heal an issue"""
        logger.info(f"🔧 Attempting to heal: {issue.description}")
        
        # Create healing plan
        plan = await self.create_healing_plan(issue)
        
        if not plan:
            logger.warning(f"No healing plan available for {issue.type}")
            return None
        
        # Check if confirmation needed
        if plan.requires_confirmation:
            logger.info(f"Healing plan requires confirmation: {plan.actions}")
            # In automated mode, skip actions requiring confirmation
            return None
        
        # Execute healing plan
        result = await self.execute_healing_plan(issue, plan)
        
        # Record the heal
        self.recent_heals.append({
            'timestamp': datetime.now(),
            'issue_type': issue.type,
            'success': result.success
        })
        
        # Learn from the result
        self.knowledge.record_healing(issue, result)
        
        # Log result
        if result.success:
            logger.info(f"✅ Successfully healed: {issue.description}")
        else:
            logger.error(f"❌ Failed to heal: {issue.description} - {result.error}")
        
        return result
    
    async def create_healing_plan(self, issue: Issue) -> Optional[HealingPlan]:
        """Create a plan to heal an issue"""
        # Check if we have a strategy for this issue type
        if issue.type not in self.strategies:
            return None
        
        # Get the strategy
        strategy = self.strategies[issue.type]
        
        # Execute strategy to get plan
        return await strategy(issue)
    
    async def execute_healing_plan(self, issue: Issue, plan: HealingPlan) -> HealingResult:
        """Execute a healing plan with automatic backup"""
        start_time = datetime.now()
        metrics_before = self.monitor.get_quick_status()
        actions_taken = []
        success = True
        error = None
        restore_point_id = None
        
        # Create backup before healing
        try:
            restore_point_id = await self.backup_manager.backup_before_heal(
                issue.id, issue.type
            )
            if restore_point_id:
                logger.info(f"📸 Created restore point {restore_point_id} before healing")
                actions_taken.append(f"backup_{restore_point_id}")
        except Exception as e:
            logger.warning(f"Could not create backup: {e}")
        
        try:
            for action in plan.actions:
                logger.debug(f"Executing healing action: {action.value}")
                
                if action == HealingAction.RESTART_SERVICE:
                    service_name = issue.metrics.get('service')
                    if service_name:
                        await self._restart_service(service_name)
                        actions_taken.append(f"restart_{service_name}")
                
                elif action == HealingAction.CLEAR_CACHE:
                    await self._clear_caches()
                    actions_taken.append("clear_cache")
                
                elif action == HealingAction.GARBAGE_COLLECT:
                    await self._run_garbage_collection()
                    actions_taken.append("garbage_collect")
                
                elif action == HealingAction.FREE_MEMORY:
                    await self._free_memory()
                    actions_taken.append("free_memory")
                
                elif action == HealingAction.CLEAN_DISK:
                    mount = issue.metrics.get('mount', '/')
                    await self._clean_disk(mount)
                    actions_taken.append(f"clean_disk_{mount}")
                
                elif action == HealingAction.OPTIMIZE_STORE:
                    await self._optimize_nix_store()
                    actions_taken.append("optimize_store")
                
                # Add more action implementations as needed
                
                # Wait a bit between actions
                await asyncio.sleep(2)
        
        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Error executing healing plan: {e}")
            
            # Attempt rollback if we have a restore point
            if restore_point_id:
                logger.warning(f"⚠️ Healing failed, attempting rollback to {restore_point_id}")
                rollback_success = await self.backup_manager.rollback_if_heal_failed(
                    restore_point_id, issue.id, error
                )
                if rollback_success:
                    actions_taken.append(f"rollback_{restore_point_id}")
                    error += " (rolled back successfully)"
                else:
                    error += " (rollback failed)"
        
        # Get metrics after
        await asyncio.sleep(5)  # Wait for changes to take effect
        metrics_after = self.monitor.get_quick_status()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return HealingResult(
            issue_id=issue.id,
            success=success,
            actions_taken=actions_taken,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            duration_seconds=duration,
            error=error
        )
    
    # Healing strategies for different issue types
    
    async def _heal_high_memory(self, issue: Issue) -> HealingPlan:
        """Strategy for healing high memory usage"""
        actions = []
        confidence = 0.7
        
        # First try clearing caches
        actions.append(HealingAction.CLEAR_CACHE)
        
        # If very high, also try freeing memory
        if issue.metrics['memory_percent'] > 95:
            actions.append(HealingAction.FREE_MEMORY)
            confidence = 0.6
        
        # Check past fixes
        fixes = self.knowledge.get_successful_fixes(issue)
        if fixes:
            confidence = self.knowledge.get_confidence(issue, actions)
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'memory_freed_percent': 10},
            confidence=confidence,
            requires_confirmation=False,
            rollback_possible=False
        )
    
    async def _heal_disk_full(self, issue: Issue) -> HealingPlan:
        """Strategy for healing full disk"""
        actions = []
        mount = issue.metrics.get('mount', '/')
        
        if mount == '/':
            # For root, garbage collect
            actions.append(HealingAction.GARBAGE_COLLECT)
            actions.append(HealingAction.OPTIMIZE_STORE)
        else:
            # For other mounts, try cleaning
            actions.append(HealingAction.CLEAN_DISK)
        
        confidence = self.knowledge.get_confidence(issue, actions)
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'disk_freed_percent': 15},
            confidence=confidence,
            requires_confirmation=mount == '/',  # Require confirmation for root
            rollback_possible=False
        )
    
    async def _heal_high_cpu(self, issue: Issue) -> HealingPlan:
        """Strategy for healing high CPU usage"""
        # Import healing plans for actual implementation
        from luminous_nix.self_healing.healing_plans import HealingPlans
        
        if not hasattr(self, 'healing_plans'):
            self.healing_plans = HealingPlans()
        
        # Execute the CPU healing plan
        context = {
            'cpu_percent': issue.metrics.get('cpu_percent', 100),
            'temperature': issue.metrics.get('temperature', 0)
        }
        
        result = await self.healing_plans.heal_high_cpu(context)
        
        # Convert to HealingPlan format
        if result.get('success'):
            return HealingPlan(
                issue_id=issue.id,
                actions=[HealingAction.KILL_PROCESS, HealingAction.ADJUST_LIMITS],
                estimated_impact={'cpu_reduction': 20},
                confidence=0.7,
                requires_confirmation=False,
                rollback_possible=False
            )
        
        return None
    
    async def _heal_high_temperature(self, issue: Issue) -> HealingPlan:
        """Strategy for healing high temperature issues"""
        # Import healing plans for actual implementation
        from luminous_nix.self_healing.healing_plans import HealingPlans
        
        if not hasattr(self, 'healing_plans'):
            self.healing_plans = HealingPlans()
        
        # Execute the temperature healing plan
        context = {
            'temperature': issue.metrics.get('temperature', 90),
            'cpu_percent': issue.metrics.get('cpu_percent', 0)
        }
        
        result = await self.healing_plans.heal_high_temperature(context)
        
        # Convert to HealingPlan format
        if result.get('success'):
            return HealingPlan(
                issue_id=issue.id,
                actions=[HealingAction.ADJUST_LIMITS],
                estimated_impact={'temperature_reduction': 10},
                confidence=0.8,
                requires_confirmation=False,
                rollback_possible=False
            )
        
        return None
    
    async def _heal_network_issues(self, issue: Issue) -> HealingPlan:
        """Strategy for healing network issues"""
        # Import healing plans for actual implementation
        from luminous_nix.self_healing.healing_plans import HealingPlans
        
        if not hasattr(self, 'healing_plans'):
            self.healing_plans = HealingPlans()
        
        # Execute the network healing plan
        context = {
            'issue': issue.metrics.get('issue_type', 'connectivity')
        }
        
        result = await self.healing_plans.heal_network_issues(context)
        
        # Convert to HealingPlan format
        if result.get('success'):
            return HealingPlan(
                issue_id=issue.id,
                actions=[HealingAction.RESTART_SERVICE],
                estimated_impact={'network_restored': True},
                confidence=0.7,
                requires_confirmation=False,
                rollback_possible=False
            )
        
        return None
    
    async def _heal_failed_service(self, issue: Issue) -> HealingPlan:
        """Strategy for healing failed service"""
        service = issue.metrics.get('service')
        if not service:
            return None
        
        actions = [HealingAction.RESTART_SERVICE]
        confidence = 0.8  # Restarting usually helps
        
        # Check if this service fails frequently
        fixes = self.knowledge.get_successful_fixes(issue)
        if len(fixes) > 5:
            # Frequent failures, might need repair
            actions.append(HealingAction.REPAIR_SERVICE)
            confidence = 0.6
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'service_restored': True},
            confidence=confidence,
            requires_confirmation=False,
            rollback_possible=False
        )
    
    async def _heal_slow_system(self, issue: Issue) -> HealingPlan:
        """Strategy for healing slow system"""
        # Multi-pronged approach
        actions = [
            HealingAction.CLEAR_CACHE,
            HealingAction.FREE_MEMORY
        ]
        
        confidence = self.knowledge.get_confidence(issue, actions)
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'performance_improvement': 20},
            confidence=confidence,
            requires_confirmation=False,
            rollback_possible=False
        )
    
    async def _heal_broken_generation(self, issue: Issue) -> HealingPlan:
        """Strategy for healing broken NixOS generation"""
        actions = [HealingAction.ROLLBACK_GENERATION]
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'system_restored': True},
            confidence=0.9,  # Rollback is very reliable
            requires_confirmation=True,  # Always confirm rollbacks
            rollback_possible=True
        )
    
    # Action implementations
    
    async def _restart_service(self, service_name: str):
        """Restart a systemd service"""
        import subprocess
        try:
            # Use systemctl to restart
            result = subprocess.run(
                ['systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                raise Exception(f"Failed to restart {service_name}: {result.stderr}")
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            raise
    
    async def _clear_caches(self):
        """Clear system caches"""
        try:
            # Clear PageCache, dentries and inodes
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3')
            logger.debug("Cleared system caches")
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
            raise
    
    async def _run_garbage_collection(self):
        """Run Nix garbage collection"""
        import subprocess
        try:
            result = subprocess.run(
                ['nix-collect-garbage', '-d'],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                raise Exception(f"Garbage collection failed: {result.stderr}")
            logger.debug("Completed garbage collection")
        except Exception as e:
            logger.error(f"Error in garbage collection: {e}")
            raise
    
    async def _free_memory(self):
        """Free up system memory"""
        # This is a placeholder - actual implementation would be more sophisticated
        await self._clear_caches()
        
        # Could also:
        # - Identify and kill memory-hungry processes
        # - Restart heavy services
        # - Clear swap
    
    async def _clean_disk(self, mount: str):
        """Clean disk space on a mount point"""
        # Placeholder for disk cleaning logic
        # Would implement based on mount point
        pass
    
    async def _optimize_nix_store(self):
        """Optimize the Nix store"""
        import subprocess
        try:
            result = subprocess.run(
                ['nix-store', '--optimise'],
                capture_output=True,
                text=True,
                timeout=600
            )
            if result.returncode != 0:
                raise Exception(f"Store optimization failed: {result.stderr}")
            logger.debug("Optimized Nix store")
        except Exception as e:
            logger.error(f"Error optimizing store: {e}")
            raise

    
    # File system healing methods
    
    def _handle_file_issue(self, issue_data: Dict[str, Any]):
        """Handle file system issues from the file monitor"""
        # Convert to our Issue format
        issue = Issue(
            id=f"file_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            type='file_system_issue',
            severity=Severity[issue_data.get('severity', 'medium').upper()],
            description=issue_data.get('description', 'File system issue detected'),
            metrics={'file_path': issue_data.get('file_path'), 
                    'event_type': issue_data.get('event_type')},
            affected_components=[issue_data.get('file_path', 'unknown')]
        )
        
        # Queue for healing (if event loop is running)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.heal_issue(issue))
        except RuntimeError:
            # No event loop, log for later processing
            logger.warning(f"No event loop to queue healing for: {issue.description}")
    
    async def _heal_file_issue(self, issue: Issue) -> HealingPlan:
        """General strategy for file system issues"""
        file_path = issue.metrics.get('file_path')
        event_type = issue.metrics.get('event_type')
        
        actions = []
        
        if event_type == 'deleted':
            actions.append(HealingAction.RESTORE_FILE)
        elif event_type == 'corrupted':
            actions.append(HealingAction.REPAIR_CORRUPTED_FILE)
        elif event_type == 'permission_changed':
            actions.append(HealingAction.FIX_PERMISSIONS)
        
        return HealingPlan(
            issue_id=issue.id,
            actions=actions,
            estimated_impact={'file_restored': True},
            confidence=0.7,
            requires_confirmation=True,
            rollback_possible=True
        )
    
    async def _heal_deleted_file(self, issue: Issue) -> HealingPlan:
        """Strategy for deleted critical files"""
        return HealingPlan(
            issue_id=issue.id,
            actions=[HealingAction.RESTORE_FILE],
            estimated_impact={'file_restored': True},
            confidence=0.8,
            requires_confirmation=True,
            rollback_possible=False
        )
    
    async def _heal_corrupted_file(self, issue: Issue) -> HealingPlan:
        """Strategy for corrupted files"""
        return HealingPlan(
            issue_id=issue.id,
            actions=[HealingAction.REPAIR_CORRUPTED_FILE],
            estimated_impact={'file_repaired': True},
            confidence=0.6,
            requires_confirmation=True,
            rollback_possible=True
        )
    
    async def _heal_permission_issue(self, issue: Issue) -> HealingPlan:
        """Strategy for permission issues"""
        return HealingPlan(
            issue_id=issue.id,
            actions=[HealingAction.FIX_PERMISSIONS],
            estimated_impact={'permissions_fixed': True},
            confidence=0.9,
            requires_confirmation=False,
            rollback_possible=True
        )
    
    async def _restore_file(self, file_path: str):
        """Restore a deleted file from backup or generation"""
        import subprocess
        try:
            # Try to restore from previous generation
            result = subprocess.run(
                ['nix-store', '--restore', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                # Try to copy from backup
                backup_path = Path(file_path + '.backup')
                if backup_path.exists():
                    import shutil
                    shutil.copy2(backup_path, file_path)
                    logger.info(f"Restored {file_path} from backup")
                else:
                    raise Exception(f"No backup found for {file_path}")
        except Exception as e:
            logger.error(f"Error restoring file {file_path}: {e}")
            raise
    
    async def _fix_permissions(self, file_path: str):
        """Fix file permissions to expected values"""
        import subprocess
        try:
            # Get expected permissions from NixOS config
            # For now, use sensible defaults
            path = Path(file_path)
            
            if path.suffix == '.nix':
                # Configuration files should be readable
                subprocess.run(['chmod', '644', file_path], check=True)
            elif path.is_dir():
                # Directories need execute permission
                subprocess.run(['chmod', '755', file_path], check=True)
            else:
                # Default to readable file
                subprocess.run(['chmod', '644', file_path], check=True)
            
            logger.info(f"Fixed permissions for {file_path}")
        except Exception as e:
            logger.error(f"Error fixing permissions for {file_path}: {e}")
            raise
    
    def add_configuration_hot_reload(self, config_path: Path):
        """Add hot-reload for configuration files"""
        def reload_config(path: Path):
            """Reload configuration when changed"""
            try:
                # Reload the configuration
                logger.info(f"Reloading configuration from {path}")
                # Implementation depends on your config system
                # For now just log it
                if PROMETHEUS_AVAILABLE and hasattr(self, 'metrics_config_reloads'):
                    self.metrics_config_reloads.inc()
            except Exception as e:
                logger.error(f"Failed to reload config: {e}")
        
        self.file_monitor.add_hot_reload(config_path, reload_config)
    
    async def start_metrics_server(self, host: str = '0.0.0.0', port: int = 9090):
        """
        Start the Prometheus metrics server.
        
        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 9090)
        """
        from luminous_nix.self_healing.metrics_server import MetricsServer
        
        if self.metrics_server:
            logger.warning("Metrics server already running")
            return
        
        self.metrics_server = MetricsServer(
            healing_engine=self,
            host=host,
            port=port
        )
        
        await self.metrics_server.start()
        logger.info(f"📊 Metrics available at http://{host}:{port}/metrics")
    
    async def stop_metrics_server(self):
        """Stop the metrics server if running."""
        if self.metrics_server:
            await self.metrics_server.stop()
            self.metrics_server = None


# Convenience function
def create_self_healing_engine() -> SelfHealingEngine:
    """Create a self-healing engine instance"""
    return SelfHealingEngine()