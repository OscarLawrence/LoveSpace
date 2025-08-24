"""
Service discovery and registry management
"""

import asyncio
import time
from typing import Dict, List, Any
from .data_models import ServiceInfo, ServiceStatus


class ServiceDiscovery:
    """Handles service discovery and registry management"""
    
    def __init__(self, services: Dict[str, ServiceInfo], core_services: List[str]):
        self.services = services
        self.core_services = core_services
        self.service_dependencies = {
            "ai-optimizer": ["protocols", "performance-metrics"],
            "workspace-integration": ["ai-optimizer", "performance-metrics"],
            "optimization-engine": ["ai-optimizer", "performance-metrics"],
        }
    
    async def discover_services(self) -> None:
        """Discover available services in the system"""
        # Simulate service discovery
        discovered_services = [
            "ai-optimizer-1",
            "performance-metrics-1", 
            "workspace-integration-1",
            "optimization-engine-1",
            "protocols-1"
        ]
        
        for service_id in discovered_services:
            if service_id not in self.services:
                # New service discovered
                service_type = service_id.split('-')[0] + '-' + service_id.split('-')[1]
                
                self.services[service_id] = ServiceInfo(
                    service_id=service_id,
                    service_type=service_type,
                    status=ServiceStatus.STARTING,
                    health_score=1.0,
                    last_heartbeat=time.time(),
                    configuration=self._get_default_configuration(service_type),
                    dependencies=self.service_dependencies.get(service_type, []),
                    performance_metrics={}
                )
                
                print(f"🔍 Discovered new service: {service_id}")
    
    async def update_service_registry(self) -> None:
        """Update service registry with current information"""
        current_time = time.time()
        
        for service_id, service in self.services.items():
            # Update last seen time for active services
            if service.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                service.last_heartbeat = current_time
            
            # Check for stale services
            if current_time - service.last_heartbeat > 300:  # 5 minutes
                if service.status != ServiceStatus.OFFLINE:
                    service.status = ServiceStatus.OFFLINE
                    print(f"⚠️ Service {service_id} marked as offline")
    
    def _get_default_configuration(self, service_type: str) -> Dict[str, Any]:
        """Get default configuration for service type"""
        configurations = {
            "ai-optimizer": {
                "max_memory": "2GB",
                "cpu_limit": "2.0",
                "optimization_interval": 60,
                "strategy_timeout": 30
            },
            "performance-metrics": {
                "max_memory": "1GB", 
                "cpu_limit": "1.0",
                "collection_interval": 10,
                "retention_days": 30
            },
            "workspace-integration": {
                "max_memory": "1GB",
                "cpu_limit": "1.0", 
                "sync_interval": 30,
                "batch_size": 100
            },
            "optimization-engine": {
                "max_memory": "4GB",
                "cpu_limit": "4.0",
                "worker_threads": 4,
                "queue_size": 1000
            },
            "protocols": {
                "max_memory": "512MB",
                "cpu_limit": "0.5",
                "heartbeat_interval": 30,
                "message_timeout": 60
            }
        }
        
        return configurations.get(service_type, {
            "max_memory": "1GB",
            "cpu_limit": "1.0"
        })
    
    async def ensure_core_services(self) -> None:
        """Ensure all core services are running"""
        for service_type in self.core_services:
            # Check if we have a healthy instance of this service type
            healthy_instances = [
                s for s in self.services.values()
                if s.service_type == service_type and s.status == ServiceStatus.HEALTHY
            ]
            
            if not healthy_instances:
                await self._start_core_service(service_type)
    
    async def _start_core_service(self, service_type: str) -> None:
        """Start a core service instance"""
        service_id = f"{service_type}-{int(time.time())}"
        
        self.services[service_id] = ServiceInfo(
            service_id=service_id,
            service_type=service_type,
            status=ServiceStatus.STARTING,
            health_score=1.0,
            last_heartbeat=time.time(),
            configuration=self._get_default_configuration(service_type),
            dependencies=self.service_dependencies.get(service_type, []),
            performance_metrics={}
        )
        
        print(f"🚀 Starting core service: {service_id}")
        
        # Simulate startup time
        await asyncio.sleep(2.0)
        
        self.services[service_id].status = ServiceStatus.HEALTHY
        print(f"✅ Core service started: {service_id}")