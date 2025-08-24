"""Commercial CLI wrapper for OM tool."""

import click
import sys
import os
import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from .license import (
    LicenseValidator, 
    SubscriptionManager, 
    FeatureManager,
    LicenseValidationError,
    FeatureNotAvailableError,
    FeatureFlag
)


class CommercialCLIWrapper:
    """Wraps OM CLI with commercial licensing and usage tracking."""
    
    def __init__(self):
        self.license_validator = LicenseValidator()
        self.subscription_manager = SubscriptionManager()
        self.feature_manager = FeatureManager(self.subscription_manager)
        self._original_cli = None
    
    def validate_license_on_startup(self) -> bool:
        """Validate license before allowing any commands."""
        try:
            config = self.license_validator.load_license()
            license_key = config.get("license_key")
            
            if not license_key:
                self._show_trial_message()
                return self._check_trial_status()
            
            # Validate license
            license_data = self.license_validator.validate(license_key)
            
            # Update subscription data
            self._sync_subscription_with_license(license_data)
            
            return True
            
        except LicenseValidationError as e:
            click.echo(f"License validation failed: {e}", err=True)
            self._show_purchase_info()
            return False
        except Exception as e:
            click.echo(f"Unexpected error during license validation: {e}", err=True)
            return False
    
    def check_usage_limits(self, command_name: str) -> bool:
        """Check if command is within usage limits."""
        return self.subscription_manager.check_usage_limits(command_name)
    
    def record_command_usage(self, command_name: str) -> None:
        """Record command usage for billing/analytics."""
        self.subscription_manager.record_usage(command_name)
    
    def check_feature_access(self, feature: FeatureFlag) -> bool:
        """Check if feature is available in current plan."""
        return self.feature_manager.is_feature_enabled(feature)
    
    def require_feature(self, feature: FeatureFlag) -> None:
        """Require feature or show upgrade message."""
        try:
            self.feature_manager.require_feature(feature)
        except FeatureNotAvailableError:
            click.echo(self.feature_manager.get_upgrade_message(feature), err=True)
            sys.exit(1)
    
    def wrap_command(self, original_func, command_name: str, required_features: list = None):
        """Wrap original OM command with commercial checks."""
        @click.pass_context
        def wrapper(ctx, *args, **kwargs):
            # License validation
            if not self.validate_license_on_startup():
                sys.exit(1)
            
            # Usage limits check
            if not self.check_usage_limits(command_name):
                click.echo("Daily usage limit reached. Upgrade your plan for more usage.", err=True)
                self._show_upgrade_info()
                sys.exit(1)
            
            # Feature access check
            if required_features:
                for feature in required_features:
                    self.require_feature(feature)
            
            # Record usage
            self.record_command_usage(command_name)
            
            # Execute original command
            try:
                return original_func(*args, **kwargs)
            except Exception as e:
                # Log error for customer support
                self._log_error(command_name, str(e))
                raise
        
        return wrapper
    
    def _check_trial_status(self) -> bool:
        """Check if trial period is still valid."""
        subscription = self.subscription_manager.load_subscription()
        
        if subscription.get("status") != "trial":
            return True
        
        trial_end = datetime.datetime.fromisoformat(subscription["trial_ends_at"])
        if datetime.datetime.now() > trial_end:
            click.echo("Trial period has expired. Please purchase a license to continue.", err=True)
            self._show_purchase_info()
            return False
        
        days_left = (trial_end - datetime.datetime.now()).days
        click.echo(f"Trial: {days_left} days remaining")
        return True
    
    def _sync_subscription_with_license(self, license_data: Dict[str, Any]) -> None:
        """Sync local subscription with license server data."""
        subscription = self.subscription_manager.load_subscription()
        
        # Update with license data
        subscription.update({
            "tier": license_data.get("plan", "starter"),
            "status": "active",
            "license_validated_at": datetime.datetime.now().isoformat()
        })
        
        self.subscription_manager._save_subscription(subscription)
    
    def _show_trial_message(self) -> None:
        """Show trial information."""
        click.echo("OM Commercial - Trial Version")
        click.echo("Get full access with a commercial license.")
    
    def _show_purchase_info(self) -> None:
        """Show purchase information."""
        click.echo("\nPurchase OM Commercial:")
        click.echo("• Starter: $50/month - Basic features")
        click.echo("• Pro: $200/month - Advanced features") 
        click.echo("• Enterprise: $500/month - Full features + support")
        click.echo("\nVisit: https://om-commercial.com/pricing")
    
    def _show_upgrade_info(self) -> None:
        """Show upgrade information."""
        subscription = self.subscription_manager.load_subscription()
        current_tier = subscription.get("tier", "starter")
        
        if current_tier == "starter":
            click.echo("\nUpgrade to Pro ($200/month) for:")
            click.echo("• 1000 commands/day")
            click.echo("• Advanced analysis")
            click.echo("• Team collaboration")
        
        click.echo("\nUpgrade at: https://om-commercial.com/upgrade")
    
    def _log_error(self, command: str, error: str) -> None:
        """Log error for customer support tracking."""
        log_path = Path.home() / ".om" / "error.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            timestamp = datetime.datetime.now().isoformat()
            f.write(f"{timestamp} | {command} | {error}\n")


# Global wrapper instance
cli_wrapper = CommercialCLIWrapper()
