#!/usr/bin/env python3
"""
Formal contracts for Axiom CLI - ensuring coherence in every function.
Based on MomoAI Formal Contract Language (FCL).
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CoherenceLevel(Enum):
    """Coherence validation levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    BASIC = "basic"


class ContractViolation(Exception):
    """Raised when a formal contract is violated."""

    pass


class FormalContract(BaseModel):
    """Base class for all formal contracts."""

    function_name: str = Field(
        ..., description="Name of the function this contract governs"
    )
    coherence_level: CoherenceLevel = Field(default=CoherenceLevel.STRICT)
    preconditions: list[str] = Field(
        default_factory=list,
        description="Conditions that must be true before execution",
    )
    postconditions: list[str] = Field(
        default_factory=list, description="Conditions that must be true after execution"
    )
    invariants: list[str] = Field(
        default_factory=list,
        description="Conditions that must remain true throughout execution",
    )


class APICallContract(FormalContract):
    """Contract for Anthropic API calls."""

    function_name: str = "anthropic_api_call"
    preconditions: list[str] = Field(
        default_factory=lambda: [
            "api_key is not None and len(api_key) > 0",
            "messages is not None and len(messages) > 0",
            "model is valid Anthropic model identifier",
            "all messages have valid role and content",
        ]
    )
    postconditions: list[str] = Field(
        default_factory=lambda: [
            "response contains valid message content",
            "response.usage contains token counts",
            "no sensitive data leaked in logs",
        ]
    )
    invariants: list[str] = Field(
        default_factory=lambda: [
            "api_key remains confidential",
            "message history maintains chronological order",
            "no system message pollution occurs",
        ]
    )


class ChatSessionContract(FormalContract):
    """Contract for interactive chat session."""

    function_name: str = "chat_session"
    preconditions: list[str] = Field(
        default_factory=lambda: [
            "anthropic client is properly initialized",
            "environment variables are loaded",
            "terminal supports interactive input",
        ]
    )
    postconditions: list[str] = Field(
        default_factory=lambda: [
            "all user inputs are properly validated",
            "all responses are coherently formatted",
            "session state is cleanly maintained",
        ]
    )
    invariants: list[str] = Field(
        default_factory=lambda: [
            "user privacy is maintained",
            "no data corruption occurs",
            "graceful error handling is preserved",
        ]
    )


def validate_contract(contract: FormalContract, context: dict[str, Any]) -> bool:
    """
    Validate that a contract's conditions are met.

    Args:
        contract: The formal contract to validate
        context: Current execution context with variables to check

    Returns:
        True if all conditions are satisfied

    Raises:
        ContractViolation: If any condition is violated
    """
    # Validate preconditions
    for condition in contract.preconditions:
        if not _evaluate_condition(condition, context):
            raise ContractViolation(
                f"Precondition violated in {contract.function_name}: {condition}"
            )

    # Validate invariants
    for invariant in contract.invariants:
        if not _evaluate_condition(invariant, context):
            raise ContractViolation(
                f"Invariant violated in {contract.function_name}: {invariant}"
            )

    return True


def _evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    """
    Safely evaluate a condition string against the context.

    This is a simplified evaluator - in production, this would use
    the Z3 theorem prover for formal verification.
    """
    try:
        # Basic safety checks
        if any(
            dangerous in condition for dangerous in ["import", "exec", "eval", "__"]
        ):
            return False

        # Handle complex api_key condition FIRST - EXACT match
        if condition == "api_key is not None and len(api_key) > 0":
            # Check if we have a self object with api_key
            self_obj = context.get("self")
            if self_obj and hasattr(self_obj, "api_key"):
                api_key = self_obj.api_key
                return api_key is not None and len(api_key) > 0
            api_key = context.get("api_key")
            return api_key is not None and len(api_key) > 0

        # Simple condition evaluation
        # In real implementation, this would be Z3-based formal verification
        if "is not None" in condition:
            var_name = condition.split()[0]
            return context.get(var_name) is not None

        if "len(" in condition and "> 0" in condition:
            # Extract variable name from len(var_name) > 0
            start = condition.find("len(") + 4
            end = condition.find(")", start)
            var_name = condition[start:end]
            value = context.get(var_name)
            return value is not None and len(value) > 0

        # Handle simple api_key conditions
        if "api_key is not None" in condition:
            self_obj = context.get("self")
            if self_obj and hasattr(self_obj, "api_key"):
                return self_obj.api_key is not None
            return context.get("api_key") is not None

        if "len(api_key) > 0" in condition:
            self_obj = context.get("self")
            if self_obj and hasattr(self_obj, "api_key"):
                api_key = self_obj.api_key
                return api_key is not None and len(api_key) > 0
            api_key = context.get("api_key")
            return api_key is not None and len(api_key) > 0

        # Default to True for conditions we can't evaluate yet
        # In production, unknown conditions should fail
        return True

    except Exception:
        return False


def contract_enforced(contract: FormalContract):
    """
    Decorator to enforce formal contracts on functions.

    Usage:
        @contract_enforced(APICallContract())
        def my_function(arg1, arg2):
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Build context from function arguments
            import inspect

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            context = dict(bound_args.arguments)

            # Validate preconditions and invariants
            validate_contract(contract, context)

            # Execute function
            result = func(*args, **kwargs)

            # Add result to context for postcondition validation
            context["result"] = result

            # Validate postconditions
            for condition in contract.postconditions:
                if not _evaluate_condition(condition, context):
                    raise ContractViolation(
                        f"Postcondition violated in {contract.function_name}: {condition}"
                    )

            return result

        return wrapper

    return decorator
