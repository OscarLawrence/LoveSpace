"""
OM Deployment Module - Pure Logic, Zero Inconsistencies
Eliminates built-in tool chaos through unified OM interface.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class DeploymentResult:
    """Deployment operation result."""
    success: bool
    url: Optional[str] = None
    logs: List[str] = None
    error: Optional[str] = None
    platform: Optional[str] = None


class OMDeployment:
    """Pure OM deployment interface - no built-in tool dependencies."""
    
    def __init__(self):
        self.supported_platforms = ['railway', 'render', 'heroku', 'vercel']
        self.deployment_history = []
    
    def deploy_live_platform(self, platform: str = 'railway') -> DeploymentResult:
        """Deploy live collaboration platform through OM."""
        if platform not in self.supported_platforms:
            return DeploymentResult(
                success=False,
                error=f"Platform {platform} not supported. Use: {self.supported_platforms}"
            )
        
        try:
            if platform == 'railway':
                return self._deploy_railway()
            elif platform == 'render':
                return self._deploy_render()
            elif platform == 'heroku':
                return self._deploy_heroku()
            elif platform == 'vercel':
                return self._deploy_vercel()
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=str(e),
                platform=platform
            )
    
    def _deploy_railway(self) -> DeploymentResult:
        """Railway deployment through OM."""
        try:
            # Check if railway CLI available
            result = subprocess.run(['railway', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return DeploymentResult(
                    success=False,
                    error="Railway CLI not installed. Use: npm install -g @railway/cli"
                )
            
            # Deploy
            deploy_result = subprocess.run(['railway', 'up'], 
                                         capture_output=True, text=True)
            
            if deploy_result.returncode == 0:
                # Extract URL from output
                url = self._extract_railway_url(deploy_result.stdout)
                
                result = DeploymentResult(
                    success=True,
                    url=url,
                    logs=[deploy_result.stdout],
                    platform='railway'
                )
                self.deployment_history.append(result)
                return result
            else:
                return DeploymentResult(
                    success=False,
                    error=deploy_result.stderr,
                    logs=[deploy_result.stdout],
                    platform='railway'
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=f"Railway deployment failed: {str(e)}",
                platform='railway'
            )
    
    def _extract_railway_url(self, output: str) -> Optional[str]:
        """Extract deployment URL from Railway output."""
        lines = output.split('\n')
        for line in lines:
            if 'https://' in line and 'railway.app' in line:
                # Extract URL
                import re
                url_match = re.search(r'https://[^\s]+', line)
                if url_match:
                    return url_match.group(0)
        return None
    
    def _deploy_render(self) -> DeploymentResult:
        """Render deployment through OM."""
        return DeploymentResult(
            success=False,
            error="Render deployment requires web interface connection to GitHub repo",
            platform='render'
        )
    
    def _deploy_heroku(self) -> DeploymentResult:
        """Heroku deployment through OM."""
        try:
            # Check Heroku CLI
            result = subprocess.run(['heroku', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return DeploymentResult(
                    success=False,
                    error="Heroku CLI not installed",
                    platform='heroku'
                )
            
            # Create app and deploy
            app_name = 'om-collaboration-platform'
            create_result = subprocess.run(['heroku', 'create', app_name], 
                                         capture_output=True, text=True)
            
            deploy_result = subprocess.run(['git', 'push', 'heroku', 'master'], 
                                         capture_output=True, text=True)
            
            if deploy_result.returncode == 0:
                url = f"https://{app_name}.herokuapp.com"
                result = DeploymentResult(
                    success=True,
                    url=url,
                    logs=[create_result.stdout, deploy_result.stdout],
                    platform='heroku'
                )
                self.deployment_history.append(result)
                return result
            else:
                return DeploymentResult(
                    success=False,
                    error=deploy_result.stderr,
                    platform='heroku'
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                error=f"Heroku deployment failed: {str(e)}",
                platform='heroku'
            )
    
    def _deploy_vercel(self) -> DeploymentResult:
        """Vercel deployment through OM."""
        return DeploymentResult(
            success=False,
            error="Vercel optimized for frontend. Use Railway/Heroku for Flask apps",
            platform='vercel'
        )
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment status through OM."""
        return {
            'total_deployments': len(self.deployment_history),
            'successful_deployments': len([d for d in self.deployment_history if d.success]),
            'platforms_used': list(set(d.platform for d in self.deployment_history if d.platform)),
            'latest_deployment': self.deployment_history[-1] if self.deployment_history else None
        }
    
    def check_live_platform(self, url: str) -> Dict[str, Any]:
        """Check if live platform is accessible through OM."""
        try:
            import requests
            response = requests.get(url, timeout=10)
            
            return {
                'accessible': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'url': url
            }
        except Exception as e:
            return {
                'accessible': False,
                'error': str(e),
                'url': url
            }


def deploy_collaboration_platform(platform: str = 'railway') -> DeploymentResult:
    """OM function to deploy live collaboration platform."""
    deployer = OMDeployment()
    return deployer.deploy_live_platform(platform)


def check_platform_status(url: str) -> Dict[str, Any]:
    """OM function to check platform status."""
    deployer = OMDeployment()
    return deployer.check_live_platform(url)