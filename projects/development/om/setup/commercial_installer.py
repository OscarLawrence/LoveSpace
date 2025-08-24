"""Commercial OM installation and setup system."""

import os
import sys
import subprocess
import shutil
import json
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional


class CommercialInstaller:
    """Handles installation and setup of OM Commercial."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_version = sys.version_info
        self.install_dir = Path.home() / ".om"
        self.required_python = (3, 8)
        
    def install(self, license_key: Optional[str] = None) -> bool:
        """Main installation process."""
        print("🚀 Installing OM Commercial...")
        
        try:
            # Pre-installation checks
            if not self._check_system_requirements():
                return False
            
            # Create directories
            self._create_directories()
            
            # Install dependencies
            if not self._install_dependencies():
                return False
            
            # Configure license
            if license_key:
                self._configure_license(license_key)
            
            # Set up shell integration
            self._setup_shell_integration()
            
            # Create desktop shortcuts (if GUI available)
            self._create_shortcuts()
            
            # Run post-install validation
            if not self._validate_installation():
                return False
            
            print("✅ OM Commercial installed successfully!")
            self._show_next_steps()
            return True
            
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def uninstall(self) -> bool:
        """Uninstall OM Commercial."""
        print("🗑️  Uninstalling OM Commercial...")
        
        try:
            # Remove installation directory
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
            
            # Remove shell integration
            self._remove_shell_integration()
            
            # Remove desktop shortcuts
            self._remove_shortcuts()
            
            print("✅ OM Commercial uninstalled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Uninstallation failed: {e}")
            return False
    
    def _check_system_requirements(self) -> bool:
        """Check system requirements."""
        print("🔍 Checking system requirements...")
        
        # Python version check
        if self.python_version < self.required_python:
            print(f"❌ Python {self.required_python[0]}.{self.required_python[1]}+ required")
            print(f"   Current version: {self.python_version[0]}.{self.python_version[1]}")
            return False
        
        # Check available disk space (require 500MB)
        free_space = shutil.disk_usage(Path.home()).free
        required_space = 500 * 1024 * 1024  # 500MB
        
        if free_space < required_space:
            print(f"❌ Insufficient disk space. Required: 500MB, Available: {free_space // 1024 // 1024}MB")
            return False
        
        # Check internet connectivity
        if not self._check_internet():
            print("❌ Internet connection required for installation")
            return False
        
        print("✅ System requirements satisfied")
        return True
    
    def _check_internet(self) -> bool:
        """Check internet connectivity."""
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            return True
        except:
            return False
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        directories = [
            self.install_dir,
            self.install_dir / "logs",
            self.install_dir / "cache",
            self.install_dir / "analytics",
            self.install_dir / "support"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _install_dependencies(self) -> bool:
        """Install required Python packages."""
        print("📦 Installing dependencies...")
        
        dependencies = [
            "click>=8.0.0",
            "requests>=2.25.0",
            "pydantic>=1.8.0",
            "psutil>=5.8.0",
            "cryptography>=3.0.0"
        ]
        
        try:
            for dep in dependencies:
                print(f"  Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Failed to install {dep}")
                    print(result.stderr)
                    return False
            
            print("✅ Dependencies installed")
            return True
            
        except Exception as e:
            print(f"❌ Dependency installation failed: {e}")
            return False
    
    def _configure_license(self, license_key: str) -> None:
        """Configure license key."""
        print("🔑 Configuring license...")
        
        config = {
            "license_key": license_key,
            "configured_at": "2025-08-18T12:00:00",
            "installer_version": "1.0.0"
        }
        
        config_file = self.install_dir / "commercial.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ License configured")
    
    def _setup_shell_integration(self) -> None:
        """Set up shell integration for easy command access."""
        print("🐚 Setting up shell integration...")
        
        # Create shell script wrapper
        script_content = self._get_shell_script()
        
        if self.platform == "windows":
            script_path = self.install_dir / "om.bat"
            with open(script_path, 'w') as f:
                f.write(f"@echo off\npython -m om.commercial.cli %*\n")
        else:
            script_path = self.install_dir / "om"
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
        
        # Try to add to PATH
        self._add_to_path(str(self.install_dir))
        
        print("✅ Shell integration configured")
    
    def _get_shell_script(self) -> str:
        """Get shell script content."""
        return f"""#!/bin/bash
