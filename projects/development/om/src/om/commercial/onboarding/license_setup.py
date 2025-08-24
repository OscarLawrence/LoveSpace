"""License activation and validation utilities."""

import json
from pathlib import Path


class LicenseActivator:
    """Handles license key activation."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        
    def activate_license(self, license_key: str) -> bool:
        """Activate license key."""
        try:
            from ...license import LicenseValidator
            validator = LicenseValidator()
            
            # Validate license
            license_data = validator.validate(license_key)
            
            # Save license config
            config = {
                "license_key": license_key,
                "activated_at": license_data.get("activated_at"),
                "plan": license_data.get("plan")
            }
            
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_dir / "commercial.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ License activated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ License activation failed: {e}")
            return False
    
    def start_trial(self) -> bool:
        """Start trial period."""
        print("✅ Starting 14-day free trial...")
        # Trial is created by default in SubscriptionManager
        return True
    
    def setup_license(self, subscription_manager) -> bool:
        """Set up license key."""
        print("📋 Step 1: License Setup")
        
        # Check if license already exists
        try:
            subscription = subscription_manager.load_subscription()
            if subscription.get("status") == "active":
                print("✅ Valid license already configured")
                return True
        except:
            pass
        
        # Check for trial
        print("Choose an option:")
        print("1. Enter license key")
        print("2. Start 14-day free trial")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            license_key = input("Enter your license key: ").strip()
            return self.activate_license(license_key)
        elif choice == "2":
            return self.start_trial()
        else:
            print("Invalid choice")
            return False
