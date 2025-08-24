"""Customer onboarding system."""

from .onboarding.license_setup import LicenseSetup
from .onboarding.support import SupportTicket
from .onboarding.system import OnboardingSystem
from .onboarding.wizard import SetupWizard
from .onboarding.workspace_setup import WorkspaceSetup

__all__ = [
    "OnboardingSystem",
    "SetupWizard",
    "LicenseSetup",
    "WorkspaceSetup",
    "SupportTicket",
]
