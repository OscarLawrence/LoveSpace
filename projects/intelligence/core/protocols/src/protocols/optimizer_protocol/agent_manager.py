"""
Agent management for optimizer protocol
"""

import time
from typing import Dict, List
from .data_models import AgentInfo


class AgentManager:
    """Manages connected agents and their state"""
    
    def __init__(self, heartbeat_interval: float = 30.0):
        self.connected_agents: Dict[str, AgentInfo] = {}
        self.heartbeat_interval = heartbeat_interval
    
    async def update_agent_heartbeat(self, agent_id: str, agent_type: str, 
                                   capabilities: List[str], timestamp: float) -> None:
        """Update agent heartbeat information"""
        if agent_id not in self.connected_agents:
            # New agent
            self.connected_agents[agent_id] = AgentInfo(
                agent_id=agent_id,
                agent_type=agent_type,
                last_seen=timestamp,
                capabilities=capabilities,
                performance_metrics={}
            )
        else:
            # Update existing agent
            agent_info = self.connected_agents[agent_id]
            agent_info.last_seen = timestamp
            agent_info.capabilities = capabilities
    
    async def update_agent_performance(self, agent_id: str, 
                                     performance_metrics: Dict[str, float]) -> None:
        """Update agent performance metrics"""
        if agent_id in self.connected_agents:
            self.connected_agents[agent_id].performance_metrics = performance_metrics
    
    async def disconnect_agent(self, agent_id: str) -> None:
        """Mark agent as disconnected"""
        if agent_id in self.connected_agents:
            # Keep the agent info but could mark as disconnected
            # For now, we'll remove it entirely
            del self.connected_agents[agent_id]
    
    def cleanup_inactive_agents(self) -> None:
        """Remove agents that haven't sent heartbeat recently"""
        current_time = time.time()
        timeout_threshold = self.heartbeat_interval * 3
        
        inactive_agents = [
            agent_id for agent_id, agent_info in self.connected_agents.items()
            if current_time - agent_info.last_seen > timeout_threshold
        ]
        
        for agent_id in inactive_agents:
            del self.connected_agents[agent_id]
    
    def get_connected_agents(self) -> Dict[str, AgentInfo]:
        """Get information about connected agents"""
        return self.connected_agents.copy()
    
    def get_active_agents_count(self) -> int:
        """Get count of active agents"""
        current_time = time.time()
        timeout_threshold = self.heartbeat_interval * 2
        
        active_count = sum(
            1 for agent_info in self.connected_agents.values()
            if current_time - agent_info.last_seen <= timeout_threshold
        )
        
        return active_count
    
    def get_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """Get agents that have a specific capability"""
        return [
            agent_info for agent_info in self.connected_agents.values()
            if capability in agent_info.capabilities
        ]