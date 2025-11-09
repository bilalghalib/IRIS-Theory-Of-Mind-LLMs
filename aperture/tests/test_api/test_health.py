"""
Tests for health check and basic endpoints.
"""

import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Aperture API"
    assert "version" in data
    assert "docs" in data


def test_docs_available(client):
    """Test that API docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_spec(client):
    """Test OpenAPI spec is generated."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "info" in spec
    assert spec["info"]["title"] == "Aperture API"
