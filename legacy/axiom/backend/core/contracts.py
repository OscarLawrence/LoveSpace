"""
MomoAI Formal Contract Language (FCL) - Adapted for Axiom
Mathematical specification language for coherent code development

Design Principles:
1. Mathematical precision - every contract is formally verifiable
2. Human readable - developers can understand and write contracts
3. Z3 translatable - contracts compile to SMT-LIB for verification
4. Axiom compatible - AI can generate and verify contracts
5. Incremental adoption - can be added to existing code
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class ComplexityClass(Enum):
    """Time/space complexity classifications"""

    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n²)"
    CUBIC = "O(n³)"
    EXPONENTIAL = "O(2^n)"
    FACTORIAL = "O(n!)"


class ContractType(Enum):
    """Types of formal contracts"""

    PRECONDITION = "requires"
    POSTCONDITION = "ensures"
    INVARIANT = "maintains"
    COMPLEXITY = "complexity"
    PURITY = "pure"
    SIDE_EFFECTS = "modifies"


@dataclass
class FormalPredicate:
    """A formal logical predicate that can be verified by Z3"""

    expression: str
    variables: list[str]
    type_constraints: dict[str, str]
    description: str

    def to_z3_smt(self) -> str:
        """Convert predicate to Z3 SMT-LIB format"""
        # This will be implemented to generate Z3 code
        return f"(assert {self.expression})"


@dataclass
class FormalContract:
    """Complete formal specification for a function"""

    function_name: str
    input_types: dict[str, str]
    output_type: str
    preconditions: list[FormalPredicate]
    postconditions: list[FormalPredicate]
    invariants: list[FormalPredicate]
    complexity_time: ComplexityClass
    complexity_space: ComplexityClass
    is_pure: bool
    side_effects: list[str]

    def verify_with_z3(self, implementation: str) -> bool:
        """Verify implementation satisfies contract using Z3"""
        # This will integrate with our Z3 verifier
        pass


class ContractViolation(Exception):
    """Raised when a formal contract is violated at runtime"""

    pass


def coherence_contract(
    input_types: dict[str, str] = None,
    output_type: str = None,
    requires: list[str] = None,
    ensures: list[str] = None,
    maintains: list[str] = None,
    complexity_time: str | ComplexityClass = None,
    complexity_space: str | ComplexityClass = None,
    pure: bool = False,
    modifies: list[str] = None,
    description: str = None,
):
    """
    Decorator for adding formal contracts to functions

    Example:
    @coherence_contract(
        input_types={"items": "List[int]", "reverse": "bool"},
        output_type="List[int]",
        requires=["len(items) >= 0"],
        ensures=["len(result) == len(items)", "is_sorted(result) or reverse"],
        complexity_time="O(n log n)",
        pure=True
    )
    def sort_list(items: List[int], reverse: bool = False) -> List[int]:
        return sorted(items, reverse=reverse)
    """

    def decorator(func):
        # Extract function signature
        sig = inspect.signature(func)
        func_name = func.__name__

        # Build formal contract
        contract = FormalContract(
            function_name=func_name,
            input_types=input_types or {},
            output_type=output_type or "Any",
            preconditions=[
                FormalPredicate(req, [], {}, req) for req in (requires or [])
            ],
            postconditions=[
                FormalPredicate(ens, [], {}, ens) for ens in (ensures or [])
            ],
            invariants=[FormalPredicate(inv, [], {}, inv) for inv in (maintains or [])],
            complexity_time=ComplexityClass(complexity_time)
            if isinstance(complexity_time, str)
            else complexity_time,
            complexity_space=ComplexityClass(complexity_space)
            if isinstance(complexity_space, str)
            else complexity_space,
            is_pure=pure,
            side_effects=modifies or [],
        )

        # Attach contract to function
        func._formal_contract = contract

        # Also store description if provided
        if description:
            func.__doc__ = description

        # Add runtime verification wrapper with preserved signature
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Pre-condition checking
                if not verify_preconditions(contract, args, kwargs):
                    raise ContractViolation(f"Precondition violated in {func_name}")

                # Execute async function
                result = await func(*args, **kwargs)

                # Post-condition checking
                if not verify_postconditions(contract, args, kwargs, result):
                    raise ContractViolation(f"Postcondition violated in {func_name}")

                return result

            wrapper = async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Pre-condition checking
                if not verify_preconditions(contract, args, kwargs):
                    raise ContractViolation(f"Precondition violated in {func_name}")

                # Execute function
                result = func(*args, **kwargs)

                # Post-condition checking
                if not verify_postconditions(contract, args, kwargs, result):
                    raise ContractViolation(f"Postcondition violated in {func_name}")

                return result

            wrapper = sync_wrapper

        # Preserve contract metadata
        wrapper._formal_contract = contract
        wrapper.__signature__ = sig  # Preserve signature for FastAPI

        return wrapper

    return decorator


# Contract verification functions (placeholders)
def verify_preconditions(contract: FormalContract, args, kwargs) -> bool:
    """Verify function preconditions - placeholder implementation"""
    return True


def verify_postconditions(contract: FormalContract, args, kwargs, result) -> bool:
    """Verify function postconditions - placeholder implementation"""
    return True


def get_contract_info(func) -> FormalContract | None:
    """Get contract information from a function"""
    return getattr(func, "_formal_contract", None)


# Legacy contract_enforced decorator for backward compatibility
def contract_enforced(
    preconditions: list[str] | None = None,
    postconditions: list[str] | None = None,
    description: str | None = None,
) -> Callable[[F], F]:
    """
    Legacy decorator for enforcing formal contracts on functions
    Use coherence_contract for new code
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Store contract metadata
            wrapper._contract = {
                "preconditions": preconditions or [],
                "postconditions": postconditions or [],
                "description": description or func.__doc__ or "",
                "signature": str(inspect.signature(func)),
            }

            # Execute function (contract validation can be added here)
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


