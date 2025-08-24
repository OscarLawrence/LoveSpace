#!/usr/bin/env python3
"""
Direct Anthropic API client with formal contract enforcement.
No SDK pollution - pure HTTP requests with coherence validation.
"""

import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console

from .contracts import APICallContract, ContractViolation, contract_enforced

# Load environment variables
load_dotenv()

console = Console()


class AnthropicMessage(BaseModel):
    """Anthropic API message format."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class AnthropicResponse(BaseModel):
    """Anthropic API response format."""

    content: list[dict[str, Any]] = Field(..., description="Response content blocks")
    usage: dict[str, Any] = Field(
        ..., description="Token usage statistics"
    )  # Changed to Any to handle new fields
    model: str = Field(..., description="Model used for generation")
    stop_reason: str | None = Field(None, description="Reason for stopping")

    class Config:
        extra = "allow"  # Allow extra fields we don't know about


class AnthropicClient:
    """
    Direct Anthropic API client with formal contract enforcement.

    This client makes pure HTTP requests without any SDK pollution,
    ensuring complete transparency and coherence validation.
    """

    def __init__(self) -> None:
        """Initialize the Anthropic client with API key from environment."""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ContractViolation("ANTHROPIC_API_KEY environment variable not found")

        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4
        self.max_tokens = 4096

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01",
            },
        )

    @contract_enforced(APICallContract())
    async def send_message(
        self,
        messages: list[AnthropicMessage],
        max_tokens: int | None = None,
        system_message: str | None = None,
    ) -> AnthropicResponse:
        """
        Send messages to Claude Sonnet 4 with formal contract enforcement.

        Args:
            messages: List of messages in the conversation
            max_tokens: Maximum tokens to generate (optional)
            system_message: System message to set context (optional)

        Returns:
            AnthropicResponse with the model's reply

        Raises:
            ContractViolation: If any formal contract is violated
            httpx.HTTPError: If API request fails
        """
        # Validate inputs according to contract
        if not messages:
            raise ContractViolation("Messages list cannot be empty")

        for msg in messages:
            if msg.role not in ["user", "assistant"]:
                raise ContractViolation(f"Invalid message role: {msg.role}")
            if not msg.content.strip():
                raise ContractViolation("Message content cannot be empty")

        # Prepare API request
        request_data = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in messages
            ],
        }

        # Add system message if provided
        if system_message:
            request_data["system"] = system_message

        try:
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/messages", json=request_data
            )
            response.raise_for_status()

            # Parse response
            response_data = response.json()

            # Validate response format
            if "content" not in response_data:
                raise ContractViolation("API response missing content field")
            if "usage" not in response_data:
                raise ContractViolation("API response missing usage field")

            return AnthropicResponse(**response_data)

        except httpx.HTTPError as e:
            console.print(f"[red]API request failed: {e}[/red]")
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]Failed to parse API response: {e}[/red]")
            raise ContractViolation("Invalid JSON response from API")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    def __del__(self) -> None:
        """Cleanup on deletion."""
        # Don't try to close async client in __del__ - causes warnings
        pass


async def create_anthropic_client() -> AnthropicClient:
    """
    Factory function to create an Anthropic client with contract validation.

    Returns:
        Initialized AnthropicClient instance

    Raises:
        ContractViolation: If client cannot be properly initialized
    """
    try:
        client = AnthropicClient()
        console.print(
            "[green]✓[/green] Anthropic client initialized with formal contracts"
        )
        return client
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize Anthropic client: {e}")
        raise ContractViolation(f"Client initialization failed: {e}")


def load_system_message() -> str:
    """
    Load the system message from file.

    Returns:
        System message content

    Raises:
        ContractViolation: If system message file cannot be read
    """
    try:
        system_message_path = Path(__file__).parent / "system_message.txt"
        with open(system_message_path, encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            raise ContractViolation("System message file is empty")

        return content

    except FileNotFoundError:
        raise ContractViolation(f"System message file not found: {system_message_path}")
    except Exception as e:
        raise ContractViolation(f"Failed to load system message: {e}")
