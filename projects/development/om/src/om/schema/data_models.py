"""
Data models for schema generation
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class TypeSchema:
    """Represents a type schema."""
    name: str
    type_kind: str  # 'primitive', 'class', 'union', 'generic', 'callable'
    base_type: str
    properties: Dict[str, Any]
    required: List[str]
    description: str
    examples: List[str]
