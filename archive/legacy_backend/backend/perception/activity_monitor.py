"""
from typing import List, Dict, Optional
Activity Monitor - ActivityWatch integration for behavioral awareness

This module provides privacy-first integration with ActivityWatch to understand
user behavior patterns without compromising privacy.
"""

import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

from ..knowledge_graph.skg import SymbioticKnowledgeGraph


@dataclass
class ActivitySnapshot:
    """Point-in-time activity data"""
    timestamp: datetime
    active_window: str
    active_app: str
    window_title: str
    afk_duration: int  # seconds away from keyboard
    keystroke_rate: float  # keystrokes per minute
    mouse_activity: float  # movement intensity 0-1
    window_switches: int  # in last 5 minutes


@dataclass
class ActivityPattern:
    """Analyzed activity pattern"""
    pattern_type: str  # 'focused', 'exploring', 'struggling', etc.
    confidence: float
    duration_minutes: float
    key_indicators: Dict[str, float]


class ActivityMonitor:
    """
    Monitors user activity through ActivityWatch for context awareness
    
    Key principles:
    1. Privacy first - only aggregate patterns, no content
    2. User control - easy to disable/configure
    3. Local only - no data leaves the machine
    4. Transparent - user can see what's tracked
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph, 
                 aw_host: str = "localhost", aw_port: int = 5600):
        self.skg = skg
        self.aw_host = aw_host
        self.aw_port = aw_port
        self.aw_url = f"http://{aw_host}:{aw_port}/api"
        
        self.logger = logging.getLogger(__name__)
        
        # Privacy settings
        self.privacy_mode = "aggregate"  # 'strict', 'aggregate', 'full'
        self.excluded_apps = ['1password', 'bitwarden', 'banking']
        self.excluded_patterns = ['password', 'private', 'incognito']
        
        # Activity tracking
        self.activity_buffer = []
        self.current_pattern = None
        self.pattern_history = []
        
        # ActivityWatch bucket names
        self.window_bucket = None
        self.afk_bucket = None
        self.active = False
        
    async def connect(self) -> bool:
        """Connect to ActivityWatch server"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if ActivityWatch is running
                async with session.get(f"{self.aw_url}/0/info") as response:
                    if response.status == 200:
                        info = await response.json()
                        self.logger.info(f"Connected to ActivityWatch {info.get('version', 'unknown')}")
                        
                        # Get bucket names
                        await self._discover_buckets()
                        self.active = True
                        return True
                        
        except aiohttp.ClientError as e:
            self.logger.warning(f"Could not connect to ActivityWatch: {e}")
            self.active = False
            return False
            
    async def _discover_buckets(self):
        """Discover available ActivityWatch buckets"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.aw_url}/0/buckets") as response:
                if response.status == 200:
                    buckets = await response.json()
                    
                    # Find window and AFK buckets
                    for bucket_id, bucket_info in buckets.items():
                        if 'window' in bucket_id:
                            self.window_bucket = bucket_id
                        elif 'afk' in bucket_id:
                            self.afk_bucket = bucket_id
                            
                    self.logger.info(f"Found buckets - Window: {self.window_bucket}, AFK: {self.afk_bucket}")
                    
    async def get_current_activity(self) -> Optional[ActivitySnapshot]:
        """Get current activity snapshot from ActivityWatch"""
        if not self.active:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                # Get current window
                window_data = await self._get_current_window(session)
                
                # Get AFK status
                afk_data = await self._get_afk_status(session)
                
                # Get recent activity metrics
                metrics = await self._get_activity_metrics(session)
                
                # Create snapshot
                snapshot = ActivitySnapshot(
                    timestamp=datetime.now(),
                    active_window=window_data.get('window', 'unknown'),
                    active_app=window_data.get('app', 'unknown'),
                    window_title=self._sanitize_window_title(window_data.get('title', '')),
                    afk_duration=afk_data.get('duration', 0),
                    keystroke_rate=metrics.get('keystroke_rate', 0),
                    mouse_activity=metrics.get('mouse_activity', 0),
                    window_switches=metrics.get('window_switches', 0)
                )
                
                # Apply privacy filters
                snapshot = self._apply_privacy_filters(snapshot)
                
                # Update buffer
                self.activity_buffer.append(snapshot)
                self._maintain_buffer_size()
                
                return snapshot
                
        except Exception as e:
            self.logger.error(f"Error getting activity: {e}")
            return None
            
    async def _get_current_window(self, session: aiohttp.ClientSession) -> Dict:
        """Get current active window from ActivityWatch"""
        if not self.window_bucket:
            return {}
            
        try:
            # Get latest window event
            query = {
                "timeperiods": [f"{datetime.now().isoformat()}/{datetime.now().isoformat()}"],
                "query": [
                    f"events = query_bucket(find_bucket('{self.window_bucket}'));",
                    "RETURN = events;"
                ]
            }
            
            async with session.post(f"{self.aw_url}/0/query", json=query) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and result[0]:
                        latest_event = result[0][-1] if result[0] else {}
                        return latest_event.get('data', {})
                        
        except Exception as e:
            self.logger.error(f"Error getting window data: {e}")
            
        return {}
        
    async def _get_afk_status(self, session: aiohttp.ClientSession) -> Dict:
        """Get AFK (Away From Keyboard) status"""
        if not self.afk_bucket:
            return {'duration': 0}
            
        try:
            # Get latest AFK event
            query = {
                "timeperiods": [f"{(datetime.now() - timedelta(minutes=5)).isoformat()}/{datetime.now().isoformat()}"],
                "query": [
                    f"events = query_bucket(find_bucket('{self.afk_bucket}'));",
                    "RETURN = events;"
                ]
            }
            
            async with session.post(f"{self.aw_url}/0/query", json=query) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and result[0]:
                        # Calculate AFK duration
                        afk_duration = 0
                        for event in result[0]:
                            if event.get('data', {}).get('status') == 'afk':
                                afk_duration += event.get('duration', 0)
                                
                        return {'duration': int(afk_duration)}
                        
        except Exception as e:
            self.logger.error(f"Error getting AFK status: {e}")
            
        return {'duration': 0}
        
    async def _get_activity_metrics(self, session: aiohttp.ClientSession) -> Dict:
        """Calculate activity metrics from recent data"""
        metrics = {
            'keystroke_rate': 0,
            'mouse_activity': 0,
            'window_switches': 0
        }
        
        if not self.window_bucket:
            return metrics
            
        try:
            # Get events from last 5 minutes
            start_time = datetime.now() - timedelta(minutes=5)
            query = {
                "timeperiods": [f"{start_time.isoformat()}/{datetime.now().isoformat()}"],
                "query": [
                    f"events = query_bucket(find_bucket('{self.window_bucket}'));",
                    "RETURN = events;"
                ]
            }
            
            async with session.post(f"{self.aw_url}/0/query", json=query) as response:
                if response.status == 200:
                    result = await response.json()
                    if result and result[0]:
                        events = result[0]
                        
                        # Count window switches
                        unique_windows = set()
                        for event in events:
                            window = event.get('data', {}).get('window')
                            if window:
                                unique_windows.add(window)
                                
                        metrics['window_switches'] = len(unique_windows) - 1
                        
                        # Estimate keystroke rate (simplified)
                        # In real implementation, would need keyboard event data
                        metrics['keystroke_rate'] = 60  # Default estimate
                        
                        # Estimate mouse activity
                        metrics['mouse_activity'] = 0.5  # Default estimate
                        
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            
        return metrics
        
    def _sanitize_window_title(self, title: str) -> str:
        """Remove sensitive information from window titles"""
        if self.privacy_mode == "strict":
            return "[REDACTED]"
            
        # Remove URLs, emails, file paths
        import re
        
        # Remove URLs
        title = re.sub(r'https?://[^\s]+', '[URL]', title)
        
        # Remove email addresses
        title = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', title)
        
        # Remove file paths
        title = re.sub(r'(/[\w\.-]+)+', '[PATH]', title)
        title = re.sub(r'([A-Za-z]:\\[\w\.-\\]+)+', '[PATH]', title)
        
        # Check excluded patterns
        for pattern in self.excluded_patterns:
            if pattern.lower() in title.lower():
                return "[PRIVATE]"
                
        return title
        
    def _apply_privacy_filters(self, snapshot: ActivitySnapshot) -> ActivitySnapshot:
        """Apply privacy filters to activity data"""
        # Check if app is excluded
        if any(excluded in snapshot.active_app.lower() for excluded in self.excluded_apps):
            snapshot.active_app = "[EXCLUDED_APP]"
            snapshot.window_title = "[PRIVATE]"
            
        return snapshot
        
    def _maintain_buffer_size(self):
        """Keep activity buffer at reasonable size"""
        max_buffer_size = 100
        if len(self.activity_buffer) > max_buffer_size:
            self.activity_buffer = self.activity_buffer[-max_buffer_size:]
            
    def analyze_activity_pattern(self) -> Optional[ActivityPattern]:
        """Analyze recent activity to identify patterns"""
        if len(self.activity_buffer) < 5:
            return None
            
        recent_activity = self.activity_buffer[-10:]
        
        # Calculate pattern indicators
        indicators = self._calculate_pattern_indicators(recent_activity)
        
        # Determine pattern type
        pattern_type = self._determine_pattern_type(indicators)
        
        # Calculate confidence
        confidence = self._calculate_pattern_confidence(indicators, pattern_type)
        
        # Create pattern
        pattern = ActivityPattern(
            pattern_type=pattern_type,
            confidence=confidence,
            duration_minutes=len(recent_activity) * 0.5,  # Assuming 30s sampling
            key_indicators=indicators
        )
        
        # Update current pattern
        self.current_pattern = pattern
        self.pattern_history.append({
            'pattern': pattern,
            'timestamp': datetime.now().isoformat()
        })
        
        # Record in knowledge graph
        self._record_activity_pattern(pattern)
        
        return pattern
        
    def _calculate_pattern_indicators(self, activities: List[ActivitySnapshot]) -> Dict[str, float]:
        """Calculate indicators from activity snapshots"""
        if not activities:
            return {}
            
        # Average metrics
        avg_keystrokes = sum(a.keystroke_rate for a in activities) / len(activities)
        avg_switches = sum(a.window_switches for a in activities) / len(activities)
        avg_afk = sum(a.afk_duration for a in activities) / len(activities)
        
        # App consistency
        apps = [a.active_app for a in activities]
        most_common_app = max(set(apps), key=apps.count)
        app_consistency = apps.count(most_common_app) / len(apps)
        
        return {
            'keystroke_rate': avg_keystrokes,
            'window_switches': avg_switches,
            'afk_duration': avg_afk,
            'app_consistency': app_consistency,
            'activity_variance': self._calculate_variance(activities)
        }
        
    def _calculate_variance(self, activities: List[ActivitySnapshot]) -> float:
        """Calculate variance in activity patterns"""
        if len(activities) < 2:
            return 0.0
            
        # Variance in keystroke rates
        keystrokes = [a.keystroke_rate for a in activities]
        mean = sum(keystrokes) / len(keystrokes)
        variance = sum((k - mean) ** 2 for k in keystrokes) / len(keystrokes)
        
        # Normalize to 0-1
        return min(1.0, variance / 1000)
        
    def _determine_pattern_type(self, indicators: Dict[str, float]) -> str:
        """Determine the type of activity pattern"""
        keystrokes = indicators.get('keystroke_rate', 0)
        switches = indicators.get('window_switches', 0)
        consistency = indicators.get('app_consistency', 0)
        afk = indicators.get('afk_duration', 0)
        
        if keystrokes > 80 and switches < 2 and consistency > 0.8:
            return 'deep_focus'
        elif keystrokes > 50 and switches < 4:
            return 'focused_work'
        elif switches > 6 and keystrokes < 40:
            return 'exploring'
        elif afk > 180:
            return 'break_time'
        elif switches > 8 and consistency < 0.3:
            return 'context_switching'
        elif keystrokes < 20 and switches < 2:
            return 'reading'
        else:
            return 'mixed_activity'
            
    def _calculate_pattern_confidence(self, indicators: Dict[str, float],
                                    pattern_type: str) -> float:
        """Calculate confidence in pattern detection"""
        # Base confidence on how well indicators match pattern
        confidence_factors = {
            'deep_focus': lambda i: (
                min(i.get('keystroke_rate', 0) / 100, 1.0) *
                (1 - min(i.get('window_switches', 0) / 5, 1.0)) *
                i.get('app_consistency', 0)
            ),
            'exploring': lambda i: (
                min(i.get('window_switches', 0) / 8, 1.0) *
                (1 - i.get('app_consistency', 1.0))
            ),
            'break_time': lambda i: min(i.get('afk_duration', 0) / 180, 1.0)
        }
        
        calculator = confidence_factors.get(pattern_type)
        if calculator:
            return calculator(indicators)
            
        return 0.5  # Default confidence
        
    def _record_activity_pattern(self, pattern: ActivityPattern):
        """Record activity pattern in knowledge graph"""
        pattern_id = f"activity_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'phenomenological', 'activity_pattern', ?)
        """, (
            pattern_id,
            json.dumps({
                'pattern_type': pattern.pattern_type,
                'confidence': pattern.confidence,
                'duration_minutes': pattern.duration_minutes,
                'indicators': pattern.key_indicators,
                'timestamp': datetime.now().isoformat()
            })
        ))
        
        self.skg.conn.commit()
        
    def get_activity_context(self) -> Dict[str, Any]:
        """Get current activity context for decision making"""
        if not self.current_pattern:
            self.analyze_activity_pattern()
            
        context = {
            'active': self.active,
            'current_pattern': self.current_pattern.__dict__ if self.current_pattern else None,
            'recent_patterns': self._get_recent_patterns(),
            'focus_level': self._calculate_focus_level(),
            'interruption_readiness': self._assess_interruption_readiness()
        }
        
        return context
        
    def _get_recent_patterns(self) -> List[str]:
        """Get recent pattern types"""
        return [
            p['pattern'].pattern_type
            for p in self.pattern_history[-5:]
        ]
        
    def _calculate_focus_level(self) -> float:
        """Calculate current focus level from activity"""
        if not self.current_pattern:
            return 0.5
            
        focus_patterns = ['deep_focus', 'focused_work', 'reading']
        if self.current_pattern.pattern_type in focus_patterns:
            return 0.8 * self.current_pattern.confidence
        else:
            return 0.3
            
    def _assess_interruption_readiness(self) -> str:
        """Assess if user is ready for interruptions"""
        if not self.current_pattern:
            return 'unknown'
            
        pattern = self.current_pattern.pattern_type
        
        if pattern in ['deep_focus', 'focused_work']:
            return 'not_ready'
        elif pattern in ['exploring', 'context_switching']:
            return 'ready'
        elif pattern == 'break_time':
            return 'ideal'
        else:
            return 'neutral'
            
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous activity monitoring"""
        self.logger.info("Starting activity monitoring...")
        
        while self.active:
            try:
                # Get current activity
                snapshot = await self.get_current_activity()
                
                # Analyze patterns periodically
                if len(self.activity_buffer) % 10 == 0:
                    self.analyze_activity_pattern()
                    
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
                
    def stop_monitoring(self):
        """Stop activity monitoring"""
        self.active = False
        self.logger.info("Stopped activity monitoring")
        
    def get_privacy_report(self) -> Dict[str, Any]:
        """Get report on privacy protection measures"""
        return {
            'privacy_mode': self.privacy_mode,
            'excluded_apps': self.excluded_apps,
            'excluded_patterns': self.excluded_patterns,
            'data_retention': 'Local only - no external transmission',
            'data_collected': {
                'window_titles': 'Sanitized',
                'app_names': 'Yes (with exclusions)',
                'content': 'Never',
                'keystrokes': 'Rate only, no content',
                'websites': 'Domain only if not private'
            }
        }