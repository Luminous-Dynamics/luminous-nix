#!/usr/bin/env python3
"""
Simple predictive maintenance using basic time-series analysis.

Following our simplicity principle: Start with the simplest solution that works.
No complex ML models - just trend analysis and pattern recognition.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import statistics
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric measurement"""
    timestamp: datetime
    value: float
    component: str
    metric_type: str  # cpu, memory, disk, etc.


@dataclass 
class Prediction:
    """Prediction of future issue"""
    component: str
    metric_type: str
    current_value: float
    predicted_value: float
    time_to_threshold: Optional[timedelta]
    confidence: float  # 0.0 to 1.0
    recommendation: str
    severity: str  # low, medium, high


class SimplePredictiveEngine:
    """
    Simple predictive maintenance using basic statistics.
    
    Principles:
    - Moving averages for trend detection
    - Linear regression for simple predictions
    - Pattern matching for recurring issues
    - No external ML libraries required
    """
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        self.metrics_history: Dict[str, deque] = {}
        self.pattern_database: Dict[str, List[Dict]] = {}
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
        }
        self.load_patterns()
    
    def record_metric(self, metric: MetricPoint):
        """Record a metric measurement"""
        key = f"{metric.component}_{metric.metric_type}"
        
        if key not in self.metrics_history:
            self.metrics_history[key] = deque(maxlen=self.history_size)
        
        self.metrics_history[key].append(metric)
    
    def calculate_trend(self, component: str, metric_type: str) -> Optional[float]:
        """
        Calculate trend using simple linear regression.
        Returns rate of change per hour.
        """
        key = f"{component}_{metric_type}"
        
        if key not in self.metrics_history:
            return None
        
        history = list(self.metrics_history[key])
        
        if len(history) < 3:  # Need at least 3 points
            return None
        
        # Simple linear regression
        # y = mx + b, we want m (slope)
        
        # Convert timestamps to hours from first measurement
        first_time = history[0].timestamp
        x_values = [(m.timestamp - first_time).total_seconds() / 3600 for m in history]
        y_values = [m.value for m in history]
        
        if max(x_values) - min(x_values) < 0.01:  # Less than 36 seconds of data
            return None
        
        # Calculate slope using least squares
        n = len(x_values)
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator  # Rate of change per hour
        return slope
    
    def predict_time_to_threshold(
        self, 
        component: str, 
        metric_type: str,
        threshold: float
    ) -> Optional[Tuple[timedelta, float]]:
        """
        Predict when metric will reach threshold.
        Returns (time_to_threshold, confidence).
        """
        key = f"{component}_{metric_type}"
        
        if key not in self.metrics_history:
            return None
        
        history = list(self.metrics_history[key])
        if len(history) < 3:
            return None
        
        current_value = history[-1].value
        trend = self.calculate_trend(component, metric_type)
        
        if trend is None or trend <= 0:
            return None  # Not increasing
        
        # Calculate time to reach threshold
        if current_value >= threshold:
            return timedelta(0), 1.0  # Already at threshold
        
        hours_to_threshold = (threshold - current_value) / trend
        
        if hours_to_threshold > 24 * 7:  # More than a week
            return None  # Too far in future
        
        # Calculate confidence based on trend stability
        values = [m.value for m in history[-10:]]  # Last 10 measurements
        if len(values) < 3:
            confidence = 0.5
        else:
            # Use coefficient of variation as stability measure
            mean_val = statistics.mean(values)
            if mean_val > 0:
                cv = statistics.stdev(values) / mean_val
                # Lower CV = more stable = higher confidence
                confidence = max(0.3, min(0.9, 1.0 - cv))
            else:
                confidence = 0.5
        
        return timedelta(hours=hours_to_threshold), confidence
    
    def detect_patterns(self, component: str, metric_type: str) -> List[str]:
        """
        Detect recurring patterns (e.g., daily spikes).
        Returns list of detected patterns.
        """
        key = f"{component}_{metric_type}"
        patterns = []
        
        if key not in self.metrics_history:
            return patterns
        
        history = list(self.metrics_history[key])
        if len(history) < 24:  # Need at least 24 data points
            return patterns
        
        values = [m.value for m in history]
        
        # Check for regular spikes
        high_threshold = statistics.mean(values) + statistics.stdev(values)
        spikes = [i for i, v in enumerate(values) if v > high_threshold]
        
        if len(spikes) >= 3:
            # Check if spikes are regular
            intervals = [spikes[i+1] - spikes[i] for i in range(len(spikes)-1)]
            if intervals:
                avg_interval = statistics.mean(intervals)
                if all(abs(i - avg_interval) < avg_interval * 0.2 for i in intervals):
                    patterns.append(f"Regular spikes every {avg_interval:.1f} measurements")
        
        # Check for gradual increase
        trend = self.calculate_trend(component, metric_type)
        if trend and trend > 0.5:  # Increasing by >0.5 per hour
            patterns.append(f"Gradual increase: {trend:.1f}% per hour")
        
        return patterns
    
    async def analyze(self) -> List[Prediction]:
        """
        Analyze all metrics and generate predictions.
        """
        predictions = []
        
        for key in self.metrics_history:
            parts = key.rsplit('_', 1)
            if len(parts) != 2:
                continue
                
            component, metric_type = parts
            
            # Get threshold for this metric type
            threshold_key = f"{metric_type}_percent"
            if threshold_key not in self.thresholds:
                continue
            
            threshold = self.thresholds[threshold_key]
            
            # Current value
            history = list(self.metrics_history[key])
            if not history:
                continue
            
            current = history[-1].value
            
            # Predict future
            prediction_result = self.predict_time_to_threshold(
                component, metric_type, threshold
            )
            
            if prediction_result:
                time_to_threshold, confidence = prediction_result
                
                # Determine severity
                if time_to_threshold < timedelta(hours=1):
                    severity = "high"
                    recommendation = f"Immediate action needed for {component}"
                elif time_to_threshold < timedelta(hours=6):
                    severity = "medium"  
                    recommendation = f"Plan maintenance for {component} within 6 hours"
                else:
                    severity = "low"
                    recommendation = f"Monitor {component}, issues expected in {time_to_threshold.total_seconds()/3600:.1f} hours"
                
                # Check patterns
                patterns = self.detect_patterns(component, metric_type)
                if patterns:
                    recommendation += f". Patterns: {', '.join(patterns)}"
                
                predictions.append(Prediction(
                    component=component,
                    metric_type=metric_type,
                    current_value=current,
                    predicted_value=threshold,
                    time_to_threshold=time_to_threshold,
                    confidence=confidence,
                    recommendation=recommendation,
                    severity=severity
                ))
        
        # Sort by severity and time
        predictions.sort(
            key=lambda p: (
                {'high': 0, 'medium': 1, 'low': 2}[p.severity],
                p.time_to_threshold.total_seconds() if p.time_to_threshold else float('inf')
            )
        )
        
        return predictions
    
    def learn_pattern(self, issue_type: str, context: Dict[str, Any]):
        """
        Learn from resolved issues to improve predictions.
        Simple pattern storage - no complex ML.
        """
        if issue_type not in self.pattern_database:
            self.pattern_database[issue_type] = []
        
        pattern = {
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'metrics_before': self._get_recent_metrics()
        }
        
        self.pattern_database[issue_type].append(pattern)
        
        # Keep only recent patterns
        if len(self.pattern_database[issue_type]) > 50:
            self.pattern_database[issue_type] = self.pattern_database[issue_type][-50:]
        
        self.save_patterns()
    
    def _get_recent_metrics(self) -> Dict[str, List[float]]:
        """Get recent metrics for pattern learning"""
        recent = {}
        for key, history in self.metrics_history.items():
            if history:
                recent[key] = [m.value for m in list(history)[-10:]]
        return recent
    
    def save_patterns(self):
        """Save learned patterns to disk"""
        pattern_file = Path.home() / '.cache' / 'luminous-nix' / 'predictive_patterns.json'
        pattern_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pattern_file, 'w') as f:
            json.dump(self.pattern_database, f, indent=2, default=str)
    
    def load_patterns(self):
        """Load learned patterns from disk"""
        pattern_file = Path.home() / '.cache' / 'luminous-nix' / 'predictive_patterns.json'
        
        if pattern_file.exists():
            try:
                with open(pattern_file, 'r') as f:
                    self.pattern_database = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load patterns: {e}")
                self.pattern_database = {}
        else:
            self.pattern_database = {}


