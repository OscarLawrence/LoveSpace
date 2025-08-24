"""
Data models for integration examples
"""

from typing import List
from dataclasses import dataclass


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
