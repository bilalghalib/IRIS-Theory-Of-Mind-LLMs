"""
Pytest configuration and fixtures for Aperture tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
import os

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["APERTURE_API_KEY"] = "test-api-key"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["OPENAI_API_KEY"] = "sk-test"

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Headers with valid API key."""
    return {"X-Aperture-API-Key": "test-api-key"}


@pytest.fixture
def mock_db():
    """Mock database client."""
    mock = Mock()

    # Mock common DB operations
    mock.get_or_create_user = AsyncMock(return_value={
        "id": "user_123",
        "external_id": "test_user",
        "metadata": {}
    })

    mock.create_conversation = AsyncMock(return_value={
        "id": "conv_123",
        "user_id": "user_123",
        "metadata": {},
        "created_at": "2024-01-01T00:00:00Z"
    })

    mock.add_message = AsyncMock(return_value={
        "id": "msg_123",
        "conversation_id": "conv_123",
        "role": "user",
        "content": "Hello",
        "created_at": "2024-01-01T00:00:00Z"
    })

    mock.create_assessment = AsyncMock(return_value={
        "id": "assess_123",
        "user_id": "user_123",
        "element": "technical_confidence",
        "value_type": "score",
        "value_data": {"score": 0.7},
        "reasoning": "User seems confident",
        "confidence": 0.8,
        "created_at": "2024-01-01T00:00:00Z"
    })

    return mock


@pytest.fixture
def mock_llm():
    """Mock LLM proxy."""
    mock = Mock()
    mock.send_message = AsyncMock(return_value=(
        "This is a test response from the LLM.",
        {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "usage": {"total_tokens": 100}
        }
    ))
    return mock


@pytest.fixture
def sample_user_message():
    """Sample user message for testing."""
    return {
        "user_id": "test_user",
        "message": "I'm trying to deploy my app on AWS but keep getting errors",
        "llm_provider": "openai",
        "llm_api_key": "sk-test",
        "llm_model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 500
    }


@pytest.fixture
def sample_assessment():
    """Sample assessment data."""
    return {
        "id": "assess_123",
        "user_id": "user_123",
        "element": "technical_confidence",
        "value_type": "score",
        "value_data": {"score": 0.7},
        "reasoning": "User demonstrates moderate technical knowledge",
        "confidence": 0.8,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "user_corrected": False,
        "observation_count": 3,
        "metadata": {}
    }


@pytest.fixture
def sample_evidence():
    """Sample evidence data."""
    return [
        {
            "id": "ev_1",
            "assessment_id": "assess_123",
            "user_message": "I'm trying to deploy on AWS",
            "context": "Discussion about deployment",
            "timestamp": "2024-01-01T00:00:00Z",
            "confidence_contribution": 0.8
        }
    ]
