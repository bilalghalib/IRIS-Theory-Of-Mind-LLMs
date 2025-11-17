"""
Pytest fixtures and configuration for integration tests.
"""

import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import uuid

# Import main app
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from main import app
from db.supabase_client import SupabaseClient


@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration."""
    return {
        "base_url": "http://testserver",
        "test_user_id": "test_user_123",
        "test_api_key": "test_aperture_key_123",
        "test_openai_key": "sk-test-key-123",
        "test_anthropic_key": "sk-ant-test-key-123"
    }


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def mock_supabase():
    """Mock Supabase client."""
    mock_client = Mock(spec=SupabaseClient)

    # Mock common methods
    mock_client.create_user.return_value = {
        "id": "user_123",
        "created_at": "2024-01-01T00:00:00Z"
    }

    mock_client.create_conversation.return_value = {
        "id": "conv_123",
        "user_id": "user_123",
        "metadata": {},
        "created_at": "2024-01-01T00:00:00Z"
    }

    mock_client.create_message.return_value = {
        "id": "msg_123",
        "conversation_id": "conv_123",
        "role": "user",
        "content": "Test message",
        "created_at": "2024-01-01T00:00:00Z"
    }

    mock_client.create_assessment.return_value = {
        "id": "assess_123",
        "user_id": "user_123",
        "element": "technical_confidence",
        "value_type": "score",
        "value_data": {"score": 0.7},
        "reasoning": "Test reasoning",
        "confidence": 0.85,
        "created_at": "2024-01-01T00:00:00Z"
    }

    mock_client.get_assessments.return_value = []

    return mock_client


@pytest.fixture(scope="function")
def mock_llm_response():
    """Mock LLM API responses."""
    openai_response = {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "This is a test response from the AI assistant."
            }
        }],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 20,
            "total_tokens": 70
        },
        "model": "gpt-4"
    }

    anthropic_response = {
        "content": [{
            "type": "text",
            "text": "This is a test response from Claude."
        }],
        "usage": {
            "input_tokens": 50,
            "output_tokens": 20
        },
        "model": "claude-3-sonnet-20240229"
    }

    return {
        "openai": openai_response,
        "anthropic": anthropic_response
    }


@pytest.fixture(scope="function")
def sample_conversation():
    """Sample conversation data."""
    return {
        "conversation_id": f"conv_{uuid.uuid4().hex[:8]}",
        "user_id": f"user_{uuid.uuid4().hex[:8]}",
        "messages": [
            {
                "role": "user",
                "content": "I'm trying to deploy my app on AWS but keep getting errors"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you troubleshoot your AWS deployment..."
            },
            {
                "role": "user",
                "content": "The error is about permissions"
            }
        ]
    }


@pytest.fixture(scope="function")
def sample_assessment():
    """Sample assessment data."""
    return {
        "id": f"assess_{uuid.uuid4().hex[:8]}",
        "user_id": "user_123",
        "element": "technical_confidence",
        "value_type": "score",
        "value_data": {"score": 0.6, "range": [0, 1]},
        "reasoning": "User is encountering AWS deployment errors and seeking help",
        "confidence": 0.8,
        "evidence": [
            {
                "user_message": "I'm trying to deploy my app on AWS but keep getting errors",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ]
    }


@pytest.fixture(scope="function")
def auth_headers(test_config):
    """Authentication headers for API requests."""
    return {
        "X-Aperture-API-Key": test_config["test_api_key"]
    }


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Cleanup happens here


@pytest.fixture(scope="function")
def mock_embedding_service():
    """Mock embedding service."""
    mock = Mock()
    mock.generate_embedding.return_value = [0.1] * 1536  # Standard embedding size
    mock.cosine_similarity.return_value = 0.85
    mock.find_similar.return_value = []
    mock.cluster_embeddings.return_value = []
    return mock


@pytest.fixture(scope="function")
def mock_pattern_discovery():
    """Mock pattern discovery service."""
    mock = Mock()
    mock.discover_patterns.return_value = {
        "patterns_found": 2,
        "patterns": [
            {
                "name": "AWS Deployment Struggles",
                "description": "Users frequently struggle with AWS deployment permissions",
                "detected_in": 15,
                "occurrence_rate": 0.3,
                "confidence": 0.85,
                "suggested_construct": {
                    "name": "aws_deployment_expertise",
                    "element": "aws_expertise",
                    "value_type": "score"
                },
                "evidence": [
                    "deployment errors",
                    "AWS permissions",
                    "configuration issues"
                ]
            }
        ]
    }
    return mock


# Pytest hooks
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
