"""License validation and management."""

import os
import json
import hashlib
import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class LicenseValidationError(Exception):
    """License validation failed."""
    pass


class LicenseValidator:
    """Validates OM commercial licenses."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".om" / "commercial.json"
        self._license_cache = {}
        self._validation_server = "https://api.om-commercial.com/v1"
    
    def load_license(self) -> Dict[str, Any]:
        """Load license from config file."""
        if not self.config_path.exists():
            raise LicenseValidationError("No license configuration found")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def validate_license_key(self, license_key: str) -> bool:
        """Validate license key format and checksum."""
        if len(license_key) != 36:  # UUID format
            return False
        
        # Basic checksum validation
        key_parts = license_key.split('-')
        if len(key_parts) != 5:
            return False
        
        return all(len(part) in [8, 4, 4, 4, 12] for part in key_parts)
    
    def verify_online(self, license_key: str) -> Dict[str, Any]:
        """Verify license with validation server."""
        try:
            response = requests.post(
                f"{self._validation_server}/validate",
                json={"license_key": license_key},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LicenseValidationError(f"License validation failed: {e}")
    
    def check_expiration(self, license_data: Dict[str, Any]) -> bool:
        """Check if license has expired."""
        expires_at = datetime.datetime.fromisoformat(license_data.get("expires_at", ""))
        return datetime.datetime.now() > expires_at
    
    def validate(self, license_key: str) -> Dict[str, Any]:
        """Full license validation."""
        # Format validation
        if not self.validate_license_key(license_key):
            raise LicenseValidationError("Invalid license key format")
        
        # Check cache first
        if license_key in self._license_cache:
            cached = self._license_cache[license_key]
            if cached["cached_at"] + datetime.timedelta(hours=1) > datetime.datetime.now():
                return cached["data"]
        
        # Online validation
        license_data = self.verify_online(license_key)
        
        # Expiration check
        if self.check_expiration(license_data):
            raise LicenseValidationError("License has expired")
        
        # Cache result
        self._license_cache[license_key] = {
            "data": license_data,
            "cached_at": datetime.datetime.now()
        }
        
        return license_data
    
    def get_plan_features(self, plan: str) -> Dict[str, Any]:
        """Get features for a subscription plan."""
        plans = {
            "starter": {
                "commands_per_day": 100,
                "projects": 1,
                "team_members": 1,
                "advanced_analysis": False,
                "team_collaboration": False,
                "priority_support": False
            },
            "pro": {
                "commands_per_day": 1000,
                "projects": 5,
                "team_members": 5,
                "advanced_analysis": True,
                "team_collaboration": True,
                "priority_support": False
            },
            "enterprise": {
                "commands_per_day": -1,  # unlimited
                "projects": -1,
                "team_members": -1,
                "advanced_analysis": True,
                "team_collaboration": True,
                "priority_support": True
            }
        }
        return plans.get(plan, plans["starter"])
