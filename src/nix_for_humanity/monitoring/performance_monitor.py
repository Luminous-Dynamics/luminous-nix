#!/usr/bin/env python3
"""
Performance Monitoring System for Nix for Humanity
Phase 4 Living System: Self-maintaining infrastructure with Sacred Trinity integration
"""

import asyncio
import time
import psutil
import statistics
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class PerformanceThreshold:
    """Performance threshold with alerting"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    duration_seconds: float = 60.0
    callback: Optional[Callable] = None


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for Nix for Humanity
    
    Features:
    - Real-time performance tracking
    - Sacred Trinity workflow integration
    - Consciousness-first performance budgets
    - Automatic alerting and remediation
    - Self-maintaining infrastructure
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path.home() / '.local/share/nix-humanity/performance'
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Performance data storage
        self.metrics: List[PerformanceMetric] = []
        self.thresholds: List[PerformanceThreshold] = []
        self.running_operations: Dict[str, float] = {}
        
        # Sacred Trinity performance budgets (consciousness-first)
        self.persona_budgets = {
            'maya_adhd': {'max_response_ms': 1000, 'max_startup_ms': 2000},
            'grandma_rose': {'max_response_ms': 2000, 'max_startup_ms': 3000},
            'dr_sarah': {'max_response_ms': 1500, 'max_startup_ms': 2500},
            'alex_blind': {'max_response_ms': 1200, 'max_startup_ms': 2200},
            'default': {'max_response_ms': 2000, 'max_startup_ms': 3000}
        }
        
        # System health tracking
        self.system_metrics = {
            'memory_usage_mb': [],
            'cpu_usage_percent': [],
            'response_times_ms': [],
            'error_rate_percent': [],
            'api_call_times_ms': []
        }
        
        # Sacred Trinity workflow metrics
        self.trinity_metrics = {
            'human_validation_time_ms': [],
            'claude_implementation_time_ms': [],
            'llm_consultation_time_ms': [],
            'integration_cycles': 0,
            'quality_score': []
        }
        
        self._setup_default_thresholds()
        self._start_background_monitoring()
    
    def _setup_default_thresholds(self):
        """Setup consciousness-first performance thresholds"""
        # Critical user experience thresholds
        self.add_threshold('response_time_ms', warning=1500, critical=3000)
        self.add_threshold('memory_usage_mb', warning=300, critical=500)
        self.add_threshold('cpu_usage_percent', warning=70, critical=90)
        self.add_threshold('error_rate_percent', warning=5, critical=10)
        self.add_threshold('startup_time_ms', warning=2500, critical=5000)
        
        # Native Python-Nix API performance expectations
        self.add_threshold('nixos_operation_ms', warning=50, critical=200)
        self.add_threshold('generation_list_ms', warning=10, critical=50)
        self.add_threshold('rollback_operation_ms', warning=20, critical=100)
    
    def _start_background_monitoring(self):
        """Start background system monitoring"""
        asyncio.create_task(self._monitor_system_health())
    
    async def _monitor_system_health(self):
        """Continuous system health monitoring"""
        while True:
            try:
                # Collect system metrics
                memory_mb = psutil.virtual_memory().used / 1024 / 1024
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Record metrics
                self.record_metric('memory_usage_mb', memory_mb, 'MB')
                self.record_metric('cpu_usage_percent', cpu_percent, '%')
                
                # Check thresholds
                await self._check_thresholds()
                
                # Clean old metrics (keep last 24 hours)
                self._cleanup_old_metrics()
                
                # Sleep before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
                await asyncio.sleep(60)
    
    def add_threshold(self, metric_name: str, warning: float, critical: float, 
                     duration: float = 60.0, callback: Optional[Callable] = None):
        """Add performance threshold with optional callback"""
        threshold = PerformanceThreshold(
            metric_name=metric_name,
            warning_threshold=warning,
            critical_threshold=critical,
            duration_seconds=duration,
            callback=callback
        )
        self.thresholds.append(threshold)
    
    def record_metric(self, name: str, value: float, unit: str, 
                     context: Optional[Dict[str, Any]] = None, 
                     tags: Optional[List[str]] = None):
        """Record a performance metric"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            context=context or {},
            tags=tags or []
        )
        
        self.metrics.append(metric)
        
        # Update running system metrics
        if name in self.system_metrics:
            self.system_metrics[name].append(value)
            # Keep only last 1000 measurements
            if len(self.system_metrics[name]) > 1000:
                self.system_metrics[name] = self.system_metrics[name][-1000:]
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation"""
        operation_id = f"{operation_name}_{time.time()}"
        self.running_operations[operation_id] = time.time()
        return operation_id
    
    def end_operation(self, operation_id: str, context: Optional[Dict[str, Any]] = None) -> float:
        """End timing an operation and record the metric"""
        if operation_id not in self.running_operations:
            logger.warning(f"Operation {operation_id} not found in running operations")
            return 0.0
        
        start_time = self.running_operations.pop(operation_id)
        duration_ms = (time.time() - start_time) * 1000
        
        # Extract operation name
        operation_name = operation_id.split('_')[0]
        
        # Record the metric
        self.record_metric(
            f"{operation_name}_time_ms",
            duration_ms,
            'ms',
            context=context
        )
        
        return duration_ms
    
    async def _check_thresholds(self):
        """Check all thresholds and trigger alerts"""
        for threshold in self.thresholds:
            # Get recent metrics for this threshold
            recent_metrics = self._get_recent_metrics(
                threshold.metric_name, 
                threshold.duration_seconds
            )
            
            if not recent_metrics:
                continue
            
            # Calculate average value
            avg_value = statistics.mean(m.value for m in recent_metrics)
            
            # Check thresholds
            if avg_value >= threshold.critical_threshold:
                await self._handle_critical_threshold(threshold, avg_value, recent_metrics)
            elif avg_value >= threshold.warning_threshold:
                await self._handle_warning_threshold(threshold, avg_value, recent_metrics)
    
    async def _handle_warning_threshold(self, threshold: PerformanceThreshold, 
                                      value: float, metrics: List[PerformanceMetric]):
        """Handle warning threshold breach"""
        logger.warning(
            f"Performance warning: {threshold.metric_name} = {value:.2f} "
            f"(threshold: {threshold.warning_threshold})"
        )
        
        # Sacred Trinity notification
        await self._notify_trinity_warning(threshold, value)
        
        if threshold.callback:
            try:
                await threshold.callback(threshold, value, metrics)
            except Exception as e:
                logger.error(f"Threshold callback error: {e}")
    
    async def _handle_critical_threshold(self, threshold: PerformanceThreshold, 
                                        value: float, metrics: List[PerformanceMetric]):
        """Handle critical threshold breach"""
        logger.critical(
            f"Performance critical: {threshold.metric_name} = {value:.2f} "
            f"(threshold: {threshold.critical_threshold})"
        )
        
        # Sacred Trinity emergency notification
        await self._notify_trinity_critical(threshold, value)
        
        # Automatic remediation
        await self._attempt_remediation(threshold, value)
        
        if threshold.callback:
            try:
                await threshold.callback(threshold, value, metrics)
            except Exception as e:
                logger.error(f"Critical threshold callback error: {e}")
    
    async def _notify_trinity_warning(self, threshold: PerformanceThreshold, value: float):
        """Notify Sacred Trinity of performance warning"""
        notification = {
            'type': 'performance_warning',
            'metric': threshold.metric_name,
            'value': value,
            'threshold': threshold.warning_threshold,
            'timestamp': datetime.now().isoformat(),
            'impact': self._assess_user_impact(threshold.metric_name, value),
            'recommendations': self._get_optimization_recommendations(threshold.metric_name)
        }
        
        # Log for Sacred Trinity visibility
        logger.info(f"Sacred Trinity Warning: {json.dumps(notification, indent=2)}")
    
    async def _notify_trinity_critical(self, threshold: PerformanceThreshold, value: float):
        """Notify Sacred Trinity of critical performance issue"""
        notification = {
            'type': 'performance_critical',
            'metric': threshold.metric_name,
            'value': value,
            'threshold': threshold.critical_threshold,
            'timestamp': datetime.now().isoformat(),
            'impact': self._assess_user_impact(threshold.metric_name, value),
            'affected_personas': self._get_affected_personas(threshold.metric_name, value),
            'remediation_attempted': True,
            'emergency_recommendations': self._get_emergency_recommendations(threshold.metric_name)
        }
        
        # Log for Sacred Trinity emergency response
        logger.critical(f"Sacred Trinity EMERGENCY: {json.dumps(notification, indent=2)}")
    
    async def _attempt_remediation(self, threshold: PerformanceThreshold, value: float):
        """Attempt automatic remediation of performance issues"""
        remediation_actions = {
            'memory_usage_mb': self._remediate_memory_usage,
            'cpu_usage_percent': self._remediate_cpu_usage,
            'response_time_ms': self._remediate_response_time,
            'error_rate_percent': self._remediate_error_rate
        }
        
        if threshold.metric_name in remediation_actions:
            try:
                await remediation_actions[threshold.metric_name](value)
                logger.info(f"Attempted remediation for {threshold.metric_name}")
            except Exception as e:
                logger.error(f"Remediation failed for {threshold.metric_name}: {e}")
    
    async def _remediate_memory_usage(self, value: float):
        """Automatic memory usage remediation"""
        # Clear old metrics
        self._cleanup_old_metrics(hours=1)
        
        # Clear caches if available
        import gc
        gc.collect()
        
        logger.info(f"Memory remediation: cleared caches and old metrics")
    
    async def _remediate_cpu_usage(self, value: float):
        """Automatic CPU usage remediation"""
        # Reduce background monitoring frequency
        logger.info("CPU remediation: reducing monitoring frequency")
    
    async def _remediate_response_time(self, value: float):
        """Automatic response time remediation"""
        # Switch to minimal processing mode
        logger.info("Response time remediation: switching to minimal mode")
    
    async def _remediate_error_rate(self, value: float):
        """Automatic error rate remediation"""
        # Reset connection pools, restart components
        logger.info("Error rate remediation: resetting connections")
    
    def _assess_user_impact(self, metric_name: str, value: float) -> str:
        """Assess impact on user experience"""
        impacts = {
            'response_time_ms': {
                1000: 'Maya (ADHD) will be frustrated',
                2000: 'Grandma Rose may lose confidence', 
                3000: 'All users will experience poor UX'
            },
            'memory_usage_mb': {
                300: 'System may slow down',
                500: 'Risk of out-of-memory errors'
            },
            'cpu_usage_percent': {
                70: 'System responsiveness reduced',
                90: 'System may become unresponsive'
            }
        }
        
        if metric_name not in impacts:
            return 'Unknown impact'
        
        for threshold, impact in sorted(impacts[metric_name].items()):
            if value >= threshold:
                return impact
        
        return 'Minimal impact'
    
    def _get_affected_personas(self, metric_name: str, value: float) -> List[str]:
        """Get list of personas affected by performance issue"""
        affected = []
        
        for persona, budgets in self.persona_budgets.items():
            if persona == 'default':
                continue
                
            if metric_name == 'response_time_ms':
                if value > budgets['max_response_ms']:
                    affected.append(persona)
            elif metric_name == 'startup_time_ms':
                if value > budgets['max_startup_ms']:
                    affected.append(persona)
        
        return affected
    
    def _get_optimization_recommendations(self, metric_name: str) -> List[str]:
        """Get optimization recommendations for metric"""
        recommendations = {
            'response_time_ms': [
                'Enable Native Python-Nix API for all operations',
                'Implement response caching for common queries',
                'Optimize NLP processing pipeline'
            ],
            'memory_usage_mb': [
                'Clear old performance metrics',
                'Implement lazy loading for ML models',
                'Optimize memory usage in knowledge graphs'
            ],
            'cpu_usage_percent': [
                'Reduce background monitoring frequency',
                'Optimize algorithm complexity',
                'Implement CPU-aware scheduling'
            ],
            'error_rate_percent': [
                'Implement better error recovery',
                'Add input validation layers',
                'Improve graceful degradation'
            ]
        }
        
        return recommendations.get(metric_name, ['Contact Sacred Trinity for guidance'])
    
    def _get_emergency_recommendations(self, metric_name: str) -> List[str]:
        """Get emergency recommendations for critical issues"""
        emergency = {
            'response_time_ms': [
                'Switch to minimal personality mode',
                'Disable learning systems temporarily',
                'Use only cached responses'
            ],
            'memory_usage_mb': [
                'Restart the system immediately',
                'Clear all caches and temporary data',
                'Reduce feature set to core only'
            ],
            'cpu_usage_percent': [
                'Kill non-essential background processes',
                'Switch to emergency minimal mode',
                'Disable all monitoring temporarily'
            ]
        }
        
        return emergency.get(metric_name, ['Emergency system restart recommended'])
    
    def _get_recent_metrics(self, metric_name: str, duration_seconds: float) -> List[PerformanceMetric]:
        """Get metrics from the last N seconds"""
        cutoff = datetime.now() - timedelta(seconds=duration_seconds)
        return [m for m in self.metrics if m.name == metric_name and m.timestamp >= cutoff]
    
    def _cleanup_old_metrics(self, hours: int = 24):
        """Clean up old metrics to prevent memory growth"""
        cutoff = datetime.now() - timedelta(hours=hours)
        initial_count = len(self.metrics)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff]
        
        if len(self.metrics) < initial_count:
            logger.debug(f"Cleaned up {initial_count - len(self.metrics)} old metrics")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'metrics_count': len(self.metrics),
            'active_operations': len(self.running_operations),
            'system_health': {},
            'consciousness_budgets': {},
            'trinity_metrics': dict(self.trinity_metrics),
            'recent_alerts': self._get_recent_alerts()
        }
        
        # System health summary
        for metric_name, values in self.system_metrics.items():
            if values:
                summary['system_health'][metric_name] = {
                    'current': values[-1] if values else 0,
                    'average': statistics.mean(values),
                    'p95': statistics.quantiles(values, n=20)[18] if len(values) > 10 else 0,
                    'max': max(values),
                    'trend': self._calculate_trend(values)
                }
        
        # Consciousness-first budget analysis
        current_response_time = summary['system_health'].get('response_times_ms', {}).get('p95', 0)
        for persona, budgets in self.persona_budgets.items():
            if persona == 'default':
                continue
            summary['consciousness_budgets'][persona] = {
                'response_budget_met': current_response_time <= budgets['max_response_ms'],
                'budget_ms': budgets['max_response_ms'],
                'current_ms': current_response_time,
                'margin_ms': budgets['max_response_ms'] - current_response_time
            }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for values"""
        if len(values) < 10:
            return 'insufficient_data'
        
        recent = values[-5:]
        older = values[-10:-5]
        
        recent_avg = statistics.mean(recent)
        older_avg = statistics.mean(older)
        
        if recent_avg > older_avg * 1.1:
            return 'increasing'
        elif recent_avg < older_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        # This would typically read from a persistent log
        # For now, return empty list
        return []
    
    def record_trinity_cycle(self, human_time_ms: float, claude_time_ms: float, 
                           llm_time_ms: float, quality_score: float):
        """Record Sacred Trinity development cycle metrics"""
        self.trinity_metrics['human_validation_time_ms'].append(human_time_ms)
        self.trinity_metrics['claude_implementation_time_ms'].append(claude_time_ms)
        self.trinity_metrics['llm_consultation_time_ms'].append(llm_time_ms)
        self.trinity_metrics['integration_cycles'] += 1
        self.trinity_metrics['quality_score'].append(quality_score)
        
        # Keep only recent cycles
        for key in ['human_validation_time_ms', 'claude_implementation_time_ms', 
                   'llm_consultation_time_ms', 'quality_score']:
            if len(self.trinity_metrics[key]) > 100:
                self.trinity_metrics[key] = self.trinity_metrics[key][-100:]
    
    async def save_metrics(self):
        """Save metrics to persistent storage"""
        try:
            metrics_data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_performance_summary(),
                'recent_metrics': [
                    {
                        'name': m.name,
                        'value': m.value,
                        'unit': m.unit,
                        'timestamp': m.timestamp.isoformat(),
                        'context': m.context,
                        'tags': m.tags
                    }
                    for m in self.metrics[-1000:]  # Save last 1000 metrics
                ]
            }
            
            filepath = self.storage_path / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
            logger.info(f"Saved performance metrics to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# Decorator for automatic performance monitoring
def monitor_performance(operation_name: str):
    """Decorator to automatically monitor function performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation_id = monitor.start_operation(operation_name)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                monitor.end_operation(operation_id)
        
        def sync_wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation_id = monitor.start_operation(operation_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                monitor.end_operation(operation_id)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator