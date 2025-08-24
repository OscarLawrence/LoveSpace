"""
Configuration management and optimization
"""

import asyncio
import time
from typing import Dict, Any
from .data_models import ServiceInfo, ServiceStatus


class ConfigurationManager:
    """Manages service configuration and optimization"""
    
    def __init__(self, services: Dict[str, ServiceInfo], system_configuration: Dict[str, Any]):
        self.services = services
        self.system_configuration = system_configuration
    
    async def optimize_service_configuration(self) -> None:
        """Optimize configuration for all services"""
        for service in self.services.values():
            if service.status == ServiceStatus.HEALTHY:
                await self._analyze_and_adjust_service(service)
    
    async def _analyze_and_adjust_service(self, service: ServiceInfo) -> None:
        """Analyze and adjust configuration for a specific service"""
        # Get current performance metrics
        cpu_usage = service.performance_metrics.get("cpu_usage", 0.5)
        memory_usage = service.performance_metrics.get("memory_usage", 0.5)
        response_time = service.performance_metrics.get("response_time", 100)
        
        # Adjust configuration based on performance
        config_changed = False
        
        # CPU optimization
        if cpu_usage > 0.8:
            current_cpu = float(service.configuration.get("cpu_limit", "1.0").rstrip("GB"))
            new_cpu = min(current_cpu * 1.2, 8.0)
            service.configuration["cpu_limit"] = f"{new_cpu:.1f}"
            config_changed = True
        elif cpu_usage < 0.3:
            current_cpu = float(service.configuration.get("cpu_limit", "1.0").rstrip("GB"))
            new_cpu = max(current_cpu * 0.9, 0.5)
            service.configuration["cpu_limit"] = f"{new_cpu:.1f}"
            config_changed = True
        
        # Memory optimization
        if memory_usage > 0.8:
            current_memory = service.configuration.get("max_memory", "1GB")
            memory_value = float(current_memory.rstrip("GB"))
            new_memory = min(memory_value * 1.2, 16.0)
            service.configuration["max_memory"] = f"{new_memory:.1f}GB"
            config_changed = True
        elif memory_usage < 0.3:
            current_memory = service.configuration.get("max_memory", "1GB")
            memory_value = float(current_memory.rstrip("GB"))
            new_memory = max(memory_value * 0.9, 0.5)
            service.configuration["max_memory"] = f"{new_memory:.1f}GB"
            config_changed = True
        
        # Response time optimization
        if response_time > 150:
            # Increase worker threads if available
            if "worker_threads" in service.configuration:
                current_threads = service.configuration["worker_threads"]
                service.configuration["worker_threads"] = min(current_threads + 1, 8)
                config_changed = True
        
        if config_changed:
            print(f"⚙️ Optimized configuration for {service.service_id}")
    
    async def handle_service_scaling(self) -> None:
        """Handle service scaling based on load"""
        # Group services by type
        service_types = {}
        for service in self.services.values():
            if service.service_type not in service_types:
                service_types[service.service_type] = []
            service_types[service.service_type].append(service)
        
        # Check each service type for scaling needs
        for service_type, instances in service_types.items():
            healthy_instances = [s for s in instances if s.status == ServiceStatus.HEALTHY]
            
            if not healthy_instances:
                continue
            
            # Calculate average load
            avg_cpu = sum(s.performance_metrics.get("cpu_usage", 0.5) for s in healthy_instances) / len(healthy_instances)
            avg_memory = sum(s.performance_metrics.get("memory_usage", 0.5) for s in healthy_instances) / len(healthy_instances)
            
            # Scale up if high load
            if avg_cpu > 0.8 or avg_memory > 0.8:
                if len(healthy_instances) < 3:  # Max 3 instances per service type
                    await self._scale_up_service(service_type)
            
            # Scale down if low load
            elif avg_cpu < 0.3 and avg_memory < 0.3:
                if len(healthy_instances) > 1:  # Keep at least 1 instance
                    await self._scale_down_service(service_type)
    
    async def _scale_up_service(self, service_type: str) -> None:
        """Scale up a service type"""
        print(f"📈 Scaling up {service_type}")
        # Implementation would create new service instance
        # For now, just log the action
    
    async def _scale_down_service(self, service_type: str) -> None:
        """Scale down a service type"""
        print(f"📉 Scaling down {service_type}")
        
        # Find the least loaded instance to remove
        instances = [s for s in self.services.values() 
                    if s.service_type == service_type and s.status == ServiceStatus.HEALTHY]
        
        if len(instances) > 1:
            # Remove the instance with lowest CPU usage
            least_loaded = min(instances, key=lambda s: s.performance_metrics.get("cpu_usage", 0.5))
            least_loaded.status = ServiceStatus.STOPPING
            print(f"🔻 Stopping instance: {least_loaded.service_id}")
    
    async def update_system_configuration(self) -> None:
        """Update global system configuration"""
        # Calculate system-wide metrics
        total_services = len(self.services)
        healthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        
        self.system_configuration.update({
            "total_services": total_services,
            "healthy_services": healthy_services,
            "system_health_ratio": healthy_services / max(total_services, 1),
            "last_updated": time.time()
        })
    
    async def apply_configuration_changes(self) -> None:
        """Apply pending configuration changes"""
        # In a real system, this would apply configuration changes
        # to running services through their management APIs
        for service in self.services.values():
            if service.status == ServiceStatus.HEALTHY:
                # Simulate applying configuration
                await asyncio.sleep(0.1)
        
        print("⚙️ Applied configuration changes to all services")