"""
Axiom - Minimal CLI for direct Claude Sonnet 4 interaction with formal contracts.

A clean foundation for building coherent AI tools without system message pollution.
"""

from .anthropic_client import AnthropicClient, AnthropicMessage, create_anthropic_client
from .contracts import (
    APICallContract,
    ChatSessionContract,
    CoherenceLevel,
    ContractViolation,
    FormalContract,
    contract_enforced,
    validate_contract,
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "AnthropicClient",
    "AnthropicMessage",
    # Contract system
    "FormalContract",
    "APICallContract",
    "ChatSessionContract",
    "CoherenceLevel",
    "ContractViolation",
    # Functions
    "create_anthropic_client",
    "contract_enforced",
    "validate_contract",
]
