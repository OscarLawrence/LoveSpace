"""Subscription management and billing logic."""

import json
import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path


class PlanTier(Enum):
    """Subscription plan tiers."""
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class SubscriptionLimits:
    """Usage limits for subscription plans."""
    commands_per_day: int
    projects: int
    team_members: int
    storage_gb: int = 10
    api_calls_per_hour: int = 100


@dataclass
class SubscriptionFeatures:
    """Features enabled for subscription plans."""
    advanced_analysis: bool = False
    team_collaboration: bool = False
    priority_support: bool = False
    custom_integrations: bool = False
    sla_guarantee: bool = False


class SubscriptionManager:
    """Manages subscription plans and billing cycles."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".om" / "subscription.json"
        self._usage_cache = {}
        
    def get_plan_config(self, tier: PlanTier) -> Dict[str, Any]:
        """Get configuration for subscription tier."""
        configs = {
            PlanTier.STARTER: {
                "price_monthly": 50,
                "limits": SubscriptionLimits(
                    commands_per_day=100,
                    projects=1,
                    team_members=1,
                    storage_gb=5,
                    api_calls_per_hour=50
                ),
                "features": SubscriptionFeatures()
            },
            PlanTier.PRO: {
                "price_monthly": 200,
                "limits": SubscriptionLimits(
                    commands_per_day=1000,
                    projects=5,
                    team_members=5,
                    storage_gb=50,
                    api_calls_per_hour=500
                ),
                "features": SubscriptionFeatures(
                    advanced_analysis=True,
                    team_collaboration=True
                )
            },
            PlanTier.ENTERPRISE: {
                "price_monthly": 500,
                "limits": SubscriptionLimits(
                    commands_per_day=-1,  # unlimited
                    projects=-1,
                    team_members=-1,
                    storage_gb=500,
                    api_calls_per_hour=-1
                ),
                "features": SubscriptionFeatures(
                    advanced_analysis=True,
                    team_collaboration=True,
                    priority_support=True,
                    custom_integrations=True,
                    sla_guarantee=True
                )
            }
        }
        return configs[tier]
    
    def load_subscription(self) -> Dict[str, Any]:
        """Load current subscription data."""
        if not self.config_path.exists():
            return self._create_default_subscription()
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _create_default_subscription(self) -> Dict[str, Any]:
        """Create default starter subscription."""
        default = {
            "tier": PlanTier.STARTER.value,
            "status": "trial",
            "created_at": datetime.datetime.now().isoformat(),
            "trial_ends_at": (datetime.datetime.now() + datetime.timedelta(days=14)).isoformat(),
            "billing_cycle": "monthly",
            "usage": {
                "commands_today": 0,
                "last_reset": datetime.date.today().isoformat()
            }
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(default, f, indent=2)
        
        return default
    
    def check_usage_limits(self, command_type: str = "general") -> bool:
        """Check if usage is within subscription limits."""
        subscription = self.load_subscription()
        tier = PlanTier(subscription["tier"])
        config = self.get_plan_config(tier)
        
        # Check daily command limit
        usage = subscription.get("usage", {})
        today = datetime.date.today().isoformat()
        
        if usage.get("last_reset") != today:
            # Reset daily counters
            usage["commands_today"] = 0
            usage["last_reset"] = today
            subscription["usage"] = usage
            self._save_subscription(subscription)
        
        daily_limit = config["limits"].commands_per_day
        if daily_limit > 0 and usage["commands_today"] >= daily_limit:
            return False
        
        return True
    
    def record_usage(self, command_type: str = "general") -> None:
        """Record command usage."""
        subscription = self.load_subscription()
        usage = subscription.get("usage", {})
        
        usage["commands_today"] = usage.get("commands_today", 0) + 1
        subscription["usage"] = usage
        
        self._save_subscription(subscription)
    
    def _save_subscription(self, data: Dict[str, Any]) -> None:
        """Save subscription data to file."""
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
