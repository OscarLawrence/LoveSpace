"""
Data models for optimizer protocol communication
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MessageType(Enum):
    """Types of optimizer messages"""
    PERFORMANCE_UPDATE = "performance_update"
    STRATEGY_CHANGE = "strategy_change"
    OPTIMIZATION_REQUEST = "optimization_request"
    FEEDBACK_REPORT = "feedback_report"
    COORDINATION_SYNC = "coordination_sync"
    ALERT = "alert"
    HEARTBEAT = "heartbeat"


class Priority(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class OptimizerMessage:
    """Message for optimizer communication"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    priority: Priority
    timestamp: float
    payload: Dict[str, Any]
    requires_ack: bool = False
    ttl: float = 300.0  # Time to live in seconds


@dataclass
class AgentInfo:
    """Information about connected agents"""
    agent_id: str
    agent_type: str
    last_seen: float
    capabilities: List[str]
    performance_metrics: Dict[str, float]