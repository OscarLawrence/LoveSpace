"""
Optimizer Protocol Package
Multi-agent communication for performance optimization coordination
"""

from .agent_manager import AgentManager
from .communication_handlers import CommunicationHandlers
from .data_models import AgentInfo, MessageType, OptimizerMessage, Priority
from .message_manager import MessageManager
from .protocol_engine import ProtocolEngine

# Main class for backward compatibility
OptimizerProtocol = ProtocolEngine

__all__ = [
    "OptimizerProtocol",
    "ProtocolEngine",
    "MessageManager",
    "AgentManager",
    "CommunicationHandlers",
    "MessageType",
    "Priority",
    "OptimizerMessage",
    "AgentInfo",
]
