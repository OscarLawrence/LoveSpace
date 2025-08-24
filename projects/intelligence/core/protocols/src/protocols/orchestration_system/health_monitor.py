"""
Health monitoring and service recovery
"""

import asyncio
import time
import random
from typing import Dict, List
from .data_models import ServiceInfo, ServiceStatus


class HealthMonitor:
    """Monitors service health and handles recovery"""
    
    def __init__(self, services: Dict[str, ServiceInfo]):
        self.services = services
        self.degradation_threshold = 0.7
        self.failure_threshold = 0.3
    
    async def check_service_health(self, service_id: str) -> None:
        """Check health of a specific service"""
        if service_id not in self.services:
            return
        
        service = self.services[service_id]
        
        # Simulate health check
        health_score = self._calculate_health_score(service)
        service.health_score = health_score
        
        # Update status based on health score
        if health_score >= self.degradation_threshold:
            service.status = ServiceStatus.HEALTHY
        elif health_score >= self.failure_threshold:
            service.status = ServiceStatus.DEGRADED
        else:
            service.status = ServiceStatus.UNHEALTHY
        
        # Update performance metrics
        service.performance_metrics.update({
            "cpu_usage": random.uniform(0.1, 0.9),
            "memory_usage": random.uniform(0.2, 0.8),
            "response_time": random.uniform(10, 200),
            "error_rate": random.uniform(0.0, 0.1)
        })
        
        service.last_heartbeat = time.time()
    
    def _calculate_health_score(self, service: ServiceInfo) -> float:
        """Calculate health score for a service"""
        # Simulate health calculation based on various factors
        base_score = 1.0
        
        # Factor in service age (newer services might be less stable)
        service_age = time.time() - service.last_heartbeat
        age_factor = max(0.8, 1.0 - (service_age / 3600))  # Degrade over 1 hour
        
        # Factor in dependencies
        dependency_factor = 1.0
        for dep in service.dependencies:
            dep_services = [s for s in self.services.values() if s.service_type == dep]
            if not dep_services or all(s.status != ServiceStatus.HEALTHY for s in dep_services):
                dependency_factor *= 0.7
        
        # Random variation to simulate real-world conditions
        random_factor = random.uniform(0.9, 1.0)
        
        health_score = base_score * age_factor * dependency_factor * random_factor
        return max(0.0, min(1.0, health_score))
    
    async def handle_unhealthy_services(self) -> None:
        """Handle services that are unhealthy"""
        unhealthy_services = [
            service_id for service_id, service in self.services.items()
            if service.status == ServiceStatus.UNHEALTHY
        ]
        
        for service_id in unhealthy_services:
            print(f"🚨 Handling unhealthy service: {service_id}")
            await self.attempt_service_recovery(service_id)
    
    async def attempt_service_recovery(self, service_id: str) -> None:
        """Attempt to recover an unhealthy service"""
        if service_id not in self.services:
            return
        
        service = self.services[service_id]
        
        print(f"🔧 Attempting recovery for service: {service_id}")
        
        # Try restart first
        await self._attempt_service_restart(service_id)
        
        # Check if restart was successful
        await asyncio.sleep(5.0)
        await self.check_service_health(service_id)
        
        if service.status == ServiceStatus.UNHEALTHY:
            print(f"❌ Recovery failed for service: {service_id}")
            # Could implement more recovery strategies here
        else:
            print(f"✅ Recovery successful for service: {service_id}")
    
    async def _attempt_service_restart(self, service_id: str) -> None:
        """Attempt to restart a service"""
        if service_id not in self.services:
            return
        
        service = self.services[service_id]
        
        print(f"🔄 Restarting service: {service_id}")
        
        # Mark as stopping
        service.status = ServiceStatus.STOPPING
        await asyncio.sleep(2.0)
        
        # Mark as starting
        service.status = ServiceStatus.STARTING
        await asyncio.sleep(3.0)
        
        # Reset health score and update timestamp
        service.health_score = 1.0
        service.last_heartbeat = time.time()
        service.status = ServiceStatus.HEALTHY
        
        print(f"✅ Service restarted: {service_id}")
    
    def get_health_summary(self) -> Dict[str, int]:
        """Get summary of service health status"""
        status_counts = {}
        for status in ServiceStatus:
            status_counts[status.value] = len([
                s for s in self.services.values() if s.status == status
            ])
        return status_counts