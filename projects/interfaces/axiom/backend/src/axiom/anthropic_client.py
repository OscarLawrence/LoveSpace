"""Direct HTTP client for Anthropic API without SDK pollution."""

import json
import os
from typing import AsyncGenerator, Dict, List

import httpx


class DirectAnthropicClient:
    """Direct HTTP client for Anthropic API with streaming support."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    
    async def stream_messages(
        self,
        model: str,
        max_tokens: int,
        system: str,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Stream messages from Anthropic API."""
        
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str == "[DONE]":
                            break
                            
                        try:
                            data = json.loads(data_str)
                            
                            # Handle different event types
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                                        
                        except json.JSONDecodeError:
                            # Skip malformed JSON lines
                            continue


def create_client() -> DirectAnthropicClient:
    """Create Anthropic client with API key from environment."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return DirectAnthropicClient(api_key)