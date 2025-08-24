"""Analytics data models and metrics."""

import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class UsageMetric:
    """Individual usage metric."""
    timestamp: str
    command: str
    duration_ms: int
    success: bool
    user_id: str
    session_id: str


@dataclass
class PerformanceMetric:
    """Performance metric."""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    disk_io_mb: float
    network_io_mb: float


@dataclass
class ErrorMetric:
    """Error tracking metric."""
    timestamp: str
    command: str
    error_type: str
    error_message: str
    stack_trace: str


class MetricUtils:
    """Utility functions for metrics."""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID."""
        import hashlib
        timestamp = datetime.datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:8]
    
    @staticmethod
    def get_user_id(data_dir) -> str:
        """Get anonymized user ID."""
        import hashlib
        from pathlib import Path
        
        user_file = data_dir / "user_id"
        
        if user_file.exists():
            return user_file.read_text().strip()
        
        # Generate new user ID
        user_id = hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()[:12]
        user_file.write_text(user_id)
        return user_id
