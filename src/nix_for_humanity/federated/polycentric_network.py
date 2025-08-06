"""
Polycentric Network Manager for Federated Nix for Humanity

This module implements the three-layer polycentric architecture for federated
learning with proper temporal dissonance handling between layers:

- Layer 0 (Heart): Individual devices with instant responses
- Layer 2 (Polis): Community aggregation with minute-scale consensus  
- Layer 1 (Bridge): Global settlement with 7-day finality

Research Foundation:
- Polycentric Architecture Integration
- Temporal Dissonance Management
- Guided Emergence Governance
- Defense-in-Depth Security Model

Phase 4 Living System Component
"""

import asyncio
import logging
import time
import json
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable, Union
from datetime import datetime, timedelta
import secrets
import aiohttp
import websockets

from .zk_learning_protocol import (
    ZKLearningProtocol, ModelUpdate, AggregateUpdate, ZKProof,
    FederatedUpdateType, PrivacyLevel
)

logger = logging.getLogger(__name__)

# Layer timing parameters (respecting temporal dissonance)
LAYER_TIMINGS = {
    "L0": {
        "response_time": 0.0,      # Instant local operations
        "finality_time": 0.0,      # Immediate local finality
        "rollback_window": 86400,  # 24 hour local rollback
    },
    "L2": {
        "response_time": 5.0,      # 5 second response
        "finality_time": 60.0,     # 1 minute consensus
        "rollback_window": 3600,   # 1 hour rollback window
    },
    "L1": {
        "response_time": 300.0,    # 5 minute response
        "finality_time": 604800.0, # 7 day settlement finality
        "rollback_window": 0,      # No rollback after finality
    }
}

class LayerType(Enum):
    """Polycentric architecture layers"""
    L0_HEART = "l0_heart"        # Individual agent-centric layer
    L2_POLIS = "l2_polis"        # Community aggregation layer
    L1_BRIDGE = "l1_bridge"      # Global settlement layer

class NetworkState(Enum):
    """Network connectivity and health states"""
    OFFLINE = "offline"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"

class ConsensusState(Enum):
    """Consensus formation states"""
    PENDING = "pending"
    FORMING = "forming"
    REACHED = "reached"
    FAILED = "failed"
    FINALIZED = "finalized"

@dataclass
class LayerNode:
    """Represents a node in a specific layer"""
    node_id: str
    layer: LayerType
    endpoint: str
    public_key: str
    reputation_score: float
    last_seen: float
    capabilities: Set[str]
    stake_amount: float

@dataclass
class ConsensusProposal:
    """Proposal for layer consensus"""
    proposal_id: str
    layer: LayerType
    proposal_type: str  # update_aggregate, governance_change, etc.
    content: Dict[str, Any]
    proposer: str
    timestamp: float
    votes_for: int
    votes_against: int
    required_votes: int
    finalization_deadline: float

@dataclass
class NetworkHealth:
    """Overall network health metrics"""
    l0_active_nodes: int
    l2_active_nodes: int
    l1_active_nodes: int
    average_latency: Dict[str, float]
    consensus_success_rate: float
    byzantine_fault_tolerance: bool
    last_health_check: float