class PredictiveHealingEngine:
    """
    Combines predictive maintenance with self-healing.
    Prevents issues before they become critical.
    """
    
    def __init__(self, healing_engine=None):
        self.healing_engine = healing_engine
        self.predictor = SimplePredictiveEngine()
        self.monitoring = False
    
    async def monitor_and_predict(self, interval: int = 60):
        """
        Monitor system and make predictions.
        """
        self.monitoring = True
        
        while self.monitoring:
            try:
                # Collect current metrics
                if self.healing_engine:
                    await self._collect_metrics()
                
                # Generate predictions
                predictions = await self.predictor.analyze()
                
                # Log predictions
                for pred in predictions:
                    if pred.severity == "high":
                        logger.warning(f"⚠️  {pred.recommendation}")
                    elif pred.severity == "medium":
                        logger.info(f"📊 {pred.recommendation}")
                    else:
                        logger.debug(f"📈 {pred.recommendation}")
                
                # Take preventive action for high severity
                if self.healing_engine:
                    await self._preventive_healing(predictions)
                
            except Exception as e:
                logger.error(f"Prediction error: {e}")
            
            await asyncio.sleep(interval)
    
    async def _collect_metrics(self):
        """Collect metrics from healing engine"""
        if not self.healing_engine:
            return
        
        # Get current system state
        await self.healing_engine.detector.monitor.update_category('full')
        state = self.healing_engine.detector.monitor.get_state()
        
        # Record metrics
        now = datetime.now()
        
        if 'cpu' in state and hasattr(state['cpu'], 'percent'):
            self.predictor.record_metric(MetricPoint(
                timestamp=now,
                value=state['cpu'].percent,
                component='system',
                metric_type='cpu'
            ))
        
        if 'memory' in state and hasattr(state['memory'], 'percent_used'):
            self.predictor.record_metric(MetricPoint(
                timestamp=now,
                value=state['memory'].percent_used,
                component='system',
                metric_type='memory'
            ))
        
        if 'disk' in state and state['disk']:
            for disk in state['disk']:
                if hasattr(disk, 'percent_used'):
                    self.predictor.record_metric(MetricPoint(
                        timestamp=now,
                        value=disk.percent_used,
                        component='disk',
                        metric_type='disk'
                    ))
    
    async def _preventive_healing(self, predictions: List[Prediction]):
        """Take preventive action for high-risk predictions"""
        for pred in predictions:
            if pred.severity != "high":
                continue
            
            if pred.confidence < 0.7:
                continue  # Not confident enough
            
            # Create preventive action
            if pred.metric_type == "disk" and pred.time_to_threshold < timedelta(hours=2):
                logger.info(f"🔧 Preventive disk cleanup (predicted full in {pred.time_to_threshold})")
                # Trigger disk cleanup before it becomes critical
                action = {
                    'action': 'clean_nix_store',
                    'parameters': {},
                    'preventive': True
                }
                
                if not self.healing_engine.dry_run:
                    from .permission_handler_v2 import execute_healing_action
                    result = await execute_healing_action(action['action'], action['parameters'])
                    
                    # Learn from this
                    self.predictor.learn_pattern('disk_preventive', {
                        'prediction': pred.__dict__,
                        'action_result': result.__dict__ if result else None
                    })


