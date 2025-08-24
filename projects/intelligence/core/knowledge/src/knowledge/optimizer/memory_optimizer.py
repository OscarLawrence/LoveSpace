"""
Main memory integrated optimizer class
"""

from pathlib import Path
from typing import Any

from .analysis import PerformanceAnalyzer
from .memory_consolidation import MemoryConsolidation
from .pattern_storage import PatternStorage
from .recommendation_engine import RecommendationEngine
from .session_manager import SessionManager


class MemoryIntegratedOptimizer:
    """AI Memory system integrated with performance optimization"""

    def __init__(self, storage_path: str | None = None):
        self.storage_path = (
            Path(storage_path) if storage_path else Path("optimizer_memory")
        )
        self.storage_path.mkdir(exist_ok=True)

        self.pattern_storage = PatternStorage(self.storage_path)
        self.session_manager = SessionManager(self.storage_path)
        self.recommendation_engine = RecommendationEngine(self.pattern_storage)
        self.memory_consolidation = MemoryConsolidation()
        self.analyzer = PerformanceAnalyzer()

        self._load_memory_state()

    def store_performance_pattern(
        self,
        context_type: str,
        strategy_name: str,
        performance_metrics: dict[str, float],
        improvement_score: float,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a performance pattern in memory"""
        pattern_id = self.pattern_storage.store_pattern(
            context_type,
            strategy_name,
            performance_metrics,
            improvement_score,
            metadata,
        )

        self.memory_consolidation.record_usage(pattern_id, improvement_score)

        return pattern_id

    def retrieve_similar_patterns(
        self, context_type: str, current_metrics: dict[str, float], top_k: int = 5
    ):
        """Retrieve patterns similar to current context"""
        return self.pattern_storage.retrieve_similar_patterns(
            context_type, current_metrics, top_k
        )

    def start_optimization_session(self, context_data: dict[str, Any]) -> str:
        """Start a new optimization session"""
        return self.session_manager.start_session(context_data)

    def update_session(
        self, session_id: str, strategy_used: str, performance_metrics: dict[str, float]
    ) -> None:
        """Update optimization session with new data"""
        self.session_manager.update_session(
            session_id, strategy_used, performance_metrics
        )

    def end_optimization_session(
        self,
        session_id: str,
        final_metrics: dict[str, float],
        lessons_learned: list[str] | None = None,
    ) -> None:
        """End optimization session and extract learnings"""
        self.session_manager.end_session(session_id, final_metrics, lessons_learned)

    def get_strategy_recommendations(
        self, context_type: str, current_metrics: dict[str, float]
    ) -> list[dict[str, Any]]:
        """Get strategy recommendations based on memory"""
        return self.recommendation_engine.get_recommendations(
            context_type, current_metrics
        )

    def analyze_performance_history(
        self, context_type: str | None = None
    ) -> dict[str, Any]:
        """Analyze historical performance patterns"""
        return self.analyzer.analyze_history(
            self.pattern_storage.performance_patterns,
            self.session_manager.optimization_sessions,
            context_type,
        )

    def get_memory_summary(self) -> dict[str, Any]:
        """Get comprehensive memory system summary"""
        return {
            "total_patterns": len(self.pattern_storage.performance_patterns),
            "total_sessions": len(self.session_manager.optimization_sessions),
            "pattern_correlations": len(self.memory_consolidation.pattern_correlations),
            "usage_history_length": len(
                self.memory_consolidation.pattern_usage_history
            ),
            "cross_session_learnings": len(
                self.session_manager.cross_session_learnings
            ),
            "storage_path": str(self.storage_path),
            "memory_consolidation_threshold": self.memory_consolidation.consolidation_threshold,
            "patterns_by_context": {
                context: len(
                    [
                        p
                        for p in self.pattern_storage.performance_patterns.values()
                        if p.context_type == context
                    ]
                )
                for context in set(
                    p.context_type
                    for p in self.pattern_storage.performance_patterns.values()
                )
            },
        }

    def _load_memory_state(self) -> None:
        """Load memory state from persistent storage"""
        self.pattern_storage.load_patterns()
        self.session_manager.load_sessions()
