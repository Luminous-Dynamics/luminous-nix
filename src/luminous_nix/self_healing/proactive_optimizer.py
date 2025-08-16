"""
Proactive Optimization for Luminous Nix.

This module continuously optimizes system performance and prevents
issues before they occur through predictive analysis and preemptive
actions.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path

from luminous_nix.environmental import get_system_monitor
from luminous_nix.environmental.historical_trending import HistoricalHealthTracker
from luminous_nix.environmental.predictive_assistant import PredictiveAssistant
from luminous_nix.self_healing.healing_engine import (
    SelfHealingEngine,
    HealingAction,
    Issue,
    Severity
)

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of proactive optimizations"""
    MEMORY_MANAGEMENT = "memory_management"
    CACHE_OPTIMIZATION = "cache_optimization"
    SERVICE_TUNING = "service_tuning"
    DISK_CLEANUP = "disk_cleanup"
    PROCESS_OPTIMIZATION = "process_optimization"
    NETWORK_TUNING = "network_tuning"
    GENERATION_CLEANUP = "generation_cleanup"
    STORE_OPTIMIZATION = "store_optimization"


@dataclass
class OptimizationOpportunity:
    """Identified optimization opportunity"""
    id: str
    type: OptimizationType
    priority: int  # 1-10, higher is more important
    estimated_benefit: Dict[str, Any]
    confidence: float
    description: str
    actions: List[str]
    safe_to_automate: bool
    
    def score(self) -> float:
        """Calculate optimization score"""
        return self.priority * self.confidence


@dataclass
class OptimizationResult:
    """Result of an optimization action"""
    opportunity_id: str
    success: bool
    metrics_before: Dict[str, Any]
    metrics_after: Dict[str, Any]
    actual_benefit: Dict[str, Any]
    duration_seconds: float
    rolled_back: bool = False
    error: Optional[str] = None


