"""Customer onboarding system."""

from .onboarding.system import OnboardingSystem
from .onboarding.wizard import SetupWizard
from .onboarding.license_setup import LicenseSetup
from .onboarding.workspace_setup import WorkspaceSetup
from .onboarding.support import SupportTicket

__all__ = ["OnboardingSystem", "SetupWizard", "LicenseSetup", "WorkspaceSetup", "SupportTicket"]