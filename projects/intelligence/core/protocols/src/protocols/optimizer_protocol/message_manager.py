"""
Message management for optimizer protocol
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from .data_models import OptimizerMessage, MessageType, Priority, AgentInfo


class MessageManager:
    """Handles message sending, receiving, and queuing"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        
        # Message queues
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.outbound_queue: asyncio.Queue = asyncio.Queue()
        
        # Message tracking
        self.pending_messages: Dict[str, OptimizerMessage] = {}
        self.message_history: List[OptimizerMessage] = []
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
        # Configuration
        self.message_timeout = 60.0
        self.max_history_size = 1000
        
        # Statistics
        self.message_stats = {
            "sent": 0,
            "received": 0,
            "failed": 0,
            "timeouts": 0
        }
    
    def register_handler(self, message_type: MessageType, handler: Callable) -> None:
        """Register message handler for specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    async def send_message(self, recipient_id: str, message_type: MessageType,
                          payload: Dict[str, Any], priority: Priority = Priority.MEDIUM,
                          requires_ack: bool = False) -> str:
        """Send message to specific agent"""
        message = OptimizerMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            priority=priority,
            timestamp=time.time(),
            payload=payload,
            requires_ack=requires_ack
        )
        
        await self.outbound_queue.put(message)
        
        if requires_ack:
            self.pending_messages[message.message_id] = message
        
        return message.message_id
    
    async def broadcast_message(self, message_type: MessageType,
                              payload: Dict[str, Any], priority: Priority = Priority.MEDIUM) -> str:
        """Broadcast message to all connected agents"""
        message = OptimizerMessage(
            message_id=str(uuid.uuid4()),
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=None,  # Broadcast
            priority=priority,
            timestamp=time.time(),
            payload=payload,
            requires_ack=False
        )
        
        await self.outbound_queue.put(message)
        return message.message_id
    
    async def handle_message(self, message: OptimizerMessage) -> None:
        """Handle incoming message"""
        # Add to history
        self.message_history.append(message)
        
        # Handle acknowledgment if required
        if message.requires_ack:
            await self._send_acknowledgment(message)
        
        # Process message based on type
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    print(f"Handler error for {message.message_type}: {e}")
    
    async def _send_acknowledgment(self, original_message: OptimizerMessage) -> None:
        """Send acknowledgment for received message"""
        ack_payload = {
            "original_message_id": original_message.message_id,
            "status": "received",
            "timestamp": time.time()
        }
        
        if original_message.sender_id:
            await self.send_message(
                original_message.sender_id,
                MessageType.COORDINATION_SYNC,
                ack_payload,
                Priority.LOW
            )
    
    def cleanup_expired_messages(self) -> None:
        """Clean up expired pending messages"""
        current_time = time.time()
        
        expired_messages = [
            msg_id for msg_id, msg in self.pending_messages.items()
            if current_time - msg.timestamp > self.message_timeout
        ]
        
        for msg_id in expired_messages:
            del self.pending_messages[msg_id]
            self.message_stats["timeouts"] += 1
        
        # Trim message history
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message statistics"""
        return {
            "message_stats": self.message_stats.copy(),
            "pending_messages": len(self.pending_messages),
            "message_history_size": len(self.message_history)
        }