# Convenience function
async def start_predictive_maintenance(healing_engine=None, interval: int = 60):
    """
    Start predictive maintenance monitoring.
    
    Example:
        engine = create_self_healing_engine()
        await start_predictive_maintenance(engine, interval=300)  # Every 5 minutes
    """
    predictive = PredictiveHealingEngine(healing_engine)
    await predictive.monitor_and_predict(interval)


if __name__ == "__main__":
    # Demo/test
    async def demo():
        predictor = SimplePredictiveEngine()
        
        # Simulate increasing disk usage
        base_time = datetime.now()
        for i in range(20):
            predictor.record_metric(MetricPoint(
                timestamp=base_time + timedelta(minutes=i*5),
                value=70 + i * 1.5,  # Increasing by 1.5% every 5 minutes
                component="disk",
                metric_type="disk"
            ))
        
        # Make predictions
        predictions = await predictor.analyze()
        
        print("📊 Predictive Maintenance Demo")
        print("=" * 50)
        
        for pred in predictions:
            print(f"\n🎯 Component: {pred.component}")
            print(f"   Metric: {pred.metric_type}")
            print(f"   Current: {pred.current_value:.1f}%")
            print(f"   Time to threshold: {pred.time_to_threshold}")
            print(f"   Confidence: {pred.confidence:.1%}")
            print(f"   Severity: {pred.severity}")
            print(f"   Recommendation: {pred.recommendation}")
    
    asyncio.run(demo())