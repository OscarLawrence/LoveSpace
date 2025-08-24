#!/usr/bin/env python3
"""
Tests for Anthropic API client.
"""

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from axiom.anthropic_client import (
    AnthropicClient,
    AnthropicMessage,
    create_anthropic_client,
)
from axiom.contracts import ContractViolation


class TestAnthropicMessage:
    """Test AnthropicMessage model."""

    def test_valid_message_creation(self) -> None:
        """Test creating valid messages."""
        msg = AnthropicMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

        msg = AnthropicMessage(role="assistant", content="Hi there!")
        assert msg.role == "assistant"
        assert msg.content == "Hi there!"

    def test_message_validation(self) -> None:
        """Test message validation."""
        # Valid roles should work
        AnthropicMessage(role="user", content="test")
        AnthropicMessage(role="assistant", content="test")

        # Content is required
        with pytest.raises(ValueError):
            AnthropicMessage(role="user")


class TestAnthropicClient:
    """Test AnthropicClient functionality."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    def test_client_initialization_success(self) -> None:
        """Test successful client initialization."""
        client = AnthropicClient()
        assert client.api_key == "test_key"
        assert client.model == "claude-sonnet-4-20250514"
        assert client.max_tokens == 4096

    @patch.dict(os.environ, {}, clear=True)
    def test_client_initialization_no_api_key(self) -> None:
        """Test client initialization without API key."""
        with pytest.raises(ContractViolation, match="ANTHROPIC_API_KEY environment variable not found"):
            AnthropicClient()

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_send_message_contract_validation(self) -> None:
        """Test that send_message validates contracts."""
        client = AnthropicClient()

        # Empty messages should fail
        with pytest.raises(ContractViolation, match="Messages list cannot be empty"):
            await client.send_message([])

        # Invalid role should fail
        invalid_msg = AnthropicMessage(role="invalid", content="test")
        with pytest.raises(ContractViolation, match="Invalid message role"):
            await client.send_message([invalid_msg])

        # Empty content should fail
        empty_msg = AnthropicMessage(role="user", content="   ")
        with pytest.raises(ContractViolation, match="Message content cannot be empty"):
            await client.send_message([empty_msg])

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_send_message_success(self) -> None:
        """Test successful message sending with mocked API."""
        client = AnthropicClient()

        # Mock the HTTP response
        mock_response_data = {
            "content": [{"type": "text", "text": "Hello! How can I help you?"}],
            "usage": {"input_tokens": 10, "output_tokens": 8},
            "model": "claude-sonnet-4-20250514",
            "stop_reason": "end_turn"
        }

        with patch.object(client.client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            messages = [AnthropicMessage(role="user", content="Hello")]
            response = await client.send_message(messages)

            assert response.content[0]["text"] == "Hello! How can I help you?"
            assert response.usage["input_tokens"] == 10
            assert response.usage["output_tokens"] == 8
            assert response.model == "claude-sonnet-4-20250514"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_send_message_api_error(self) -> None:
        """Test handling of API errors."""
        client = AnthropicClient()

        with patch.object(client.client, 'post') as mock_post:
            mock_post.side_effect = httpx.HTTPError("API Error")

            messages = [AnthropicMessage(role="user", content="Hello")]
            with pytest.raises(httpx.HTTPError):
                await client.send_message(messages)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_send_message_invalid_response(self) -> None:
        """Test handling of invalid API responses."""
        client = AnthropicClient()

        # Mock response missing required fields
        mock_response_data = {"invalid": "response"}

        with patch.object(client.client, 'post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            messages = [AnthropicMessage(role="user", content="Hello")]
            with pytest.raises(ContractViolation, match="API response missing content field"):
                await client.send_message(messages)


class TestClientFactory:
    """Test client factory function."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"})
    @pytest.mark.asyncio
    async def test_create_anthropic_client_success(self) -> None:
        """Test successful client creation."""
        client = await create_anthropic_client()
        assert isinstance(client, AnthropicClient)
        assert client.api_key == "test_key"

    @patch.dict(os.environ, {}, clear=True)
    @pytest.mark.asyncio
    async def test_create_anthropic_client_failure(self) -> None:
        """Test client creation failure."""
        with pytest.raises(ContractViolation):
            await create_anthropic_client()
