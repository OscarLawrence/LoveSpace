"""OM Commercial SaaS Implementation."""

__version__ = "1.0.0"

# Import main components
from . import license
from .cli_wrapper import CommercialCLIWrapper, cli_wrapper
from .analytics import AnalyticsCollector, UsageMetric, PerformanceMetric
from .docs import DocumentationGenerator
from .onboarding import OnboardingSystem

__all__ = [
    "license",
    "CommercialCLIWrapper", 
    "cli_wrapper",
    "AnalyticsCollector",
    "UsageMetric",
    "PerformanceMetric", 
    "DocumentationGenerator",
    "OnboardingSystem"
]
