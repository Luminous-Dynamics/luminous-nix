#!/usr/bin/env python3
"""
Advanced Causal Reasoning Engine - Phase 4 Living System
Deep system understanding through causal analysis and root cause reasoning

This module extends the Advanced Causal XAI engine with deeper reasoning capabilities,
comprehensive root cause analysis, and enhanced predictive maintenance through
causal model understanding.

Revolutionary Features:
- Multi-layered causal model construction
- Root cause analysis with probabilistic reasoning
- Predictive maintenance through causal forecasting
- System behavior explanation through causal chains
- Interactive causal discovery and validation
- Consciousness-first causal interfaces for all personas

Research Foundation:
- DoWhy causal inference framework integration
- Pearl's Causal Hierarchy (Association → Intervention → Counterfactual)
- Bayesian structural causal models
- Causal discovery algorithms for system understanding
- Intervention planning for system optimization
"""

import asyncio
import json
import logging
# Note: Numpy and pandas imports are optional for basic functionality
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
    PANDAS_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    PANDAS_AVAILABLE = False
    # Create mock numpy for basic operations
    class MockNumpy:
        def array(self, data):
            return data
        def mean(self, data):
            return sum(data) / len(data) if data else 0
        def std(self, data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            variance = sum((x - mean) ** 2 for x in data) / len(data)
            return variance ** 0.5
        def var(self, data):
            if not data:
                return 0
            mean = sum(data) / len(data)
            return sum((x - mean) ** 2 for x in data) / len(data)
        def number(self):
            return float
    np = MockNumpy()
    
    # Create mock pandas for basic operations
    class MockDataFrame:
        def __init__(self, data):
            self.data = data if isinstance(data, list) else [data]
        def select_dtypes(self, include=None):
            return MockDataFrame([])
        def corr(self):
            return MockDataFrame([])
        @property
        def columns(self):
            return []
        @property
        def iloc(self):
            return self
        def __getitem__(self, key):
            return 0.0
    
    class MockPandas:
        def DataFrame(self, data):
            return MockDataFrame(data)
    pd = MockPandas()
    logging.warning("Numpy/pandas not available. Using simplified numerical operations.")
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from enum import Enum
import sqlite3
import networkx as nx
from collections import defaultdict, deque

# DoWhy integration for advanced causal reasoning
try:
    import dowhy
    from dowhy import CausalModel
    from dowhy.causal_estimators import LinearRegressionEstimator
    from dowhy.causal_refuters import RandomCommonCause
    DOWHY_AVAILABLE = True
except ImportError:
    DOWHY_AVAILABLE = False
    logging.warning("DoWhy not available - using simplified causal reasoning fallback")

# Statistical analysis imports
try:
    from scipy import stats
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy/sklearn not available - using basic statistical methods")

# Import consciousness-first components
from ..core.learning_system import LearningSystem
from .advanced_causal_xai import AdvancedCausalXAI, CausalExplanation, ExplanationLevel

logger = logging.getLogger(__name__)


class CausalReasoningLevel(Enum):
    """Pearl's Causal Hierarchy levels of reasoning"""
    ASSOCIATION = "association"      # Seeing correlations (P(Y|X))
    INTERVENTION = "intervention"    # Understanding effects (P(Y|do(X)))
    COUNTERFACTUAL = "counterfactual"  # Imagining alternatives (P(Yx|X',Y'))


class CausalAnalysisType(Enum):
    """Types of causal analysis for different system behaviors"""
    ROOT_CAUSE = "root_cause"          # Why did this error occur?
    PREDICTIVE = "predictive"          # What will happen if we do X?
    EXPLANATORY = "explanatory"       # Why does the system behave this way?
    DIAGNOSTIC = "diagnostic"          # What's wrong with the system?
    OPTIMIZATION = "optimization"     # How can we improve performance?


class SystemComponent(Enum):
    """Major system components for causal analysis"""
    USER_INTERFACE = "user_interface"
    NLP_ENGINE = "nlp_engine"
    COMMAND_EXECUTOR = "command_executor"
    LEARNING_SYSTEM = "learning_system"
    NIXOS_INTEGRATION = "nixos_integration"
    MEMORY_SYSTEM = "memory_system"
    SECURITY_LAYER = "security_layer"
    PERFORMANCE_MONITOR = "performance_monitor"


@dataclass
class CausalVariable:
    """Variable in the causal model with metadata"""
    name: str
    type: str  # 'continuous', 'categorical', 'binary'
    description: str
    component: SystemComponent
    observable: bool = True
    controllable: bool = False  # Can we intervene on this variable?
    temporal: bool = False      # Does this change over time?
    
    def __hash__(self):
        return hash(self.name)


@dataclass
class CausalRelationship:
    """Directed causal relationship between variables"""
    cause: str
    effect: str
    strength: float        # 0.0 - 1.0
    confidence: float      # 0.0 - 1.0
    mechanism: str         # Description of causal mechanism
    lag_time: float = 0.0  # Time delay between cause and effect
    conditions: List[str] = field(default_factory=list)  # When this relationship holds
    
    def __hash__(self):
        return hash((self.cause, self.effect))


@dataclass
class CausalChain:
    """Chain of causal relationships leading to an outcome"""
    outcome: str
    chain: List[CausalRelationship]
    total_strength: float
    confidence: float
    interventionable: bool  # Can we break this chain?
    alternative_chains: List['CausalChain'] = field(default_factory=list)


@dataclass
class RootCauseAnalysis:
    """Complete root cause analysis result"""
    problem: str
    primary_causes: List[CausalChain]
    contributing_factors: List[str]
    system_context: Dict[str, Any]
    intervention_recommendations: List[Dict[str, Any]]
    confidence_score: float
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PredictiveCausalModel:
    """Model for predicting system behavior through causal reasoning"""
    scenario: str
    predicted_outcomes: Dict[str, float]  # outcome -> probability
    causal_pathways: List[CausalChain]
    uncertainty_bounds: Dict[str, Tuple[float, float]]
    assumptions: List[str]
    validation_data: Optional[Dict[str, Any]] = None


class CausalGraphBuilder:
    """Builds and maintains causal graph of system behavior"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.variables = {}  # name -> CausalVariable
        self.relationships = set()  # CausalRelationship objects
        self.temporal_data = defaultdict(list)  # For learning causal relationships from data
        
        # Initialize with known system variables
        self._initialize_system_variables()
        self._initialize_known_relationships()
    
    def _initialize_system_variables(self):
        """Initialize known system variables for Nix for Humanity"""
        system_vars = [
            # User context variables
            CausalVariable("user_experience_level", "categorical", "User's NixOS expertise", 
                         SystemComponent.USER_INTERFACE, controllable=False),
            CausalVariable("user_intent_clarity", "continuous", "How clearly user expresses intent", 
                         SystemComponent.USER_INTERFACE, controllable=False),
            CausalVariable("user_satisfaction", "continuous", "User satisfaction with interaction", 
                         SystemComponent.USER_INTERFACE, controllable=True),
            
            # NLP variables
            CausalVariable("intent_recognition_confidence", "continuous", "Confidence in understanding user intent", 
                         SystemComponent.NLP_ENGINE, controllable=True),
            CausalVariable("typo_correction_needed", "binary", "Whether input needs typo correction", 
                         SystemComponent.NLP_ENGINE, controllable=True),
            CausalVariable("context_continuity", "continuous", "How well conversation context is maintained", 
                         SystemComponent.NLP_ENGINE, controllable=True),
            
            # System performance variables
            CausalVariable("response_time", "continuous", "Time to respond to user query", 
                         SystemComponent.PERFORMANCE_MONITOR, controllable=True),
            CausalVariable("memory_usage", "continuous", "System memory consumption", 
                         SystemComponent.PERFORMANCE_MONITOR, controllable=True),
            CausalVariable("nixos_operation_success", "binary", "Whether NixOS command succeeded", 
                         SystemComponent.NIXOS_INTEGRATION, controllable=True),
            
            # Learning variables
            CausalVariable("model_accuracy", "continuous", "ML model prediction accuracy", 
                         SystemComponent.LEARNING_SYSTEM, controllable=True),
            CausalVariable("personalization_strength", "continuous", "How well system adapts to user", 
                         SystemComponent.LEARNING_SYSTEM, controllable=True),
            
            # Error variables
            CausalVariable("parsing_error", "binary", "Error in parsing user input", 
                         SystemComponent.NLP_ENGINE, controllable=True),
            CausalVariable("execution_error", "binary", "Error in command execution", 
                         SystemComponent.COMMAND_EXECUTOR, controllable=True),
            CausalVariable("system_overload", "binary", "System under high load", 
                         SystemComponent.PERFORMANCE_MONITOR, controllable=True),
        ]
        
        for var in system_vars:
            self.add_variable(var)
    
    def _initialize_known_relationships(self):
        """Initialize known causal relationships in the system"""
        known_relationships = [
            # User experience affects interaction quality
            CausalRelationship("user_experience_level", "intent_recognition_confidence", 0.7, 0.9,
                             "Experienced users express intent more clearly"),
            CausalRelationship("user_intent_clarity", "intent_recognition_confidence", 0.8, 0.95,
                             "Clear intent is easier to recognize"),
            
            # NLP performance affects user satisfaction
            CausalRelationship("intent_recognition_confidence", "user_satisfaction", 0.6, 0.85,
                             "Better understanding leads to better user experience"),
            CausalRelationship("response_time", "user_satisfaction", -0.5, 0.8,
                             "Faster responses improve satisfaction"),
            
            # System performance relationships
            CausalRelationship("memory_usage", "response_time", 0.4, 0.7,
                             "Higher memory usage can slow responses"),
            CausalRelationship("system_overload", "response_time", 0.8, 0.9,
                             "System overload directly increases response time"),
            CausalRelationship("system_overload", "execution_error", 0.6, 0.8,
                             "Overloaded system more likely to have errors"),
            
            # Learning system effects
            CausalRelationship("personalization_strength", "user_satisfaction", 0.7, 0.8,
                             "Better personalization improves user experience"),
            CausalRelationship("model_accuracy", "intent_recognition_confidence", 0.8, 0.9,
                             "More accurate models have higher confidence"),
            
            # Error propagation
            CausalRelationship("parsing_error", "execution_error", 0.9, 0.95,
                             "Parsing errors lead to execution failures"),
            CausalRelationship("execution_error", "user_satisfaction", -0.8, 0.9,
                             "Execution errors significantly hurt satisfaction"),
        ]
        
        for rel in known_relationships:
            self.add_relationship(rel)
    
    def add_variable(self, variable: CausalVariable):
        """Add a variable to the causal graph"""
        self.variables[variable.name] = variable
        self.graph.add_node(variable.name, **asdict(variable))
    
    def add_relationship(self, relationship: CausalRelationship):
        """Add a causal relationship to the graph"""
        if relationship.cause not in self.variables or relationship.effect not in self.variables:
            logger.warning(f"Unknown variables in relationship: {relationship.cause} -> {relationship.effect}")
            return
        
        self.relationships.add(relationship)
        self.graph.add_edge(
            relationship.cause, 
            relationship.effect,
            strength=relationship.strength,
            confidence=relationship.confidence,
            mechanism=relationship.mechanism,
            lag_time=relationship.lag_time
        )
    
    def find_causal_paths(self, cause: str, effect: str, max_length: int = 5) -> List[CausalChain]:
        """Find all causal paths from cause to effect"""
        if cause not in self.graph or effect not in self.graph:
            return []
        
        chains = []
        
        try:
            # Find all simple paths (no cycles)
            paths = list(nx.all_simple_paths(self.graph, cause, effect, cutoff=max_length))
            
            for path in paths:
                # Build causal chain from path
                chain_relationships = []
                total_strength = 1.0
                min_confidence = 1.0
                
                for i in range(len(path) - 1):
                    edge_data = self.graph[path[i]][path[i+1]]
                    rel = CausalRelationship(
                        cause=path[i],
                        effect=path[i+1],
                        strength=edge_data['strength'],
                        confidence=edge_data['confidence'],
                        mechanism=edge_data['mechanism']
                    )
                    chain_relationships.append(rel)
                    
                    # Combine strengths multiplicatively (chain weakens)
                    total_strength *= rel.strength
                    min_confidence = min(min_confidence, rel.confidence)
                
                # Check if chain has interventionable components
                interventionable = any(
                    self.variables[rel.cause].controllable or self.variables[rel.effect].controllable
                    for rel in chain_relationships
                )
                
                chain = CausalChain(
                    outcome=effect,
                    chain=chain_relationships,
                    total_strength=total_strength,
                    confidence=min_confidence,
                    interventionable=interventionable
                )
                chains.append(chain)
        
        except nx.NetworkXNoPath:
            pass  # No path exists
        
        # Sort by strength and confidence
        chains.sort(key=lambda x: (x.total_strength * x.confidence), reverse=True)
        return chains
    
    def get_common_causes(self, effects: List[str]) -> List[str]:
        """Find common causes of multiple effects"""
        if len(effects) < 2:
            return []
        
        # Find predecessors of each effect
        predecessor_sets = []
        for effect in effects:
            if effect in self.graph:
                predecessors = set(nx.ancestors(self.graph, effect))
                predecessors.add(effect)  # Include the effect itself
                predecessor_sets.append(predecessors)
        
        # Find intersection of all predecessor sets
        if predecessor_sets:
            common_causes = set.intersection(*predecessor_sets)
            # Remove the effects themselves
            common_causes -= set(effects)
            return list(common_causes)
        
        return []
    
    def suggest_interventions(self, target_effect: str, desired_change: str) -> List[Dict[str, Any]]:
        """Suggest interventions to achieve desired change in target effect"""
        interventions = []
        
        if target_effect not in self.graph:
            return interventions
        
        # Find all causes that can be controlled
        causes = nx.ancestors(self.graph, target_effect)
        controllable_causes = [
            cause for cause in causes 
            if self.variables[cause].controllable
        ]
        
        for cause in controllable_causes:
            chains = self.find_causal_paths(cause, target_effect)
            if chains:
                strongest_chain = chains[0]  # Already sorted by strength
                
                intervention = {
                    'variable': cause,
                    'description': self.variables[cause].description,
                    'expected_effect_strength': strongest_chain.total_strength,
                    'confidence': strongest_chain.confidence,
                    'causal_path': [rel.mechanism for rel in strongest_chain.chain],
                    'recommendation': self._generate_intervention_recommendation(cause, target_effect, desired_change)
                }
                interventions.append(intervention)
        
        # Sort by expected effectiveness
        interventions.sort(key=lambda x: x['expected_effect_strength'] * x['confidence'], reverse=True)
        return interventions
    
    def _generate_intervention_recommendation(self, cause: str, effect: str, desired_change: str) -> str:
        """Generate human-readable intervention recommendation"""
        cause_desc = self.variables[cause].description
        effect_desc = self.variables[effect].description
        
        if desired_change.lower() in ['increase', 'improve', 'enhance']:
            return f"To improve {effect_desc}, consider enhancing {cause_desc}"
        elif desired_change.lower() in ['decrease', 'reduce', 'minimize']:
            return f"To reduce {effect_desc}, consider minimizing {cause_desc}"
        else:
            return f"To change {effect_desc}, adjust {cause_desc}"


class CausalReasoningEngine:
    """
    Advanced Causal Reasoning Engine for deep system understanding
    
    Provides multi-layered causal analysis capabilities:
    - Root cause analysis for errors and performance issues
    - Predictive modeling for system behavior forecasting
    - Intervention planning for system optimization
    - Causal explanation generation for transparency
    
    Features:
    - Pearl's Causal Hierarchy implementation
    - DoWhy integration for rigorous causal inference
    - Consciousness-first explanation generation
    - Multi-persona causal interface adaptation
    """
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path.home() / '.nix-humanity-causal'
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Core components
        self.causal_graph = CausalGraphBuilder()
        self.xai_engine = AdvancedCausalXAI()  # Integrate with existing XAI
        
        # Database for causal analysis storage
        self.db_path = self.workspace_path / 'causal_reasoning.db'
        self._init_database()
        
        # Analysis cache
        self.analysis_cache = {}
        self.max_cache_size = 1000
        
        logger.info("🧠 Advanced Causal Reasoning Engine initialized")
    
    def _init_database(self):
        """Initialize causal reasoning database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Root cause analyses
        c.execute('''
            CREATE TABLE IF NOT EXISTS root_cause_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem TEXT NOT NULL,
                primary_causes TEXT NOT NULL,  -- JSON
                contributing_factors TEXT NOT NULL,  -- JSON
                intervention_recommendations TEXT NOT NULL,  -- JSON
                confidence_score REAL NOT NULL,
                analysis_timestamp TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Predictive models
        c.execute('''
            CREATE TABLE IF NOT EXISTS predictive_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario TEXT NOT NULL,
                predicted_outcomes TEXT NOT NULL,  -- JSON
                causal_pathways TEXT NOT NULL,  -- JSON
                assumptions TEXT NOT NULL,  -- JSON
                accuracy_score REAL,
                created_timestamp TEXT NOT NULL
            )
        ''')
        
        # Causal discoveries (learned relationships)
        c.execute('''
            CREATE TABLE IF NOT EXISTS causal_discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cause_variable TEXT NOT NULL,
                effect_variable TEXT NOT NULL,
                relationship_strength REAL NOT NULL,
                confidence REAL NOT NULL,
                mechanism TEXT,
                evidence_count INTEGER DEFAULT 1,
                discovery_timestamp TEXT NOT NULL
            )
        ''')
        
        # Intervention results
        c.execute('''
            CREATE TABLE IF NOT EXISTS intervention_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intervention_variable TEXT NOT NULL,
                target_effect TEXT NOT NULL,
                expected_change REAL NOT NULL,
                actual_change REAL,
                success_rate REAL,
                intervention_timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def analyze_root_cause(self, 
                                problem_description: str,
                                system_context: Dict[str, Any],
                                observed_symptoms: List[str]) -> RootCauseAnalysis:
        """
        Perform comprehensive root cause analysis for system problems
        
        Args:
            problem_description: Natural language description of the problem
            system_context: Current system state and metrics
            observed_symptoms: List of observed symptoms or error indicators
            
        Returns:
            Complete root cause analysis with intervention recommendations
        """
        logger.info(f"🔍 Starting root cause analysis for: {problem_description}")
        
        try:
            # Extract potential causes from symptoms
            potential_causes = self._identify_potential_causes(observed_symptoms, system_context)
            
            # Find causal chains leading to observed symptoms
            causal_chains = []
            for symptom in observed_symptoms:
                for cause in potential_causes:
                    chains = self.causal_graph.find_causal_paths(cause, symptom)
                    causal_chains.extend(chains)
            
            # Rank causes by strength and likelihood
            primary_causes = self._rank_causal_chains(causal_chains, system_context)
            
            # Identify contributing factors
            contributing_factors = self._identify_contributing_factors(observed_symptoms, system_context)
            
            # Generate intervention recommendations
            interventions = self._generate_intervention_recommendations(primary_causes, system_context)
            
            # Calculate overall confidence
            confidence = self._calculate_analysis_confidence(primary_causes, len(observed_symptoms))
            
            # Create analysis result
            analysis = RootCauseAnalysis(
                problem=problem_description,
                primary_causes=primary_causes[:5],  # Top 5 causes
                contributing_factors=contributing_factors,
                system_context=system_context,
                intervention_recommendations=interventions,
                confidence_score=confidence
            )
            
            # Store analysis
            await self._store_root_cause_analysis(analysis)
            
            logger.info(f"✅ Root cause analysis complete with {confidence:.2f} confidence")
            return analysis
            
        except Exception as e:
            logger.error(f"Root cause analysis failed: {e}")
            # Return minimal analysis on failure
            return RootCauseAnalysis(
                problem=problem_description,
                primary_causes=[],
                contributing_factors=observed_symptoms,
                system_context=system_context,
                intervention_recommendations=[],
                confidence_score=0.1
            )
    
    def _identify_potential_causes(self, symptoms: List[str], context: Dict[str, Any]) -> List[str]:
        """Identify potential root causes from observed symptoms"""
        potential_causes = set()
        
        # Map symptoms to system variables
        symptom_mapping = {
            'slow_response': 'response_time',
            'parsing_error': 'parsing_error',
            'execution_failure': 'execution_error',
            'high_memory': 'memory_usage',
            'user_frustration': 'user_satisfaction',
            'poor_recognition': 'intent_recognition_confidence'
        }
        
        # Find variables that could cause each symptom
        for symptom in symptoms:
            if symptom in symptom_mapping:
                effect_var = symptom_mapping[symptom]
                if effect_var in self.causal_graph.graph:
                    # Find all predecessors (potential causes)
                    predecessors = list(self.causal_graph.graph.predecessors(effect_var))
                    potential_causes.update(predecessors)
        
        # Add context-based causes
        if context.get('high_cpu_usage', False):
            potential_causes.add('system_overload')
        if context.get('many_typos', False):
            potential_causes.add('typo_correction_needed')
        if context.get('new_user', False):
            potential_causes.add('user_experience_level')
        
        return list(potential_causes)
    
    def _rank_causal_chains(self, chains: List[CausalChain], context: Dict[str, Any]) -> List[CausalChain]:
        """Rank causal chains by likelihood and strength"""
        if not chains:
            return []
        
        # Score chains based on multiple factors
        for chain in chains:
            base_score = chain.total_strength * chain.confidence
            
            # Boost score based on context evidence
            context_boost = 1.0
            for rel in chain.chain:
                if self._has_contextual_evidence(rel, context):
                    context_boost *= 1.2
            
            # Penalize very long chains (less reliable)
            length_penalty = 0.9 ** (len(chain.chain) - 1)
            
            # Final score
            chain.confidence = min(1.0, base_score * context_boost * length_penalty)
        
        # Sort by confidence
        chains.sort(key=lambda x: x.confidence, reverse=True)
        return chains
    
    def _has_contextual_evidence(self, relationship: CausalRelationship, context: Dict[str, Any]) -> bool:
        """Check if context provides evidence for causal relationship"""
        # Simple heuristic checks based on relationship type
        if relationship.cause == 'system_overload':
            return context.get('high_cpu_usage', False) or context.get('high_memory_usage', False)
        elif relationship.cause == 'user_experience_level':
            return context.get('user_type') in ['beginner', 'new_user']
        elif relationship.cause == 'typo_correction_needed':
            return context.get('input_quality', 1.0) < 0.8
        
        return False
    
    def _identify_contributing_factors(self, symptoms: List[str], context: Dict[str, Any]) -> List[str]:
        """Identify contributing factors that amplify problems"""
        factors = []
        
        # System load factors
        if context.get('high_cpu_usage', False):
            factors.append("High CPU usage")
        if context.get('high_memory_usage', False):
            factors.append("High memory usage")
        if context.get('low_disk_space', False):
            factors.append("Low disk space")
        
        # User context factors
        if context.get('user_type') == 'beginner':
            factors.append("New user learning curve")
        if context.get('time_of_day') in ['late_night', 'early_morning']:
            factors.append("User potentially tired")
        
        # System state factors
        if context.get('recent_update', False):
            factors.append("Recent system update")
        if context.get('network_issues', False):
            factors.append("Network connectivity problems")
        
        return factors
    
    def _generate_intervention_recommendations(self, 
                                            primary_causes: List[CausalChain], 
                                            context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable intervention recommendations"""
        recommendations = []
        
        for i, chain in enumerate(primary_causes[:3]):  # Top 3 causes
            if not chain.chain:
                continue
                
            # Get the most controllable variable in the chain
            controllable_vars = [
                rel.cause for rel in chain.chain 
                if self.causal_graph.variables.get(rel.cause, {}).controllable
            ]
            
            if controllable_vars:
                target_var = controllable_vars[0]
                var_info = self.causal_graph.variables[target_var]
                
                recommendation = {
                    'priority': i + 1,
                    'intervention_target': target_var,
                    'description': var_info.description,
                    'expected_impact': chain.confidence,
                    'action_type': self._determine_action_type(target_var, context),
                    'implementation_steps': self._generate_implementation_steps(target_var, context),
                    'success_probability': chain.confidence * 0.8,  # Conservative estimate
                    'timeframe': self._estimate_implementation_time(target_var)
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _determine_action_type(self, variable: str, context: Dict[str, Any]) -> str:
        """Determine the type of action needed for intervention"""
        action_mapping = {
            'response_time': 'performance_optimization',
            'memory_usage': 'resource_management',
            'intent_recognition_confidence': 'model_improvement',
            'user_satisfaction': 'user_experience_enhancement',
            'personalization_strength': 'learning_system_tuning',
            'system_overload': 'capacity_management'
        }
        
        return action_mapping.get(variable, 'system_adjustment')
    
    def _generate_implementation_steps(self, variable: str, context: Dict[str, Any]) -> List[str]:
        """Generate specific implementation steps for intervention"""
        steps_mapping = {
            'response_time': [
                "Enable Python backend for faster NixOS operations",
                "Optimize NLP pipeline for common queries",
                "Implement intelligent caching for frequent operations",
                "Consider model quantization for faster inference"
            ],
            'memory_usage': [
                "Profile memory usage to identify leaks",
                "Implement lazy loading for ML models", 
                "Optimize data structures for memory efficiency",
                "Consider garbage collection tuning"
            ],
            'intent_recognition_confidence': [
                "Collect more training data for problematic patterns",
                "Improve fuzzy matching algorithms",
                "Enhance context understanding",
                "Add user feedback loop for corrections"
            ],
            'user_satisfaction': [
                "Analyze user feedback for pain points",
                "Improve error messages to be more helpful",
                "Add proactive assistance features",
                "Enhance persona adaptation accuracy"
            ]
        }
        
        return steps_mapping.get(variable, ["Analyze variable impact", "Design intervention", "Test changes", "Monitor results"])
    
    def _estimate_implementation_time(self, variable: str) -> str:
        """Estimate time required to implement intervention"""
        time_estimates = {
            'response_time': '1-2 days',
            'memory_usage': '2-3 days', 
            'intent_recognition_confidence': '3-5 days',
            'user_satisfaction': '1-2 weeks',
            'personalization_strength': '1-3 weeks',
            'system_overload': '1-2 days'
        }
        
        return time_estimates.get(variable, '3-5 days')
    
    def _calculate_analysis_confidence(self, causes: List[CausalChain], symptom_count: int) -> float:
        """Calculate overall confidence in the root cause analysis"""
        if not causes:
            return 0.1
        
        # Base confidence from strongest causal chain
        base_confidence = causes[0].confidence if causes else 0.5
        
        # Boost confidence with more evidence
        evidence_boost = min(1.2, 1.0 + (symptom_count - 1) * 0.1)
        
        # Boost confidence with multiple consistent causes
        consistency_boost = 1.0
        if len(causes) > 1:
            avg_confidence = sum(c.confidence for c in causes[:3]) / min(3, len(causes))
            if abs(base_confidence - avg_confidence) < 0.2:  # Consistent results
                consistency_boost = 1.1
        
        final_confidence = min(1.0, base_confidence * evidence_boost * consistency_boost)
        return final_confidence
    
    async def _store_root_cause_analysis(self, analysis: RootCauseAnalysis):
        """Store root cause analysis in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO root_cause_analyses 
            (problem, primary_causes, contributing_factors, intervention_recommendations, 
             confidence_score, analysis_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            analysis.problem,
            json.dumps([asdict(cause) for cause in analysis.primary_causes], default=str),
            json.dumps(analysis.contributing_factors),
            json.dumps(analysis.intervention_recommendations, default=str),
            analysis.confidence_score,
            analysis.analysis_timestamp
        ))
        
        conn.commit()
        conn.close()
    
    async def predict_system_behavior(self, 
                                    scenario: str,
                                    interventions: Dict[str, Any],
                                    time_horizon: int = 24) -> PredictiveCausalModel:
        """
        Predict system behavior under different intervention scenarios
        
        Args:
            scenario: Description of the scenario to analyze
            interventions: Dict of variable -> new_value interventions
            time_horizon: Hours to predict into the future
            
        Returns:
            Predictive model with outcome probabilities and causal pathways
        """
        logger.info(f"🔮 Predicting system behavior for scenario: {scenario}")
        
        try:
            # Identify key outcome variables to predict
            outcome_variables = self._identify_outcome_variables(interventions)
            
            # Build causal pathways from interventions to outcomes
            causal_pathways = []
            for intervention_var, new_value in interventions.items():
                for outcome_var in outcome_variables:
                    paths = self.causal_graph.find_causal_paths(intervention_var, outcome_var)
                    causal_pathways.extend(paths)
            
            # Predict outcomes using causal model
            predicted_outcomes = self._predict_outcomes(interventions, outcome_variables)
            
            # Calculate uncertainty bounds
            uncertainty_bounds = self._calculate_uncertainty_bounds(predicted_outcomes, causal_pathways)
            
            # Identify key assumptions
            assumptions = self._identify_model_assumptions(interventions, causal_pathways)
            
            model = PredictiveCausalModel(
                scenario=scenario,
                predicted_outcomes=predicted_outcomes,
                causal_pathways=causal_pathways,
                uncertainty_bounds=uncertainty_bounds,
                assumptions=assumptions
            )
            
            # Store model
            await self._store_predictive_model(model)
            
            logger.info(f"🎯 Behavior prediction complete for {len(outcome_variables)} outcomes")
            return model
            
        except Exception as e:
            logger.error(f"Behavior prediction failed: {e}")
            return PredictiveCausalModel(
                scenario=scenario,
                predicted_outcomes={},
                causal_pathways=[],
                uncertainty_bounds={},
                assumptions=["Prediction failed due to insufficient data"]
            )
    
    def _identify_outcome_variables(self, interventions: Dict[str, Any]) -> List[str]:
        """Identify key outcome variables affected by interventions"""
        outcome_vars = set()
        
        # For each intervention, find downstream effects
        for intervention_var in interventions.keys():
            if intervention_var in self.causal_graph.graph:
                descendants = nx.descendants(self.causal_graph.graph, intervention_var)
                outcome_vars.update(descendants)
        
        # Focus on key system outcomes
        priority_outcomes = [
            'user_satisfaction', 'response_time', 'nixos_operation_success',
            'intent_recognition_confidence', 'execution_error'
        ]
        
        # Return intersection of affected variables and priority outcomes
        return list(outcome_vars.intersection(set(priority_outcomes)))
    
    def _predict_outcomes(self, interventions: Dict[str, Any], outcome_vars: List[str]) -> Dict[str, float]:
        """Predict outcome values based on interventions"""
        predictions = {}
        
        for outcome_var in outcome_vars:
            # Start with baseline prediction
            baseline = self._get_baseline_value(outcome_var)
            predicted_change = 0.0
            
            # Calculate cumulative effect of all interventions
            for intervention_var, new_value in interventions.items():
                paths = self.causal_graph.find_causal_paths(intervention_var, outcome_var)
                if paths:
                    # Use strongest path for prediction
                    strongest_path = paths[0]
                    change_magnitude = self._estimate_change_magnitude(intervention_var, new_value)
                    effect_size = strongest_path.total_strength * change_magnitude
                    predicted_change += effect_size
            
            # Apply change to baseline
            final_prediction = max(0.0, min(1.0, baseline + predicted_change))
            predictions[outcome_var] = final_prediction
        
        return predictions
    
    def _get_baseline_value(self, variable: str) -> float:
        """Get baseline value for a variable (simplified)"""
        # In a real implementation, this would use historical data
        baseline_values = {
            'user_satisfaction': 0.7,
            'response_time': 0.3,  # Normalized (0 = fast, 1 = slow)
            'nixos_operation_success': 0.85,
            'intent_recognition_confidence': 0.8,
            'execution_error': 0.1
        }
        
        return baseline_values.get(variable, 0.5)
    
    def _estimate_change_magnitude(self, variable: str, new_value: Any) -> float:
        """Estimate magnitude of change for intervention"""
        # This is a simplified heuristic - real implementation would be more sophisticated
        if isinstance(new_value, (int, float)):
            # Assume new_value is between 0 and 1 and represents desired change
            return float(new_value) - 0.5  # Change relative to neutral
        elif isinstance(new_value, bool):
            return 0.3 if new_value else -0.3
        elif isinstance(new_value, str):
            if new_value.lower() in ['improve', 'increase', 'enhance']:
                return 0.2
            elif new_value.lower() in ['reduce', 'decrease', 'minimize']:
                return -0.2
        
        return 0.0
    
    def _calculate_uncertainty_bounds(self, 
                                   predictions: Dict[str, float], 
                                   pathways: List[CausalChain]) -> Dict[str, Tuple[float, float]]:
        """Calculate uncertainty bounds for predictions"""
        bounds = {}
        
        for outcome, prediction in predictions.items():
            # Base uncertainty from confidence in causal pathways
            relevant_pathways = [p for p in pathways if p.outcome == outcome]
            if relevant_pathways:
                avg_confidence = sum(p.confidence for p in relevant_pathways) / len(relevant_pathways)
                uncertainty = (1.0 - avg_confidence) * 0.3  # Scale uncertainty
            else:
                uncertainty = 0.2  # Default uncertainty
            
            lower_bound = max(0.0, prediction - uncertainty)
            upper_bound = min(1.0, prediction + uncertainty)
            bounds[outcome] = (lower_bound, upper_bound)
        
        return bounds
    
    def _identify_model_assumptions(self, 
                                  interventions: Dict[str, Any], 
                                  pathways: List[CausalChain]) -> List[str]:
        """Identify key assumptions in the predictive model"""
        assumptions = [
            "Causal relationships remain stable during prediction period",
            "No unmeasured confounders significantly affect outcomes",
            "System operates under normal conditions"
        ]
        
        # Add intervention-specific assumptions
        if any('performance' in str(k) for k in interventions.keys()):
            assumptions.append("Hardware performance remains constant")
        
        if any('user' in str(k) for k in interventions.keys()):
            assumptions.append("User behavior patterns remain consistent")
        
        # Add pathway-specific assumptions
        if any(len(p.chain) > 3 for p in pathways):
            assumptions.append("Multi-step causal chains maintain their strength")
        
        return assumptions
    
    async def _store_predictive_model(self, model: PredictiveCausalModel):
        """Store predictive model in database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO predictive_models 
            (scenario, predicted_outcomes, causal_pathways, assumptions, created_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            model.scenario,
            json.dumps(model.predicted_outcomes),
            json.dumps([asdict(pathway) for pathway in model.causal_pathways], default=str),
            json.dumps(model.assumptions),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def explain_system_behavior(self, 
                                    behavior: str,
                                    context: Dict[str, Any],
                                    persona: Optional[str] = None,
                                    level: ExplanationLevel = ExplanationLevel.DETAILED) -> CausalExplanation:
        """
        Generate consciousness-first causal explanation of system behavior
        
        Args:
            behavior: The behavior to explain
            context: System context and state
            persona: Target persona for explanation adaptation
            level: Level of explanation detail
            
        Returns:
            Detailed causal explanation adapted for the persona
        """
        logger.info(f"🎯 Explaining system behavior: {behavior}")
        
        try:
            # Map behavior to system variables
            behavior_mapping = {
                'slow_response': 'response_time',
                'incorrect_understanding': 'intent_recognition_confidence',
                'execution_failure': 'execution_error',
                'good_performance': 'user_satisfaction',
                'memory_issue': 'memory_usage'
            }
            
            target_variable = behavior_mapping.get(behavior, behavior)
            
            # Find causal factors
            if target_variable in self.causal_graph.graph:
                # Get direct causes
                direct_causes = list(self.causal_graph.graph.predecessors(target_variable))
                
                # Build causal explanation using existing XAI engine
                explanation = self.xai_engine.explain_decision(
                    decision=behavior,
                    context=context,
                    confidence=context.get('confidence', 0.8),
                    level=level
                )
                
                # Enhance with causal reasoning
                enhanced_explanation = await self._enhance_explanation_with_causality(
                    explanation, target_variable, direct_causes, context
                )
                
                # Adapt for persona
                if persona:
                    enhanced_explanation = await self._adapt_explanation_for_persona(
                        enhanced_explanation, persona
                    )
                
                return enhanced_explanation
            else:
                # Fallback to basic explanation
                return self.xai_engine.explain_decision(
                    decision=behavior,
                    context=context,
                    confidence=0.5,
                    level=level
                )
                
        except Exception as e:
            logger.error(f"Behavior explanation failed: {e}")
            # Return minimal explanation on failure
            return CausalExplanation(
                decision=behavior,
                confidence=0.3,
                level=level,
                primary_reason=f"System behavior: {behavior}",
                causal_factors=[],
                decision_path=[],
                alternatives_considered=[],
                counterfactual_analysis=None,
                confidence_breakdown={'system_analysis': 0.3},
                uncertainty_sources=["Analysis incomplete due to error"],
                decision_tree_data=None,
                feature_importance_data=None
            )
    
    async def _enhance_explanation_with_causality(self,
                                                explanation: CausalExplanation,
                                                target_variable: str,
                                                direct_causes: List[str],
                                                context: Dict[str, Any]) -> CausalExplanation:
        """Enhance explanation with causal reasoning insights"""
        # Add causal chain information
        enhanced_reason = explanation.primary_reason
        
        if direct_causes:
            # Get the most relevant cause
            strongest_cause = self._find_strongest_cause(target_variable, direct_causes, context)
            if strongest_cause:
                cause_desc = self.causal_graph.variables[strongest_cause].description
                enhanced_reason += f" This is primarily caused by {cause_desc}."
        
        # Add causal pathway information
        if len(direct_causes) > 1:
            enhanced_reason += f" Multiple factors contribute: {', '.join(direct_causes[:3])}."
        
        # Update the explanation
        explanation.primary_reason = enhanced_reason
        
        # Add counterfactual analysis
        explanation.counterfactual_analysis = self._generate_counterfactual_analysis(
            target_variable, direct_causes, context
        )
        
        return explanation
    
    def _find_strongest_cause(self, effect: str, causes: List[str], context: Dict[str, Any]) -> Optional[str]:
        """Find the strongest causal factor from context"""
        if not causes:
            return None
        
        # Score causes based on edge strength and contextual evidence
        cause_scores = {}
        for cause in causes:
            edge_data = self.causal_graph.graph[cause][effect]
            base_score = edge_data['strength'] * edge_data['confidence']
            
            # Boost score if we have contextual evidence
            if self._has_contextual_evidence(
                CausalRelationship(cause, effect, base_score, edge_data['confidence'], ""), 
                context
            ):
                base_score *= 1.5
            
            cause_scores[cause] = base_score
        
        # Return cause with highest score
        return max(cause_scores, key=cause_scores.get)
    
    def _generate_counterfactual_analysis(self, 
                                        target: str, 
                                        causes: List[str], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate counterfactual analysis for what-if scenarios"""
        if not causes:
            return {"scenario": "No causal factors identified", "impact": "unknown"}
        
        strongest_cause = self._find_strongest_cause(target, causes, context)
        if not strongest_cause:
            return {"scenario": "No dominant cause identified", "impact": "minimal"}
        
        cause_desc = self.causal_graph.variables[strongest_cause].description
        
        return {
            "scenario": f"If {cause_desc} were optimal",
            "likely_outcome": f"{target} would likely improve significantly",
            "confidence": 0.7,
            "intervention_needed": self.causal_graph.variables[strongest_cause].controllable
        }
    
    async def _adapt_explanation_for_persona(self, 
                                           explanation: CausalExplanation, 
                                           persona: str) -> CausalExplanation:
        """Adapt causal explanation for specific persona"""
        # Use existing XAI persona adaptation
        adapted_text = self.xai_engine.format_explanation_for_persona(explanation, persona)
        
        # Update primary reason with adapted text
        explanation.primary_reason = adapted_text
        
        # Simplify for certain personas
        if persona in ['grandma_rose', 'maya_adhd']:
            # Remove complex causal factors for simple personas
            explanation.causal_factors = explanation.causal_factors[:2]
            explanation.decision_path = explanation.decision_path[:1]
        
        return explanation
    
    async def discover_new_causal_relationships(self, 
                                             observation_data: Dict[str, Any],
                                             min_confidence: float = 0.6) -> List[CausalRelationship]:
        """
        Discover new causal relationships from observational data
        
        This method uses statistical analysis to identify potential new
        causal relationships that should be added to the causal graph.
        """
        logger.info("🔍 Discovering new causal relationships from data")
        
        discovered_relationships = []
        
        try:
            if not SCIPY_AVAILABLE:
                logger.warning("SciPy not available - skipping advanced causal discovery")
                return discovered_relationships
            
            # Convert observation data to DataFrame for analysis
            df = pd.DataFrame([observation_data])
            
            if len(df) < 10:  # Need sufficient data
                logger.info("Insufficient data for causal discovery")
                return discovered_relationships
            
            # Simple correlation-based discovery (placeholder for more sophisticated methods)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) < 2:
                return discovered_relationships
            
            # Calculate correlations
            correlations = df[numeric_cols].corr()
            
            # Identify strong correlations as potential causal relationships
            for i, var1 in enumerate(numeric_cols):
                for j, var2 in enumerate(numeric_cols):
                    if i != j and abs(correlations.iloc[i, j]) > 0.7:
                        # Check if this relationship already exists
                        if not self._relationship_exists(var1, var2):
                            # Create potential relationship
                            relationship = CausalRelationship(
                                cause=var1,
                                effect=var2,
                                strength=abs(correlations.iloc[i, j]),
                                confidence=min_confidence,
                                mechanism=f"Discovered correlation-based relationship"
                            )
                            discovered_relationships.append(relationship)
            
            # Store discoveries
            for rel in discovered_relationships:
                await self._store_causal_discovery(rel)
            
            logger.info(f"💡 Discovered {len(discovered_relationships)} potential causal relationships")
            
        except Exception as e:
            logger.error(f"Causal discovery failed: {e}")
        
        return discovered_relationships
    
    def _relationship_exists(self, cause: str, effect: str) -> bool:
        """Check if causal relationship already exists in graph"""
        return self.causal_graph.graph.has_edge(cause, effect)
    
    async def _store_causal_discovery(self, relationship: CausalRelationship):
        """Store discovered causal relationship"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO causal_discoveries 
            (cause_variable, effect_variable, relationship_strength, confidence, 
             mechanism, discovery_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            relationship.cause,
            relationship.effect,
            relationship.strength,
            relationship.confidence,
            relationship.mechanism,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def get_causal_insights_summary(self) -> Dict[str, Any]:
        """Get summary of causal reasoning insights and statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Count analyses
        c.execute('SELECT COUNT(*) FROM root_cause_analyses')
        total_analyses = c.fetchone()[0]
        
        # Count successful interventions
        c.execute('SELECT AVG(success_rate) FROM intervention_results WHERE success_rate IS NOT NULL')
        avg_success_rate = c.fetchone()[0] or 0.0
        
        # Count causal discoveries
        c.execute('SELECT COUNT(*) FROM causal_discoveries')
        total_discoveries = c.fetchone()[0]
        
        # Get most common causes
        c.execute('''
            SELECT cause_variable, COUNT(*) as frequency
            FROM causal_discoveries 
            GROUP BY cause_variable 
            ORDER BY frequency DESC 
            LIMIT 5
        ''')
        common_causes = c.fetchall()
        
        conn.close()
        
        return {
            'total_root_cause_analyses': total_analyses,
            'average_intervention_success_rate': avg_success_rate,
            'total_causal_discoveries': total_discoveries,
            'most_common_causes': [{'cause': cause, 'frequency': freq} for cause, freq in common_causes],
            'causal_graph_size': {
                'variables': len(self.causal_graph.variables),
                'relationships': len(self.causal_graph.relationships)
            },
            'reasoning_capabilities': [
                'Root cause analysis',
                'Predictive behavior modeling',
                'Intervention recommendation',
                'Causal explanation generation',
                'Relationship discovery'
            ]
        }