# OM Commercial launcher script
export OM_INSTALL_DIR="{self.install_dir}"
{sys.executable} -m om.commercial.cli "$@"
"""
    
    def _add_to_path(self, directory: str) -> None:
        """Add directory to system PATH."""
        try:
            if self.platform == "windows":
                # Windows PATH modification
                subprocess.run([
                    "setx", "PATH", f"%PATH%;{directory}"
                ], check=False, capture_output=True)
            else:
                # Unix-like systems - add to shell profile
                shell_profiles = [
                    Path.home() / ".bashrc",
                    Path.home() / ".zshrc",
                    Path.home() / ".profile"
                ]
                
                path_line = f'export PATH="$PATH:{directory}"\n'
                
                for profile in shell_profiles:
                    if profile.exists():
                        with open(profile, 'a') as f:
                            f.write(f"\n# OM Commercial\n{path_line}")
                        break
        except Exception:
            # Non-critical failure
            pass
    
    def _create_shortcuts(self) -> None:
        """Create desktop shortcuts."""
        if self.platform == "linux" and os.environ.get("DISPLAY"):
            self._create_linux_desktop_entry()
        elif self.platform == "windows":
            self._create_windows_shortcut()
    
    def _create_linux_desktop_entry(self) -> None:
        """Create Linux desktop entry."""
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        entry_content = f"""[Desktop Entry]
Name=OM Commercial
Comment=AI-first monorepo management tool
Exec={sys.executable} -m om.commercial.cli
Icon=terminal
Terminal=true
Type=Application
Categories=Development;
"""
        
        with open(desktop_dir / "om-commercial.desktop", 'w') as f:
            f.write(entry_content)
    
    def _create_windows_shortcut(self) -> None:
        """Create Windows shortcut."""
        # Simplified - would use pywin32 in production
        pass
    
    def _remove_shell_integration(self) -> None:
        """Remove shell integration."""
        script_paths = [
            self.install_dir / "om",
            self.install_dir / "om.bat"
        ]
        
        for path in script_paths:
            if path.exists():
                path.unlink()
    
    def _remove_shortcuts(self) -> None:
        """Remove desktop shortcuts."""
        if self.platform == "linux":
            desktop_file = Path.home() / ".local" / "share" / "applications" / "om-commercial.desktop"
            if desktop_file.exists():
                desktop_file.unlink()
    
    def _validate_installation(self) -> bool:
        """Validate installation."""
        print("✅ Validating installation...")
        
        # Check directory structure
        required_dirs = ["logs", "cache", "analytics"]
        for dir_name in required_dirs:
            if not (self.install_dir / dir_name).exists():
                print(f"❌ Missing directory: {dir_name}")
                return False
        
        # Test import
        try:
            result = subprocess.run([
                sys.executable, "-c", "import om.commercial"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ OM Commercial import failed")
                return False
        except Exception:
            print("❌ Could not validate OM Commercial")
            return False
        
        print("✅ Installation validated")
        return True
    
    def _show_next_steps(self) -> None:
        """Show next steps after installation."""
        print("\n🎉 Installation Complete!")
        print("\nNext steps:")
        print("1. Restart your terminal")
        print("2. Run: om --help")
        print("3. Start setup: om setup")
        print("\nDocumentation: https://docs.om-commercial.com")
        print("Support: support@om-commercial.com")


def main():
    """Main installer entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OM Commercial Installer")
    parser.add_argument("--license-key", help="License key for activation")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall OM Commercial")
    
    args = parser.parse_args()
    
    installer = CommercialInstaller()
    
    if args.uninstall:
        success = installer.uninstall()
    else:
        success = installer.install(args.license_key)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
