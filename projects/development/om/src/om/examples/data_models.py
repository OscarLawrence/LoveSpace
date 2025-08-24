"""
Data models for integration examples
"""

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
    prerequisites: list[str]
    related_commands: list[str]
    expected_output: str
    tags: list[str]
