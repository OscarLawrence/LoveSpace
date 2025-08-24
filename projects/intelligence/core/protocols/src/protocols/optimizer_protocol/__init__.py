"""
Optimizer Protocol Package
Multi-agent communication for performance optimization coordination
"""

from .data_models import MessageType, Priority, OptimizerMessage, AgentInfo
from .protocol_engine import ProtocolEngine
from .message_manager import MessageManager
from .agent_manager import AgentManager
from .communication_handlers import CommunicationHandlers

# Main class for backward compatibility
OptimizerProtocol = ProtocolEngine

__all__ = [
    'OptimizerProtocol',
    'ProtocolEngine', 
    'MessageManager',
    'AgentManager',
    'CommunicationHandlers',
    'MessageType',
    'Priority', 
    'OptimizerMessage',
    'AgentInfo'
]