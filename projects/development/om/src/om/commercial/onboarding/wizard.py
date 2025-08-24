"""Setup wizard for OM Commercial onboarding."""

import sys
import subprocess
from pathlib import Path
from .license_setup import LicenseActivator
from .workspace_setup import WorkspaceDetector, PreferencesSetup


class SetupWizard:
    """Interactive setup wizard."""
    
    def __init__(self, subscription_manager):
        self.subscription_manager = subscription_manager
        self.config_dir = Path.home() / ".om"
        self.license_activator = LicenseActivator(self.config_dir)
        self.workspace_detector = WorkspaceDetector()
        self.preferences_setup = PreferencesSetup(self.config_dir)
        
    def run_setup_wizard(self) -> bool:
        """Run interactive setup wizard."""
        print("🎉 Welcome to OM Commercial!")
        print("Let's get you set up in just a few steps.\n")
        
        try:
            # Step 1: License activation
            if not self.license_activator.setup_license(self.subscription_manager):
                return False
            
            # Step 2: Workspace detection
            self.workspace_detector.detect_workspace()
            
            # Step 3: Preferences setup
            self.preferences_setup.setup_preferences()
            
            # Step 4: Initial validation
            self._validate_setup()
            
            # Step 5: Success message
            self._show_success_message()
            
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False
    
    def _validate_setup(self) -> None:
        """Validate setup configuration."""
        print("\n🔍 Step 4: Validating Setup")
        
        # Check license
        try:
            subscription = self.subscription_manager.load_subscription()
            print("✅ License configuration valid")
        except Exception as e:
            print(f"⚠️  License issue: {e}")
        
        # Check preferences
        prefs_file = self.config_dir / "preferences.json"
        if prefs_file.exists():
            print("✅ Preferences configured")
        else:
            print("⚠️  Preferences not found")
        
        # Test basic command
        try:
            result = subprocess.run([sys.executable, "-c", "import om.commercial"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ OM Commercial installation valid")
            else:
                print("⚠️  OM Commercial import issue")
        except Exception:
            print("⚠️  Could not validate OM Commercial installation")
    
    def _show_success_message(self) -> None:
        """Show setup completion message."""
        print("\n🎉 Setup Complete!")
        print("\nNext steps:")
        print("1. Try: om workspace info")
        print("2. Generate docs: om docs generate")
        print("3. Analyze code: om code analyze")
        print("\nNeed help? Visit: https://docs.om-commercial.com")
        print("Support: support@om-commercial.com\n")
