"""Documentation generation core."""

import json
from typing import Dict, Any, List
from pathlib import Path
from ..license import SubscriptionManager, PlanTier


class DocumentationGenerator:
    """Generates customer-specific documentation."""
    
    def __init__(self, subscription_manager: SubscriptionManager = None):
        self.subscription_manager = subscription_manager or SubscriptionManager()
        self.templates_dir = Path(__file__).parent / "templates"
        
    def generate_getting_started(self) -> str:
        """Generate getting started guide."""
        subscription = self.subscription_manager.load_subscription()
        tier = PlanTier(subscription["tier"])
        config = self.subscription_manager.get_plan_config(tier)
        
        content = f"""# OM Commercial - Getting Started

## Welcome to OM Commercial {tier.value.title()}!

### Your Plan Features
- **Commands per day:** {self._format_limit(config["limits"].commands_per_day)}
- **Projects:** {self._format_limit(config["limits"].projects)}
- **Team members:** {self._format_limit(config["limits"].team_members)}
- **Storage:** {config["limits"].storage_gb}GB

### Available Commands

#### Basic Commands (All Plans)
```bash
om workspace info          # Show workspace information
om docs generate          # Generate documentation
om code analyze           # Basic code analysis
om find search <query>    # Search codebase
```

#### Pro/Enterprise Features
"""
        
        if config["features"].advanced_analysis:
            content += """
```bash
om code analyze --advanced    # Advanced analysis with insights
om code quality --deep       # Deep quality analysis
```
"""
        
        if config["features"].team_collaboration:
            content += """
```bash
om workspace share <email>   # Share workspace with team
om session collaborate      # Start collaboration session
```
"""
        
        content += """
### Quick Setup
1. Ensure your license is activated
2. Run `om workspace init` in your project
3. Configure preferences with `om preferences set`
4. Start with `om docs generate` for documentation

### Support
"""
        
        if config["features"].priority_support:
            content += "- **Priority Support:** support@om-commercial.com (24h response)\n"
        else:
            content += "- **Standard Support:** support@om-commercial.com (72h response)\n"
            
        content += "- **Documentation:** https://docs.om-commercial.com\n"
        content += "- **Community:** https://community.om-commercial.com\n"
        
        return content
    
    def _format_limit(self, limit: int) -> str:
        """Format usage limit for display."""
        return "Unlimited" if limit == -1 else str(limit)
