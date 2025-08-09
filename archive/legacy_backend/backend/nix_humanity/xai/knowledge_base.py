"""
from typing import Dict, List, Optional
Causal Knowledge Base for NixOS operations

Stores causal relationships and models for different operation types.
"""

from typing import Dict, List, Any, Optional
import networkx as nx
from dataclasses import dataclass


@dataclass
class CausalNode:
    """Represents a node in a causal graph"""
    id: str
    name: str
    node_type: str  # 'observed', 'treatment', 'outcome', 'confounder'
    description: str
    value_type: str  # 'boolean', 'numeric', 'categorical'
    possible_values: Optional[List[Any]] = None


@dataclass
class CausalEdge:
    """Represents a causal relationship"""
    from_node: str
    to_node: str
    mechanism: str  # 'direct', 'mediated', 'moderated'
    strength: float  # 0.0 to 1.0
    description: str


class CausalKnowledgeBase:
    """
    Stores causal models for NixOS operations.
    
    This knowledge base contains pre-defined causal relationships
    that help explain why certain decisions are made.
    """
    
    def __init__(self):
        self.operation_models = self._initialize_operation_models()
        self.user_patterns = self._initialize_user_patterns()
        self.system_constraints = self._initialize_constraints()
    
    def _initialize_operation_models(self) -> Dict[str, Dict]:
        """Define causal models for each operation type"""
        return {
            'install_package': self._create_install_package_model(),
            'update_system': self._create_update_system_model(),
            'remove_package': self._create_remove_package_model(),
            'rollback_system': self._create_rollback_model(),
            'search_package': self._create_search_model(),
            'check_status': self._create_status_check_model(),
        }
    
    def _create_install_package_model(self) -> Dict:
        """Causal model for package installation decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='user_need',
                    name='User Need',
                    node_type='observed',
                    description='What the user wants to accomplish',
                    value_type='categorical',
                    possible_values=['web_browser', 'text_editor', 'development_tool', 'multimedia', 'utility']
                ),
                CausalNode(
                    id='package_match',
                    name='Package Match Score',
                    node_type='observed',
                    description='How well the package matches the user need',
                    value_type='numeric'
                ),
                CausalNode(
                    id='package_availability',
                    name='Package Availability',
                    node_type='observed',
                    description='Whether package exists in nixpkgs',
                    value_type='boolean'
                ),
                CausalNode(
                    id='system_compatibility',
                    name='System Compatibility',
                    node_type='observed',
                    description='Whether system meets package requirements',
                    value_type='boolean'
                ),
                CausalNode(
                    id='disk_space',
                    name='Available Disk Space',
                    node_type='observed',
                    description='Sufficient space for installation',
                    value_type='boolean'
                ),
                CausalNode(
                    id='user_preference',
                    name='User Preferences',
                    node_type='confounder',
                    description='User\'s historical preferences',
                    value_type='categorical',
                    possible_values=['open_source', 'popular', 'lightweight', 'feature_rich']
                ),
                CausalNode(
                    id='installation_method',
                    name='Installation Method',
                    node_type='treatment',
                    description='How to install the package',
                    value_type='categorical',
                    possible_values=['declarative', 'imperative', 'user_profile']
                ),
                CausalNode(
                    id='installation_success',
                    name='Installation Success',
                    node_type='outcome',
                    description='Whether installation succeeds',
                    value_type='boolean'
                ),
                CausalNode(
                    id='user_satisfaction',
                    name='User Satisfaction',
                    node_type='outcome',
                    description='Whether user is satisfied with result',
                    value_type='numeric'
                )
            ],
            'edges': [
                CausalEdge('user_need', 'package_match', 'direct', 0.9, 'User need determines package selection'),
                CausalEdge('package_match', 'installation_success', 'direct', 0.8, 'Better match increases success'),
                CausalEdge('package_availability', 'installation_success', 'direct', 1.0, 'Must be available to install'),
                CausalEdge('system_compatibility', 'installation_success', 'direct', 0.9, 'Compatibility affects success'),
                CausalEdge('disk_space', 'installation_success', 'direct', 0.7, 'Space needed for installation'),
                CausalEdge('user_preference', 'package_match', 'direct', 0.6, 'Preferences influence selection'),
                CausalEdge('user_preference', 'installation_method', 'direct', 0.5, 'Preferences affect method choice'),
                CausalEdge('installation_method', 'installation_success', 'direct', 0.4, 'Method affects success rate'),
                CausalEdge('installation_success', 'user_satisfaction', 'direct', 0.9, 'Success leads to satisfaction'),
                CausalEdge('package_match', 'user_satisfaction', 'direct', 0.7, 'Good match increases satisfaction')
            ]
        }
    
    def _create_update_system_model(self) -> Dict:
        """Causal model for system update decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='current_generation',
                    name='Current System Generation',
                    node_type='observed',
                    description='Current NixOS generation number',
                    value_type='numeric'
                ),
                CausalNode(
                    id='available_updates',
                    name='Available Updates',
                    node_type='observed',
                    description='Number of packages with updates',
                    value_type='numeric'
                ),
                CausalNode(
                    id='security_updates',
                    name='Security Updates',
                    node_type='observed',
                    description='Whether security updates are available',
                    value_type='boolean'
                ),
                CausalNode(
                    id='system_stability',
                    name='System Stability',
                    node_type='observed',
                    description='Current system stability score',
                    value_type='numeric'
                ),
                CausalNode(
                    id='last_update_days',
                    name='Days Since Last Update',
                    node_type='observed',
                    description='Days since system was last updated',
                    value_type='numeric'
                ),
                CausalNode(
                    id='update_method',
                    name='Update Method',
                    node_type='treatment',
                    description='How to perform the update',
                    value_type='categorical',
                    possible_values=['switch', 'boot', 'test']
                ),
                CausalNode(
                    id='update_success',
                    name='Update Success',
                    node_type='outcome',
                    description='Whether update completes successfully',
                    value_type='boolean'
                ),
                CausalNode(
                    id='system_improvement',
                    name='System Improvement',
                    node_type='outcome',
                    description='Improvement in system performance/security',
                    value_type='numeric'
                )
            ],
            'edges': [
                CausalEdge('available_updates', 'system_improvement', 'direct', 0.7, 'Updates improve system'),
                CausalEdge('security_updates', 'system_improvement', 'direct', 0.9, 'Security updates critical'),
                CausalEdge('security_updates', 'update_method', 'direct', 0.8, 'Security affects urgency'),
                CausalEdge('system_stability', 'update_success', 'direct', 0.8, 'Stable systems update better'),
                CausalEdge('last_update_days', 'available_updates', 'direct', 0.6, 'Time increases updates'),
                CausalEdge('update_method', 'update_success', 'direct', 0.5, 'Method affects success'),
                CausalEdge('update_success', 'system_improvement', 'direct', 1.0, 'Success required for improvement')
            ]
        }
    
    def _create_remove_package_model(self) -> Dict:
        """Causal model for package removal decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='package_unused',
                    name='Package Unused',
                    node_type='observed',
                    description='Whether package is actively used',
                    value_type='boolean'
                ),
                CausalNode(
                    id='disk_pressure',
                    name='Disk Space Pressure',
                    node_type='observed',
                    description='Need to free disk space',
                    value_type='numeric'
                ),
                CausalNode(
                    id='dependencies',
                    name='Package Dependencies',
                    node_type='observed',
                    description='Other packages depending on this',
                    value_type='numeric'
                ),
                CausalNode(
                    id='removal_method',
                    name='Removal Method',
                    node_type='treatment',
                    description='How to remove the package',
                    value_type='categorical',
                    possible_values=['immediate', 'garbage_collect', 'profile_update']
                ),
                CausalNode(
                    id='removal_success',
                    name='Removal Success',
                    node_type='outcome',
                    description='Whether removal succeeds',
                    value_type='boolean'
                ),
                CausalNode(
                    id='space_freed',
                    name='Space Freed',
                    node_type='outcome',
                    description='Amount of disk space recovered',
                    value_type='numeric'
                )
            ],
            'edges': [
                CausalEdge('package_unused', 'removal_success', 'direct', 0.9, 'Unused packages safe to remove'),
                CausalEdge('dependencies', 'removal_success', 'direct', -0.8, 'Dependencies prevent removal'),
                CausalEdge('disk_pressure', 'removal_method', 'direct', 0.7, 'Pressure affects urgency'),
                CausalEdge('removal_method', 'removal_success', 'direct', 0.5, 'Method affects success'),
                CausalEdge('removal_success', 'space_freed', 'direct', 1.0, 'Success frees space')
            ]
        }
    
    def _create_rollback_model(self) -> Dict:
        """Causal model for system rollback decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='system_broken',
                    name='System Issues',
                    node_type='observed',
                    description='Current system has problems',
                    value_type='boolean'
                ),
                CausalNode(
                    id='previous_generation_stable',
                    name='Previous Generation Stable',
                    node_type='observed',
                    description='Previous generation was stable',
                    value_type='boolean'
                ),
                CausalNode(
                    id='generations_available',
                    name='Available Generations',
                    node_type='observed',
                    description='Number of generations to rollback to',
                    value_type='numeric'
                ),
                CausalNode(
                    id='rollback_distance',
                    name='Rollback Distance',
                    node_type='treatment',
                    description='How many generations to roll back',
                    value_type='numeric'
                ),
                CausalNode(
                    id='rollback_success',
                    name='Rollback Success',
                    node_type='outcome',
                    description='Whether rollback succeeds',
                    value_type='boolean'
                ),
                CausalNode(
                    id='system_restored',
                    name='System Restored',
                    node_type='outcome',
                    description='System functionality restored',
                    value_type='boolean'
                )
            ],
            'edges': [
                CausalEdge('system_broken', 'rollback_distance', 'direct', 0.8, 'Problems trigger rollback'),
                CausalEdge('previous_generation_stable', 'rollback_success', 'direct', 0.9, 'Stable target helps'),
                CausalEdge('generations_available', 'rollback_success', 'direct', 0.7, 'Need available generations'),
                CausalEdge('rollback_distance', 'rollback_success', 'direct', -0.3, 'Further rollback riskier'),
                CausalEdge('rollback_success', 'system_restored', 'direct', 0.95, 'Success restores system')
            ]
        }
    
    def _create_search_model(self) -> Dict:
        """Causal model for package search decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='search_terms',
                    name='Search Terms Quality',
                    node_type='observed',
                    description='Quality and specificity of search terms',
                    value_type='numeric'
                ),
                CausalNode(
                    id='category_filter',
                    name='Category Filter',
                    node_type='treatment',
                    description='Whether to filter by category',
                    value_type='boolean'
                ),
                CausalNode(
                    id='search_results',
                    name='Search Results Quality',
                    node_type='outcome',
                    description='Relevance of search results',
                    value_type='numeric'
                )
            ],
            'edges': [
                CausalEdge('search_terms', 'search_results', 'direct', 0.9, 'Better terms improve results'),
                CausalEdge('category_filter', 'search_results', 'direct', 0.6, 'Filtering improves relevance')
            ]
        }
    
    def _create_status_check_model(self) -> Dict:
        """Causal model for system status check decisions"""
        return {
            'nodes': [
                CausalNode(
                    id='check_type',
                    name='Status Check Type',
                    node_type='treatment',
                    description='What aspect to check',
                    value_type='categorical',
                    possible_values=['disk_space', 'memory', 'updates', 'services']
                ),
                CausalNode(
                    id='information_quality',
                    name='Information Quality',
                    node_type='outcome',
                    description='Quality of status information',
                    value_type='numeric'
                )
            ],
            'edges': [
                CausalEdge('check_type', 'information_quality', 'direct', 1.0, 'Type determines info')
            ]
        }
    
    def _initialize_user_patterns(self) -> Dict[str, Any]:
        """Initialize common user behavior patterns"""
        return {
            'beginner': {
                'prefers_simple': True,
                'needs_confirmations': True,
                'common_operations': ['install', 'search', 'update']
            },
            'developer': {
                'prefers_declarative': True,
                'uses_advanced_features': True,
                'common_operations': ['install', 'shell', 'rollback']
            },
            'sysadmin': {
                'monitors_system': True,
                'automates_tasks': True,
                'common_operations': ['update', 'status', 'rollback']
            }
        }
    
    def _initialize_constraints(self) -> Dict[str, Any]:
        """Initialize system constraints"""
        return {
            'min_disk_space_gb': 1.0,
            'min_memory_mb': 512,
            'max_rollback_generations': 100,
            'update_check_interval_hours': 24
        }
    
    def get_model(self, operation: str) -> Optional[Dict]:
        """Get causal model for an operation"""
        return self.operation_models.get(operation)
    
    def build_graph(self, model_dict: Dict) -> nx.DiGraph:
        """Build NetworkX graph from model dictionary"""
        graph = nx.DiGraph()
        
        # Add nodes
        for node in model_dict['nodes']:
            graph.add_node(
                node.id,
                name=node.name,
                node_type=node.node_type,
                description=node.description,
                value_type=node.value_type,
                possible_values=node.possible_values
            )
        
        # Add edges
        for edge in model_dict['edges']:
            graph.add_edge(
                edge.from_node,
                edge.to_node,
                mechanism=edge.mechanism,
                strength=edge.strength,
                description=edge.description
            )
        
        return graph
    
    def get_treatments(self, operation: str) -> List[str]:
        """Get treatment variables for an operation"""
        model = self.get_model(operation)
        if not model:
            return []
        
        return [
            node.id for node in model['nodes'] 
            if node.node_type == 'treatment'
        ]
    
    def get_outcomes(self, operation: str) -> List[str]:
        """Get outcome variables for an operation"""
        model = self.get_model(operation)
        if not model:
            return []
        
        return [
            node.id for node in model['nodes'] 
            if node.node_type == 'outcome'
        ]