# Built-in predicates for common operations
class BuiltinPredicates:
    """Standard predicates for common programming concepts"""

    @staticmethod
    def is_sorted(lst: list) -> str:
        """Predicate: list is sorted in ascending order"""
        return "all(lst[i] <= lst[i+1] for i in range(len(lst)-1))"

    @staticmethod
    def same_elements(lst1: list, lst2: list) -> str:
        """Predicate: two lists contain the same elements"""
        return "sorted(lst1) == sorted(lst2)"

    @staticmethod
    def is_unique(lst: list) -> str:
        """Predicate: all elements in list are unique"""
        return "len(lst) == len(set(lst))"

    @staticmethod
    def is_positive(x: int | float) -> str:
        """Predicate: number is positive"""
        return "x > 0"

    @staticmethod
    def is_non_empty(container) -> str:
        """Predicate: container is not empty"""
        return "len(container) > 0"


def get_contract_info(func: Callable) -> dict[str, Any]:
    """Extract contract information from a decorated function"""
    if hasattr(func, "_formal_contract"):
        contract = func._formal_contract
        return {
            "function_name": contract.function_name,
            "input_types": contract.input_types,
            "output_type": contract.output_type,
            "preconditions": [p.expression for p in contract.preconditions],
            "postconditions": [p.expression for p in contract.postconditions],
            "complexity_time": contract.complexity_time.value
            if contract.complexity_time
            else None,
            "complexity_space": contract.complexity_space.value
            if contract.complexity_space
            else None,
            "is_pure": contract.is_pure,
            "side_effects": contract.side_effects,
        }
    elif hasattr(func, "_contract"):
        return func._contract
    return {
        "preconditions": [],
        "postconditions": [],
        "description": func.__doc__ or "",
        "signature": str(inspect.signature(func)),
    }


@coherence_contract(
    input_types={"x": "int"},
    output_type="int",
    requires=["x >= 0"],
    ensures=["result == x * 2"],
    complexity_time=ComplexityClass.CONSTANT,
    pure=True,
    description="Example contract-enforced function for demonstration",
)
def example_function(x: int) -> int:
    """Example function with formal contract"""
    return x * 2
