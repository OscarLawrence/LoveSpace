"""Execution halt controller - 200 LOC max"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from .models import HaltEvent, HaltReason, ValidationSession


class HaltController:
    """Controls execution halting based on validation results"""
    
    def __init__(self):
        self.halt_conditions = {
            HaltReason.LOGICAL_CONTRADICTION: {
                'threshold': 0.8,
                'auto_halt': True,
                'recoverable': False
            },
            HaltReason.MISSING_CONTEXT: {
                'threshold': 0.7,
                'auto_halt': False,
                'recoverable': True
            },
            HaltReason.TOKEN_LIMIT: {
                'threshold': 0.9,
                'auto_halt': True,
                'recoverable': True
            },
            HaltReason.CRITICAL_ERROR: {
                'threshold': 1.0,
                'auto_halt': True,
                'recoverable': False
            }
        }
        
        self.active_sessions: Dict[str, ValidationSession] = {}
        self.halt_log_file = "halt_events.jsonl"
    
    def evaluate_halt_condition(self, session_id: str, reason: HaltReason, 
                              confidence: float, context: Dict[str, Any]) -> bool:
        """Evaluate if execution should halt"""
        
        condition = self.halt_conditions.get(reason)
        if not condition:
            return False
        
        should_halt = (
            condition['auto_halt'] and 
            confidence >= condition['threshold']
        )
        
        if should_halt:
            self._trigger_halt(session_id, reason, confidence, context, condition['recoverable'])
        
        return should_halt
    
    def register_session(self, session: ValidationSession) -> None:
        """Register validation session for monitoring"""
        self.active_sessions[session.session_id] = session
    
    def force_halt(self, session_id: str, reason: str, context: Dict[str, Any]) -> None:
        """Force halt for specific session"""
        self._trigger_halt(
            session_id, 
            HaltReason.USER_REQUEST, 
            1.0, 
            {**context, 'reason': reason},
            True
        )
    
    def check_contradiction_halt(self, session_id: str, contradictions: List[Any]) -> bool:
        """Check if contradictions warrant halting"""
        
        if not contradictions:
            return False
        
        # Calculate aggregate confidence
        avg_confidence = sum(c.confidence for c in contradictions) / len(contradictions)
        
        context = {
            'contradiction_count': len(contradictions),
            'avg_confidence': avg_confidence,
            'contradictions': [c.__dict__ for c in contradictions]
        }
        
        return self.evaluate_halt_condition(
            session_id, 
            HaltReason.LOGICAL_CONTRADICTION, 
            avg_confidence, 
            context
        )
    
    def check_token_limit_halt(self, session_id: str, current_tokens: int, 
                              max_tokens: int) -> bool:
        """Check if token usage warrants halting"""
        
        usage_ratio = current_tokens / max_tokens
        
        context = {
            'current_tokens': current_tokens,
            'max_tokens': max_tokens,
            'usage_ratio': usage_ratio
        }
        
        return self.evaluate_halt_condition(
            session_id,
            HaltReason.TOKEN_LIMIT,
            usage_ratio,
            context
        )
    
    def check_context_halt(self, session_id: str, completeness_score: float,
                          missing_critical: List[str]) -> bool:
        """Check if missing context warrants halting"""
        
        # Higher incompleteness = higher halt confidence
        halt_confidence = 1.0 - completeness_score
        
        context = {
            'completeness_score': completeness_score,
            'missing_critical': missing_critical,
            'critical_count': len(missing_critical)
        }
        
        # Only halt if critical elements are missing
        if missing_critical:
            return self.evaluate_halt_condition(
                session_id,
                HaltReason.MISSING_CONTEXT,
                halt_confidence,
                context
            )
        
        return False
    
    def _trigger_halt(self, session_id: str, reason: HaltReason, confidence: float,
                     context: Dict[str, Any], recoverable: bool) -> None:
        """Trigger execution halt"""
        
        halt_event = HaltEvent(
            reason=reason,
            message=self._get_halt_message(reason, context),
            timestamp=datetime.now().isoformat(),
            context=context,
            recoverable=recoverable
        )
        
        # Add to session if exists
        if session_id in self.active_sessions:
            self.active_sessions[session_id].halt_events.append(halt_event)
            self.active_sessions[session_id].active = False
        
        # Log halt event
        self._log_halt_event(session_id, halt_event)
        
        print(f"EXECUTION HALTED: {halt_event.message}")
    
    def _get_halt_message(self, reason: HaltReason, context: Dict[str, Any]) -> str:
        """Generate halt message based on reason and context"""
        
        messages = {
            HaltReason.LOGICAL_CONTRADICTION: 
                f"Logical contradictions detected (confidence: {context.get('avg_confidence', 0):.2f})",
            HaltReason.MISSING_CONTEXT:
                f"Critical context missing: {', '.join(context.get('missing_critical', []))}",
            HaltReason.TOKEN_LIMIT:
                f"Token limit approached ({context.get('usage_ratio', 0):.1%})",
            HaltReason.CRITICAL_ERROR:
                f"Critical error encountered: {context.get('error', 'Unknown')}",
            HaltReason.USER_REQUEST:
                f"User requested halt: {context.get('reason', 'No reason provided')}"
        }
        
        return messages.get(reason, f"Execution halted: {reason.value}")
    
    def _log_halt_event(self, session_id: str, halt_event: HaltEvent) -> None:
        """Log halt event to file"""
        
        log_entry = {
            'session_id': session_id,
            'timestamp': halt_event.timestamp,
            'reason': halt_event.reason.value,
            'message': halt_event.message,
            'recoverable': halt_event.recoverable,
            'context': halt_event.context
        }
        
        try:
            with open(self.halt_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Failed to log halt event: {e}")
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of validation session"""
        
        if session_id not in self.active_sessions:
            return {'status': 'not_found'}
        
        session = self.active_sessions[session_id]
        
        return {
            'status': 'active' if session.active else 'halted',
            'halt_count': len(session.halt_events),
            'last_halt': session.halt_events[-1].__dict__ if session.halt_events else None,
            'validation_count': len(session.validation_results)
        }
    
    def resume_session(self, session_id: str) -> bool:
        """Attempt to resume halted session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session = self.active_sessions[session_id]
        
        # Check if last halt was recoverable
        if session.halt_events:
            last_halt = session.halt_events[-1]
            if not last_halt.recoverable:
                return False
        
        session.active = True
        return True
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session resources"""
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
    
    def get_halt_statistics(self) -> Dict[str, Any]:
        """Get statistics about halt events"""
        
        total_halts = sum(len(session.halt_events) for session in self.active_sessions.values())
        
        reason_counts = {}
        for session in self.active_sessions.values():
            for halt_event in session.halt_events:
                reason = halt_event.reason.value
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        return {
            'total_sessions': len(self.active_sessions),
            'total_halts': total_halts,
            'halt_by_reason': reason_counts,
            'active_sessions': len([s for s in self.active_sessions.values() if s.active])
        }
    
    def configure_halt_condition(self, reason: HaltReason, threshold: float, 
                                auto_halt: bool, recoverable: bool) -> None:
        """Configure halt condition parameters"""
        
        self.halt_conditions[reason] = {
            'threshold': threshold,
            'auto_halt': auto_halt,
            'recoverable': recoverable
        }
