"""
Data models for schema generation
"""

from dataclasses import dataclass
from typing import Any, Dict, List


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
