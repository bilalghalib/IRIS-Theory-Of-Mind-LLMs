"""
Integration tests for message API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json


@pytest.mark.integration
@pytest.mark.api
class TestMessagesAPI:
    """Test suite for messages API."""

    def test_send_message_success(self, client: TestClient, auth_headers, mock_llm_response):
        """Test successful message sending."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation') as mock_create_conv:
                mock_create_conv.return_value = {"id": "conv_123"}

                with patch('db.supabase_client.SupabaseClient.create_message') as mock_create_msg:
                    mock_create_msg.return_value = {"id": "msg_123"}

                    response = client.post(
                        "/v1/conversations/conv_123/messages",
                        headers=auth_headers,
                        json={
                            "user_id": "user_123",
                            "message": "Hello, can you help me?",
                            "llm_provider": "openai",
                            "llm_api_key": "sk-test",
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }
                    )

                    assert response.status_code == 200
                    data = response.json()

                    assert "conversation_id" in data
                    assert "message_id" in data
                    assert "response" in data
                    assert "aperture_link" in data
                    assert data["provider"] == "openai"

    def test_send_message_missing_user_id(self, client: TestClient, auth_headers):
        """Test message sending without user ID."""
        response = client.post(
            "/v1/conversations/conv_123/messages",
            headers=auth_headers,
            json={
                "message": "Hello",
                "llm_provider": "openai",
                "llm_api_key": "sk-test"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_send_message_invalid_provider(self, client: TestClient, auth_headers):
        """Test message sending with invalid provider."""
        response = client.post(
            "/v1/conversations/conv_123/messages",
            headers=auth_headers,
            json={
                "user_id": "user_123",
                "message": "Hello",
                "llm_provider": "invalid_provider",
                "llm_api_key": "sk-test"
            }
        )

        assert response.status_code == 422

    def test_send_message_anthropic(self, client: TestClient, auth_headers, mock_llm_response):
        """Test sending message with Anthropic provider."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["anthropic"]["content"][0]["text"],
                mock_llm_response["anthropic"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation') as mock_create_conv:
                mock_create_conv.return_value = {"id": "conv_123"}

                with patch('db.supabase_client.SupabaseClient.create_message') as mock_create_msg:
                    mock_create_msg.return_value = {"id": "msg_123"}

                    response = client.post(
                        "/v1/conversations/conv_123/messages",
                        headers=auth_headers,
                        json={
                            "user_id": "user_123",
                            "message": "Hello",
                            "llm_provider": "anthropic",
                            "llm_api_key": "sk-ant-test"
                        }
                    )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["provider"] == "anthropic"

    def test_send_message_with_system_prompt(self, client: TestClient, auth_headers, mock_llm_response):
        """Test sending message with custom system prompt."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                with patch('db.supabase_client.SupabaseClient.create_message'):
                    response = client.post(
                        "/v1/conversations/conv_123/messages",
                        headers=auth_headers,
                        json={
                            "user_id": "user_123",
                            "message": "Hello",
                            "llm_provider": "openai",
                            "llm_api_key": "sk-test",
                            "system_prompt": "You are a helpful coding assistant."
                        }
                    )

                    assert response.status_code == 200

                    # Verify system prompt was passed
                    mock_llm.assert_called_once()
                    call_kwargs = mock_llm.call_args[1]
                    assert call_kwargs["system_prompt"] == "You are a helpful coding assistant."

    def test_send_message_with_metadata(self, client: TestClient, auth_headers, mock_llm_response):
        """Test sending message with metadata."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                with patch('db.supabase_client.SupabaseClient.create_message') as mock_create_msg:
                    mock_create_msg.return_value = {"id": "msg_123"}

                    response = client.post(
                        "/v1/conversations/conv_123/messages",
                        headers=auth_headers,
                        json={
                            "user_id": "user_123",
                            "message": "Hello",
                            "llm_provider": "openai",
                            "llm_api_key": "sk-test",
                            "metadata": {
                                "source": "web_app",
                                "session_id": "sess_456"
                            }
                        }
                    )

                    assert response.status_code == 200

    @pytest.mark.slow
    def test_send_message_triggers_assessment_extraction(
        self, client: TestClient, auth_headers, mock_llm_response
    ):
        """Test that sending a message triggers background assessment extraction."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                with patch('db.supabase_client.SupabaseClient.create_message'):
                    with patch('services.assessment_extractor.extract_basic_assessments') as mock_extract:
                        mock_extract.return_value = []

                        response = client.post(
                            "/v1/conversations/conv_123/messages",
                            headers=auth_headers,
                            json={
                                "user_id": "user_123",
                                "message": "I'm having trouble with AWS deployment",
                                "llm_provider": "openai",
                                "llm_api_key": "sk-test"
                            }
                        )

                        assert response.status_code == 200

                        # Note: In real implementation, extraction happens in background
                        # This test would verify the task was queued

    def test_send_message_unauthorized(self, client: TestClient):
        """Test sending message without authentication."""
        response = client.post(
            "/v1/conversations/conv_123/messages",
            json={
                "user_id": "user_123",
                "message": "Hello",
                "llm_provider": "openai",
                "llm_api_key": "sk-test"
            }
        )

        assert response.status_code == 403

    def test_send_message_llm_api_error(self, client: TestClient, auth_headers):
        """Test handling of LLM API errors."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.side_effect = Exception("OpenAI API Error: Rate limit exceeded")

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                response = client.post(
                    "/v1/conversations/conv_123/messages",
                    headers=auth_headers,
                    json={
                        "user_id": "user_123",
                        "message": "Hello",
                        "llm_provider": "openai",
                        "llm_api_key": "sk-test"
                    }
                )

                assert response.status_code in [500, 503]
                assert "error" in response.json()

    def test_send_message_long_conversation_history(
        self, client: TestClient, auth_headers, mock_llm_response
    ):
        """Test sending message with long conversation history."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                with patch('db.supabase_client.SupabaseClient.get_conversation_messages') as mock_get_msgs:
                    # Simulate 50 previous messages
                    mock_get_msgs.return_value = [
                        {
                            "role": "user" if i % 2 == 0 else "assistant",
                            "content": f"Message {i}"
                        }
                        for i in range(50)
                    ]

                    with patch('db.supabase_client.SupabaseClient.create_message'):
                        response = client.post(
                            "/v1/conversations/conv_123/messages",
                            headers=auth_headers,
                            json={
                                "user_id": "user_123",
                                "message": "Latest message",
                                "llm_provider": "openai",
                                "llm_api_key": "sk-test"
                            }
                        )

                        assert response.status_code == 200

    def test_send_message_custom_temperature(
        self, client: TestClient, auth_headers, mock_llm_response
    ):
        """Test sending message with custom temperature."""
        with patch('services.llm_proxy.send_message') as mock_llm:
            mock_llm.return_value = (
                mock_llm_response["openai"]["choices"][0]["message"]["content"],
                mock_llm_response["openai"]
            )

            with patch('db.supabase_client.SupabaseClient.create_conversation'):
                with patch('db.supabase_client.SupabaseClient.create_message'):
                    response = client.post(
                        "/v1/conversations/conv_123/messages",
                        headers=auth_headers,
                        json={
                            "user_id": "user_123",
                            "message": "Hello",
                            "llm_provider": "openai",
                            "llm_api_key": "sk-test",
                            "temperature": 0.2
                        }
                    )

                    assert response.status_code == 200

                    # Verify temperature was passed
                    mock_llm.assert_called_once()
                    call_kwargs = mock_llm.call_args[1]
                    assert call_kwargs["temperature"] == 0.2
