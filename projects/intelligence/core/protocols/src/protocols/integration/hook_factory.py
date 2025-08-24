"""
Hook factory for creating integration monitoring hooks
"""

from typing import Callable, Any, Optional


class HookFactory:
    """Factory for creating integration monitoring hooks"""
    
    def __init__(self, metrics_collector: Optional[Any] = None):
        self.metrics_collector = metrics_collector
    
    def create_hook(self, hook_type: str, project_name: str) -> Callable:
        """Create monitoring hook based on type"""
        if hook_type == "source_code_monitoring":
            return self._create_source_monitoring_hook(project_name)
        elif hook_type == "test_monitoring":
            return self._create_test_monitoring_hook(project_name)
        elif hook_type == "ai_performance_monitoring":
            return self._create_ai_performance_hook(project_name)
        else:
            return self._create_basic_monitoring_hook(project_name)
    
    def _create_source_monitoring_hook(self, project_name: str) -> Callable:
        """Create source code monitoring hook"""
        async def source_hook():
            if self.metrics_collector:
                self.metrics_collector.collect_metric(
                    "source_activity",
                    1.0,
                    tags={"project": project_name, "type": "source_monitoring"}
                )
        
        return source_hook
    
    def _create_test_monitoring_hook(self, project_name: str) -> Callable:
        """Create test monitoring hook"""
        async def test_hook():
            if self.metrics_collector:
                self.metrics_collector.collect_metric(
                    "test_activity",
                    1.0,
                    tags={"project": project_name, "type": "test_monitoring"}
                )
        
        return test_hook
    
    def _create_ai_performance_hook(self, project_name: str) -> Callable:
        """Create AI performance monitoring hook"""
        async def ai_hook():
            if self.metrics_collector:
                self.metrics_collector.collect_metric(
                    "ai_performance",
                    1.0,
                    tags={"project": project_name, "type": "ai_monitoring"}
                )
        
        return ai_hook
    
    def _create_basic_monitoring_hook(self, project_name: str) -> Callable:
        """Create basic monitoring hook"""
        async def basic_hook():
            if self.metrics_collector:
                self.metrics_collector.collect_metric(
                    "project_activity",
                    1.0,
                    tags={"project": project_name, "type": "basic_monitoring"}
                )
        
        return basic_hook
