#!/usr/bin/env python3
"""
Tests for formal contract system.
"""

import pytest
from axiom.contracts import (
    APICallContract,
    ChatSessionContract,
    ContractViolation,
    _evaluate_condition,
    contract_enforced,
    validate_contract,
)


class TestContractValidation:
    """Test formal contract validation."""

    def test_api_call_contract_creation(self) -> None:
        """Test that API call contract can be created with proper defaults."""
        contract = APICallContract()

        assert contract.function_name == "anthropic_api_call"
        assert len(contract.preconditions) > 0
        assert len(contract.postconditions) > 0
        assert len(contract.invariants) > 0

    def test_chat_session_contract_creation(self) -> None:
        """Test that chat session contract can be created with proper defaults."""
        contract = ChatSessionContract()

        assert contract.function_name == "chat_session"
        assert len(contract.preconditions) > 0
        assert len(contract.postconditions) > 0
        assert len(contract.invariants) > 0

    def test_condition_evaluation_not_none(self) -> None:
        """Test evaluation of 'is not None' conditions."""
        context = {"api_key": "test_key"}

        assert _evaluate_condition("api_key is not None", context) is True

        context = {"api_key": None}
        assert _evaluate_condition("api_key is not None", context) is False

    def test_condition_evaluation_length(self) -> None:
        """Test evaluation of length conditions."""
        context = {"messages": ["msg1", "msg2"]}

        assert _evaluate_condition("len(messages) > 0", context) is True

        context = {"messages": []}
        assert _evaluate_condition("len(messages) > 0", context) is False

    def test_contract_validation_success(self) -> None:
        """Test successful contract validation."""
        contract = APICallContract()
        context = {
            "api_key": "test_key",
            "messages": ["test_message"],
            "model": "claude-sonnet-4-20250514",
        }

        # Should not raise exception
        assert validate_contract(contract, context) is True

    def test_contract_validation_failure(self) -> None:
        """Test contract validation failure."""
        contract = APICallContract()
        context = {
            "api_key": None,  # This should cause failure
            "messages": ["test_message"],
            "model": "claude-sonnet-4-20250514",
        }

        with pytest.raises(ContractViolation):
            validate_contract(contract, context)

    def test_contract_enforced_decorator(self) -> None:
        """Test the contract enforcement decorator."""

        @contract_enforced(APICallContract())
        def test_function(api_key: str, messages: list, model: str) -> str:
            return "success"

        # Should succeed with valid inputs
        result = test_function(
            api_key="test_key", messages=["test"], model="claude-sonnet-4-20250514"
        )
        assert result == "success"

        # Should fail with invalid inputs (empty api_key)
        with pytest.raises(ContractViolation):
            test_function(
                api_key="",  # Empty string should fail len(api_key) > 0
                messages=["test"],
                model="claude-sonnet-4-20250514",
            )

        # Should fail with None api_key
        with pytest.raises(ContractViolation):
            test_function(
                api_key=None,  # None should fail api_key is not None
                messages=["test"],
                model="claude-sonnet-4-20250514",
            )


class TestContractSafety:
    """Test contract system safety features."""

    def test_dangerous_condition_rejection(self) -> None:
        """Test that dangerous conditions are rejected."""
        dangerous_conditions = [
            "import os",
            "exec('malicious code')",
            "eval('dangerous')",
            "__import__('os')",
        ]

        context = {}
        for condition in dangerous_conditions:
            assert _evaluate_condition(condition, context) is False

    def test_unknown_condition_handling(self) -> None:
        """Test handling of unknown/complex conditions."""
        # For now, unknown conditions return True
        # In production, they should fail for safety
        context = {"x": 5}

        # Complex condition that our simple evaluator can't handle
        result = _evaluate_condition("x > 3 and x < 10", context)
        assert result is True  # Current behavior

        # In production, this should be:
        # assert result is False  # Fail-safe behavior
