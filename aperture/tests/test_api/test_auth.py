"""
Tests for API authentication.
"""

import pytest


def test_missing_api_key(client):
    """Test that requests without API key are rejected."""
    response = client.get("/v1/users/test_user/assessments")
    assert response.status_code == 422  # Missing required header


def test_invalid_api_key(client):
    """Test that invalid API keys are rejected."""
    response = client.get(
        "/v1/users/test_user/assessments",
        headers={"X-Aperture-API-Key": "invalid-key"}
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


def test_valid_api_key(client, auth_headers):
    """Test that valid API key is accepted."""
    # This will return 200 or 404 depending on if data exists,
    # but should NOT return 401
    response = client.get(
        "/v1/users/test_user/assessments",
        headers=auth_headers
    )
    assert response.status_code != 401
