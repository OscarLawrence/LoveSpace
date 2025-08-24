"""
Communication handlers for optimizer protocol
"""

import time
from typing import Dict, Any, Optional
from .data_models import OptimizerMessage, MessageType, Priority, AgentInfo


class CommunicationHandlers:
    """Handles specific communication patterns and message types"""
    
    def __init__(self, agent_id: str, agent_type: str, message_manager, agent_manager):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_manager = message_manager
        self.agent_manager = agent_manager
        self.capabilities = ["performance_monitoring", "strategy_selection", "feedback_processing"]
    
    async def send_performance_update(self, performance_metrics: Dict[str, float],
                                    context: Optional[Dict[str, Any]] = None) -> None:
        """Send performance update to coordination network"""
        payload = {
            "metrics": performance_metrics,
            "context": context or {},
            "agent_type": self.agent_type,
            "timestamp": time.time()
        }
        
        await self.message_manager.broadcast_message(
            MessageType.PERFORMANCE_UPDATE,
            payload,
            Priority.MEDIUM
        )
    
    async def send_strategy_change(self, old_strategy: str, new_strategy: str,
                                 reason: str, expected_improvement: float) -> None:
        """Notify network of strategy change"""
        payload = {
            "old_strategy": old_strategy,
            "new_strategy": new_strategy,
            "reason": reason,
            "expected_improvement": expected_improvement,
            "agent_id": self.agent_id
        }
        
        await self.message_manager.broadcast_message(
            MessageType.STRATEGY_CHANGE,
            payload,
            Priority.HIGH
        )
    
    async def request_optimization(self, target_agent: str, optimization_type: str,
                                 parameters: Dict[str, Any]) -> str:
        """Request optimization from specific agent"""
        payload = {
            "optimization_type": optimization_type,
            "parameters": parameters,
            "requester": self.agent_id
        }
        
        return await self.message_manager.send_message(
            target_agent,
            MessageType.OPTIMIZATION_REQUEST,
            payload,
            Priority.HIGH,
            requires_ack=True
        )
    
    async def send_feedback_report(self, strategy_name: str, performance_change: float,
                                 success: bool, details: Dict[str, Any]) -> None:
        """Send feedback report about strategy performance"""
        payload = {
            "strategy_name": strategy_name,
            "performance_change": performance_change,
            "success": success,
            "details": details,
            "reporter": self.agent_id
        }
        
        await self.message_manager.broadcast_message(
            MessageType.FEEDBACK_REPORT,
            payload,
            Priority.MEDIUM
        )
    
    async def send_alert(self, alert_type: str, severity: str, message: str,
                        data: Optional[Dict[str, Any]] = None) -> None:
        """Send alert to coordination network"""
        payload = {
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "data": data or {},
            "source": self.agent_id
        }
        
        await self.message_manager.broadcast_message(
            MessageType.ALERT,
            payload,
            Priority.CRITICAL if severity == "critical" else Priority.HIGH
        )
    
    async def send_heartbeat(self) -> None:
        """Send heartbeat message"""
        payload = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "status": "active",
            "timestamp": time.time()
        }
        
        await self.message_manager.broadcast_message(
            MessageType.HEARTBEAT,
            payload,
            Priority.LOW
        )
    
    async def handle_heartbeat(self, message: OptimizerMessage) -> None:
        """Handle heartbeat message"""
        payload = message.payload
        agent_id = payload.get("agent_id")
        
        if agent_id and agent_id != self.agent_id:
            await self.agent_manager.update_agent_heartbeat(
                agent_id,
                payload.get("agent_type", "unknown"),
                payload.get("capabilities", []),
                message.timestamp
            )
    
    async def handle_coordination_sync(self, message: OptimizerMessage) -> None:
        """Handle coordination synchronization message"""
        payload = message.payload
        
        if "original_message_id" in payload:
            # This is an acknowledgment
            msg_id = payload["original_message_id"]
            if msg_id in self.message_manager.pending_messages:
                del self.message_manager.pending_messages[msg_id]
        
        elif payload.get("action") == "disconnect":
            # Agent disconnecting
            agent_id = payload.get("agent_id")
            if agent_id:
                await self.agent_manager.disconnect_agent(agent_id)
    
    async def handle_performance_update(self, message: OptimizerMessage) -> None:
        """Handle performance update message"""
        payload = message.payload
        agent_id = message.sender_id
        
        if agent_id:
            await self.agent_manager.update_agent_performance(
                agent_id,
                payload.get("metrics", {})
            )