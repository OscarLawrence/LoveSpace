"""
Real-time coherence monitoring system.
Integrates with existing OM validation components for continuous coherence tracking.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import threading
import time
from .validator import LogicalCoherenceValidator, CoherenceResult, CoherenceLevel


@dataclass
class CoherenceEvent:
    """A coherence validation event"""
    timestamp: datetime
    source: str
    content: str
    result: CoherenceResult
    context: Dict[str, Any] = field(default_factory=dict)


class CoherenceMonitor:
    """
    Real-time coherence monitoring system.
    Tracks coherence across all AI operations and provides immediate feedback.
    """
    
    def __init__(self, validator: Optional[LogicalCoherenceValidator] = None):
        self.validator = validator or LogicalCoherenceValidator()
        self.events: List[CoherenceEvent] = []
        self.subscribers: List[Callable[[CoherenceEvent], None]] = []
        self.running = False
        self.lock = threading.Lock()
        
        # Coherence thresholds
        self.warning_threshold = CoherenceLevel.MEDIUM
        self.error_threshold = CoherenceLevel.LOW
        
        # Statistics
        self.total_validations = 0
        self.coherence_trend = []
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.running = True
        print("🔍 Coherence monitoring started")
        
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.running = False
        print("⏹️  Coherence monitoring stopped")
        
    def validate_and_monitor(self, content: str, source: str = "unknown", 
                           context: Optional[Dict[str, Any]] = None) -> CoherenceResult:
        """Validate content and add to monitoring stream"""
        if not self.running:
            return self.validator.validate_statement(content)
            
        # Perform validation
        result = self.validator.validate_statement(content)
        
        # Create event
        event = CoherenceEvent(
            timestamp=datetime.now(),
            source=source,
            content=content,
            result=result,
            context=context or {}
        )
        
        # Store and notify
        with self.lock:
            self.events.append(event)
            self.total_validations += 1
            self.coherence_trend.append(result.score)
            
            # Keep only last 1000 events
            if len(self.events) > 1000:
                self.events = self.events[-1000:]
            
            # Keep only last 100 trend points
            if len(self.coherence_trend) > 100:
                self.coherence_trend = self.coherence_trend[-100:]
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"⚠️  Error in coherence subscriber: {e}")
        
        # Check thresholds and alert
        self._check_thresholds(event)
        
        return result
    
    def validate_reasoning_chain_and_monitor(self, reasoning_steps: List[str], 
                                           source: str = "reasoning", 
                                           context: Optional[Dict[str, Any]] = None) -> CoherenceResult:
        """Validate reasoning chain and add to monitoring"""
        if not self.running:
            return self.validator.validate_reasoning_chain(reasoning_steps)
            
        # Perform validation
        result = self.validator.validate_reasoning_chain(reasoning_steps)
        
        # Create event
        event = CoherenceEvent(
            timestamp=datetime.now(),
            source=source,
            content=" → ".join(reasoning_steps),
            result=result,
            context=context or {}
        )
        
        # Store and notify (same as above)
        with self.lock:
            self.events.append(event)
            self.total_validations += 1
            self.coherence_trend.append(result.score)
            
            if len(self.events) > 1000:
                self.events = self.events[-1000:]
            if len(self.coherence_trend) > 100:
                self.coherence_trend = self.coherence_trend[-100:]
        
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                print(f"⚠️  Error in coherence subscriber: {e}")
        
        self._check_thresholds(event)
        
        return result
    
    def subscribe(self, callback: Callable[[CoherenceEvent], None]):
        """Subscribe to coherence events"""
        self.subscribers.append(callback)
        
    def unsubscribe(self, callback: Callable[[CoherenceEvent], None]):
        """Unsubscribe from coherence events"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_recent_events(self, count: int = 10) -> List[CoherenceEvent]:
        """Get recent coherence events"""
        with self.lock:
            return self.events[-count:] if self.events else []
    
    def get_coherence_statistics(self) -> Dict[str, Any]:
        """Get coherence monitoring statistics"""
        with self.lock:
            if not self.coherence_trend:
                return {
                    "total_validations": 0,
                    "average_coherence": 0.0,
                    "trend_direction": "unknown",
                    "recent_average": 0.0
                }
            
            avg_coherence = sum(self.coherence_trend) / len(self.coherence_trend)
            recent_avg = sum(self.coherence_trend[-10:]) / min(10, len(self.coherence_trend))
            
            # Calculate trend
            if len(self.coherence_trend) >= 10:
                early_avg = sum(self.coherence_trend[:10]) / 10
                trend = "improving" if recent_avg > early_avg else "declining"
            else:
                trend = "insufficient_data"
            
            return {
                "total_validations": self.total_validations,
                "average_coherence": avg_coherence,
                "trend_direction": trend,
                "recent_average": recent_avg,
                "coherence_distribution": self._get_coherence_distribution()
            }
    
    def _check_thresholds(self, event: CoherenceEvent):
        """Check coherence thresholds and alert if necessary"""
        result = event.result
        
        if result.level.value <= self.error_threshold.value:
            print(f"🚨 COHERENCE ERROR: {event.source}")
            print(f"   Content: {event.content[:100]}...")
            print(f"   Score: {result.score:.2f} ({result.level.name})")
            if result.contradictions:
                print(f"   Contradictions: {result.contradictions}")
                
        elif result.level.value <= self.warning_threshold.value:
            print(f"⚠️  COHERENCE WARNING: {event.source}")
            print(f"   Score: {result.score:.2f} ({result.level.name})")
    
    def _get_coherence_distribution(self) -> Dict[str, int]:
        """Get distribution of coherence levels"""
        distribution = {level.name: 0 for level in CoherenceLevel}
        
        for event in self.events:
            distribution[event.result.level.name] += 1
            
        return distribution
    
    def print_status(self):
        """Print current coherence monitoring status"""
        stats = self.get_coherence_statistics()
        
        print("\n🔍 Coherence Monitor Status")
        print("=" * 40)
        print(f"Status: {'🟢 Running' if self.running else '🔴 Stopped'}")
        print(f"Total Validations: {stats['total_validations']}")
        print(f"Average Coherence: {stats['average_coherence']:.3f}")
        print(f"Recent Average: {stats['recent_average']:.3f}")
        print(f"Trend: {stats['trend_direction']}")
        
        if 'coherence_distribution' in stats:
            print("\nCoherence Distribution:")
            for level, count in stats['coherence_distribution'].items():
                if count > 0:
                    print(f"  {level}: {count}")
        
        recent_events = self.get_recent_events(3)
        if recent_events:
            print("\nRecent Events:")
            for event in recent_events:
                print(f"  {event.timestamp.strftime('%H:%M:%S')} | {event.source} | "
                      f"{event.result.level.name} ({event.result.score:.2f})")


# Global monitor instance
_global_monitor: Optional[CoherenceMonitor] = None


def get_global_monitor() -> CoherenceMonitor:
    """Get or create the global coherence monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = CoherenceMonitor()
    return _global_monitor


def start_global_monitoring():
    """Start global coherence monitoring"""
    monitor = get_global_monitor()
    monitor.start_monitoring()
    return monitor


def validate_with_monitoring(content: str, source: str = "unknown", 
                           context: Optional[Dict[str, Any]] = None) -> CoherenceResult:
    """Convenience function for monitored validation"""
    monitor = get_global_monitor()
    return monitor.validate_and_monitor(content, source, context)