class PolycentricNetworkManager:
    """
    Manages the three-layer polycentric federated learning network
    
    This manager handles the complexity of operating across multiple
    layers with different temporal characteristics, ensuring proper
    consensus formation while respecting the natural timing of each layer.
    
    Key Responsibilities:
    1. Layer coordination and state management
    2. Temporal dissonance handling between layers
    3. Byzantine fault tolerance and security
    4. Consensus formation and finalization
    5. Economic incentives and reputation management
    """
    
    def __init__(self, 
                 node_id: Optional[str] = None,
                 storage_path: Optional[Path] = None):
        self.node_id = node_id or self._generate_node_id()
        self.storage_path = storage_path or Path.home() / ".nix-humanity" / "polycentric"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Layer management
        self.layer_connections = {
            LayerType.L0_HEART: NetworkState.OFFLINE,
            LayerType.L2_POLIS: NetworkState.OFFLINE,
            LayerType.L1_BRIDGE: NetworkState.OFFLINE
        }
        
        # Node discovery and management
        self.known_nodes = {
            LayerType.L0_HEART: {},
            LayerType.L2_POLIS: {},
            LayerType.L1_BRIDGE: {}
        }
        
        # Consensus tracking
        self.active_proposals = {}
        self.consensus_history = []
        
        # Economic and reputation system
        self.reputation_scores = {}
        self.stake_amounts = {}
        self.economic_incentives = EconomicIncentiveSystem()
        
        # Network health monitoring
        self.health_monitor = NetworkHealthMonitor()
        
        # Security and Byzantine fault tolerance
        self.security_manager = PolycentricSecurityManager()
        
        logger.info(f"Polycentric Network Manager initialized for node {self.node_id}")
    
    def _generate_node_id(self) -> str:
        """Generate unique node identifier"""
        return f"node_{secrets.token_hex(16)}"
    
    async def initialize_network(self) -> Dict[str, Any]:
        """Initialize connections to all network layers"""
        try:
            initialization_results = {}
            
            # Initialize L0 (always available - local)
            l0_result = await self._initialize_l0_layer()
            initialization_results["L0"] = l0_result
            
            # Initialize L2 (community aggregation)
            l2_result = await self._initialize_l2_layer()
            initialization_results["L2"] = l2_result
            
            # Initialize L1 (global settlement) - only if mature enough
            if await self._should_connect_to_l1():
                l1_result = await self._initialize_l1_layer()
                initialization_results["L1"] = l1_result
            else:
                initialization_results["L1"] = {
                    "status": "not_ready",
                    "reason": "Network not mature enough for L1 participation"
                }
            
            # Start health monitoring
            await self.health_monitor.start_monitoring(self)
            
            return {
                "success": True,
                "node_id": self.node_id,
                "layer_states": initialization_results,
                "network_ready": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize polycentric network: {e}")
            return {
                "success": False,
                "error": str(e),
                "node_id": self.node_id
            }
    
    async def _initialize_l0_layer(self) -> Dict[str, Any]:
        """Initialize Layer 0 (Heart) - individual device layer"""
        try:
            # L0 is always available since it's local
            self.layer_connections[LayerType.L0_HEART] = NetworkState.CONNECTED
            
            # Register self as L0 node
            self.known_nodes[LayerType.L0_HEART][self.node_id] = LayerNode(
                node_id=self.node_id,
                layer=LayerType.L0_HEART,
                endpoint="local://agent",
                public_key=self._get_public_key(),
                reputation_score=1.0,  # Perfect local reputation
                last_seen=time.time(),
                capabilities={"local_learning", "zk_proofs", "instant_response"},
                stake_amount=0.0  # No economic stake needed for local operations
            )
            
            logger.info("L0 (Heart) layer initialized - instant local operations ready")
            
            return {
                "status": "connected",
                "response_time": LAYER_TIMINGS["L0"]["response_time"],
                "capabilities": ["instant_learning", "local_privacy", "immediate_rollback"],
                "nodes_available": 1  # Just this local node
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize L0 layer: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _initialize_l2_layer(self) -> Dict[str, Any]:
        """Initialize Layer 2 (Polis) - community aggregation layer"""
        try:
            # Discover L2 aggregation nodes
            l2_nodes = await self._discover_l2_nodes()
            
            if not l2_nodes:
                self.layer_connections[LayerType.L2_POLIS] = NetworkState.OFFLINE
                return {
                    "status": "offline",
                    "reason": "No L2 aggregation nodes discovered",
                    "retry_in": 300  # Retry in 5 minutes
                }
            
            # Connect to L2 nodes
            connected_nodes = 0
            for node_info in l2_nodes:
                try:
                    connection_result = await self._connect_to_l2_node(node_info)
                    if connection_result["success"]:
                        connected_nodes += 1
                        self.known_nodes[LayerType.L2_POLIS][node_info["node_id"]] = LayerNode(
                            node_id=node_info["node_id"],
                            layer=LayerType.L2_POLIS,
                            endpoint=node_info["endpoint"],
                            public_key=node_info["public_key"],
                            reputation_score=node_info.get("reputation", 0.5),
                            last_seen=time.time(),
                            capabilities=set(node_info.get("capabilities", [])),
                            stake_amount=node_info.get("stake", 0.0)
                        )
                except Exception as e:
                    logger.warning(f"Failed to connect to L2 node {node_info['node_id']}: {e}")
            
            if connected_nodes > 0:
                self.layer_connections[LayerType.L2_POLIS] = NetworkState.CONNECTED
                logger.info(f"L2 (Polis) layer initialized - connected to {connected_nodes} aggregation nodes")
                
                return {
                    "status": "connected",
                    "connected_nodes": connected_nodes,
                    "consensus_time": LAYER_TIMINGS["L2"]["finality_time"],
                    "capabilities": ["community_aggregation", "minute_consensus", "privacy_preserving"]
                }
            else:
                self.layer_connections[LayerType.L2_POLIS] = NetworkState.OFFLINE
                return {
                    "status": "failed",
                    "reason": "Could not connect to any L2 nodes"
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize L2 layer: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _initialize_l1_layer(self) -> Dict[str, Any]:
        """Initialize Layer 1 (Bridge) - global settlement layer"""
        try:
            # L1 connection requires network maturity and stake
            maturity_check = await self._check_network_maturity()
            if not maturity_check["mature_enough"]:
                return {
                    "status": "not_ready",
                    "reason": maturity_check["reason"],
                    "requirements": maturity_check["requirements"]
                }
            
            # Discover L1 settlement nodes
            l1_nodes = await self._discover_l1_nodes()
            
            if not l1_nodes:
                return {
                    "status": "offline",
                    "reason": "No L1 settlement nodes available"
                }
            
            # Connect to L1 settlement layer
            connected_nodes = 0
            for node_info in l1_nodes:
                try:
                    connection_result = await self._connect_to_l1_node(node_info)
                    if connection_result["success"]:
                        connected_nodes += 1
                        self.known_nodes[LayerType.L1_BRIDGE][node_info["node_id"]] = LayerNode(
                            node_id=node_info["node_id"],
                            layer=LayerType.L1_BRIDGE,
                            endpoint=node_info["endpoint"],
                            public_key=node_info["public_key"],
                            reputation_score=node_info.get("reputation", 0.5),
                            last_seen=time.time(),
                            capabilities=set(node_info.get("capabilities", [])),
                            stake_amount=node_info.get("stake", 0.0)
                        )
                except Exception as e:
                    logger.warning(f"Failed to connect to L1 node {node_info['node_id']}: {e}")
            
            if connected_nodes > 0:
                self.layer_connections[LayerType.L1_BRIDGE] = NetworkState.CONNECTED
                logger.info(f"L1 (Bridge) layer initialized - connected to {connected_nodes} settlement nodes")
                
                return {
                    "status": "connected",
                    "connected_nodes": connected_nodes,
                    "finality_time": LAYER_TIMINGS["L1"]["finality_time"],
                    "capabilities": ["global_settlement", "seven_day_finality", "immutable_audit"]
                }
            else:
                return {
                    "status": "failed",
                    "reason": "Could not connect to any L1 nodes"
                }
                
        except Exception as e:
            logger.error(f"Failed to initialize L1 layer: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def submit_to_layer(self, 
                            layer: LayerType, 
                            content: Dict[str, Any],
                            consensus_required: bool = True) -> Dict[str, Any]:
        """
        Submit content to specific layer with appropriate timing handling
        
        Each layer has different temporal characteristics:
        - L0: Instant response (0.00s)
        - L2: Minute-scale consensus (60s)
        - L1: 7-day settlement (604800s)
        """
        try:
            layer_timing = LAYER_TIMINGS[layer.value.upper()]
            
            if layer == LayerType.L0_HEART:
                # L0: Instant local processing
                result = await self._process_l0_submission(content)
                return {
                    "success": True,
                    "layer": "L0",
                    "processed_instantly": True,
                    "response_time": 0.0,
                    "result": result
                }
            
            elif layer == LayerType.L2_POLIS:
                # L2: Community aggregation with minute-scale consensus
                if self.layer_connections[layer] != NetworkState.CONNECTED:
                    return {
                        "success": False,
                        "error": "L2 layer not connected",
                        "fallback_to_l0": True
                    }
                
                submission_result = await self._submit_to_l2_consensus(content, consensus_required)
                
                if consensus_required:
                    # Wait for consensus formation (up to 60 seconds)
                    consensus_result = await self._await_l2_consensus(
                        submission_result["proposal_id"],
                        timeout=layer_timing["finality_time"]
                    )
                    
                    return {
                        "success": True,
                        "layer": "L2",
                        "consensus_reached": consensus_result["consensus_reached"],
                        "response_time": consensus_result["time_taken"],
                        "participating_nodes": consensus_result["participating_nodes"],
                        "result": consensus_result
                    }
                else:
                    return {
                        "success": True,
                        "layer": "L2",
                        "submitted": True,
                        "consensus_pending": True,
                        "proposal_id": submission_result["proposal_id"]
                    }
            
            elif layer == LayerType.L1_BRIDGE:
                # L1: Global settlement with 7-day finality
                if self.layer_connections[layer] != NetworkState.CONNECTED:
                    return {
                        "success": False,
                        "error": "L1 layer not connected",
                        "fallback_to_l2": True
                    }
                
                settlement_result = await self._submit_to_l1_settlement(content)
                
                return {
                    "success": True,
                    "layer": "L1",
                    "submitted_for_settlement": True,
                    "expected_finality": time.time() + layer_timing["finality_time"],
                    "settlement_id": settlement_result["settlement_id"],
                    "challenge_period": layer_timing["finality_time"]
                }
            
            else:
                raise ValueError(f"Unknown layer type: {layer}")
                
        except Exception as e:
            logger.error(f"Failed to submit to layer {layer}: {e}")
            return {
                "success": False,
                "error": str(e),
                "layer": layer.value
            }
    
    async def _process_l0_submission(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Process submission at L0 (instant local processing)"""
        # L0 operations are always instant and local
        processing_start = time.time()
        
        # Validate content locally
        if not await self._validate_content_locally(content):
            raise ValueError("Content failed local validation")
        
        # Process immediately
        result = {
            "processed": True,
            "local_state_updated": True,
            "processing_time": time.time() - processing_start,
            "layer": "L0",
            "finality": "immediate"
        }
        
        return result
    
    async def _submit_to_l2_consensus(self, content: Dict[str, Any], consensus_required: bool) -> Dict[str, Any]:
        """Submit to L2 layer for community consensus"""
        proposal = ConsensusProposal(
            proposal_id=f"l2_prop_{int(time.time())}_{secrets.token_hex(8)}",
            layer=LayerType.L2_POLIS,
            proposal_type=content.get("type", "federated_update"),
            content=content,
            proposer=self.node_id,
            timestamp=time.time(),
            votes_for=0,
            votes_against=0,
            required_votes=self._calculate_required_votes(LayerType.L2_POLIS),
            finalization_deadline=time.time() + LAYER_TIMINGS["L2"]["finality_time"]
        )
        
        # Store proposal
        self.active_proposals[proposal.proposal_id] = proposal
        
        # Broadcast to L2 nodes
        broadcast_result = await self._broadcast_to_l2_nodes({
            "type": "consensus_proposal",
            "proposal": asdict(proposal)
        })
        
        return {
            "proposal_id": proposal.proposal_id,
            "broadcast_success": broadcast_result["success"],
            "nodes_reached": broadcast_result["nodes_reached"]
        }
    
    async def _await_l2_consensus(self, proposal_id: str, timeout: float) -> Dict[str, Any]:
        """Wait for L2 consensus formation with timeout"""
        start_time = time.time()
        proposal = self.active_proposals.get(proposal_id)
        
        if not proposal:
            return {
                "consensus_reached": False,
                "error": "Proposal not found"
            }
        
        # Poll for consensus formation
        while time.time() - start_time < timeout:
            # Check current vote status
            votes_result = await self._check_proposal_votes(proposal_id)
            
            if votes_result["votes_for"] >= proposal.required_votes:
                # Consensus reached
                await self._finalize_l2_consensus(proposal_id)
                
                return {
                    "consensus_reached": True,
                    "time_taken": time.time() - start_time,
                    "votes_for": votes_result["votes_for"],
                    "votes_against": votes_result["votes_against"],
                    "participating_nodes": votes_result["participating_nodes"],
                    "finalized": True
                }
            
            elif votes_result["votes_against"] > len(self.known_nodes[LayerType.L2_POLIS]) // 2:
                # Consensus failed
                return {
                    "consensus_reached": False,
                    "reason": "Majority voted against proposal",
                    "votes_against": votes_result["votes_against"],
                    "time_taken": time.time() - start_time
                }
            
            # Wait before next check
            await asyncio.sleep(5.0)
        
        # Timeout reached
        return {
            "consensus_reached": False,
            "reason": "Consensus timeout",
            "time_taken": timeout,
            "votes_for": proposal.votes_for,
            "votes_against": proposal.votes_against
        }
    
    async def _submit_to_l1_settlement(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Submit to L1 layer for global settlement"""
        settlement_id = f"l1_settle_{int(time.time())}_{secrets.token_hex(8)}"
        
        # Create settlement proposal
        settlement_proposal = {
            "settlement_id": settlement_id,
            "content": content,
            "proposer": self.node_id,
            "timestamp": time.time(),
            "challenge_period_end": time.time() + LAYER_TIMINGS["L1"]["finality_time"]
        }
        
        # Submit to L1 settlement nodes
        settlement_result = await self._broadcast_to_l1_nodes({
            "type": "settlement_proposal",
            "proposal": settlement_proposal
        })
        
        return {
            "settlement_id": settlement_id,
            "submitted": settlement_result["success"],
            "nodes_reached": settlement_result["nodes_reached"]
        }
    
    async def get_network_health(self) -> NetworkHealth:
        """Get current network health across all layers"""
        try:
            l0_nodes = len(self.known_nodes[LayerType.L0_HEART])
            l2_nodes = len([n for n in self.known_nodes[LayerType.L2_POLIS].values() 
                           if time.time() - n.last_seen < 300])  # Active in last 5 minutes
            l1_nodes = len([n for n in self.known_nodes[LayerType.L1_BRIDGE].values()
                           if time.time() - n.last_seen < 3600])  # Active in last hour
            
            # Calculate average latencies
            avg_latencies = {}
            for layer_key, timing in LAYER_TIMINGS.items():
                avg_latencies[layer_key] = timing["response_time"]
            
            # Calculate consensus success rate
            recent_proposals = [p for p in self.consensus_history[-100:] 
                             if time.time() - p.get("timestamp", 0) < 3600]
            consensus_success_rate = (
                len([p for p in recent_proposals if p.get("consensus_reached", False)]) / 
                max(len(recent_proposals), 1)
            )
            
            # Check Byzantine fault tolerance
            byzantine_fault_tolerance = (
                l2_nodes >= 4 and  # Need at least 4 nodes for BFT (3f+1 where f=1)
                l1_nodes >= 4
            )
            
            return NetworkHealth(
                l0_active_nodes=l0_nodes,
                l2_active_nodes=l2_nodes,
                l1_active_nodes=l1_nodes,
                average_latency=avg_latencies,
                consensus_success_rate=consensus_success_rate,
                byzantine_fault_tolerance=byzantine_fault_tolerance,
                last_health_check=time.time()
            )
            
        except Exception as e:
            logger.error(f"Failed to get network health: {e}")
            return NetworkHealth(
                l0_active_nodes=1,  # At least local node
                l2_active_nodes=0,
                l1_active_nodes=0,
                average_latency={"L0": 0.0, "L2": float('inf'), "L1": float('inf')},
                consensus_success_rate=0.0,
                byzantine_fault_tolerance=False,
                last_health_check=time.time()
            )
    
    # Implementation helpers (simplified for demonstration)
    
    def _get_public_key(self) -> str:
        """Get node's public key"""
        return f"pubkey_{self.node_id}"
    
    async def _discover_l2_nodes(self) -> List[Dict[str, Any]]:
        """Discover available L2 aggregation nodes"""
        # In real implementation, would use DHT, DNS, or bootstrap nodes
        return []  # Simplified - would return actual node discovery results
    
    async def _discover_l1_nodes(self) -> List[Dict[str, Any]]:
        """Discover available L1 settlement nodes"""
        # In real implementation, would discover settlement infrastructure
        return []  # Simplified
    
    async def _should_connect_to_l1(self) -> bool:
        """Determine if node should connect to L1 settlement layer"""
        # Check network maturity and node reputation
        return False  # Simplified - would check actual readiness criteria
    
    async def _check_network_maturity(self) -> Dict[str, Any]:
        """Check if network is mature enough for L1 participation"""
        return {
            "mature_enough": False,
            "reason": "Network still in early development",
            "requirements": {
                "min_active_nodes": 1000,
                "min_reputation_score": 0.8,
                "min_uptime_days": 30
            }
        }
    
    async def _connect_to_l2_node(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to specific L2 node"""
        return {"success": False}  # Simplified
    
    async def _connect_to_l1_node(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """Connect to specific L1 node"""
        return {"success": False}  # Simplified
    
    async def _validate_content_locally(self, content: Dict[str, Any]) -> bool:
        """Validate content at local L0 layer"""
        return True  # Simplified validation
    
    def _calculate_required_votes(self, layer: LayerType) -> int:
        """Calculate required votes for consensus in layer"""
        nodes_count = len(self.known_nodes[layer])
        if nodes_count == 0:
            return 1
        
        # Byzantine fault tolerance: need 2f+1 votes where f is max faulty nodes
        f = (nodes_count - 1) // 3  # Max faulty nodes
        return 2 * f + 1

# Supporting classes (simplified implementations)

class EconomicIncentiveSystem:
    """Manages economic incentives and reputation"""
    def __init__(self):
        pass

class NetworkHealthMonitor:
    """Monitors network health across layers"""
    async def start_monitoring(self, network_manager):
        pass

class PolycentricSecurityManager:
    """Manages security across polycentric layers"""
    def __init__(self):
        pass

# Module exports
__all__ = [
    'PolycentricNetworkManager',
    'LayerType',
    'NetworkState',
    'ConsensusState',
    'LayerNode',
    'NetworkHealth'
]