"""
Main protocol engine for optimizer communication
"""

import asyncio
from typing import Dict, Any
from .data_models import MessageType
from .message_manager import MessageManager
from .agent_manager import AgentManager
from .communication_handlers import CommunicationHandlers

try:
    from ..ai_protocol import AIProtocol
except ImportError:
    AIProtocol = None


class ProtocolEngine:
    """Main engine that orchestrates the optimizer protocol"""
    
    def __init__(self, agent_id: str, agent_type: str = "optimizer"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        
        # Core components
        self.message_manager = MessageManager(agent_id, agent_type)
        self.agent_manager = AgentManager()
        self.communication_handlers = CommunicationHandlers(
            agent_id, agent_type, self.message_manager, self.agent_manager
        )
        
        # Protocol state
        self.running = False
        self.heartbeat_interval = 30.0
        
        # Setup default handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self) -> None:
        """Setup default message handlers"""
        self.message_manager.register_handler(
            MessageType.HEARTBEAT, 
            self.communication_handlers.handle_heartbeat
        )
        self.message_manager.register_handler(
            MessageType.COORDINATION_SYNC, 
            self.communication_handlers.handle_coordination_sync
        )
        self.message_manager.register_handler(
            MessageType.PERFORMANCE_UPDATE, 
            self.communication_handlers.handle_performance_update
        )
    
    async def start_protocol(self) -> None:
        """Start the optimizer protocol"""
        self.running = True
        
        # Start communication tasks
        await asyncio.gather(
            self._message_processor(),
            self._outbound_processor(),
            self._heartbeat_sender(),
            self._cleanup_task()
        )
    
    async def stop_protocol(self) -> None:
        """Stop the optimizer protocol"""
        self.running = False
        
        # Send disconnect message
        from .data_models import Priority
        await self.message_manager.broadcast_message(
            MessageType.COORDINATION_SYNC,
            {"action": "disconnect", "agent_id": self.agent_id},
            Priority.HIGH
        )
    
    async def _message_processor(self) -> None:
        """Process incoming messages"""
        while self.running:
            try:
                # Get message from queue (with timeout)
                message = await asyncio.wait_for(
                    self.message_manager.message_queue.get(),
                    timeout=1.0
                )
                
                await self.message_manager.handle_message(message)
                self.message_manager.message_stats["received"] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Message processing error: {e}")
                self.message_manager.message_stats["failed"] += 1
    
    async def _outbound_processor(self) -> None:
        """Process outbound messages"""
        while self.running:
            try:
                # Get message from outbound queue
                message = await asyncio.wait_for(
                    self.message_manager.outbound_queue.get(),
                    timeout=1.0
                )
                
                await self._send_message_impl(message)
                self.message_manager.message_stats["sent"] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Outbound processing error: {e}")
                self.message_manager.message_stats["failed"] += 1
    
    async def _heartbeat_sender(self) -> None:
        """Send periodic heartbeat messages"""
        while self.running:
            try:
                await self.communication_handlers.send_heartbeat()
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(self.heartbeat_interval)
    
    async def _cleanup_task(self) -> None:
        """Cleanup expired messages and inactive agents"""
        while self.running:
            try:
                self.message_manager.cleanup_expired_messages()
                self.agent_manager.cleanup_inactive_agents()
                
                await asyncio.sleep(60.0)  # Cleanup every minute
                
            except Exception as e:
                print(f"Cleanup error: {e}")
                await asyncio.sleep(60.0)
    
    async def _send_message_impl(self, message) -> None:
        """Implementation of message sending (would integrate with actual transport)"""
        # This would integrate with actual message transport (MQTT, WebSocket, etc.)
        # For now, simulate message sending
        
        if message.recipient_id:
            # Direct message
            print(f"Sending {message.message_type.value} to {message.recipient_id}")
        else:
            # Broadcast message
            print(f"Broadcasting {message.message_type.value} to all agents")
        
        # Simulate network delay
        await asyncio.sleep(0.01)
    
    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        message_stats = self.message_manager.get_stats()
        active_agents = self.agent_manager.get_active_agents_count()
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "running": self.running,
            "connected_agents": len(self.agent_manager.connected_agents),
            "active_agents": active_agents,
            "capabilities": self.communication_handlers.capabilities,
            "heartbeat_interval": self.heartbeat_interval,
            **message_stats
        }