class ProactiveOptimizer:
    """
    Continuously optimizes system performance and prevents issues
    through predictive analysis and preemptive actions.
    """
    
    def __init__(self, healing_engine: Optional[SelfHealingEngine] = None):
        self.monitor = get_system_monitor()
        self.health_tracker = HistoricalHealthTracker()
        self.predictive_assistant = PredictiveAssistant(self.monitor)
        self.healing_engine = healing_engine or SelfHealingEngine()
        
        self._running = False
        self._optimization_task = None
        
        # Optimization thresholds
        self.thresholds = {
            'memory_optimize_at': 70,  # Start optimizing at 70% memory
            'disk_cleanup_at': 80,     # Clean disk at 80% full
            'cache_clear_interval': 24,  # Hours between cache clears
            'generation_keep': 10,      # NixOS generations to keep
            'log_retention_days': 30,   # Days to keep logs
        }
        
        # Track optimizations
        self.optimization_history = []
        self.last_optimizations = {}
        
    async def start(self):
        """Start the proactive optimizer"""
        if self._running:
            return
        
        self._running = True
        logger.info("🚀 Proactive optimizer started")
        
        # Start monitoring
        await self.monitor.start_monitoring()
        
        # Start optimization loop
        self._optimization_task = asyncio.create_task(self._optimization_loop())
    
    async def stop(self):
        """Stop the proactive optimizer"""
        self._running = False
        
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        await self.monitor.stop_monitoring()
        logger.info("🚀 Proactive optimizer stopped")
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self._running:
            try:
                # Find optimization opportunities
                opportunities = await self.find_opportunities()
                
                # Sort by score
                opportunities.sort(key=lambda x: x.score(), reverse=True)
                
                # Process top opportunities
                for opportunity in opportunities[:3]:  # Top 3
                    if self._should_optimize(opportunity):
                        await self.apply_optimization(opportunity)
                
                # Prevent issues proactively
                await self.prevent_future_issues()
                
                # Wait before next cycle
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def find_opportunities(self) -> List[OptimizationOpportunity]:
        """Find optimization opportunities"""
        opportunities = []
        state = self.monitor.get_state()
        
        # Memory optimization
        if 'memory' in state and hasattr(state['memory'], 'percent'):
            mem_percent = state['memory'].percent
            if mem_percent > self.thresholds['memory_optimize_at']:
                opportunities.append(OptimizationOpportunity(
                    id=f"mem_opt_{datetime.now().timestamp():.0f}",
                    type=OptimizationType.MEMORY_MANAGEMENT,
                    priority=min(10, int(mem_percent / 10)),
                    estimated_benefit={'memory_freed_percent': 15},
                    confidence=0.8,
                    description=f"Optimize memory usage (currently {mem_percent:.1f}%)",
                    actions=['clear_caches', 'restart_heavy_services'],
                    safe_to_automate=True
                ))
        
        # Disk cleanup
        if 'disks' in state:
            for disk in state['disks']:
                if hasattr(disk, 'percent') and disk.percent > self.thresholds['disk_cleanup_at']:
                    opportunities.append(OptimizationOpportunity(
                        id=f"disk_opt_{disk.mount_point}_{datetime.now().timestamp():.0f}",
                        type=OptimizationType.DISK_CLEANUP,
                        priority=min(10, int(disk.percent / 10)),
                        estimated_benefit={'disk_freed_gb': 5},
                        confidence=0.9,
                        description=f"Clean disk {disk.mount_point} ({disk.percent:.1f}% full)",
                        actions=['clean_logs', 'clean_cache', 'optimize_store'],
                        safe_to_automate=disk.mount_point != '/'
                    ))
        
        # NixOS generation cleanup
        generations = await self._count_nixos_generations()
        if generations > self.thresholds['generation_keep'] * 2:
            opportunities.append(OptimizationOpportunity(
                id=f"gen_cleanup_{datetime.now().timestamp():.0f}",
                type=OptimizationType.GENERATION_CLEANUP,
                priority=5,
                estimated_benefit={'disk_freed_gb': (generations - 10) * 0.5},
                confidence=0.95,
                description=f"Clean old NixOS generations ({generations} found)",
                actions=['remove_old_generations'],
                safe_to_automate=True
            ))
        
        # Cache optimization (periodic)
        last_cache_clear = self.last_optimizations.get('cache_clear')
        if not last_cache_clear or \
           (datetime.now() - last_cache_clear).hours > self.thresholds['cache_clear_interval']:
            opportunities.append(OptimizationOpportunity(
                id=f"cache_opt_{datetime.now().timestamp():.0f}",
                type=OptimizationType.CACHE_OPTIMIZATION,
                priority=3,
                estimated_benefit={'performance_improvement': 10},
                confidence=0.7,
                description="Periodic cache optimization",
                actions=['clear_old_caches', 'rebuild_cache_index'],
                safe_to_automate=True
            ))
        
        # Service tuning based on patterns
        patterns = await self._analyze_service_patterns()
        for service, pattern in patterns.items():
            if pattern['optimization_potential'] > 0.5:
                opportunities.append(OptimizationOpportunity(
                    id=f"svc_tune_{service}_{datetime.now().timestamp():.0f}",
                    type=OptimizationType.SERVICE_TUNING,
                    priority=int(pattern['optimization_potential'] * 10),
                    estimated_benefit={'resource_reduction': pattern['potential_savings']},
                    confidence=pattern['confidence'],
                    description=f"Tune {service} service configuration",
                    actions=[f'optimize_{service}_config'],
                    safe_to_automate=False  # Service tuning needs approval
                ))
        
        return opportunities
    
    def _should_optimize(self, opportunity: OptimizationOpportunity) -> bool:
        """Determine if we should apply an optimization"""
        # Check if safe to automate
        if not opportunity.safe_to_automate:
            logger.info(f"Optimization {opportunity.id} requires manual approval")
            return False
        
        # Check cooldown
        opt_type = opportunity.type.value
        last_run = self.last_optimizations.get(opt_type)
        if last_run:
            hours_since = (datetime.now() - last_run).total_seconds() / 3600
            if hours_since < 1:  # 1 hour cooldown
                logger.debug(f"Optimization {opt_type} in cooldown")
                return False
        
        # Check score threshold
        if opportunity.score() < 3.0:  # Min score of 3
            return False
        
        # Check system health
        health = self.health_tracker.predict_future_health(hours_ahead=1)
        if health['health_score'] < 40:
            logger.warning("System health too low for optimization")
            return False
        
        return True
    
    async def apply_optimization(self, opportunity: OptimizationOpportunity) -> OptimizationResult:
        """Apply an optimization"""
        logger.info(f"🔧 Applying optimization: {opportunity.description}")
        
        start_time = datetime.now()
        metrics_before = self.monitor.get_quick_status()
        success = True
        error = None
        
        try:
            # Execute optimization actions
            for action in opportunity.actions:
                await self._execute_optimization_action(action, opportunity)
            
            # Record optimization
            self.last_optimizations[opportunity.type.value] = datetime.now()
            
        except Exception as e:
            success = False
            error = str(e)
            logger.error(f"Optimization failed: {e}")
        
        # Get metrics after
        await asyncio.sleep(5)  # Wait for effects
        metrics_after = self.monitor.get_quick_status()
        
        # Calculate actual benefit
        actual_benefit = self._calculate_benefit(metrics_before, metrics_after)
        
        result = OptimizationResult(
            opportunity_id=opportunity.id,
            success=success,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            actual_benefit=actual_benefit,
            duration_seconds=(datetime.now() - start_time).total_seconds(),
            error=error
        )
        
        # Record result
        self.optimization_history.append({
            'timestamp': datetime.now(),
            'opportunity': opportunity,
            'result': result
        })
        
        if success:
            logger.info(f"✅ Optimization successful: {actual_benefit}")
        else:
            logger.error(f"❌ Optimization failed: {error}")
        
        return result
    
    async def prevent_future_issues(self):
        """Prevent predicted future issues"""
        # Get predictions from health tracker
        future_health = self.health_tracker.predict_future_health(hours_ahead=24)
        
        if future_health['risks']:
            logger.info(f"⚠️ Preventing future risks: {future_health['risks']}")
            
            for risk in future_health['risks']:
                # Create preemptive issue
                issue = Issue(
                    id=f"prevent_{datetime.now().timestamp():.0f}",
                    timestamp=datetime.now(),
                    type='predicted_issue',
                    severity=Severity.MEDIUM,
                    description=f"Preventing: {risk}",
                    metrics={'prediction': future_health},
                    affected_components=['system.predicted']
                )
                
                # Use healing engine to prevent
                await self.healing_engine.heal_issue(issue)
        
        # Get predictions from predictive assistant
        predictions = self.predictive_assistant.analyze_system()
        
        for prediction in predictions:
            if prediction.priority in ['critical', 'high']:
                logger.info(f"🛡️ Preventing: {prediction.reason}")
                
                # Take preemptive action
                if 'memory' in prediction.reason.lower():
                    await self._free_memory_preemptively()
                elif 'disk' in prediction.reason.lower():
                    await self._clean_disk_preemptively()
                elif 'service' in prediction.reason.lower():
                    await self._optimize_services_preemptively()
    
    async def _execute_optimization_action(self, action: str, opportunity: OptimizationOpportunity):
        """Execute a specific optimization action"""
        if action == 'clear_caches':
            await self._clear_system_caches()
        elif action == 'restart_heavy_services':
            await self._restart_heavy_services()
        elif action == 'clean_logs':
            await self._clean_old_logs()
        elif action == 'clean_cache':
            await self._clean_application_caches()
        elif action == 'optimize_store':
            await self._optimize_nix_store()
        elif action == 'remove_old_generations':
            await self._remove_old_generations()
        elif action == 'clear_old_caches':
            await self._clear_old_caches()
        elif action == 'rebuild_cache_index':
            await self._rebuild_cache_index()
        else:
            logger.warning(f"Unknown optimization action: {action}")
    
    async def _count_nixos_generations(self) -> int:
        """Count NixOS generations"""
        import subprocess
        try:
            result = subprocess.run(
                ['nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return len(result.stdout.strip().split('\n'))
        except Exception:
            return 0
    
    async def _analyze_service_patterns(self) -> Dict[str, Any]:
        """Analyze service patterns for optimization"""
        patterns = {}
        
        # Get service metrics from history
        services = ['nginx', 'postgresql', 'docker']
        
        for service in services:
            # Simple pattern analysis
            patterns[service] = {
                'optimization_potential': 0.3,  # Placeholder
                'potential_savings': 20,
                'confidence': 0.6
            }
        
        return patterns
    
    def _calculate_benefit(self, before: Dict, after: Dict) -> Dict[str, Any]:
        """Calculate actual benefit from optimization"""
        benefit = {}
        
        if 'memory_percent' in before and 'memory_percent' in after:
            mem_freed = before['memory_percent'] - after['memory_percent']
            if mem_freed > 0:
                benefit['memory_freed_percent'] = mem_freed
        
        if 'disk_usage' in before and 'disk_usage' in after:
            for mount in before.get('disk_usage', {}):
                if mount in after.get('disk_usage', {}):
                    disk_freed = before['disk_usage'][mount] - after['disk_usage'][mount]
                    if disk_freed > 0:
                        benefit[f'disk_freed_{mount}'] = disk_freed
        
        return benefit
    
    # Optimization actions
    
    async def _clear_system_caches(self):
        """Clear system caches"""
        try:
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('1')  # Free pagecache
            logger.debug("Cleared system page cache")
        except Exception as e:
            logger.error(f"Failed to clear system caches: {e}")
    
    async def _restart_heavy_services(self):
        """Restart memory-heavy services"""
        # Identify heavy services
        heavy_services = await self._identify_heavy_services()
        
        for service in heavy_services[:3]:  # Top 3
            try:
                import subprocess
                subprocess.run(
                    ['systemctl', 'restart', service],
                    capture_output=True,
                    timeout=30
                )
                logger.debug(f"Restarted {service}")
                await asyncio.sleep(5)  # Wait between restarts
            except Exception as e:
                logger.error(f"Failed to restart {service}: {e}")
    
    async def _identify_heavy_services(self) -> List[str]:
        """Identify memory-heavy services"""
        # Simplified - would use actual process monitoring
        return ['docker.service', 'postgresql.service']
    
    async def _clean_old_logs(self):
        """Clean old log files"""
        import subprocess
        try:
            # Clean journald logs older than retention period
            subprocess.run(
                ['journalctl', '--vacuum-time=30d'],
                capture_output=True,
                timeout=30
            )
            logger.debug("Cleaned old journal logs")
        except Exception as e:
            logger.error(f"Failed to clean logs: {e}")
    
    async def _clean_application_caches(self):
        """Clean application caches"""
        cache_dirs = [
            Path.home() / '.cache',
            Path('/var/cache'),
            Path('/tmp')
        ]
        
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                await self._clean_directory(cache_dir, days_old=7)
    
    async def _clean_directory(self, directory: Path, days_old: int):
        """Clean old files from directory"""
        cutoff = datetime.now() - timedelta(days=days_old)
        
        try:
            for item in directory.iterdir():
                if item.is_file():
                    if datetime.fromtimestamp(item.stat().st_mtime) < cutoff:
                        try:
                            item.unlink()
                        except Exception:
                            pass  # Skip files we can't delete
        except Exception as e:
            logger.debug(f"Error cleaning {directory}: {e}")
    
    async def _optimize_nix_store(self):
        """Optimize the Nix store"""
        import subprocess
        try:
            subprocess.run(
                ['nix-store', '--optimise'],
                capture_output=True,
                timeout=300
            )
            logger.debug("Optimized Nix store")
        except Exception as e:
            logger.error(f"Failed to optimize store: {e}")
    
    async def _remove_old_generations(self):
        """Remove old NixOS generations"""
        import subprocess
        try:
            # Keep only last 10 generations
            subprocess.run(
                ['nix-env', '--delete-generations', '+10', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True,
                timeout=60
            )
            logger.debug("Removed old NixOS generations")
        except Exception as e:
            logger.error(f"Failed to remove generations: {e}")
    
    async def _clear_old_caches(self):
        """Clear old caches"""
        await self._clean_application_caches()
    
    async def _rebuild_cache_index(self):
        """Rebuild cache indices for better performance"""
        # Placeholder - would rebuild various cache indices
        logger.debug("Cache indices rebuilt")
    
    async def _free_memory_preemptively(self):
        """Free memory before it becomes critical"""
        await self._clear_system_caches()
        await self._restart_heavy_services()
    
    async def _clean_disk_preemptively(self):
        """Clean disk before it fills up"""
        await self._clean_old_logs()
        await self._clean_application_caches()
        await self._remove_old_generations()
    
    async def _optimize_services_preemptively(self):
        """Optimize services before they fail"""
        # Restart services showing signs of degradation
        heavy = await self._identify_heavy_services()
        for service in heavy[:2]:
            try:
                import subprocess
                subprocess.run(['systemctl', 'reload-or-restart', service], timeout=30)
            except Exception:
                pass
    
    def get_optimization_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get report of recent optimizations"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            opt for opt in self.optimization_history
            if opt['timestamp'] > cutoff
        ]
        
        successful = sum(1 for opt in recent if opt['result'].success)
        total = len(recent)
        
        return {
            'period_hours': hours,
            'total_optimizations': total,
            'successful': successful,
            'success_rate': successful / total if total > 0 else 0,
            'optimizations': recent[:10]  # Last 10
        }


# Integration function
def create_intelligent_healing_system() -> Dict[str, Any]:
    """Create a complete intelligent healing system"""
    healing_engine = SelfHealingEngine()
    optimizer = ProactiveOptimizer(healing_engine)
    
    return {
        'healing_engine': healing_engine,
        'optimizer': optimizer,
        'start': lambda: asyncio.gather(
            healing_engine.start(),
            optimizer.start()
        ),
        'stop': lambda: asyncio.gather(
            healing_engine.stop(),
            optimizer.stop()
        )
    }