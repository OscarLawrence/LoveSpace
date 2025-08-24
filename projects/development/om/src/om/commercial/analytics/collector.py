"""Analytics collection and monitoring."""

import json
import datetime
import platform
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import asdict

from .models import UsageMetric, PerformanceMetric, ErrorMetric, MetricUtils


class AnalyticsCollector:
    """Collects usage and performance analytics."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".om" / "analytics"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._session_id = MetricUtils.generate_session_id()
        self._user_id = MetricUtils.get_user_id(self.data_dir)
    
    def record_command_usage(self, command: str, duration_ms: int, success: bool) -> None:
        """Record command usage metrics."""
        metric = UsageMetric(
            timestamp=datetime.datetime.now().isoformat(),
            command=command,
            duration_ms=duration_ms,
            success=success,
            user_id=self._user_id,
            session_id=self._session_id
        )
        
        self._append_metric("usage", metric)
    
    def record_performance_snapshot(self) -> None:
        """Record current system performance."""
        try:
            import psutil
            
            # Safe disk I/O counters
            try:
                disk_counters = psutil.disk_io_counters()
                disk_io = sum(disk_counters[:2]) / 1024 / 1024 if disk_counters else 0
            except:
                disk_io = 0
            
            # Safe network counters
            try:
                net_counters = psutil.net_io_counters()
                net_io = sum(net_counters[:2]) / 1024 / 1024 if net_counters else 0
            except:
                net_io = 0
                
            metric = PerformanceMetric(
                timestamp=datetime.datetime.now().isoformat(),
                cpu_percent=psutil.cpu_percent(),
                memory_mb=psutil.virtual_memory().used / 1024 / 1024,
                disk_io_mb=disk_io,
                network_io_mb=net_io
            )
            
            self._append_metric("performance", metric)
            
        except Exception:
            # Don't fail command execution due to analytics
            pass
    
    def record_error(self, command: str, error: Exception) -> None:
        """Record error for analysis."""
        metric = ErrorMetric(
            timestamp=datetime.datetime.now().isoformat(),
            command=command,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=""  # Simplified for privacy
        )
        
        self._append_metric("errors", metric)
    
    def get_usage_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get usage summary for last N days."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        usage_data = self._load_metrics("usage")
        
        recent_usage = [
            metric for metric in usage_data
            if datetime.datetime.fromisoformat(metric["timestamp"]) > cutoff
        ]
        
        # Aggregate statistics
        total_commands = len(recent_usage)
        unique_commands = len(set(m["command"] for m in recent_usage))
        success_rate = sum(1 for m in recent_usage if m["success"]) / max(total_commands, 1)
        avg_duration = sum(m["duration_ms"] for m in recent_usage) / max(total_commands, 1)
        
        # Command frequency
        command_counts = {}
        for metric in recent_usage:
            cmd = metric["command"]
            command_counts[cmd] = command_counts.get(cmd, 0) + 1
        
        return {
            "period_days": days,
            "total_commands": total_commands,
            "unique_commands": unique_commands,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "top_commands": sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "daily_usage": self._get_daily_usage_counts(recent_usage)
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics."""
        performance_data = self._load_metrics("performance")
        
        if not performance_data:
            return {"status": "no_data"}
        
        # Get recent metrics (last hour)
        cutoff = datetime.datetime.now() - datetime.timedelta(hours=1)
        recent_perf = [
            metric for metric in performance_data
            if datetime.datetime.fromisoformat(metric["timestamp"]) > cutoff
        ]
        
        if not recent_perf:
            return {"status": "no_recent_data"}
        
        # Calculate averages
        avg_cpu = sum(m["cpu_percent"] for m in recent_perf) / len(recent_perf)
        avg_memory = sum(m["memory_mb"] for m in recent_perf) / len(recent_perf)
        
        return {
            "status": "healthy",
            "avg_cpu_percent": avg_cpu,
            "avg_memory_mb": avg_memory,
            "sample_count": len(recent_perf),
            "system_info": {
                "platform": platform.system(),
                "python_version": platform.python_version()
            }
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up analytics data older than specified days."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        
        for metric_type in ["usage", "performance", "errors"]:
            data = self._load_metrics(metric_type)
            filtered_data = [
                metric for metric in data
                if datetime.datetime.fromisoformat(metric["timestamp"]) > cutoff
            ]
            
            self._save_metrics(metric_type, filtered_data)
    
    def _append_metric(self, metric_type: str, metric: Any) -> None:
        """Append metric to data file."""
        file_path = self.data_dir / f"{metric_type}.jsonl"
        
        with open(file_path, 'a') as f:
            json.dump(asdict(metric), f)
            f.write('\n')
    
    def _load_metrics(self, metric_type: str) -> List[Dict[str, Any]]:
        """Load metrics from data file."""
        file_path = self.data_dir / f"{metric_type}.jsonl"
        
        if not file_path.exists():
            return []
        
        metrics = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    metrics.append(json.loads(line))
        
        return metrics
    
    def _save_metrics(self, metric_type: str, metrics: List[Dict[str, Any]]) -> None:
        """Save metrics to data file."""
        file_path = self.data_dir / f"{metric_type}.jsonl"
        
        with open(file_path, 'w') as f:
            for metric in metrics:
                json.dump(metric, f)
                f.write('\n')
    
    def _get_daily_usage_counts(self, usage_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get daily usage counts."""
        daily_counts = {}
        
        for metric in usage_data:
            date = metric["timestamp"][:10]  # YYYY-MM-DD
            daily_counts[date] = daily_counts.get(date, 0) + 1
        
        return daily_counts
