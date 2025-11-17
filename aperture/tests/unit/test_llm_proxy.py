"""
Unit tests for LLM proxy service.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from services.llm_proxy import send_message


@pytest.mark.unit
class TestLLMProxy:
    """Test suite for LLM proxy service."""

    @pytest.mark.asyncio
    async def test_send_message_openai(self):
        """Test sending message to OpenAI."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "Test response"
                    }
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                },
                "model": "gpt-4"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            response, metadata = await send_message(
                provider="openai",
                api_key="sk-test",
                messages=[{"role": "user", "content": "Hello"}]
            )

            assert response == "Test response"
            assert metadata["model"] == "gpt-4"
            assert metadata["usage"]["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_send_message_anthropic(self):
        """Test sending message to Anthropic."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "content": [{
                    "type": "text",
                    "text": "Test response from Claude"
                }],
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 5
                },
                "model": "claude-3-sonnet-20240229"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            response, metadata = await send_message(
                provider="anthropic",
                api_key="sk-ant-test",
                messages=[{"role": "user", "content": "Hello"}]
            )

            assert response == "Test response from Claude"
            assert metadata["model"].startswith("claude")

    @pytest.mark.asyncio
    async def test_send_message_with_system_prompt(self):
        """Test including system prompt in request."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {},
                "model": "gpt-4"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            await send_message(
                provider="openai",
                api_key="sk-test",
                messages=[{"role": "user", "content": "Hello"}],
                system_prompt="You are a helpful assistant."
            )

            # Verify system prompt was included in request
            call_args = mock_post.call_args
            request_body = call_args[1]['json']
            assert any(
                msg.get('role') == 'system' and 'helpful' in msg.get('content', '')
                for msg in request_body.get('messages', [])
            )

    @pytest.mark.asyncio
    async def test_send_message_custom_temperature(self):
        """Test custom temperature parameter."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {},
                "model": "gpt-4"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            await send_message(
                provider="openai",
                api_key="sk-test",
                messages=[{"role": "user", "content": "Hello"}],
                temperature=0.2
            )

            call_args = mock_post.call_args
            request_body = call_args[1]['json']
            assert request_body['temperature'] == 0.2

    @pytest.mark.asyncio
    async def test_send_message_custom_max_tokens(self):
        """Test custom max_tokens parameter."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {},
                "model": "gpt-4"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            await send_message(
                provider="openai",
                api_key="sk-test",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=500
            )

            call_args = mock_post.call_args
            request_body = call_args[1]['json']
            assert request_body['max_tokens'] == 500

    @pytest.mark.asyncio
    async def test_send_message_api_error(self):
        """Test handling of API errors."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 429
            mock_response.json.return_value = {
                "error": {
                    "message": "Rate limit exceeded",
                    "type": "rate_limit_error"
                }
            }
            mock_post.return_value = mock_response

            with pytest.raises(Exception) as exc_info:
                await send_message(
                    provider="openai",
                    api_key="sk-test",
                    messages=[{"role": "user", "content": "Hello"}]
                )

            assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_send_message_invalid_provider(self):
        """Test invalid provider handling."""
        with pytest.raises(ValueError):
            await send_message(
                provider="invalid_provider",
                api_key="test-key",
                messages=[{"role": "user", "content": "Hello"}]
            )

    @pytest.mark.asyncio
    async def test_send_message_long_conversation(self):
        """Test handling long conversation history."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {"total_tokens": 1000},
                "model": "gpt-4"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # Create 50 messages
            messages = []
            for i in range(50):
                messages.append({
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": f"Message {i}"
                })

            response, metadata = await send_message(
                provider="openai",
                api_key="sk-test",
                messages=messages
            )

            assert response == "Response"
            call_args = mock_post.call_args
            request_body = call_args[1]['json']
            assert len(request_body['messages']) <= 50

    @pytest.mark.asyncio
    async def test_send_message_custom_model(self):
        """Test specifying custom model."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response"}}],
                "usage": {},
                "model": "gpt-4-turbo"
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            await send_message(
                provider="openai",
                api_key="sk-test",
                messages=[{"role": "user", "content": "Hello"}],
                model="gpt-4-turbo"
            )

            call_args = mock_post.call_args
            request_body = call_args[1]['json']
            assert request_body['model'] == "gpt-4-turbo"

    @pytest.mark.asyncio
    async def test_send_message_timeout(self):
        """Test request timeout handling."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = TimeoutError("Request timed out")

            with pytest.raises(TimeoutError):
                await send_message(
                    provider="openai",
                    api_key="sk-test",
                    messages=[{"role": "user", "content": "Hello"}]
                )
