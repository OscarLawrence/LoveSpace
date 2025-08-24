"""
Main orchestrator engine that coordinates all components
"""

import asyncio
import time
from typing import Dict, Any
from .data_models import ServiceInfo, ServiceStatus
from .service_discovery import ServiceDiscovery
from .health_monitor import HealthMonitor
from .configuration_manager import ConfigurationManager


class OrchestratorEngine:
    """Main engine that orchestrates the system coordination"""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.orchestration_active = False
        self.system_configuration = {}
        
        # Core services
        self.core_services = [
            "ai-optimizer",
            "performance-metrics", 
            "workspace-integration",
            "optimization-engine",
            "protocols"
        ]
        
        # Configuration
        self.health_check_interval = 30.0
        
        # Initialize components
        self.service_discovery = ServiceDiscovery(self.services, self.core_services)
        self.health_monitor = HealthMonitor(self.services)
        self.configuration_manager = ConfigurationManager(self.services, self.system_configuration)
    
    async def start_orchestration(self) -> None:
        """Start system orchestration"""
        print("🎼 Starting System Orchestration...")
        
        self.orchestration_active = True
        
        # Start core monitoring tasks
        await asyncio.gather(
            self._service_discovery_loop(),
            self._health_monitoring_loop(),
            self._orchestration_loop(),
            self._configuration_management_loop()
        )
    
    async def stop_orchestration(self) -> None:
        """Stop system orchestration"""
        print("🛑 Stopping System Orchestration...")
        
        # Graceful shutdown of all services
        await self._graceful_shutdown()
        
        self.orchestration_active = False
        print("✅ System Orchestration Stopped")
    
    async def _service_discovery_loop(self) -> None:
        """Service discovery and registration loop"""
        while self.orchestration_active:
            try:
                # Discover new services
                await self.service_discovery.discover_services()
                
                # Update service registry
                await self.service_discovery.update_service_registry()
                
                await asyncio.sleep(60.0)  # Discovery every minute
                
            except Exception as e:
                print(f"Service discovery error: {e}")
                await asyncio.sleep(60.0)
    
    async def _health_monitoring_loop(self) -> None:
        """Health monitoring loop"""
        while self.orchestration_active:
            try:
                # Check health of all services
                for service_id in list(self.services.keys()):
                    await self.health_monitor.check_service_health(service_id)
                
                # Handle unhealthy services
                await self.health_monitor.handle_unhealthy_services()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _orchestration_loop(self) -> None:
        """Main orchestration loop"""
        while self.orchestration_active:
            try:
                # Ensure core services are running
                await self.service_discovery.ensure_core_services()
                
                # Handle service scaling
                await self.configuration_manager.handle_service_scaling()
                
                await asyncio.sleep(120.0)  # Orchestration every 2 minutes
                
            except Exception as e:
                print(f"Orchestration error: {e}")
                await asyncio.sleep(120.0)
    
    async def _configuration_management_loop(self) -> None:
        """Configuration management loop"""
        while self.orchestration_active:
            try:
                # Update system configuration
                await self.configuration_manager.update_system_configuration()
                
                # Optimize service configurations
                await self.configuration_manager.optimize_service_configuration()
                
                # Apply configuration changes
                await self.configuration_manager.apply_configuration_changes()
                
                await asyncio.sleep(300.0)  # Configuration updates every 5 minutes
                
            except Exception as e:
                print(f"Configuration management error: {e}")
                await asyncio.sleep(300.0)
    
    async def _graceful_shutdown(self) -> None:
        """Gracefully shutdown all services"""
        print("🔄 Initiating graceful shutdown...")
        
        # Stop all services in reverse dependency order
        for service in self.services.values():
            if service.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                service.status = ServiceStatus.STOPPING
                print(f"🛑 Stopping service: {service.service_id}")
                
                # Simulate shutdown time
                await asyncio.sleep(1.0)
                
                service.status = ServiceStatus.OFFLINE
        
        print("✅ All services stopped gracefully")
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        health_summary = self.health_monitor.get_health_summary()
        
        return {
            "orchestration_active": self.orchestration_active,
            "total_services": len(self.services),
            "service_status_counts": health_summary,
            "core_services_health": {
                service_type: len([
                    s for s in self.services.values()
                    if s.service_type == service_type and s.status == ServiceStatus.HEALTHY
                ])
                for service_type in self.core_services
            },
            "system_configuration": self.system_configuration,
            "health_check_interval": self.health_check_interval
        }