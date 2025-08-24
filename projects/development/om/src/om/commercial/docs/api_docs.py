"""API reference and integration documentation."""

from typing import Dict, Any
from ..license import SubscriptionManager, PlanTier


class APIDocumentationGenerator:
    """Generates API reference documentation."""
    
    def __init__(self, subscription_manager):
        self.subscription_manager = subscription_manager
        
    def generate_api_reference(self) -> str:
        """Generate API reference documentation."""
        subscription = self.subscription_manager.load_subscription()
        tier = PlanTier(subscription["tier"])
        config = self.subscription_manager.get_plan_config(tier)
        
        content = """# OM Commercial API Reference

## Core Commands

### Workspace Management
- `om workspace init` - Initialize new workspace
- `om workspace info` - Show workspace details
- `om workspace validate` - Validate workspace structure

### Documentation
- `om docs generate` - Generate project documentation
- `om docs serve` - Serve documentation locally
- `om docs export` - Export documentation

### Code Analysis
- `om code analyze` - Analyze code quality
- `om code format` - Format code
- `om code lint` - Lint codebase
"""
        
        if config["features"].advanced_analysis:
            content += """
### Advanced Analysis (Pro/Enterprise)
- `om code analyze --advanced` - Deep code analysis
- `om code metrics` - Code complexity metrics
- `om code dependencies` - Dependency analysis
- `om code security` - Security vulnerability scan
"""
        
        if config["features"].team_collaboration:
            content += """
### Team Collaboration (Pro/Enterprise)
- `om workspace share <email>` - Share workspace
- `om session start` - Start collaboration session
- `om session join <id>` - Join collaboration session
- `om team list` - List team members
"""
        
        if config["features"].api_access:
            content += """
### API Access (Pro/Enterprise)
- `om api generate-key` - Generate API key
- `om api test` - Test API connection
- `om api usage` - Show API usage stats

#### REST API Endpoints
- `GET /api/v1/workspaces` - List workspaces
- `POST /api/v1/analyze` - Submit analysis job
- `GET /api/v1/results/{id}` - Get analysis results
"""
        
        content += """
### Usage & Billing
- `om usage stats` - Show usage statistics
- `om billing info` - Show billing information
- `om plan upgrade` - Upgrade subscription plan

### Global Options
- `--scope <path>` - Limit scope to specific directory
- `--auto-scope` - Auto-detect scope from git changes
- `--verbose` - Enable verbose output
- `--help` - Show command help
"""
        
        return content
    
    def generate_integration_guide(self) -> str:
        """Generate integration guide."""
        subscription = self.subscription_manager.load_subscription()
        tier = PlanTier(subscription["tier"])
        config = self.subscription_manager.get_plan_config(tier)
        
        content = """# OM Commercial Integration Guide

## CI/CD Integration

### GitHub Actions
```yaml
name: OM Analysis
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup OM Commercial
        run: |
          pip install om-commercial
          echo "${{ secrets.OM_LICENSE_KEY }}" > ~/.om/license.key
      - name: Run Analysis
        run: om code analyze --output github-actions
```

### VS Code Extension
1. Install "OM Commercial" extension
2. Configure license key in settings
3. Access commands via Command Palette (Ctrl+Shift+P)

## IDE Integration

### PyCharm Plugin
1. Install OM Commercial plugin from marketplace
2. Configure API key in plugin settings
3. Use OM tools from Tools menu
"""
        
        if config["features"].api_access:
            content += """
## API Integration

### Python SDK
```python
from om_commercial import OMClient

client = OMClient(api_key="your-api-key")
result = client.analyze_workspace("/path/to/project")
print(result.quality_score)
```

### REST API
```bash
curl -H "Authorization: Bearer YOUR-API-KEY" \\
     -X POST https://api.om-commercial.com/v1/analyze \\
     -d '{"workspace_path": "/path/to/project"}'
```
"""
        
        if config["features"].custom_integrations:
            content += """
## Custom Integrations (Enterprise)

### Webhook Configuration
```json
{
  "webhook_url": "https://your-domain.com/webhook",
  "events": ["analysis_complete", "error_occurred"],
  "secret": "your-webhook-secret"
}
```

### Custom Plugins
```python
from om_commercial.plugins import BasePlugin

class CustomAnalyzer(BasePlugin):
    def analyze(self, code):
        # Your custom analysis logic
        return results
```
"""
        
        content += """
## Best Practices

1. **Regular Analysis**: Run analysis on every commit
2. **Scope Management**: Use `--scope` for large repositories
3. **Team Workflows**: Share configurations with `.om/config.json`
4. **Performance**: Enable caching for faster repeated analysis

## Troubleshooting

### Common Issues
- **License errors**: Verify license key is valid
- **Permission errors**: Check file system permissions
- **Performance**: Use scoping for large codebases

### Getting Help
- Check logs in `~/.om/logs/`
- Run with `--verbose` for detailed output
- Contact support with error details
"""
        
        return content
