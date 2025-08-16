"""
Predictive assistance based on system state and user patterns.

This module analyzes system state and user behavior to provide
proactive suggestions and prevent problems before they occur.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import psutil

from .system_monitor import SystemMonitor, SystemState

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """A predictive suggestion for the user"""
    action: str
    reason: str
    confidence: float  # 0.0 to 1.0
    priority: str  # low, medium, high, critical
    category: str  # maintenance, performance, security, optimization
    data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserPattern:
    """Observed user behavior pattern"""
    action_type: str
    frequency: int
    last_occurrence: datetime
    time_patterns: List[int]  # Hours of day when typically done
    context: Dict[str, Any]
    
    def is_due(self, current_hour: int) -> bool:
        """Check if action is due based on time patterns"""
        return current_hour in self.time_patterns


class PatternDatabase:
    """Store and analyze user behavior patterns"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / '.local' / 'share' / 'luminous-nix' / 'patterns.db'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the pattern database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY,
                action_type TEXT NOT NULL,
                command TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                hour INTEGER,
                day_of_week INTEGER,
                context TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions_made (
                id INTEGER PRIMARY KEY,
                prediction TEXT NOT NULL,
                confidence REAL,
                was_accepted BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_action(self, action_type: str, command: str, context: Dict[str, Any]):
        """Record a user action"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO user_actions (action_type, command, hour, day_of_week, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            action_type,
            command,
            now.hour,
            now.weekday(),
            json.dumps(context)
        ))
        
        conn.commit()
        conn.close()
    
    def get_patterns(self) -> List[UserPattern]:
        """Analyze recorded actions to find patterns"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Find recurring actions
        cursor.execute('''
            SELECT action_type, COUNT(*) as frequency, MAX(timestamp) as last_time,
                   GROUP_CONCAT(DISTINCT hour) as hours
            FROM user_actions
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY action_type
            HAVING frequency > 2
        ''')
        
        patterns = []
        for row in cursor.fetchall():
            action_type, frequency, last_time, hours = row
            hour_list = [int(h) for h in hours.split(',')] if hours else []
            
            patterns.append(UserPattern(
                action_type=action_type,
                frequency=frequency,
                last_occurrence=datetime.fromisoformat(last_time),
                time_patterns=hour_list,
                context={}
            ))
        
        conn.close()
        return patterns
    
    def record_prediction_result(self, prediction: str, confidence: float, accepted: bool):
        """Record whether a prediction was accepted"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions_made (prediction, confidence, was_accepted)
            VALUES (?, ?, ?)
        ''', (prediction, confidence, accepted))
        
        conn.commit()
        conn.close()
    
    def get_prediction_accuracy(self) -> float:
        """Get the accuracy of predictions"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN was_accepted THEN 1 ELSE 0 END) as accepted
            FROM predictions_made
            WHERE timestamp > datetime('now', '-7 days')
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] > 0:
            return row[1] / row[0]
        return 0.0


