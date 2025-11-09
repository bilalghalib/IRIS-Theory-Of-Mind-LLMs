from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from anthropic import Anthropic
import httpx
from datetime import datetime


class LLMProxy:
    """Proxy service for forwarding requests to LLM providers."""

    def __init__(self):
        self._openai_clients: Dict[str, OpenAI] = {}
        self._anthropic_clients: Dict[str, Anthropic] = {}

    def _get_openai_client(self, api_key: str) -> OpenAI:
        """Get or create OpenAI client for a given API key."""
        if api_key not in self._openai_clients:
            self._openai_clients[api_key] = OpenAI(api_key=api_key)
        return self._openai_clients[api_key]

    def _get_anthropic_client(self, api_key: str) -> Anthropic:
        """Get or create Anthropic client for a given API key."""
        if api_key not in self._anthropic_clients:
            self._anthropic_clients[api_key] = Anthropic(api_key=api_key)
        return self._anthropic_clients[api_key]

    async def send_message(
        self,
        provider: str,
        api_key: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Send a message to the specified LLM provider.

        Returns:
            Tuple of (response_text, metadata)
        """
        if provider == "openai":
            return await self._send_openai(
                api_key, messages, model, system_prompt, temperature, max_tokens
            )
        elif provider == "anthropic":
            return await self._send_anthropic(
                api_key, messages, model, system_prompt, temperature, max_tokens
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _send_openai(
        self,
        api_key: str,
        messages: List[Dict[str, str]],
        model: Optional[str],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Send request to OpenAI."""
        client = self._get_openai_client(api_key)

        # Default model
        if not model:
            model = "gpt-4o-mini"

        # Prepare messages
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Extract response
        response_text = response.choices[0].message.content
        metadata = {
            "provider": "openai",
            "model": model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "finish_reason": response.choices[0].finish_reason
        }

        return response_text, metadata

    async def _send_anthropic(
        self,
        api_key: str,
        messages: List[Dict[str, str]],
        model: Optional[str],
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Send request to Anthropic."""
        client = self._get_anthropic_client(api_key)

        # Default model
        if not model:
            model = "claude-3-5-sonnet-20241022"

        # Anthropic expects messages without system in the messages array
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=messages
        )

        # Extract response
        response_text = response.content[0].text
        metadata = {
            "provider": "anthropic",
            "model": model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "stop_reason": response.stop_reason
        }

        return response_text, metadata


# Singleton instance
llm_proxy = LLMProxy()
