"""
Historical trending and analysis for system health.

This module provides long-term system health tracking, pattern analysis,
and predictive maintenance based on historical data.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import statistics

import numpy as np

# Try to import scipy, but make it optional
try:
    from scipy import stats
    from scipy.signal import find_peaks
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("scipy not available - using simplified trend analysis")

logger = logging.getLogger(__name__)


@dataclass
class HealthMetric:
    """Single health metric point"""
    timestamp: datetime
    metric_type: str  # cpu, memory, disk, health_score
    value: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TrendAnalysis:
    """Analysis of a metric trend"""
    metric: str
    period: str  # hourly, daily, weekly
    trend: str  # rising, falling, stable, volatile
    slope: float
    variance: float
    anomalies: List[datetime]
    prediction: Optional[float] = None
    confidence: float = 0.0


@dataclass 
class HealthReport:
    """Comprehensive system health report"""
    period_start: datetime
    period_end: datetime
    average_health: float
    min_health: float
    max_health: float
    stability_score: float  # 0-100, how stable the system has been
    top_issues: List[Dict[str, Any]]
    recommendations: List[str]
    trends: List[TrendAnalysis]


class HistoricalHealthTracker:
    """
    Track and analyze system health over time.
    
    Features:
    - Long-term metric storage
    - Trend analysis and anomaly detection  
    - Predictive maintenance suggestions
    - Health report generation
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / '.local' / 'share' / 'luminous-nix' / 'health_history.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        
        # Thresholds for analysis
        self.thresholds = {
            'cpu_warning': 80,
            'cpu_critical': 90,
            'memory_warning': 80,
            'memory_critical': 90,
            'disk_warning': 85,
            'disk_critical': 95,
            'health_poor': 50,
            'health_fair': 70,
            'health_good': 85
        }
    
    def _init_database(self):
        """Initialize the health history database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Health metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                metadata TEXT
            )
        ''')
        
        # Create indices separately
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON health_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_type ON health_metrics(metric_type)')
        
        # System events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                severity TEXT,
                description TEXT,
                resolved BOOLEAN DEFAULT 0
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_type TEXT NOT NULL,
                predicted_value REAL,
                actual_value REAL,
                confidence REAL,
                horizon_hours INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric_type: str, value: float, metadata: Optional[Dict] = None):
        """Record a health metric"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO health_metrics (metric_type, value, metadata)
            VALUES (?, ?, ?)
        ''', (
            metric_type,
            value,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def record_system_state(self, state: Dict[str, Any]):
        """Record complete system state"""
        # Record individual metrics
        if 'cpu' in state and hasattr(state['cpu'], 'percent'):
            self.record_metric('cpu_percent', state['cpu'].percent)
        
        if 'memory' in state and hasattr(state['memory'], 'percent'):
            self.record_metric('memory_percent', state['memory'].percent)
            self.record_metric('memory_available_gb', state['memory'].available / (1024**3))
        
        if 'disks' in state:
            for disk in state['disks']:
                if hasattr(disk, 'mount_point') and hasattr(disk, 'percent'):
                    self.record_metric(
                        f'disk_{disk.mount_point}_percent',
                        disk.percent,
                        {'mount': disk.mount_point}
                    )
        
        # Calculate and record health score
        health_score = self._calculate_health_score(state)
        self.record_metric('health_score', health_score)
    
    def _calculate_health_score(self, state: Dict[str, Any]) -> float:
        """Calculate overall health score from system state"""
        score = 100.0
        
        # CPU impact
        if 'cpu' in state and hasattr(state['cpu'], 'percent'):
            cpu = state['cpu'].percent
            if cpu > self.thresholds['cpu_critical']:
                score -= 20
            elif cpu > self.thresholds['cpu_warning']:
                score -= 10
        
        # Memory impact  
        if 'memory' in state and hasattr(state['memory'], 'percent'):
            mem = state['memory'].percent
            if mem > self.thresholds['memory_critical']:
                score -= 25
            elif mem > self.thresholds['memory_warning']:
                score -= 15
        
        # Disk impact
        if 'disks' in state:
            for disk in state['disks']:
                if hasattr(disk, 'percent'):
                    if disk.percent > self.thresholds['disk_critical']:
                        score -= 20
                    elif disk.percent > self.thresholds['disk_warning']:
                        score -= 10
        
        # Service impact
        if 'services' in state:
            failed = sum(1 for s in state['services'] 
                        if hasattr(s, 'status') and s.status == 'failed')
            score -= failed * 5
        
        return max(0, min(100, score))
    
    def get_metrics(
        self,
        metric_type: str,
        hours: int = 24,
        resolution: str = 'raw'
    ) -> List[HealthMetric]:
        """Get historical metrics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        query = '''
            SELECT timestamp, metric_type, value, metadata
            FROM health_metrics
            WHERE metric_type = ? AND timestamp > ?
            ORDER BY timestamp
        '''
        
        cursor.execute(query, (metric_type, since))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append(HealthMetric(
                timestamp=datetime.fromisoformat(row[0]),
                metric_type=row[1],
                value=row[2],
                metadata=json.loads(row[3]) if row[3] else None
            ))
        
        conn.close()
        
        # Apply resolution
        if resolution == 'hourly':
            metrics = self._aggregate_metrics(metrics, timedelta(hours=1))
        elif resolution == 'daily':
            metrics = self._aggregate_metrics(metrics, timedelta(days=1))
        
        return metrics
    
    def _aggregate_metrics(
        self,
        metrics: List[HealthMetric],
        interval: timedelta
    ) -> List[HealthMetric]:
        """Aggregate metrics by time interval"""
        if not metrics:
            return []
        
        aggregated = []
        current_bucket = []
        bucket_start = metrics[0].timestamp
        
        for metric in metrics:
            if metric.timestamp - bucket_start < interval:
                current_bucket.append(metric)
            else:
                # Aggregate current bucket
                if current_bucket:
                    avg_value = statistics.mean(m.value for m in current_bucket)
                    aggregated.append(HealthMetric(
                        timestamp=bucket_start,
                        metric_type=current_bucket[0].metric_type,
                        value=avg_value,
                        metadata={'count': len(current_bucket)}
                    ))
                
                # Start new bucket
                current_bucket = [metric]
                bucket_start = metric.timestamp
        
        # Don't forget last bucket
        if current_bucket:
            avg_value = statistics.mean(m.value for m in current_bucket)
            aggregated.append(HealthMetric(
                timestamp=bucket_start,
                metric_type=current_bucket[0].metric_type,
                value=avg_value,
                metadata={'count': len(current_bucket)}
            ))
        
        return aggregated
    
    def analyze_trend(
        self,
        metric_type: str,
        hours: int = 168  # 1 week
    ) -> TrendAnalysis:
        """Analyze trend for a metric"""
        metrics = self.get_metrics(metric_type, hours)
        
        if len(metrics) < 2:
            return TrendAnalysis(
                metric=metric_type,
                period=f"{hours} hours",
                trend="insufficient_data",
                slope=0,
                variance=0,
                anomalies=[]
            )
        
        # Extract values and timestamps
        values = np.array([m.value for m in metrics])
        timestamps = np.array([(m.timestamp - metrics[0].timestamp).total_seconds() 
                               for m in metrics])
        
        # Calculate trend using linear regression
        if SCIPY_AVAILABLE:
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
        else:
            # Simple linear regression without scipy
            n = len(timestamps)
            if n > 0:
                x_mean = np.mean(timestamps)
                y_mean = np.mean(values)
                
                num = np.sum((timestamps - x_mean) * (values - y_mean))
                den = np.sum((timestamps - x_mean) ** 2)
                
                slope = num / den if den != 0 else 0
                intercept = y_mean - slope * x_mean
                
                # Simple r_value approximation
                y_pred = slope * timestamps + intercept
                ss_tot = np.sum((values - y_mean) ** 2)
                ss_res = np.sum((values - y_pred) ** 2)
                r_value = np.sqrt(1 - ss_res/ss_tot) if ss_tot != 0 else 0
            else:
                slope, intercept, r_value = 0, 0, 0
        
        # Determine trend direction
        if abs(slope) < 0.001:
            trend = "stable"
        elif slope > 0:
            trend = "rising"
        else:
            trend = "falling"
        
        # Calculate variance
        variance = np.var(values)
        
        # Detect anomalies (values > 2 std dev from mean)
        mean = np.mean(values)
        std = np.std(values)
        anomalies = []
        for i, value in enumerate(values):
            if abs(value - mean) > 2 * std:
                anomalies.append(metrics[i].timestamp)
        
        # Detect volatility
        if variance > mean * 0.3:  # High variance relative to mean
            trend = "volatile"
        
        # Make prediction for next period
        next_timestamp = timestamps[-1] + (timestamps[-1] - timestamps[0]) / len(timestamps)
        prediction = slope * next_timestamp + intercept
        confidence = abs(r_value)  # Use R-value as confidence
        
        return TrendAnalysis(
            metric=metric_type,
            period=f"{hours} hours",
            trend=trend,
            slope=slope,
            variance=variance,
            anomalies=anomalies,
            prediction=prediction,
            confidence=confidence
        )
    
    def detect_patterns(self, metric_type: str, hours: int = 168) -> Dict[str, Any]:
        """Detect patterns in metric data"""
        metrics = self.get_metrics(metric_type, hours)
        
        if len(metrics) < 24:  # Need at least 24 data points
            return {'patterns': [], 'periodicity': None}
        
        values = np.array([m.value for m in metrics])
        
        patterns = {
            'patterns': [],
            'periodicity': None,
            'peaks': [],
            'troughs': []
        }
        
        # Find peaks and troughs
        if SCIPY_AVAILABLE:
            peaks, peak_props = find_peaks(values, distance=5)
            troughs, trough_props = find_peaks(-values, distance=5)
            
            patterns['peaks'] = [metrics[i].timestamp for i in peaks]
            patterns['troughs'] = [metrics[i].timestamp for i in troughs]
        else:
            # Simple peak detection without scipy
            peaks = []
            troughs = []
            for i in range(1, len(values) - 1):
                if values[i] > values[i-1] and values[i] > values[i+1]:
                    peaks.append(i)
                elif values[i] < values[i-1] and values[i] < values[i+1]:
                    troughs.append(i)
            
            patterns['peaks'] = [metrics[i].timestamp for i in peaks]
            patterns['troughs'] = [metrics[i].timestamp for i in troughs]
        
        # Check for daily patterns (every 24 hours)
        hourly_avg = {}
        for metric in metrics:
            hour = metric.timestamp.hour
            if hour not in hourly_avg:
                hourly_avg[hour] = []
            hourly_avg[hour].append(metric.value)
        
        # Calculate hourly averages
        for hour in hourly_avg:
            hourly_avg[hour] = statistics.mean(hourly_avg[hour])
        
        # Check if there's significant variation by hour
        if hourly_avg:
            hour_values = list(hourly_avg.values())
            if max(hour_values) - min(hour_values) > statistics.mean(hour_values) * 0.2:
                patterns['patterns'].append('daily_cycle')
                patterns['periodicity'] = 24
        
        # Check for weekly patterns
        daily_avg = {}
        for metric in metrics:
            day = metric.timestamp.weekday()
            if day not in daily_avg:
                daily_avg[day] = []
            daily_avg[day].append(metric.value)
        
        for day in daily_avg:
            daily_avg[day] = statistics.mean(daily_avg[day])
        
        if daily_avg:
            day_values = list(daily_avg.values())
            if max(day_values) - min(day_values) > statistics.mean(day_values) * 0.15:
                patterns['patterns'].append('weekly_cycle')
        
        return patterns
    
    def generate_health_report(self, hours: int = 168) -> HealthReport:
        """Generate comprehensive health report"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get health scores
        health_metrics = self.get_metrics('health_score', hours)
        
        if not health_metrics:
            return HealthReport(
                period_start=start_time,
                period_end=end_time,
                average_health=0,
                min_health=0,
                max_health=0,
                stability_score=0,
                top_issues=[],
                recommendations=[],
                trends=[]
            )
        
        health_values = [m.value for m in health_metrics]
        
        # Calculate statistics
        avg_health = statistics.mean(health_values)
        min_health = min(health_values)
        max_health = max(health_values)
        
        # Calculate stability (inverse of variance)
        variance = statistics.variance(health_values) if len(health_values) > 1 else 0
        stability_score = max(0, 100 - variance)
        
        # Analyze trends for key metrics
        trends = []
        for metric in ['cpu_percent', 'memory_percent', 'health_score']:
            trend = self.analyze_trend(metric, hours)
            trends.append(trend)
        
        # Find top issues
        top_issues = self._identify_issues(hours)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(trends, top_issues, avg_health)
        
        return HealthReport(
            period_start=start_time,
            period_end=end_time,
            average_health=avg_health,
            min_health=min_health,
            max_health=max_health,
            stability_score=stability_score,
            top_issues=top_issues,
            recommendations=recommendations,
            trends=trends
        )
    
    def _identify_issues(self, hours: int) -> List[Dict[str, Any]]:
        """Identify top system issues"""
        issues = []
        
        # Check CPU issues
        cpu_metrics = self.get_metrics('cpu_percent', hours)
        if cpu_metrics:
            high_cpu_count = sum(1 for m in cpu_metrics if m.value > self.thresholds['cpu_warning'])
            if high_cpu_count > len(cpu_metrics) * 0.2:
                issues.append({
                    'type': 'cpu',
                    'severity': 'warning',
                    'frequency': high_cpu_count / len(cpu_metrics),
                    'description': f'High CPU usage {high_cpu_count} times'
                })
        
        # Check memory issues
        mem_metrics = self.get_metrics('memory_percent', hours)
        if mem_metrics:
            high_mem_count = sum(1 for m in mem_metrics if m.value > self.thresholds['memory_warning'])
            if high_mem_count > len(mem_metrics) * 0.2:
                issues.append({
                    'type': 'memory',
                    'severity': 'warning',
                    'frequency': high_mem_count / len(mem_metrics),
                    'description': f'High memory usage {high_mem_count} times'
                })
        
        # Sort by frequency
        issues.sort(key=lambda x: x['frequency'], reverse=True)
        
        return issues[:5]  # Top 5 issues
    
    def _generate_recommendations(
        self,
        trends: List[TrendAnalysis],
        issues: List[Dict],
        avg_health: float
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check trends
        for trend in trends:
            if trend.trend == "rising" and 'memory' in trend.metric:
                recommendations.append("Memory usage is trending upward. Consider investigating memory leaks.")
            elif trend.trend == "volatile" and 'cpu' in trend.metric:
                recommendations.append("CPU usage is volatile. Check for runaway processes.")
        
        # Check health score
        if avg_health < self.thresholds['health_poor']:
            recommendations.append("System health is poor. Immediate maintenance recommended.")
        elif avg_health < self.thresholds['health_fair']:
            recommendations.append("System health is fair. Schedule maintenance soon.")
        
        # Check specific issues
        for issue in issues:
            if issue['type'] == 'cpu' and issue['frequency'] > 0.5:
                recommendations.append("Frequent high CPU usage. Consider upgrading hardware or optimizing workloads.")
            elif issue['type'] == 'memory' and issue['frequency'] > 0.5:
                recommendations.append("Frequent high memory usage. Add more RAM or optimize applications.")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def predict_future_health(self, hours_ahead: int = 24) -> Dict[str, Any]:
        """Predict future system health"""
        # Analyze recent trends
        health_trend = self.analyze_trend('health_score', hours=168)
        cpu_trend = self.analyze_trend('cpu_percent', hours=168)
        memory_trend = self.analyze_trend('memory_percent', hours=168)
        
        predictions = {
            'timestamp': datetime.now() + timedelta(hours=hours_ahead),
            'health_score': health_trend.prediction if health_trend.prediction else 75,
            'confidence': health_trend.confidence,
            'risks': []
        }
        
        # Check for risks
        if cpu_trend.prediction and cpu_trend.prediction > self.thresholds['cpu_warning']:
            predictions['risks'].append(f"CPU likely to exceed {self.thresholds['cpu_warning']}%")
        
        if memory_trend.prediction and memory_trend.prediction > self.thresholds['memory_warning']:
            predictions['risks'].append(f"Memory likely to exceed {self.thresholds['memory_warning']}%")
        
        if health_trend.prediction and health_trend.prediction < self.thresholds['health_poor']:
            predictions['risks'].append("System health likely to become critical")
        
        return predictions


# Integration function
def integrate_historical_tracking(system_monitor):
    """Integrate historical tracking with system monitor"""
    tracker = HistoricalHealthTracker()
    
    # Add recording method
    def record_state():
        state = system_monitor.get_state()
        if state:
            tracker.record_system_state(state)
    
    # Schedule periodic recording
    import threading
    def record_periodically():
        while True:
            try:
                record_state()
            except Exception as e:
                logger.error(f"Error recording health: {e}")
            
            # Record every 5 minutes
            threading.Event().wait(300)
    
    # Start background thread
    thread = threading.Thread(target=record_periodically, daemon=True)
    thread.start()
    
    # Add tracker to monitor
    system_monitor.health_tracker = tracker
    
    logger.info("✅ Historical health tracking enabled")
    
    return tracker