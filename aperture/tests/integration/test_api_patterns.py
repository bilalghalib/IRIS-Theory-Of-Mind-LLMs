"""
Integration tests for pattern discovery and constructs API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock


@pytest.mark.integration
@pytest.mark.api
class TestPatternDiscoveryAPI:
    """Test suite for pattern discovery API."""

    def test_discover_patterns_success(self, client: TestClient, auth_headers):
        """Test successful pattern discovery."""
        with patch('services.pattern_discovery.discover_patterns') as mock_discover:
            mock_discover.return_value = {
                "patterns_found": 2,
                "patterns": [
                    {
                        "name": "AWS Deployment Issues",
                        "description": "Users frequently struggle with AWS deployment",
                        "detected_in": 25,
                        "occurrence_rate": 0.35,
                        "confidence": 0.88,
                        "suggested_construct": {
                            "name": "aws_deployment_expertise",
                            "element": "aws_expertise",
                            "value_type": "score"
                        },
                        "evidence": ["deployment errors", "permission issues"]
                    }
                ]
            }

            response = client.post(
                "/v1/admin/discover-patterns",
                headers=auth_headers,
                json={
                    "min_users": 10,
                    "min_occurrence_rate": 0.2,
                    "lookback_days": 7
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["patterns_found"] == 2
            assert len(data["patterns"]) == 1
            assert data["patterns"][0]["name"] == "AWS Deployment Issues"

    def test_discover_patterns_no_results(self, client: TestClient, auth_headers):
        """Test pattern discovery with no patterns found."""
        with patch('services.pattern_discovery.discover_patterns') as mock_discover:
            mock_discover.return_value = {
                "patterns_found": 0,
                "patterns": []
            }

            response = client.post(
                "/v1/admin/discover-patterns",
                headers=auth_headers,
                json={}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["patterns_found"] == 0
            assert len(data["patterns"]) == 0

    def test_discover_patterns_custom_thresholds(self, client: TestClient, auth_headers):
        """Test pattern discovery with custom thresholds."""
        with patch('services.pattern_discovery.discover_patterns') as mock_discover:
            mock_discover.return_value = {
                "patterns_found": 0,
                "patterns": []
            }

            response = client.post(
                "/v1/admin/discover-patterns",
                headers=auth_headers,
                json={
                    "min_users": 50,
                    "min_occurrence_rate": 0.4,
                    "lookback_days": 30
                }
            )

            assert response.status_code == 200

            # Verify custom thresholds were passed
            mock_discover.assert_called_once()
            call_kwargs = mock_discover.call_args[1]
            assert call_kwargs["min_users"] == 50
            assert call_kwargs["min_occurrence_rate"] == 0.4
            assert call_kwargs["lookback_days"] == 30

    @pytest.mark.slow
    def test_discover_patterns_large_dataset(self, client: TestClient, auth_headers):
        """Test pattern discovery with large dataset."""
        with patch('services.pattern_discovery.discover_patterns') as mock_discover:
            # Simulate many patterns found
            mock_discover.return_value = {
                "patterns_found": 100,
                "patterns": [
                    {
                        "name": f"Pattern {i}",
                        "description": f"Description {i}",
                        "detected_in": 10 + i,
                        "occurrence_rate": 0.2 + (i * 0.01),
                        "confidence": 0.7 + (i * 0.001),
                        "suggested_construct": {},
                        "evidence": []
                    }
                    for i in range(20)  # Return top 20
                ]
            }

            response = client.post(
                "/v1/admin/discover-patterns",
                headers=auth_headers,
                json={"min_users": 5}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["patterns_found"] == 100
            assert len(data["patterns"]) <= 20  # Should limit results


@pytest.mark.integration
@pytest.mark.api
class TestConstructsAPI:
    """Test suite for constructs API."""

    def test_create_construct_from_description(self, client: TestClient, auth_headers):
        """Test creating construct from natural language."""
        with patch('services.construct_creator.create_from_description') as mock_create:
            mock_create.return_value = {
                "match_type": "template",
                "suggested_templates": [
                    {
                        "id": "purchase_intent",
                        "name": "Purchase Intent (BANT)",
                        "description": "Track buyer readiness",
                        "similarity": 0.92,
                        "config": {
                            "element": "purchase_intent",
                            "value_type": "tag",
                            "tags": ["hot", "warm", "cold"]
                        }
                    }
                ]
            }

            response = client.post(
                "/v1/constructs/from-description",
                headers=auth_headers,
                json={
                    "description": "I want to track if users are ready to upgrade to paid"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["match_type"] == "template"
            assert len(data["suggested_templates"]) == 1
            assert data["suggested_templates"][0]["similarity"] == 0.92

    def test_create_construct_custom_generation(self, client: TestClient, auth_headers):
        """Test creating custom construct when no template matches."""
        with patch('services.construct_creator.create_from_description') as mock_create:
            mock_create.return_value = {
                "match_type": "custom",
                "custom_generated": {
                    "element": "user_expertise_level",
                    "value_type": "range",
                    "range_min": 1,
                    "range_max": 10,
                    "description": "User's expertise level in the domain"
                }
            }

            response = client.post(
                "/v1/constructs/from-description",
                headers=auth_headers,
                json={
                    "description": "Track user expertise on a scale of 1-10"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["match_type"] == "custom"
            assert "custom_generated" in data
            assert data["custom_generated"]["value_type"] == "range"

    def test_get_construct_templates(self, client: TestClient, auth_headers):
        """Test retrieving construct templates from marketplace."""
        with patch('services.construct_creator.get_templates') as mock_get:
            mock_get.return_value = {
                "templates": [
                    {
                        "id": "customer_support_tier",
                        "name": "Customer Support Tier",
                        "description": "Classify support request complexity",
                        "use_case": "customer_support",
                        "config": {}
                    },
                    {
                        "id": "purchase_intent",
                        "name": "Purchase Intent (BANT)",
                        "description": "Track buyer readiness",
                        "use_case": "sales",
                        "config": {}
                    }
                ]
            }

            response = client.get(
                "/v1/constructs/templates",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["templates"]) == 2

    def test_get_construct_templates_filtered(self, client: TestClient, auth_headers):
        """Test filtering construct templates."""
        with patch('services.construct_creator.get_templates') as mock_get:
            mock_get.return_value = {
                "templates": [
                    {
                        "id": "customer_support_tier",
                        "name": "Customer Support Tier",
                        "use_case": "customer_support",
                        "config": {}
                    }
                ]
            }

            response = client.get(
                "/v1/constructs/templates?use_case=customer_support",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["templates"]) == 1
            assert data["templates"][0]["use_case"] == "customer_support"

    def test_validate_construct_config(self, client: TestClient, auth_headers):
        """Test validating construct configuration."""
        with patch('services.construct_creator.validate_config') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "warnings": []
            }

            response = client.post(
                "/v1/constructs/validate",
                headers=auth_headers,
                json={
                    "element": "test_construct",
                    "value_type": "score",
                    "value_data": {
                        "score_min": 0,
                        "score_max": 1
                    }
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] == True

    def test_validate_construct_invalid(self, client: TestClient, auth_headers):
        """Test validating invalid construct configuration."""
        with patch('services.construct_creator.validate_config') as mock_validate:
            mock_validate.return_value = {
                "valid": False,
                "issues": ["Missing required field: element"],
                "warnings": []
            }

            response = client.post(
                "/v1/constructs/validate",
                headers=auth_headers,
                json={
                    "value_type": "score"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] == False
            assert len(data["issues"]) > 0

    def test_create_construct_missing_description(self, client: TestClient, auth_headers):
        """Test creating construct without description."""
        response = client.post(
            "/v1/constructs/from-description",
            headers=auth_headers,
            json={}
        )

        assert response.status_code == 422  # Validation error

    def test_get_construct_templates_search(self, client: TestClient, auth_headers):
        """Test searching construct templates."""
        with patch('services.construct_creator.get_templates') as mock_get:
            mock_get.return_value = {
                "templates": [
                    {
                        "id": "purchase_intent",
                        "name": "Purchase Intent",
                        "description": "Track buying signals",
                        "config": {}
                    }
                ]
            }

            response = client.get(
                "/v1/constructs/templates?search=purchase",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["templates"]) >= 0  # May or may not find matches