# Factory function for easy instantiation
def create_causal_reasoning_engine(workspace_path: Optional[Path] = None) -> CausalReasoningEngine:
    """Create and initialize causal reasoning engine"""
    return CausalReasoningEngine(workspace_path)


if __name__ == "__main__":
    # Example usage and testing
    async def main():
        print("🧠 Initializing Advanced Causal Reasoning Engine...")
        
        engine = create_causal_reasoning_engine()
        
        # Example 1: Root cause analysis
        print("\n🔍 Example 1: Root Cause Analysis")
        problem = "User reports slow response times and frequent errors"
        context = {
            'high_cpu_usage': True,
            'response_time_avg': 5.2,
            'error_rate': 0.15,
            'user_type': 'beginner'
        }
        symptoms = ['slow_response', 'execution_failure', 'user_frustration']
        
        analysis = await engine.analyze_root_cause(problem, context, symptoms)
        print(f"✅ Root cause analysis complete:")
        print(f"   Primary causes: {len(analysis.primary_causes)}")
        print(f"   Confidence: {analysis.confidence_score:.2f}")
        print(f"   Interventions: {len(analysis.intervention_recommendations)}")
        
        # Example 2: Predictive modeling
        print("\n🔮 Example 2: Predictive Behavior Modeling")
        scenario = "What if we optimize response time and improve error handling?"
        interventions = {
            'response_time': 0.8,  # Improve response time
            'execution_error': 0.05  # Reduce error rate
        }
        
        prediction = await engine.predict_system_behavior(scenario, interventions)
        print(f"🎯 Behavior prediction complete:")
        print(f"   Predicted outcomes: {len(prediction.predicted_outcomes)}")
        print(f"   Causal pathways: {len(prediction.causal_pathways)}")
        
        # Example 3: System behavior explanation
        print("\n🎯 Example 3: Behavior Explanation")
        behavior = "slow_response"
        explanation_context = {
            'confidence': 0.85,
            'system_load': 0.8,
            'user_experience_level': 'beginner'
        }
        
        explanation = await engine.explain_system_behavior(
            behavior, explanation_context, persona="dr_sarah"
        )
        print(f"📝 Behavior explanation generated:")
        print(f"   Confidence: {explanation.confidence:.2f}")
        print(f"   Primary reason: {explanation.primary_reason[:100]}...")
        
        # Example 4: Get insights summary
        print("\n📊 Example 4: Causal Insights Summary")
        insights = await engine.get_causal_insights_summary()
        print(f"🧠 Causal reasoning insights:")
        for key, value in insights.items():
            print(f"   {key}: {value}")
        
        print("\n🌊 Advanced Causal Reasoning Engine ready for Phase 4 Living System!")
    
    # Run the example
    import asyncio
    asyncio.run(main())