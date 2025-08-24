"""
Optimization session management
"""

import time
import json
import numpy as np
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path

from .data_models import OptimizationSession


class SessionManager:
    """Manages optimization sessions"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.optimization_sessions: Dict[str, OptimizationSession] = {}
        self.cross_session_learnings: Dict[str, Any] = {}
    
    def start_session(self, context_data: Dict[str, Any]) -> str:
        """Start a new optimization session"""
        session_id = f"session_{int(time.time())}_{len(self.optimization_sessions)}"
        
        session = OptimizationSession(
            session_id=session_id,
            start_time=time.time(),
            end_time=None,
            strategies_used=[],
            performance_trajectory=[],
            final_improvement=0.0,
            context_data=context_data
        )
        
        self.optimization_sessions[session_id] = session
        return session_id
    
    def update_session(self, session_id: str, strategy_used: str,
                      performance_metrics: Dict[str, float]) -> None:
        """Update optimization session with new data"""
        if session_id not in self.optimization_sessions:
            return
        
        session = self.optimization_sessions[session_id]
        
        if strategy_used not in session.strategies_used:
            session.strategies_used.append(strategy_used)
        
        performance_snapshot = performance_metrics.copy()
        performance_snapshot["timestamp"] = time.time()
        session.performance_trajectory.append(performance_snapshot)
    
    def end_session(self, session_id: str,
                   final_metrics: Dict[str, float],
                   lessons_learned: Optional[List[str]] = None) -> None:
        """End optimization session and extract learnings"""
        if session_id not in self.optimization_sessions:
            return
        
        session = self.optimization_sessions[session_id]
        session.end_time = time.time()
        
        if lessons_learned:
            session.lessons_learned = lessons_learned
        
        if session.performance_trajectory:
            initial_metrics = session.performance_trajectory[0]
            session.final_improvement = self._calculate_improvement(
                initial_metrics, final_metrics
            )
        
        self._extract_session_learnings(session)
        self._save_session(session)
    
    def _calculate_improvement(self, initial_metrics: Dict[str, float],
                             final_metrics: Dict[str, float]) -> float:
        """Calculate overall improvement score"""
        improvements = []
        
        for metric in initial_metrics:
            if metric in final_metrics and metric != "timestamp":
                initial_val = initial_metrics[metric]
                final_val = final_metrics[metric]
                
                if initial_val != 0:
                    improvement = (final_val - initial_val) / abs(initial_val)
                    improvements.append(improvement)
        
        return np.mean(improvements) if improvements else 0.0
    
    def _extract_session_learnings(self, session: OptimizationSession) -> None:
        """Extract learnings from completed session"""
        session_key = f"session_learning_{session.session_id}"
        
        strategy_effectiveness = {}
        for i, snapshot in enumerate(session.performance_trajectory):
            if i > 0:
                prev_snapshot = session.performance_trajectory[i-1]
                improvement = self._calculate_improvement(prev_snapshot, snapshot)
                
                for strategy in session.strategies_used:
                    if strategy not in strategy_effectiveness:
                        strategy_effectiveness[strategy] = []
                    strategy_effectiveness[strategy].append(improvement)
        
        self.cross_session_learnings[session_key] = {
            "session_id": session.session_id,
            "duration": session.end_time - session.start_time if session.end_time else 0,
            "strategies_effectiveness": {
                strategy: np.mean(improvements)
                for strategy, improvements in strategy_effectiveness.items()
            },
            "final_improvement": session.final_improvement,
            "context": session.context_data,
            "lessons": session.lessons_learned
        }
    
    def _save_session(self, session: OptimizationSession) -> None:
        """Save session to persistent storage"""
        session_file = self.storage_path / f"session_{session.session_id}.json"
        
        session_data = {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "strategies_used": session.strategies_used,
            "performance_trajectory": session.performance_trajectory,
            "final_improvement": session.final_improvement,
            "context_data": session.context_data,
            "lessons_learned": session.lessons_learned
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def load_sessions(self) -> None:
        """Load sessions from persistent storage"""
        if not self.storage_path.exists():
            return
        
        for session_file in self.storage_path.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                session = OptimizationSession(**session_data)
                self.optimization_sessions[session.session_id] = session
                
            except Exception as e:
                print(f"Error loading session from {session_file}: {e}")
