"""
Data models for integration examples
"""

from dataclasses import dataclass
from typing import List


@dataclass
class IntegrationExample:
    """Represents an integration example."""
    title: str
    description: str
    category: str
    difficulty: str  # 'basic', 'intermediate', 'advanced'
    code: str
    explanation: str
    prerequisites: List[str]
    related_commands: List[str]
    expected_output: str
    tags: List[str]
