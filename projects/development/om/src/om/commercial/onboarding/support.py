"""Support ticket system."""

import json
import datetime
from typing import Dict, Any
from pathlib import Path


class SupportTicketSystem:
    """Handles customer support tickets."""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path.home() / ".om"
        
    def create_support_ticket(self, issue_description: str) -> str:
        """Create support ticket."""
        ticket_id = f"OM-{hash(issue_description) % 100000:05d}"
        
        ticket_data = {
            "ticket_id": ticket_id,
            "description": issue_description,
            "created_at": datetime.datetime.now().isoformat(),
            "status": "open",
            "priority": "normal"
        }
        
        # Save ticket locally
        tickets_dir = self.config_dir / "support"
        tickets_dir.mkdir(exist_ok=True)
        
        with open(tickets_dir / f"{ticket_id}.json", 'w') as f:
            json.dump(ticket_data, f, indent=2)
        
        print(f"Support ticket created: {ticket_id}")
        print("Our team will contact you within 72 hours.")
        
        return ticket_id
    
    def list_tickets(self) -> list:
        """List all support tickets."""
        tickets_dir = self.config_dir / "support"
        
        if not tickets_dir.exists():
            return []
        
        tickets = []
        for ticket_file in tickets_dir.glob("OM-*.json"):
            with open(ticket_file, 'r') as f:
                tickets.append(json.load(f))
        
        return tickets
    
    def get_ticket_status(self, ticket_id: str) -> Dict[str, Any]:
        """Get status of specific ticket."""
        ticket_file = self.config_dir / "support" / f"{ticket_id}.json"
        
        if not ticket_file.exists():
            return {"error": "Ticket not found"}
        
        with open(ticket_file, 'r') as f:
            return json.load(f)