class PredictiveAssistant:
    """Generate predictions based on system state and patterns"""
    
    def __init__(self, monitor: SystemMonitor):
        self.monitor = monitor
        self.pattern_db = PatternDatabase()
        self.thresholds = {
            'disk_critical': 95,
            'disk_warning': 90,
            'memory_critical': 90,
            'memory_warning': 80,
            'cpu_warning': 80,
            'swap_warning': 50,
            'temp_warning': 75,
            'generations_max': 20
        }
    
    def analyze_system(self) -> List[Prediction]:
        """Analyze system state and generate predictions"""
        predictions = []
        
        # Get current state
        state = self.monitor.get_state()
        quick = self.monitor.get_quick_status()
        
        # Check memory
        memory_predictions = self._analyze_memory(state.get('memory'), quick)
        predictions.extend(memory_predictions)
        
        # Check disk space
        disk_predictions = self._analyze_disk(state.get('disk', []))
        predictions.extend(disk_predictions)
        
        # Check CPU
        cpu_predictions = self._analyze_cpu(state.get('cpu'), quick)
        predictions.extend(cpu_predictions)
        
        # Check services
        service_predictions = self._analyze_services(state.get('services', []))
        predictions.extend(service_predictions)
        
        # Check NixOS specific
        nixos_predictions = self._analyze_nixos(state.get('nixos'))
        predictions.extend(nixos_predictions)
        
        # Check user patterns
        pattern_predictions = self._analyze_patterns()
        predictions.extend(pattern_predictions)
        
        # Sort by priority and confidence
        predictions.sort(key=lambda p: (
            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[p.priority],
            -p.confidence
        ))
        
        return predictions[:5]  # Return top 5 predictions
    
    def _analyze_memory(self, memory, quick: Dict) -> List[Prediction]:
        """Analyze memory usage and generate predictions"""
        predictions = []
        
        if not memory:
            return predictions
        
        mem_percent = quick.get('memory_percent', 0)
        
        if mem_percent > self.thresholds['memory_critical']:
            predictions.append(Prediction(
                action="close memory-intensive applications",
                reason=f"Memory usage critical at {mem_percent:.1f}%",
                confidence=0.95,
                priority="critical",
                category="performance",
                data={'memory_percent': mem_percent}
            ))
            
            # Find memory hogs
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    if proc.info['memory_percent'] > 5:
                        processes.append({
                            'name': proc.info['name'],
                            'memory': proc.info['memory_percent']
                        })
                
                if processes:
                    top_process = max(processes, key=lambda p: p['memory'])
                    predictions.append(Prediction(
                        action=f"consider closing {top_process['name']}",
                        reason=f"Using {top_process['memory']:.1f}% of memory",
                        confidence=0.8,
                        priority="high",
                        category="performance",
                        data={'process': top_process}
                    ))
            except:
                pass
        
        elif mem_percent > self.thresholds['memory_warning']:
            predictions.append(Prediction(
                action="monitor memory usage",
                reason=f"Memory usage high at {mem_percent:.1f}%",
                confidence=0.7,
                priority="medium",
                category="performance"
            ))
        
        # Check swap usage
        if memory.swap_percent > self.thresholds['swap_warning']:
            predictions.append(Prediction(
                action="restart to clear swap or add more RAM",
                reason=f"Swap usage high at {memory.swap_percent:.1f}%",
                confidence=0.6,
                priority="medium",
                category="performance"
            ))
        
        return predictions
    
    def _analyze_disk(self, disks: List) -> List[Prediction]:
        """Analyze disk usage and generate predictions"""
        predictions = []
        
        for disk in disks:
            if disk.percent > self.thresholds['disk_critical']:
                predictions.append(Prediction(
                    action=f"free space on {disk.mount_point}",
                    reason=f"Disk critically full at {disk.percent:.1f}%",
                    confidence=0.95,
                    priority="critical",
                    category="maintenance",
                    data={'mount': disk.mount_point, 'percent': disk.percent}
                ))
                
                # Suggest specific cleanup for /
                if disk.mount_point == '/':
                    predictions.append(Prediction(
                        action="run garbage collection",
                        reason="Root filesystem full, clean old generations",
                        confidence=0.9,
                        priority="high",
                        category="maintenance",
                        data={'command': 'nix-collect-garbage -d'}
                    ))
                
            elif disk.percent > self.thresholds['disk_warning']:
                predictions.append(Prediction(
                    action=f"check disk usage on {disk.mount_point}",
                    reason=f"Disk nearly full at {disk.percent:.1f}%",
                    confidence=0.7,
                    priority="medium",
                    category="maintenance"
                ))
        
        # Check /nix/store specifically
        nix_store = Path('/nix/store')
        if nix_store.exists():
            try:
                store_size = sum(f.stat().st_size for f in nix_store.rglob('*') if f.is_file())
                store_gb = store_size / (1024**3)
                
                if store_gb > 50:
                    predictions.append(Prediction(
                        action="optimize nix store",
                        reason=f"Nix store is {store_gb:.1f}GB",
                        confidence=0.6,
                        priority="low",
                        category="optimization",
                        data={'command': 'nix-store --optimise'}
                    ))
            except:
                pass
        
        return predictions
    
    def _analyze_cpu(self, cpu, quick: Dict) -> List[Prediction]:
        """Analyze CPU usage and generate predictions"""
        predictions = []
        
        if not cpu:
            return predictions
        
        if cpu.percent > self.thresholds['cpu_warning']:
            predictions.append(Prediction(
                action="check CPU-intensive processes",
                reason=f"CPU usage high at {cpu.percent:.1f}%",
                confidence=0.7,
                priority="medium",
                category="performance"
            ))
        
        # Check temperature
        if cpu.temperature and cpu.temperature > self.thresholds['temp_warning']:
            predictions.append(Prediction(
                action="check system cooling",
                reason=f"CPU temperature high at {cpu.temperature}°C",
                confidence=0.8,
                priority="high",
                category="maintenance"
            ))
        
        # Check load average
        load_1, load_5, load_15 = cpu.load_avg
        if load_1 > cpu.count * 2:
            predictions.append(Prediction(
                action="system overloaded, consider restarting heavy services",
                reason=f"Load average {load_1:.1f} exceeds CPU count",
                confidence=0.6,
                priority="medium",
                category="performance"
            ))
        
        return predictions
    
    def _analyze_services(self, services: List) -> List[Prediction]:
        """Analyze service status and generate predictions"""
        predictions = []
        
        failed = [s for s in services if s.status == 'failed']
        if failed:
            for service in failed:
                predictions.append(Prediction(
                    action=f"fix failed service: {service.name}",
                    reason=f"Service {service.name} has failed",
                    confidence=0.9,
                    priority="high",
                    category="maintenance",
                    data={
                        'service': service.name,
                        'command': f'systemctl status {service.name}'
                    }
                ))
        
        # Check for services that should be running
        important_services = {
            'NetworkManager': 'network connectivity',
            'sshd': 'remote access',
            'firewalld': 'security'
        }
        
        for service in services:
            if service.name in important_services and service.status != 'active':
                predictions.append(Prediction(
                    action=f"start {service.name}",
                    reason=f"Important for {important_services[service.name]}",
                    confidence=0.5,
                    priority="medium",
                    category="security" if 'firewall' in service.name else "maintenance"
                ))
        
        return predictions
    
    def _analyze_nixos(self, nixos) -> List[Prediction]:
        """Analyze NixOS-specific state"""
        predictions = []
        
        if not nixos:
            return predictions
        
        # Check number of generations
        if len(nixos.available_generations) > self.thresholds['generations_max']:
            predictions.append(Prediction(
                action="clean old generations",
                reason=f"You have {len(nixos.available_generations)} generations",
                confidence=0.7,
                priority="low",
                category="maintenance",
                data={'command': 'nix-collect-garbage --delete-older-than 30d'}
            ))
        
        # Check for outdated channels
        for channel in nixos.channels:
            if 'unstable' not in channel['name'] and '24.05' not in channel['url']:
                predictions.append(Prediction(
                    action=f"update channel {channel['name']}",
                    reason="Channel may be outdated",
                    confidence=0.4,
                    priority="low",
                    category="maintenance"
                ))
        
        return predictions
    
    def _analyze_patterns(self) -> List[Prediction]:
        """Analyze user patterns for predictive suggestions"""
        predictions = []
        patterns = self.pattern_db.get_patterns()
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        for pattern in patterns:
            # Check if action is typically done at this time
            if pattern.is_due(current_hour):
                days_since = (datetime.now() - pattern.last_occurrence).days
                
                if days_since >= 1:  # Not done today
                    predictions.append(Prediction(
                        action=pattern.action_type,
                        reason=f"Usually done at this time ({pattern.frequency} times in past month)",
                        confidence=min(0.3 + (pattern.frequency * 0.05), 0.8),
                        priority="low",
                        category="optimization"
                    ))
        
        # Time-based suggestions
        if current_hour == 9 and current_day < 5:  # Weekday morning
            predictions.append(Prediction(
                action="check for system updates",
                reason="Good time for maintenance",
                confidence=0.3,
                priority="low",
                category="maintenance"
            ))
        
        return predictions
    
    def format_prediction(self, prediction: Prediction) -> str:
        """Format a prediction for display"""
        icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '💡',
            'low': 'ℹ️'
        }
        
        icon = icons.get(prediction.priority, '•')
        
        text = f"{icon} **Suggestion**: {prediction.action}\n"
        text += f"   *Reason*: {prediction.reason}\n"
        
        if prediction.data and 'command' in prediction.data:
            text += f"   *Command*: `{prediction.data['command']}`\n"
        
        text += f"   *Confidence*: {prediction.confidence*100:.0f}%"
        
        return text


# Integration with main service
def get_predictions(monitor: SystemMonitor) -> List[str]:
    """Get formatted predictions for display"""
    assistant = PredictiveAssistant(monitor)
    predictions = assistant.analyze_system()
    
    return [assistant.format_prediction(p) for p in predictions]