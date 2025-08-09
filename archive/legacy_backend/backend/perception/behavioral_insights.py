"""
from typing import Dict, List, Optional
Behavioral Insights - Deep understanding from activity patterns

This module analyzes behavioral patterns to provide actionable insights
that help both the user and the AI system improve together.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import numpy as np

from ..knowledge_graph.skg import SymbioticKnowledgeGraph
from .activity_monitor import ActivityMonitor, ActivityPattern
from .context_awareness import ContextAwareness, UserContext, WorkContext


@dataclass
class BehavioralInsight:
    """A single behavioral insight"""
    insight_type: str
    title: str
    description: str
    confidence: float
    impact: str  # 'high', 'medium', 'low'
    actionable: bool
    recommendations: List[str]
    supporting_data: Dict[str, Any]
    

@dataclass
class ProductivityPattern:
    """Productivity pattern analysis"""
    peak_hours: List[int]
    productive_apps: List[str]
    distraction_apps: List[str]
    optimal_session_length: int  # minutes
    break_frequency: float  # breaks per hour
    flow_triggers: List[str]
    flow_disruptors: List[str]
    

@dataclass
class LearningPattern:
    """Learning behavior pattern"""
    preferred_learning_time: str
    attention_span: int  # minutes
    concept_mastery_rate: float
    struggle_indicators: List[str]
    success_patterns: List[str]
    optimal_difficulty: float  # 0-1
    

class BehavioralInsights:
    """
    Analyzes behavioral patterns to generate actionable insights
    
    Goes beyond simple metrics to understand:
    1. Productivity patterns and optimization opportunities
    2. Learning behaviors and personalization needs
    3. Wellbeing indicators and improvement suggestions
    4. Collaboration patterns and communication preferences
    """
    
    def __init__(self, skg: SymbioticKnowledgeGraph, 
                 activity_monitor: ActivityMonitor,
                 context_awareness: ContextAwareness):
        self.skg = skg
        self.activity_monitor = activity_monitor
        self.context_awareness = context_awareness
        
        # Insight generation thresholds
        self.confidence_threshold = 0.6
        self.pattern_min_occurrences = 5
        
        # Cached insights
        self.cached_insights = []
        self.last_analysis = None
        
    def generate_insights(self, time_range_days: int = 7) -> List[BehavioralInsight]:
        """
        Generate behavioral insights from recent activity
        """
        # Get activity data
        activity_data = self._get_activity_data(time_range_days)
        
        if not activity_data:
            return []
            
        insights = []
        
        # Productivity insights
        productivity_insights = self._analyze_productivity_patterns(activity_data)
        insights.extend(productivity_insights)
        
        # Learning insights
        learning_insights = self._analyze_learning_patterns(activity_data)
        insights.extend(learning_insights)
        
        # Wellbeing insights
        wellbeing_insights = self._analyze_wellbeing_patterns(activity_data)
        insights.extend(wellbeing_insights)
        
        # Flow state insights
        flow_insights = self._analyze_flow_patterns(activity_data)
        insights.extend(flow_insights)
        
        # Context switching insights
        switching_insights = self._analyze_context_switching(activity_data)
        insights.extend(switching_insights)
        
        # Filter by confidence
        insights = [i for i in insights if i.confidence >= self.confidence_threshold]
        
        # Sort by impact
        impact_order = {'high': 3, 'medium': 2, 'low': 1}
        insights.sort(key=lambda i: impact_order.get(i.impact, 0), reverse=True)
        
        # Cache insights
        self.cached_insights = insights
        self.last_analysis = datetime.now()
        
        # Record insights in knowledge graph
        self._record_insights(insights)
        
        return insights
        
    def _get_activity_data(self, days: int) -> List[Dict]:
        """Get activity data from knowledge graph"""
        cursor = self.skg.conn.cursor()
        
        cutoff = datetime.now() - timedelta(days=days)
        
        data = cursor.execute("""
            SELECT properties
            FROM nodes
            WHERE layer = 'phenomenological'
            AND type IN ('activity_pattern', 'user_context', 'cognitive_state')
            AND created_at > ?
            ORDER BY created_at DESC
        """, (cutoff.isoformat(),)).fetchall()
        
        return [json.loads(row[0]) for row in data]
        
    def _analyze_productivity_patterns(self, activity_data: List[Dict]) -> List[BehavioralInsight]:
        """Analyze productivity patterns"""
        insights = []
        
        # Extract productivity metrics
        productivity_pattern = self._extract_productivity_pattern(activity_data)
        
        if not productivity_pattern:
            return insights
            
        # Peak hours insight
        if productivity_pattern.peak_hours:
            peak_hours_str = ', '.join([f"{h}:00" for h in productivity_pattern.peak_hours])
            insights.append(BehavioralInsight(
                insight_type='productivity_peak_hours',
                title='Your Peak Productivity Hours',
                description=f'You tend to be most productive during {peak_hours_str}',
                confidence=0.8,
                impact='high',
                actionable=True,
                recommendations=[
                    f'Schedule important tasks during {peak_hours_str}',
                    'Protect these hours from meetings and interruptions',
                    'Use other times for routine tasks'
                ],
                supporting_data={
                    'peak_hours': productivity_pattern.peak_hours,
                    'analysis_period': 'last_7_days'
                }
            ))
            
        # Distraction apps insight
        if productivity_pattern.distraction_apps:
            top_distractions = productivity_pattern.distraction_apps[:3]
            insights.append(BehavioralInsight(
                insight_type='distraction_apps',
                title='Attention Drains Identified',
                description=f'Apps that frequently interrupt your flow: {", ".join(top_distractions)}',
                confidence=0.7,
                impact='medium',
                actionable=True,
                recommendations=[
                    'Consider using app blockers during focus time',
                    'Set specific times for checking these apps',
                    'Turn off notifications from these apps'
                ],
                supporting_data={
                    'distraction_apps': productivity_pattern.distraction_apps,
                    'productive_apps': productivity_pattern.productive_apps
                }
            ))
            
        # Session length insight
        if productivity_pattern.optimal_session_length > 0:
            insights.append(BehavioralInsight(
                insight_type='optimal_session_length',
                title='Your Ideal Work Session Length',
                description=f'You maintain focus best in {productivity_pattern.optimal_session_length}-minute sessions',
                confidence=0.75,
                impact='medium',
                actionable=True,
                recommendations=[
                    f'Set a timer for {productivity_pattern.optimal_session_length} minutes',
                    f'Take a 5-10 minute break after each session',
                    'Use this rhythm for your most important work'
                ],
                supporting_data={
                    'optimal_minutes': productivity_pattern.optimal_session_length,
                    'break_frequency': productivity_pattern.break_frequency
                }
            ))
            
        return insights
        
    def _analyze_learning_patterns(self, activity_data: List[Dict]) -> List[BehavioralInsight]:
        """Analyze learning behavior patterns"""
        insights = []
        
        # Extract learning patterns
        learning_pattern = self._extract_learning_pattern(activity_data)
        
        if not learning_pattern:
            return insights
            
        # Learning time preference
        if learning_pattern.preferred_learning_time:
            insights.append(BehavioralInsight(
                insight_type='learning_time_preference',
                title='Best Time for Learning',
                description=f'You learn most effectively during {learning_pattern.preferred_learning_time}',
                confidence=0.7,
                impact='medium',
                actionable=True,
                recommendations=[
                    f'Schedule learning activities in the {learning_pattern.preferred_learning_time}',
                    'Avoid complex new topics when tired',
                    'Review material during your peak learning times'
                ],
                supporting_data={
                    'preferred_time': learning_pattern.preferred_learning_time,
                    'attention_span': learning_pattern.attention_span
                }
            ))
            
        # Struggle indicators
        if learning_pattern.struggle_indicators:
            insights.append(BehavioralInsight(
                insight_type='learning_struggles',
                title='Learning Challenge Patterns',
                description='Identified patterns when you struggle with learning',
                confidence=0.65,
                impact='high',
                actionable=True,
                recommendations=[
                    'Take breaks when you notice these patterns',
                    'Try different learning approaches',
                    'Ask for help early when stuck'
                ],
                supporting_data={
                    'struggle_indicators': learning_pattern.struggle_indicators,
                    'success_patterns': learning_pattern.success_patterns
                }
            ))
            
        return insights
        
    def _analyze_wellbeing_patterns(self, activity_data: List[Dict]) -> List[BehavioralInsight]:
        """Analyze wellbeing-related patterns"""
        insights = []
        
        # Stress indicators
        stress_patterns = self._identify_stress_patterns(activity_data)
        
        if stress_patterns['high_stress_times']:
            insights.append(BehavioralInsight(
                insight_type='stress_patterns',
                title='Stress Pattern Detected',
                description='Certain times show elevated stress indicators',
                confidence=0.7,
                impact='high',
                actionable=True,
                recommendations=[
                    'Schedule breaks during high-stress periods',
                    'Practice stress-reduction techniques',
                    'Consider workload distribution'
                ],
                supporting_data=stress_patterns
            ))
            
        # Break patterns
        break_analysis = self._analyze_break_patterns(activity_data)
        
        if break_analysis['insufficient_breaks']:
            insights.append(BehavioralInsight(
                insight_type='break_reminder',
                title='Insufficient Break Time',
                description='You tend to work for extended periods without breaks',
                confidence=0.8,
                impact='high',
                actionable=True,
                recommendations=[
                    'Set hourly break reminders',
                    'Try the Pomodoro technique',
                    'Take micro-breaks for eye rest'
                ],
                supporting_data=break_analysis
            ))
            
        return insights
        
    def _analyze_flow_patterns(self, activity_data: List[Dict]) -> List[BehavioralInsight]:
        """Analyze flow state patterns"""
        insights = []
        
        # Flow triggers and disruptors
        flow_analysis = self._extract_flow_patterns(activity_data)
        
        if flow_analysis['triggers']:
            insights.append(BehavioralInsight(
                insight_type='flow_triggers',
                title='Your Flow State Triggers',
                description='Conditions that help you enter deep focus',
                confidence=0.75,
                impact='high',
                actionable=True,
                recommendations=[
                    'Create these conditions before important work',
                    'Protect your environment when in flow',
                    'Document your ideal flow setup'
                ],
                supporting_data={
                    'triggers': flow_analysis['triggers'],
                    'disruptors': flow_analysis['disruptors']
                }
            ))
            
        return insights
        
    def _analyze_context_switching(self, activity_data: List[Dict]) -> List[BehavioralInsight]:
        """Analyze context switching patterns"""
        insights = []
        
        # Context switching frequency
        switching_analysis = self._calculate_context_switching_cost(activity_data)
        
        if switching_analysis['excessive_switching']:
            insights.append(BehavioralInsight(
                insight_type='context_switching',
                title='High Context Switching Detected',
                description='Frequent task switching is impacting your productivity',
                confidence=0.8,
                impact='high',
                actionable=True,
                recommendations=[
                    'Batch similar tasks together',
                    'Use time blocking for focused work',
                    'Close unnecessary applications',
                    'Turn off non-critical notifications'
                ],
                supporting_data=switching_analysis
            ))
            
        return insights
        
    def _extract_productivity_pattern(self, activity_data: List[Dict]) -> Optional[ProductivityPattern]:
        """Extract productivity pattern from activity data"""
        if len(activity_data) < self.pattern_min_occurrences:
            return None
            
        # Analyze peak hours
        hour_productivity = defaultdict(list)
        app_productivity = defaultdict(int)
        app_distraction = defaultdict(int)
        
        for data in activity_data:
            if 'timestamp' in data:
                hour = datetime.fromisoformat(data['timestamp']).hour
                
                if data.get('pattern_type') == 'deep_focus':
                    hour_productivity[hour].append(1.0)
                elif data.get('pattern_type') == 'focused_work':
                    hour_productivity[hour].append(0.7)
                else:
                    hour_productivity[hour].append(0.3)
                    
            # Track app patterns
            if 'active_app' in data:
                app = data['active_app']
                if data.get('pattern_type') in ['deep_focus', 'focused_work']:
                    app_productivity[app] += 1
                elif data.get('pattern_type') == 'context_switching':
                    app_distraction[app] += 1
                    
        # Calculate peak hours
        avg_productivity = {
            hour: np.mean(scores) 
            for hour, scores in hour_productivity.items()
        }
        sorted_hours = sorted(avg_productivity.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, _ in sorted_hours[:4] if avg_productivity[hour] > 0.6]
        
        # Get top apps
        productive_apps = sorted(app_productivity.items(), key=lambda x: x[1], reverse=True)
        productive_apps = [app for app, _ in productive_apps[:5]]
        
        distraction_apps = sorted(app_distraction.items(), key=lambda x: x[1], reverse=True)
        distraction_apps = [app for app, _ in distraction_apps[:5]]
        
        # Calculate optimal session length
        session_lengths = self._calculate_session_lengths(activity_data)
        optimal_length = int(np.median(session_lengths)) if session_lengths else 45
        
        return ProductivityPattern(
            peak_hours=peak_hours,
            productive_apps=productive_apps,
            distraction_apps=distraction_apps,
            optimal_session_length=optimal_length,
            break_frequency=self._calculate_break_frequency(activity_data),
            flow_triggers=self._identify_flow_triggers(activity_data),
            flow_disruptors=self._identify_flow_disruptors(activity_data)
        )
        
    def _extract_learning_pattern(self, activity_data: List[Dict]) -> Optional[LearningPattern]:
        """Extract learning behavior pattern"""
        learning_events = [
            d for d in activity_data 
            if d.get('work_context') == 'learning' or 
            d.get('pattern_type') == 'exploring'
        ]
        
        if len(learning_events) < self.pattern_min_occurrences:
            return None
            
        # Analyze learning times
        time_distribution = defaultdict(int)
        for event in learning_events:
            if 'timestamp' in event:
                hour = datetime.fromisoformat(event['timestamp']).hour
                if 5 <= hour < 12:
                    time_distribution['morning'] += 1
                elif 12 <= hour < 17:
                    time_distribution['afternoon'] += 1
                elif 17 <= hour < 22:
                    time_distribution['evening'] += 1
                else:
                    time_distribution['night'] += 1
                    
        preferred_time = max(time_distribution.items(), key=lambda x: x[1])[0]
        
        # Calculate attention span
        attention_spans = []
        for i in range(1, len(learning_events)):
            if learning_events[i].get('pattern_type') == learning_events[i-1].get('pattern_type'):
                # Consecutive learning events
                t1 = datetime.fromisoformat(learning_events[i-1]['timestamp'])
                t2 = datetime.fromisoformat(learning_events[i]['timestamp'])
                duration = (t2 - t1).seconds / 60
                if duration < 120:  # Reasonable session length
                    attention_spans.append(duration)
                    
        avg_attention_span = int(np.mean(attention_spans)) if attention_spans else 30
        
        # Identify struggle patterns
        struggle_indicators = []
        success_patterns = []
        
        for event in learning_events:
            if event.get('frustration_level', 0) > 0.6:
                struggle_indicators.append(event.get('context', 'high_frustration'))
            elif event.get('flow_level', 0) > 0.6:
                success_patterns.append(event.get('context', 'flow_state'))
                
        return LearningPattern(
            preferred_learning_time=preferred_time,
            attention_span=avg_attention_span,
            concept_mastery_rate=self._calculate_mastery_rate(activity_data),
            struggle_indicators=list(set(struggle_indicators))[:5],
            success_patterns=list(set(success_patterns))[:5],
            optimal_difficulty=0.7  # Default to slightly challenging
        )
        
    def _identify_stress_patterns(self, activity_data: List[Dict]) -> Dict:
        """Identify stress-related patterns"""
        stress_indicators = []
        high_stress_times = []
        
        for data in activity_data:
            stress_level = data.get('stress_level', 0)
            if stress_level > 0.7:
                if 'timestamp' in data:
                    hour = datetime.fromisoformat(data['timestamp']).hour
                    high_stress_times.append(hour)
                    
                # Look for patterns
                if data.get('window_switches', 0) > 8:
                    stress_indicators.append('excessive_window_switching')
                if data.get('pattern_type') == 'context_switching':
                    stress_indicators.append('frequent_context_switches')
                    
        return {
            'high_stress_times': list(set(high_stress_times)),
            'stress_indicators': list(set(stress_indicators)),
            'stress_frequency': len([d for d in activity_data if d.get('stress_level', 0) > 0.7]) / max(len(activity_data), 1)
        }
        
    def _analyze_break_patterns(self, activity_data: List[Dict]) -> Dict:
        """Analyze break-taking patterns"""
        break_events = [
            d for d in activity_data 
            if d.get('pattern_type') == 'break_time' or
            d.get('afk_duration', 0) > 180
        ]
        
        work_events = [
            d for d in activity_data
            if d.get('pattern_type') in ['deep_focus', 'focused_work']
        ]
        
        # Calculate break ratio
        break_ratio = len(break_events) / max(len(activity_data), 1)
        
        # Check for long work stretches
        long_stretches = 0
        current_stretch = 0
        
        for data in sorted(activity_data, key=lambda x: x.get('timestamp', '')):
            if data.get('pattern_type') in ['deep_focus', 'focused_work']:
                current_stretch += 1
            else:
                if current_stretch > 6:  # More than 3 hours without break
                    long_stretches += 1
                current_stretch = 0
                
        return {
            'break_ratio': break_ratio,
            'insufficient_breaks': break_ratio < 0.1,
            'long_work_stretches': long_stretches,
            'average_break_duration': np.mean([d.get('afk_duration', 0) for d in break_events]) if break_events else 0
        }
        
    def _extract_flow_patterns(self, activity_data: List[Dict]) -> Dict:
        """Extract flow state patterns"""
        flow_events = [
            d for d in activity_data
            if d.get('flow_level', 0) > 0.6 or
            d.get('pattern_type') == 'deep_focus'
        ]
        
        triggers = []
        disruptors = []
        
        # Analyze what preceded flow states
        for i, data in enumerate(activity_data):
            if data.get('flow_level', 0) > 0.6:
                # Look at previous context
                if i > 0:
                    prev = activity_data[i-1]
                    if prev.get('pattern_type') == 'break_time':
                        triggers.append('break_before_work')
                    if prev.get('work_context') == 'planning':
                        triggers.append('planning_session')
                        
                # Look at environment
                if data.get('window_switches', 0) < 2:
                    triggers.append('minimal_distractions')
                if data.get('time_context') in ['morning', 'early_morning']:
                    triggers.append('morning_hours')
                    
            # Analyze flow disruptions
            elif i > 0 and activity_data[i-1].get('flow_level', 0) > 0.6:
                # Flow was broken
                if data.get('window_switches', 0) > 5:
                    disruptors.append('excessive_app_switching')
                if data.get('pattern_type') == 'context_switching':
                    disruptors.append('context_switch')
                    
        return {
            'triggers': list(set(triggers))[:5],
            'disruptors': list(set(disruptors))[:5],
            'flow_frequency': len(flow_events) / max(len(activity_data), 1),
            'average_flow_duration': self._calculate_average_flow_duration(flow_events)
        }
        
    def _calculate_context_switching_cost(self, activity_data: List[Dict]) -> Dict:
        """Calculate the cost of context switching"""
        switch_events = [
            d for d in activity_data
            if d.get('pattern_type') == 'context_switching' or
            d.get('window_switches', 0) > 5
        ]
        
        # Calculate productivity loss
        productivity_during_switches = []
        productivity_during_focus = []
        
        for data in activity_data:
            if 'productivity_score' in data or 'flow_level' in data:
                score = data.get('productivity_score', data.get('flow_level', 0.5))
                
                if data.get('pattern_type') == 'context_switching':
                    productivity_during_switches.append(score)
                elif data.get('pattern_type') in ['deep_focus', 'focused_work']:
                    productivity_during_focus.append(score)
                    
        avg_switch_productivity = np.mean(productivity_during_switches) if productivity_during_switches else 0.3
        avg_focus_productivity = np.mean(productivity_during_focus) if productivity_during_focus else 0.8
        
        productivity_loss = avg_focus_productivity - avg_switch_productivity
        
        return {
            'switch_frequency': len(switch_events) / max(len(activity_data), 1),
            'excessive_switching': len(switch_events) / max(len(activity_data), 1) > 0.3,
            'productivity_loss': productivity_loss,
            'estimated_time_lost': len(switch_events) * 15,  # 15 minutes per switch
            'switch_patterns': self._identify_switch_patterns(switch_events)
        }
        
    def _calculate_session_lengths(self, activity_data: List[Dict]) -> List[int]:
        """Calculate lengths of productive sessions"""
        sessions = []
        current_session_start = None
        
        sorted_data = sorted(activity_data, key=lambda x: x.get('timestamp', ''))
        
        for data in sorted_data:
            if data.get('pattern_type') in ['deep_focus', 'focused_work']:
                if current_session_start is None:
                    current_session_start = datetime.fromisoformat(data['timestamp'])
            else:
                if current_session_start is not None:
                    session_end = datetime.fromisoformat(data['timestamp'])
                    duration = (session_end - current_session_start).seconds / 60
                    if 10 <= duration <= 180:  # Reasonable session length
                        sessions.append(int(duration))
                    current_session_start = None
                    
        return sessions
        
    def _calculate_break_frequency(self, activity_data: List[Dict]) -> float:
        """Calculate breaks per hour"""
        total_hours = len(set(
            datetime.fromisoformat(d['timestamp']).hour
            for d in activity_data
            if 'timestamp' in d
        ))
        
        break_count = len([
            d for d in activity_data
            if d.get('pattern_type') == 'break_time'
        ])
        
        return break_count / max(total_hours, 1)
        
    def _identify_flow_triggers(self, activity_data: List[Dict]) -> List[str]:
        """Identify conditions that trigger flow states"""
        triggers = []
        
        flow_events = [
            d for d in activity_data
            if d.get('flow_level', 0) > 0.6
        ]
        
        for event in flow_events:
            if event.get('time_context') == 'morning':
                triggers.append('morning_work')
            if event.get('energy_level', 0) > 0.7:
                triggers.append('high_energy')
            if event.get('stress_level', 0) < 0.3:
                triggers.append('low_stress')
                
        return list(set(triggers))[:5]
        
    def _identify_flow_disruptors(self, activity_data: List[Dict]) -> List[str]:
        """Identify what disrupts flow states"""
        disruptors = []
        
        for i in range(1, len(activity_data)):
            if (activity_data[i-1].get('flow_level', 0) > 0.6 and
                activity_data[i].get('flow_level', 0) < 0.3):
                # Flow was disrupted
                if activity_data[i].get('interruption_type'):
                    disruptors.append(activity_data[i]['interruption_type'])
                if activity_data[i].get('window_switches', 0) > 5:
                    disruptors.append('app_switching')
                    
        return list(set(disruptors))[:5]
        
    def _calculate_mastery_rate(self, activity_data: List[Dict]) -> float:
        """Calculate learning mastery rate"""
        mastery_events = [
            d for d in activity_data
            if 'mastery_milestone' in d.get('type', '')
        ]
        
        learning_events = [
            d for d in activity_data
            if d.get('work_context') == 'learning'
        ]
        
        if not learning_events:
            return 0.0
            
        return len(mastery_events) / len(learning_events)
        
    def _identify_switch_patterns(self, switch_events: List[Dict]) -> List[str]:
        """Identify common context switching patterns"""
        patterns = []
        
        for event in switch_events:
            if event.get('trigger'):
                patterns.append(event['trigger'])
                
        # Count occurrences
        pattern_counts = defaultdict(int)
        for pattern in patterns:
            pattern_counts[pattern] += 1
            
        # Return top patterns
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        return [pattern for pattern, _ in sorted_patterns[:5]]
        
    def _calculate_average_flow_duration(self, flow_events: List[Dict]) -> float:
        """Calculate average duration of flow states"""
        if not flow_events:
            return 0
            
        durations = []
        sorted_events = sorted(flow_events, key=lambda x: x.get('timestamp', ''))
        
        i = 0
        while i < len(sorted_events) - 1:
            if sorted_events[i].get('flow_level', 0) > 0.6:
                start = datetime.fromisoformat(sorted_events[i]['timestamp'])
                
                # Find end of flow
                j = i + 1
                while j < len(sorted_events) and sorted_events[j].get('flow_level', 0) > 0.6:
                    j += 1
                    
                if j > i + 1:
                    end = datetime.fromisoformat(sorted_events[j-1]['timestamp'])
                    duration = (end - start).seconds / 60
                    if duration < 180:  # Reasonable flow duration
                        durations.append(duration)
                        
                i = j
            else:
                i += 1
                
        return np.mean(durations) if durations else 0
        
    def _record_insights(self, insights: List[BehavioralInsight]):
        """Record insights in knowledge graph"""
        insight_batch_id = f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor = self.skg.conn.cursor()
        
        # Record batch
        cursor.execute("""
            INSERT INTO nodes (id, layer, type, properties)
            VALUES (?, 'metacognitive', 'insight_batch', ?)
        """, (
            insight_batch_id,
            json.dumps({
                'timestamp': datetime.now().isoformat(),
                'insight_count': len(insights),
                'analysis_type': 'behavioral_patterns'
            })
        ))
        
        # Record individual insights
        for i, insight in enumerate(insights):
            insight_id = f"{insight_batch_id}_{i}"
            
            cursor.execute("""
                INSERT INTO nodes (id, layer, type, properties)
                VALUES (?, 'metacognitive', 'behavioral_insight', ?)
            """, (
                insight_id,
                json.dumps({
                    'insight_type': insight.insight_type,
                    'title': insight.title,
                    'description': insight.description,
                    'confidence': insight.confidence,
                    'impact': insight.impact,
                    'actionable': insight.actionable,
                    'recommendations': insight.recommendations,
                    'supporting_data': insight.supporting_data,
                    'timestamp': datetime.now().isoformat()
                })
            ))
            
            # Create edge to batch
            cursor.execute("""
                INSERT INTO edges (from_id, to_id, relation, properties)
                VALUES (?, ?, 'part_of', ?)
            """, (
                insight_id,
                insight_batch_id,
                json.dumps({'index': i})
            ))
            
        self.skg.conn.commit()
        
    def get_personalized_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations based on behavioral patterns
        """
        if not self.cached_insights:
            self.generate_insights()
            
        recommendations = []
        
        # Group insights by type
        insight_groups = defaultdict(list)
        for insight in self.cached_insights:
            insight_groups[insight.insight_type].append(insight)
            
        # Generate holistic recommendations
        if 'productivity_peak_hours' in insight_groups:
            peak_insight = insight_groups['productivity_peak_hours'][0]
            recommendations.append({
                'category': 'Time Management',
                'recommendation': 'Optimize your schedule around peak hours',
                'specific_actions': peak_insight.recommendations,
                'priority': 'high',
                'expected_impact': 'Significant productivity improvement'
            })
            
        if 'distraction_apps' in insight_groups:
            distraction_insight = insight_groups['distraction_apps'][0]
            recommendations.append({
                'category': 'Focus Enhancement',
                'recommendation': 'Reduce digital distractions',
                'specific_actions': distraction_insight.recommendations,
                'priority': 'medium',
                'expected_impact': 'Better flow state access'
            })
            
        if 'break_reminder' in insight_groups:
            break_insight = insight_groups['break_reminder'][0]
            recommendations.append({
                'category': 'Wellbeing',
                'recommendation': 'Implement regular break schedule',
                'specific_actions': break_insight.recommendations,
                'priority': 'high',
                'expected_impact': 'Improved sustained performance'
            })
            
        return recommendations
        
    def compare_to_baseline(self, metric: str) -> Dict[str, Any]:
        """
        Compare user's patterns to healthy baselines
        """
        # Get user's current pattern
        current_pattern = self._get_current_user_pattern()
        
        # Define healthy baselines
        healthy_baselines = {
            'break_frequency': 0.25,  # Break every 4 hours minimum
            'flow_frequency': 0.2,    # In flow 20% of time
            'context_switch_rate': 0.2,  # Max 20% time switching
            'stress_frequency': 0.1,   # Stressed max 10% of time
            'learning_rate': 0.15      # Learning 15% of time
        }
        
        if metric not in healthy_baselines:
            return {'error': 'Unknown metric'}
            
        user_value = current_pattern.get(metric, 0)
        baseline = healthy_baselines[metric]
        
        # Calculate deviation
        if metric in ['context_switch_rate', 'stress_frequency']:
            # Lower is better
            deviation = user_value - baseline
            health_score = max(0, 1 - (user_value / baseline)) if baseline > 0 else 0
        else:
            # Higher is better
            deviation = baseline - user_value
            health_score = min(1, user_value / baseline) if baseline > 0 else 0
            
        return {
            'metric': metric,
            'user_value': user_value,
            'healthy_baseline': baseline,
            'deviation': deviation,
            'health_score': health_score,
            'interpretation': self._interpret_comparison(metric, health_score),
            'improvement_suggestions': self._suggest_improvements(metric, health_score)
        }
        
    def _get_current_user_pattern(self) -> Dict[str, float]:
        """Get current user behavioral pattern metrics"""
        activity_data = self._get_activity_data(7)
        
        if not activity_data:
            return {}
            
        total_events = len(activity_data)
        
        pattern = {
            'break_frequency': len([d for d in activity_data if d.get('pattern_type') == 'break_time']) / max(total_events, 1),
            'flow_frequency': len([d for d in activity_data if d.get('flow_level', 0) > 0.6]) / max(total_events, 1),
            'context_switch_rate': len([d for d in activity_data if d.get('pattern_type') == 'context_switching']) / max(total_events, 1),
            'stress_frequency': len([d for d in activity_data if d.get('stress_level', 0) > 0.7]) / max(total_events, 1),
            'learning_rate': len([d for d in activity_data if d.get('work_context') == 'learning']) / max(total_events, 1)
        }
        
        return pattern
        
    def _interpret_comparison(self, metric: str, health_score: float) -> str:
        """Interpret the health score comparison"""
        if health_score > 0.8:
            return "Excellent - you're doing great!"
        elif health_score > 0.6:
            return "Good - minor improvements possible"
        elif health_score > 0.4:
            return "Fair - room for improvement"
        else:
            return "Needs attention - significant improvement recommended"
            
    def _suggest_improvements(self, metric: str, health_score: float) -> List[str]:
        """Suggest improvements based on metric comparison"""
        if health_score > 0.8:
            return ["Keep up the excellent work!"]
            
        suggestions = {
            'break_frequency': [
                "Set hourly reminders for micro-breaks",
                "Use the 20-20-20 rule for eye health",
                "Take a 5-minute walk every hour"
            ],
            'flow_frequency': [
                "Protect morning hours for deep work",
                "Minimize interruptions during focus time",
                "Create a consistent pre-work ritual"
            ],
            'context_switch_rate': [
                "Batch similar tasks together",
                "Use time blocking for different activities",
                "Close unnecessary browser tabs and apps"
            ],
            'stress_frequency': [
                "Practice regular stress-reduction techniques",
                "Review and adjust workload distribution",
                "Take breaks before reaching peak stress"
            ],
            'learning_rate': [
                "Dedicate specific time for learning",
                "Mix learning with practical application",
                "Join study groups or communities"
            ]
        }
        
        return suggestions.get(metric, ["Focus on gradual improvement"])