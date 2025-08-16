"""
Enhanced NixOS service layer with environmental awareness.

This integrates the system monitoring, predictive assistance, and
context-aware intent recognition into the main service layer.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Tuple

from .service_simple import LuminousNixService as NixService
from .environmental import (
    SystemMonitor,
    get_system_monitor,
    PredictiveAssistant,
    ContextAwareIntentRecognizer,
    process_query_with_context
)

logger = logging.getLogger(__name__)


class AwareNixService(NixService):
    """NixOS service with environmental awareness and intelligence"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize environmental awareness
        self.monitor = get_system_monitor()
        self.assistant = PredictiveAssistant(self.monitor)
        self.intent_recognizer = ContextAwareIntentRecognizer(self.monitor)
        
        # Start monitoring in background
        self._monitoring_task = None
        self._start_monitoring()
    
    def _start_monitoring(self):
        """Start background monitoring"""
        loop = asyncio.new_event_loop()
        self._monitoring_task = loop.create_task(self.monitor.start_monitoring())
    
    async def process_natural_language(self, query: str) -> Dict[str, Any]:
        """Process natural language with context awareness"""
        # Get context-aware intent
        intent, explanation = process_query_with_context(query, self.monitor)
        
        # Log for pattern learning
        self.assistant.pattern_db.record_action(
            action_type=intent.intent_type.value,
            command=query,
            context={'confidence': intent.confidence}
        )
        
        # Build response
        response = {
            'intent': intent.intent_type.value,
            'confidence': intent.confidence,
            'explanation': explanation,
            'entities': intent.entities,
            'context': intent.context,
            'suggestions': intent.suggestions,
            'warnings': intent.warnings
        }
        
        # Add system status if relevant
        if intent.intent_type.value in ['diagnose', 'check_status', 'fix_problem']:
            response['system_status'] = self.monitor.get_quick_status()
        
        # Get predictions if helpful
        if intent.intent_type.value in ['diagnose', 'speed_up', 'free_resources']:
            predictions = self.assistant.analyze_system()
            response['predictions'] = [
                {
                    'action': p.action,
                    'reason': p.reason,
                    'confidence': p.confidence,
                    'priority': p.priority
                }
                for p in predictions[:3]
            ]
        
        # Execute the actual command based on intent
        result = await self._execute_intent(intent)
        response['result'] = result
        
        return response
    
    async def _execute_intent(self, intent) -> Dict[str, Any]:
        """Execute the recognized intent"""
        result = {'success': False, 'message': ''}
        
        try:
            if intent.intent_type.value == 'install':
                target = intent.entities.get('target')
                if target:
                    packages = await self.search_packages(target)
                    if packages:
                        result = {
                            'success': True,
                            'action': 'install',
                            'packages': packages[:5],
                            'command': f'nix-env -iA nixos.{packages[0]["name"]}'
                        }
            
            elif intent.intent_type.value == 'search':
                target = intent.entities.get('target')
                if target:
                    packages = await self.search_packages(target)
                    result = {
                        'success': True,
                        'action': 'search',
                        'packages': packages[:10]
                    }
            
            elif intent.intent_type.value == 'garbage_collect':
                result = {
                    'success': True,
                    'action': 'garbage_collect',
                    'command': 'nix-collect-garbage -d',
                    'estimated_space': self._estimate_gc_space()
                }
            
            elif intent.intent_type.value == 'diagnose':
                # Run diagnostics
                diagnostics = await self._run_diagnostics()
                result = {
                    'success': True,
                    'action': 'diagnose',
                    'diagnostics': diagnostics
                }
            
            elif intent.intent_type.value == 'check_status':
                status = self.monitor.get_quick_status()
                result = {
                    'success': True,
                    'action': 'status',
                    'status': status
                }
            
            elif intent.intent_type.value == 'speed_up':
                suggestions = await self._get_optimization_suggestions()
                result = {
                    'success': True,
                    'action': 'optimize',
                    'suggestions': suggestions
                }
            
            elif intent.intent_type.value == 'free_resources':
                actions = await self._get_resource_freeing_actions()
                result = {
                    'success': True,
                    'action': 'free_resources',
                    'actions': actions
                }
            
            else:
                # Fall back to base service
                result = await super().process_natural_language(intent.entities.get('query', ''))
        
        except Exception as e:
            logger.error(f"Error executing intent: {e}")
            result = {
                'success': False,
                'error': str(e)
            }
        
        return result
    
    async def _run_diagnostics(self) -> Dict[str, Any]:
        """Run system diagnostics"""
        state = self.monitor.get_state()
        status = self.monitor.get_quick_status()
        predictions = self.assistant.analyze_system()
        
        diagnostics = {
            'health_score': self._calculate_health_score(state, status),
            'issues': [],
            'recommendations': []
        }
        
        # Check for issues
        if status['memory_percent'] > 80:
            diagnostics['issues'].append({
                'type': 'memory',
                'severity': 'high' if status['memory_percent'] > 90 else 'medium',
                'description': f"Memory usage at {status['memory_percent']:.1f}%"
            })
        
        if status['cpu_percent'] > 80:
            diagnostics['issues'].append({
                'type': 'cpu',
                'severity': 'medium',
                'description': f"CPU usage at {status['cpu_percent']:.1f}%"
            })
        
        for mount, percent in status.get('disk_usage', {}).items():
            if percent > 90:
                diagnostics['issues'].append({
                    'type': 'disk',
                    'severity': 'high',
                    'description': f"Disk {mount} at {percent:.1f}% capacity"
                })
        
        # Add recommendations from predictions
        for pred in predictions[:3]:
            diagnostics['recommendations'].append({
                'action': pred.action,
                'reason': pred.reason,
                'priority': pred.priority
            })
        
        return diagnostics
    
    def _calculate_health_score(self, state: Dict, status: Dict) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # Deduct for resource usage
        score -= min((status.get('memory_percent', 0) - 70) * 2, 20) if status.get('memory_percent', 0) > 70 else 0
        score -= min((status.get('cpu_percent', 0) - 70) * 1, 10) if status.get('cpu_percent', 0) > 70 else 0
        
        # Deduct for disk usage
        for percent in status.get('disk_usage', {}).values():
            if percent > 90:
                score -= 15
            elif percent > 80:
                score -= 5
        
        # Deduct for failed services
        services = state.get('services', [])
        failed = len([s for s in services if hasattr(s, 'status') and s.status == 'failed'])
        score -= failed * 10
        
        return max(0, score)
    
    def _estimate_gc_space(self) -> str:
        """Estimate space that garbage collection would free"""
        try:
            # This is a rough estimate
            nixos = self.monitor.get_state().get('nixos')
            if nixos and nixos.available_generations:
                # Assume each generation takes ~500MB on average
                old_gens = len(nixos.available_generations) - 5  # Keep last 5
                if old_gens > 0:
                    estimated_mb = old_gens * 500
                    return f"~{estimated_mb/1024:.1f}GB"
        except:
            pass
        return "unknown"
    
    async def _get_optimization_suggestions(self) -> List[Dict[str, str]]:
        """Get system optimization suggestions"""
        suggestions = []
        status = self.monitor.get_quick_status()
        
        if status['memory_percent'] > 70:
            suggestions.append({
                'action': 'Restart memory-intensive applications',
                'command': 'systemctl --user restart <service>',
                'impact': 'high'
            })
        
        suggestions.append({
            'action': 'Optimize Nix store',
            'command': 'nix-store --optimise',
            'impact': 'medium'
        })
        
        suggestions.append({
            'action': 'Enable automatic garbage collection',
            'command': 'nix.gc.automatic = true;',
            'impact': 'long-term'
        })
        
        return suggestions
    
    async def _get_resource_freeing_actions(self) -> List[Dict[str, str]]:
        """Get actions to free system resources"""
        actions = []
        status = self.monitor.get_quick_status()
        
        # Memory-specific actions
        if status['memory_percent'] > 70:
            actions.append({
                'action': 'Clear system caches',
                'command': 'sync && echo 3 > /proc/sys/vm/drop_caches',
                'frees': 'memory',
                'requires': 'sudo'
            })
        
        # Disk-specific actions
        for mount, percent in status.get('disk_usage', {}).items():
            if percent > 80:
                if mount == '/':
                    actions.append({
                        'action': 'Clean old generations',
                        'command': 'nix-collect-garbage --delete-older-than 30d',
                        'frees': 'disk space',
                        'estimated': self._estimate_gc_space()
                    })
        
        # General actions
        actions.append({
            'action': 'Clean package cache',
            'command': 'nix-collect-garbage',
            'frees': 'disk space'
        })
        
        return actions
    
    def get_system_insights(self) -> Dict[str, Any]:
        """Get current system insights and predictions"""
        status = self.monitor.get_quick_status()
        predictions = self.assistant.analyze_system()
        
        return {
            'status': status,
            'health_score': self._calculate_health_score(
                self.monitor.get_state(), 
                status
            ),
            'predictions': [
                {
                    'action': p.action,
                    'reason': p.reason,
                    'priority': p.priority,
                    'confidence': p.confidence
                }
                for p in predictions
            ],
            'alerts': self._get_current_alerts(status)
        }
    
    def _get_current_alerts(self, status: Dict) -> List[str]:
        """Get current system alerts"""
        alerts = []
        
        if status['memory_percent'] > 90:
            alerts.append("🚨 Critical memory usage")
        elif status['memory_percent'] > 80:
            alerts.append("⚠️ High memory usage")
        
        if status['cpu_percent'] > 90:
            alerts.append("⚠️ High CPU usage")
        
        for mount, percent in status.get('disk_usage', {}).items():
            if percent > 95:
                alerts.append(f"🚨 Disk {mount} critically full")
            elif percent > 90:
                alerts.append(f"⚠️ Disk {mount} nearly full")
        
        return alerts
    
    def shutdown(self):
        """Clean shutdown"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        # Save state snapshot
        self.monitor.save_snapshot()
        
        logger.info("AwareNixService shutdown complete")


# Convenience function
def create_aware_service() -> AwareNixService:
    """Create an environmentally-aware Nix service"""
    return AwareNixService()