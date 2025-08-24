"""
Core systems management for integration
"""

import asyncio
from typing import Dict, Any, Optional
import json
from pathlib import Path

try:
    from ai_optimizer import AIOptimizer
    from performance_metrics import MetricsCollector, PerformanceTracker
    from protocols.optimizer_protocol import OptimizerProtocol
except ImportError:
    AIOptimizer = MetricsCollector = PerformanceTracker = OptimizerProtocol = None


class SystemManager:
    """Manages core integration systems"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.config_file = workspace_root / ".integration_config.json"
        self.integration_config = self._load_config()
        
        # Core systems
        self.metrics_collector = None
        self.performance_tracker = None
        self.optimizer_protocol = None
        self.ai_optimizer = None
        
        self._initialize_core_systems()
    
    async def start_systems(self) -> None:
        """Start core integration systems"""
        print("⚙️ Starting core systems...")
        
        # Start metrics collector
        if self.metrics_collector:
            self.metrics_collector.start_collection()
        
        # Start performance tracker
        if self.performance_tracker:
            await self.performance_tracker.start_monitoring()
        
        # Start optimizer protocol
        if self.optimizer_protocol:
            asyncio.create_task(self.optimizer_protocol.start_protocol())
        
        # Start AI optimizer
        if self.ai_optimizer:
            asyncio.create_task(self.ai_optimizer.start_optimization())
    
    async def stop_systems(self) -> None:
        """Stop core integration systems"""
        if self.metrics_collector:
            self.metrics_collector.stop_collection()
        
        if self.performance_tracker:
            await self.performance_tracker.stop_monitoring()
        
        if self.optimizer_protocol:
            await self.optimizer_protocol.stop_protocol()
        
        if self.ai_optimizer:
            await self.ai_optimizer.stop_optimization()
    
    def _initialize_core_systems(self) -> None:
        """Initialize core integration systems"""
        try:
            if MetricsCollector:
                self.metrics_collector = MetricsCollector()
            
            if PerformanceTracker:
                self.performance_tracker = PerformanceTracker()
            
            if OptimizerProtocol:
                self.optimizer_protocol = OptimizerProtocol("integration_manager", "integration")
            
            if AIOptimizer:
                self.ai_optimizer = AIOptimizer()
        except Exception as e:
            print(f"Error initializing core systems: {e}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load integration configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "auto_discovery": True,
            "monitoring_interval": 30,
            "hook_execution_interval": 10,
            "default_monitoring_level": "standard"
        }
    
    def save_config(self) -> None:
        """Save integration configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.integration_config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.integration_config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration"""
        self.integration_config.update(updates)
        self.save_config()
