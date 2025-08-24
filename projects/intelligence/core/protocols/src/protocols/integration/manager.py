"""
Main integration manager using modular components
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable, Set
from collections import defaultdict
from pathlib import Path

from .data_models import ProjectIntegration, IntegrationStatus
from .project_discovery import ProjectDiscovery
from .hook_factory import HookFactory
from .system_manager import SystemManager


class IntegrationManager:
    """Central manager for workspace-wide integration"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        
        # Integration components
        self.project_integrations: Dict[str, ProjectIntegration] = {}
        self.data_collectors: Dict[str, Any] = {}
        self.optimization_engines: Dict[str, Any] = {}
        self.integration_hooks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Modular components
        self.project_discovery = ProjectDiscovery(self.workspace_root)
        self.system_manager = SystemManager(self.workspace_root)
        self.hook_factory = HookFactory(self.system_manager.metrics_collector)
        
        # State
        self.integration_active = False
        self.background_tasks: Set[asyncio.Task] = set()
    
    async def start_integration(self) -> None:
        """Start workspace integration"""
        print(f"🚀 Starting workspace integration at {self.workspace_root}")
        
        # Discover projects
        print("🔍 Discovering projects...")
        self.project_integrations = self.project_discovery.discover_projects()
        
        # Start core systems
        await self.system_manager.start_systems()
        
        # Setup integration for each project
        await self._setup_project_integrations()
        
        # Start background monitoring
        self._start_background_monitoring()
        
        self.integration_active = True
        print(f"✅ Integration active for {len(self.project_integrations)} projects")
    
    async def stop_integration(self) -> None:
        """Stop workspace integration"""
        print("🛑 Stopping workspace integration...")
        
        self.integration_active = False
        
        # Stop background tasks
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()
        
        # Stop core systems
        await self.system_manager.stop_systems()
        
        # Clear state
        self.data_collectors.clear()
        self.optimization_engines.clear()
        self.integration_hooks.clear()
    
    async def _setup_project_integrations(self) -> None:
        """Setup integration for all discovered projects"""
        for project_name, integration in self.project_integrations.items():
            # Create data collector
            collector = self._create_project_collector(integration)
            if collector:
                self.data_collectors[project_name] = collector
            
            # Create optimizer
            optimizer = self._create_project_optimizer(integration)
            if optimizer:
                self.optimization_engines[project_name] = optimizer
            
            # Setup hooks
            for hook_type in integration.integration_hooks:
                hook_func = self.hook_factory.create_hook(hook_type, project_name)
                self.integration_hooks[hook_type].append(hook_func)
    
    def _create_project_collector(self, integration: ProjectIntegration) -> Any:
        """Create data collector for project"""
        if not integration.data_collection_enabled:
            return None
        
        return {
            "project_name": integration.project_name,
            "collection_active": True,
            "metrics_collected": 0,
            "last_collection": time.time()
        }
    
    def _create_project_optimizer(self, integration: ProjectIntegration) -> Any:
        """Create optimizer for project"""
        if not integration.optimization_enabled:
            return None
        
        return {
            "project_name": integration.project_name,
            "optimization_active": True,
            "optimizations_applied": 0,
            "last_optimization": time.time()
        }
    
    def _start_background_monitoring(self) -> None:
        """Start background monitoring tasks"""
        monitoring_task = asyncio.create_task(self._monitoring_loop())
        hook_task = asyncio.create_task(self._hook_execution_loop())
        
        self.background_tasks.add(monitoring_task)
        self.background_tasks.add(hook_task)
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        config = self.system_manager.get_config()
        interval = config.get("monitoring_interval", 30)
        
        while self.integration_active:
            try:
                await self._collect_project_data()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _hook_execution_loop(self) -> None:
        """Background hook execution loop"""
        config = self.system_manager.get_config()
        interval = config.get("hook_execution_interval", 10)
        
        while self.integration_active:
            try:
                await self._execute_hooks()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in hook execution loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_project_data(self) -> None:
        """Collect data from all projects"""
        for project_name, collector in self.data_collectors.items():
            if collector.get("collection_active", False):
                collector["metrics_collected"] += 1
                collector["last_collection"] = time.time()
    
    async def _execute_hooks(self) -> None:
        """Execute all integration hooks"""
        for hook_type, hooks in self.integration_hooks.items():
            for hook in hooks:
                try:
                    await hook()
                except Exception as e:
                    print(f"Error executing {hook_type} hook: {e}")
    
    def get_integration_status(self) -> IntegrationStatus:
        """Get current integration status"""
        return IntegrationStatus(
            total_projects=len(self.project_integrations),
            integrated_projects=len(self.data_collectors),
            active_collectors=len([c for c in self.data_collectors.values() 
                                 if c.get("collection_active", False)]),
            optimization_active=self.system_manager.ai_optimizer.optimization_active if self.system_manager.ai_optimizer else False,
            last_update=time.time()
        )
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get comprehensive integration summary"""
        return {
            "workspace_root": str(self.workspace_root),
            "integration_active": self.integration_active,
            "projects": list(self.project_integrations.keys()),
            "status": self.get_integration_status().__dict__,
            "config": self.system_manager.get_config()
        }
