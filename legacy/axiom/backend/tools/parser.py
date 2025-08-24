"""
Tool call parser for natural function calls
Extracts function calls from AI responses without complex JSON
"""

import re
from dataclasses import dataclass
from typing import Any

from core.contracts import contract_enforced


@dataclass
class ToolCall:
    """Represents a parsed tool call"""

    function_name: str
    args: list[Any]
    raw_call: str


class ToolCallParser:
    """Parses natural function calls from AI responses"""

    def __init__(self):
        # Pattern to match function calls like: function_name("arg1", "arg2", 123)
        self.function_pattern = re.compile(r"(\w+)\s*\(\s*([^)]*)\s*\)", re.MULTILINE)

        # Known tool functions
        self.known_tools = {
            "read_file",
            "write_file",
            "edit_file",
            "list_files",
            "bash_exec",
            "create_directory",
            "delete_file",
        }

    @contract_enforced(
        preconditions=["text is not empty"],
        postconditions=["returns list of valid tool calls"],
        description="Parse tool calls from AI response text",
    )
    def parse_tool_calls(self, text: str) -> list[ToolCall]:
        """
        Parse tool calls from AI response text

        Args:
            text: AI response text containing function calls

        Returns:
            List of parsed tool calls
        """
        tool_calls = []

        # Find all function call matches
        matches = self.function_pattern.findall(text)

        for function_name, args_str in matches:
            # Only process known tool functions
            if function_name not in self.known_tools:
                continue

            # Parse arguments
            args = self._parse_arguments(args_str)

            # Create tool call
            raw_call = f"{function_name}({args_str})"
            tool_call = ToolCall(
                function_name=function_name, args=args, raw_call=raw_call
            )

            tool_calls.append(tool_call)

        return tool_calls

    @contract_enforced(description="Parse function arguments from string")
    def _parse_arguments(self, args_str: str) -> list[Any]:
        """
        Parse function arguments from string

        Args:
            args_str: String containing function arguments

        Returns:
            List of parsed arguments
        """
        if not args_str.strip():
            return []

        args = []

        # Simple argument parsing - handles strings and basic types
        # For production, consider using ast.literal_eval for safety

        # Split by commas, but respect quoted strings
        current_arg = ""
        in_quotes = False
        quote_char = None

        for char in args_str:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_arg += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_arg += char
            elif char == "," and not in_quotes:
                args.append(self._parse_single_argument(current_arg.strip()))
                current_arg = ""
            else:
                current_arg += char

        # Add the last argument
        if current_arg.strip():
            args.append(self._parse_single_argument(current_arg.strip()))

        return args

    @contract_enforced(description="Parse single argument to appropriate type")
    def _parse_single_argument(self, arg_str: str) -> Any:
        """
        Parse single argument to appropriate type

        Args:
            arg_str: String representation of argument

        Returns:
            Parsed argument value
        """
        arg_str = arg_str.strip()

        # Handle quoted strings
        if (arg_str.startswith('"') and arg_str.endswith('"')) or (
            arg_str.startswith("'") and arg_str.endswith("'")
        ):
            return arg_str[1:-1]  # Remove quotes

        # Handle numbers
        try:
            if "." in arg_str:
                return float(arg_str)
            else:
                return int(arg_str)
        except ValueError:
            pass

        # Handle booleans
        if arg_str.lower() == "true":
            return True
        elif arg_str.lower() == "false":
            return False

        # Handle None
        if arg_str.lower() == "none":
            return None

        # Default to string
        return arg_str
