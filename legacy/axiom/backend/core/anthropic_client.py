"""
Pure HTTP client for Claude Sonnet 4
No SDK pollution, clean interface for coherent AI collaboration
"""
import os
from typing import AsyncGenerator

import httpx
from dotenv import load_dotenv

from .contracts import contract_enforced

# Load environment variables (auto-resolves .env up the directory tree)
# Note: load_dotenv() searches up the directory tree automatically
load_dotenv()


class AnthropicClient:
    """Pure HTTP client for Anthropic Claude API"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.model = "claude-3-5-sonnet-20241022"
        
        self.headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    
    @contract_enforced(
        preconditions=["messages is not empty", "all messages have role and content"],
        postconditions=["returns valid response with content"],
        description="Send messages to Claude and get response"
    )
    async def send_message(
        self, 
        messages: list[dict], 
        system_prompt: str | None = None,
        max_tokens: int = 4000
    ) -> dict:
        """
        Send messages to Claude API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            API response dict
        """
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    
    @contract_enforced(
        description="Stream messages from Claude for real-time responses"
    )
    async def stream_message(
        self, 
        messages: list[dict], 
        system_prompt: str | None = None,
        max_tokens: int = 4000
    ) -> AsyncGenerator[dict, None]:
        """
        Stream messages from Claude API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            
        Yields:
            Streaming response chunks
        """
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": messages,
            "stream": True
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=60.0
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            import json
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            continue