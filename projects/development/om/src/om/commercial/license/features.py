"""Feature flags and access control."""

from typing import Dict, Any, List, Optional
from enum import Enum
from .subscription import SubscriptionManager, PlanTier


class FeatureFlag(Enum):
    """Available feature flags."""
    ADVANCED_ANALYSIS = "advanced_analysis"
    TEAM_COLLABORATION = "team_collaboration"
    PRIORITY_SUPPORT = "priority_support"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    SLA_GUARANTEE = "sla_guarantee"
    BETA_FEATURES = "beta_features"
    API_ACCESS = "api_access"
    BULK_OPERATIONS = "bulk_operations"


class FeatureManager:
    """Manages feature access based on subscription."""
    
    def __init__(self, subscription_manager: Optional[SubscriptionManager] = None):
        self.subscription_manager = subscription_manager or SubscriptionManager()
        self._feature_cache = {}
    
    def is_feature_enabled(self, feature: FeatureFlag) -> bool:
        """Check if feature is enabled for current subscription."""
        subscription = self.subscription_manager.load_subscription()
        tier = PlanTier(subscription["tier"])
        config = self.subscription_manager.get_plan_config(tier)
        
        # Get feature from subscription config
        features = config["features"]
        
        # Map feature flags to subscription features
        feature_mapping = {
            FeatureFlag.ADVANCED_ANALYSIS: features.advanced_analysis,
            FeatureFlag.TEAM_COLLABORATION: features.team_collaboration,
            FeatureFlag.PRIORITY_SUPPORT: features.priority_support,
            FeatureFlag.CUSTOM_INTEGRATIONS: features.custom_integrations,
            FeatureFlag.SLA_GUARANTEE: features.sla_guarantee,
            FeatureFlag.BETA_FEATURES: tier in [PlanTier.PRO, PlanTier.ENTERPRISE],
            FeatureFlag.API_ACCESS: tier in [PlanTier.PRO, PlanTier.ENTERPRISE],
            FeatureFlag.BULK_OPERATIONS: tier == PlanTier.ENTERPRISE
        }
        
        return feature_mapping.get(feature, False)
    
    def get_enabled_features(self) -> List[FeatureFlag]:
        """Get list of enabled features for current subscription."""
        return [
            feature for feature in FeatureFlag
            if self.is_feature_enabled(feature)
        ]
    
    def require_feature(self, feature: FeatureFlag) -> None:
        """Raise exception if feature is not enabled."""
        if not self.is_feature_enabled(feature):
            raise FeatureNotAvailableError(
                f"Feature '{feature.value}' requires a higher subscription plan"
            )
    
    def get_feature_description(self, feature: FeatureFlag) -> str:
        """Get human-readable description of feature."""
        descriptions = {
            FeatureFlag.ADVANCED_ANALYSIS: "Advanced code analysis and insights",
            FeatureFlag.TEAM_COLLABORATION: "Multi-user workspace sharing",
            FeatureFlag.PRIORITY_SUPPORT: "Priority customer support",
            FeatureFlag.CUSTOM_INTEGRATIONS: "Custom API integrations",
            FeatureFlag.SLA_GUARANTEE: "99.9% uptime SLA guarantee",
            FeatureFlag.BETA_FEATURES: "Access to beta features",
            FeatureFlag.API_ACCESS: "Full API access",
            FeatureFlag.BULK_OPERATIONS: "Bulk processing operations"
        }
        return descriptions.get(feature, feature.value)
    
    def get_upgrade_message(self, feature: FeatureFlag) -> str:
        """Get upgrade message for disabled feature."""
        subscription = self.subscription_manager.load_subscription()
        current_tier = PlanTier(subscription["tier"])
        
        # Determine required tier for feature
        required_tier = self._get_required_tier(feature)
        
        if required_tier == PlanTier.PRO and current_tier == PlanTier.STARTER:
            return f"Upgrade to Pro ($200/month) to unlock {self.get_feature_description(feature)}"
        elif required_tier == PlanTier.ENTERPRISE:
            return f"Upgrade to Enterprise ($500/month) to unlock {self.get_feature_description(feature)}"
        
        return f"Feature '{feature.value}' is not available in your current plan"
    
    def _get_required_tier(self, feature: FeatureFlag) -> PlanTier:
        """Get minimum tier required for feature."""
        tier_requirements = {
            FeatureFlag.ADVANCED_ANALYSIS: PlanTier.PRO,
            FeatureFlag.TEAM_COLLABORATION: PlanTier.PRO,
            FeatureFlag.PRIORITY_SUPPORT: PlanTier.ENTERPRISE,
            FeatureFlag.CUSTOM_INTEGRATIONS: PlanTier.ENTERPRISE,
            FeatureFlag.SLA_GUARANTEE: PlanTier.ENTERPRISE,
            FeatureFlag.BETA_FEATURES: PlanTier.PRO,
            FeatureFlag.API_ACCESS: PlanTier.PRO,
            FeatureFlag.BULK_OPERATIONS: PlanTier.ENTERPRISE
        }
        return tier_requirements.get(feature, PlanTier.ENTERPRISE)


class FeatureNotAvailableError(Exception):
    """Feature is not available in current subscription plan."""
    pass


def feature_required(feature: FeatureFlag):
    """Decorator to require feature for function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            feature_manager = FeatureManager()
            feature_manager.require_feature(feature)
            return func(*args, **kwargs)
        return wrapper
    return decorator
