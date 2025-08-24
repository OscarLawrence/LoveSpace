"""
Data models for schema generation
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class TypeSchema:
    """Represents a type schema."""

    name: str
    type_kind: str  # 'primitive', 'class', 'union', 'generic', 'callable'
    base_type: str
    properties: dict[str, Any]
    required: list[str]
    description: str
    examples: list[str]
