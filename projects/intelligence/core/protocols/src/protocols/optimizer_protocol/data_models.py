"""
Data models for optimizer protocol communication
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


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
    recipient_id: str | None  # None for broadcast
    priority: Priority
    timestamp: float
    payload: dict[str, Any]
    requires_ack: bool = False
    ttl: float = 300.0  # Time to live in seconds


@dataclass
class AgentInfo:
    """Information about connected agents"""

    agent_id: str
    agent_type: str
    last_seen: float
    capabilities: list[str]
    performance_metrics: dict[str, float]
