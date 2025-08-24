"""Execution control system for automatic halting of incoherent operations"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from .logical_coherence_validator import CoherenceResult


@dataclass
class HaltEvent:
    timestamp: float
    command: str
    reason: str
    coherence_score: float
    halt_type: str  # 'contradiction', 'impossibility', 'low_score'


class AutoHaltController:
    """Controls execution flow and halts incoherent operations"""
    
    def __init__(self):
        self.halt_threshold = 0.5
        self.halt_log = []
        self.halt_patterns = {
            'critical_contradictions': [
                'delete.*create',
                'remove.*add', 
                'start.*stop'
            ],
            'resource_violations': [
                'insufficient.*memory',
                'missing.*dependency',
                'unavailable.*service'
            ]
        }
    
    def should_halt_execution(self, coherence_result: CoherenceResult, command: str) -> bool:
        """Determine if execution should be halted"""
        
        # Always halt on contradictions
        if coherence_result.contradictions:
            self.log_halt_event(command, "Logical contradictions detected", 
                              coherence_result.score, "contradiction")
            return True
        
        # Halt on critical impossibilities
        critical_impossibilities = self._check_critical_impossibilities(coherence_result.impossibilities)
        if critical_impossibilities:
            self.log_halt_event(command, f"Critical impossibilities: {critical_impossibilities}", 
                              coherence_result.score, "impossibility")
            return True
        
        # Halt on low coherence score
        if coherence_result.score < self.halt_threshold:
            self.log_halt_event(command, f"Low coherence score: {coherence_result.score}", 
                              coherence_result.score, "low_score")
            return True
        
        return False
    
    def generate_halt_reason(self, coherence_result: CoherenceResult, command: str) -> str:
        """Generate human-readable halt explanation"""
        
        reasons = []
        
        if coherence_result.contradictions:
            reasons.append(f"Contradictions found: {'; '.join(coherence_result.contradictions[:2])}")
        
        if coherence_result.impossibilities:
            critical = self._check_critical_impossibilities(coherence_result.impossibilities)
            if critical:
                reasons.append(f"Critical issues: {'; '.join(critical[:2])}")
        
        if coherence_result.score < self.halt_threshold:
            reasons.append(f"Coherence score too low: {coherence_result.score:.2f} < {self.halt_threshold}")
        
        if not reasons:
            return "Execution halted for safety"
            
        return " | ".join(reasons)
    
    def log_halt_event(self, command: str, reason: str, score: float, halt_type: str):
        """Log halt event for analytics and debugging"""
        
        event = HaltEvent(
            timestamp=time.time(),
            command=command[:200],  # Truncate for privacy
            reason=reason,
            coherence_score=score,
            halt_type=halt_type
        )
        
        self.halt_log.append(event)
        
        # Persist to file
        self._persist_halt_log(event)
    
    def get_halt_statistics(self) -> Dict[str, Any]:
        """Get analytics on halt events"""
        
        if not self.halt_log:
            return {"total_halts": 0}
        
        halt_types = {}
        avg_score = 0
        
        for event in self.halt_log:
            halt_types[event.halt_type] = halt_types.get(event.halt_type, 0) + 1
            avg_score += event.coherence_score
        
        avg_score /= len(self.halt_log)
        
        return {
            "total_halts": len(self.halt_log),
            "halt_types": halt_types,
            "average_coherence_score": avg_score,
            "recent_halts": len([e for e in self.halt_log if time.time() - e.timestamp < 3600])
        }
    
    def adjust_threshold(self, new_threshold: float):
        """Dynamically adjust halt threshold based on usage patterns"""
        if 0.0 <= new_threshold <= 1.0:
            self.halt_threshold = new_threshold
    
    def _check_critical_impossibilities(self, impossibilities: List[str]) -> List[str]:
        """Filter impossibilities for critical issues that must halt execution"""
        
        critical = []
        
        for impossibility in impossibilities:
            impossibility_lower = impossibility.lower()
            
            # Check against critical patterns
            for pattern_type, patterns in self.halt_patterns.items():
                for pattern in patterns:
                    if any(word in impossibility_lower for word in pattern.split('.*')):
                        critical.append(impossibility)
                        break
        
        return critical
    
    def _persist_halt_log(self, event: HaltEvent):
        """Save halt event to persistent storage"""
        
        log_file = Path('.') / 'halt_events.jsonl'
        
        try:
            with open(log_file, 'a') as f:
                event_dict = {
                    'timestamp': event.timestamp,
                    'command_hash': hash(event.command) % 10000,  # Anonymized
                    'reason': event.reason,
                    'coherence_score': event.coherence_score,
                    'halt_type': event.halt_type
                }
                f.write(json.dumps(event_dict) + '\n')
        except Exception:
            pass  # Silent fail for logging
    
    def emergency_halt(self, reason: str = "Emergency halt triggered"):
        """Emergency halt for critical system states"""
        
        self.log_halt_event("EMERGENCY", reason, 0.0, "emergency")
        
        # Could integrate with system shutdown procedures
        print(f"EMERGENCY HALT: {reason}")
        
        return True
