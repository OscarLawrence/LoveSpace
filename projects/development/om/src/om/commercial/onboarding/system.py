"""Onboarding system main interface."""

from .wizard import SetupWizard
from .support import SupportTicketSystem
from ..license import SubscriptionManager


class OnboardingSystem:
    """Handles customer onboarding and setup."""
    
    def __init__(self, subscription_manager=None):
        self.subscription_manager = subscription_manager or SubscriptionManager()
        self.wizard = SetupWizard(self.subscription_manager)
        self.support = SupportTicketSystem()
        
    def run_setup_wizard(self) -> bool:
        """Run interactive setup wizard."""
        return self.wizard.run_setup_wizard()
    
    def create_support_ticket(self, issue_description: str) -> str:
        """Create support ticket."""
        return self.support.create_support_ticket(issue_description)
    
    def list_support_tickets(self) -> list:
        """List all support tickets."""
        return self.support.list_tickets()
    
    def get_ticket_status(self, ticket_id: str) -> dict:
        """Get status of specific ticket."""
        return self.support.get_ticket_status(ticket_id)
