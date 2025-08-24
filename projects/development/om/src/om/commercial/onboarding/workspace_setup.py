"""Workspace detection and initialization utilities."""

import json
from pathlib import Path


class WorkspaceDetector:
    """Handles workspace detection and initialization."""
    
    def detect_workspace(self) -> None:
        """Detect and configure workspace."""
        print("\n📁 Step 2: Workspace Detection")
        
        current_dir = Path.cwd()
        
        # Check if already in a project
        if self._is_project_directory(current_dir):
            print(f"✅ Project detected: {current_dir.name}")
            self._initialize_workspace(current_dir)
        else:
            print("No project detected in current directory")
            print("You can initialize a workspace later with: om workspace init")
    
    def _is_project_directory(self, path: Path) -> bool:
        """Check if directory contains a project."""
        project_files = [
            "pyproject.toml", "package.json", "Cargo.toml",
            "go.mod", "pom.xml", "requirements.txt", ".git"
        ]
        
        return any((path / file).exists() for file in project_files)
    
    def _initialize_workspace(self, path: Path) -> None:
        """Initialize OM workspace in directory."""
        om_dir = path / ".om"
        om_dir.mkdir(exist_ok=True)
        
        # Create basic workspace config
        config = {
            "workspace_type": "project",
            "created_at": "2025-08-18T12:00:00",
            "om_version": "1.0.0"
        }
        
        with open(om_dir / "workspace.json", 'w') as f:
            json.dump(config, f, indent=2)


class PreferencesSetup:
    """Handles user preferences setup."""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def setup_preferences(self) -> None:
        """Setup user preferences."""
        print("\n⚙️  Step 3: Preferences Setup")
        
        preferences = {
            "output_format": "pretty",
            "auto_scope": False,
            "analytics_enabled": True
        }
        
        # Ask for key preferences
        print("Configure preferences (press Enter for defaults):")
        
        analytics = input("Enable usage analytics? (Y/n): ").strip().lower()
        if analytics in ['n', 'no']:
            preferences["analytics_enabled"] = False
        
        auto_scope = input("Enable auto-scope for git repos? (y/N): ").strip().lower()
        if auto_scope in ['y', 'yes']:
            preferences["auto_scope"] = True
        
        # Save preferences
        with open(self.config_dir / "preferences.json", 'w') as f:
            json.dump(preferences, f, indent=2)
        
        print("✅ Preferences saved")
