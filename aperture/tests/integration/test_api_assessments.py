"""
Integration tests for assessments API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from datetime import datetime


@pytest.mark.integration
@pytest.mark.api
class TestAssessmentsAPI:
    """Test suite for assessments API."""

    def test_get_assessments(self, client: TestClient, auth_headers):
        """Test retrieving user assessments."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = [
                {
                    "id": "assess_1",
                    "user_id": "user_123",
                    "element": "technical_confidence",
                    "value_type": "score",
                    "value_data": {"score": 0.7},
                    "reasoning": "User demonstrates moderate technical knowledge",
                    "confidence": 0.85,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            ]

            response = client.get(
                "/v1/users/user_123/assessments",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["element"] == "technical_confidence"

    def test_get_assessments_with_element_filter(self, client: TestClient, auth_headers):
        """Test filtering assessments by element."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = []

            response = client.get(
                "/v1/users/user_123/assessments?element=technical_confidence",
                headers=auth_headers
            )

            assert response.status_code == 200
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["element"] == "technical_confidence"

    def test_get_assessments_with_confidence_filter(self, client: TestClient, auth_headers):
        """Test filtering assessments by confidence threshold."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = []

            response = client.get(
                "/v1/users/user_123/assessments?min_confidence=0.8",
                headers=auth_headers
            )

            assert response.status_code == 200
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["min_confidence"] == 0.8

    def test_get_assessment_by_id(self, client: TestClient, auth_headers):
        """Test retrieving specific assessment with evidence."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = {
                "id": "assess_123",
                "user_id": "user_123",
                "element": "technical_confidence",
                "value_type": "score",
                "value_data": {"score": 0.7},
                "reasoning": "Test reasoning",
                "confidence": 0.85,
                "evidence": [
                    {
                        "user_message": "I'm having trouble with deployment",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "conversation_id": "conv_123"
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z"
            }

            response = client.get(
                "/v1/users/user_123/assessments/assess_123",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "assess_123"
            assert "evidence" in data
            assert len(data["evidence"]) == 1

    def test_get_assessment_not_found(self, client: TestClient, auth_headers):
        """Test retrieving non-existent assessment."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = None

            response = client.get(
                "/v1/users/user_123/assessments/nonexistent",
                headers=auth_headers
            )

            assert response.status_code == 404

    def test_correct_assessment(self, client: TestClient, auth_headers):
        """Test submitting user correction for assessment."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = {
                "id": "assess_123",
                "user_id": "user_123",
                "element": "technical_confidence"
            }

            with patch('db.supabase_client.SupabaseClient.update_assessment') as mock_update:
                mock_update.return_value = {
                    "id": "assess_123",
                    "user_corrected": True
                }

                response = client.put(
                    "/v1/users/user_123/assessments/assess_123/correct",
                    headers=auth_headers,
                    json={
                        "correction_type": "wrong_value",
                        "user_explanation": "I'm actually very confident with AWS"
                    }
                )

                assert response.status_code == 200
                data = response.json()
                assert data["user_corrected"] == True

    def test_correct_assessment_wrong_interpretation(self, client: TestClient, auth_headers):
        """Test correction with wrong interpretation type."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = {"id": "assess_123", "user_id": "user_123"}

            with patch('db.supabase_client.SupabaseClient.update_assessment') as mock_update:
                mock_update.return_value = {"id": "assess_123"}

                response = client.put(
                    "/v1/users/user_123/assessments/assess_123/correct",
                    headers=auth_headers,
                    json={
                        "correction_type": "wrong_interpretation",
                        "user_explanation": "I wasn't asking for help, just explaining what I did"
                    }
                )

                assert response.status_code == 200

    def test_correct_assessment_not_applicable(self, client: TestClient, auth_headers):
        """Test marking assessment as not applicable."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = {"id": "assess_123", "user_id": "user_123"}

            with patch('db.supabase_client.SupabaseClient.update_assessment') as mock_update:
                mock_update.return_value = {"id": "assess_123"}

                response = client.put(
                    "/v1/users/user_123/assessments/assess_123/correct",
                    headers=auth_headers,
                    json={
                        "correction_type": "not_applicable",
                        "user_explanation": "This doesn't apply to my situation"
                    }
                )

                assert response.status_code == 200

    def test_correct_assessment_unauthorized_user(self, client: TestClient, auth_headers):
        """Test correcting assessment for different user."""
        with patch('db.supabase_client.SupabaseClient.get_assessment') as mock_get:
            mock_get.return_value = {
                "id": "assess_123",
                "user_id": "different_user"
            }

            response = client.put(
                "/v1/users/user_123/assessments/assess_123/correct",
                headers=auth_headers,
                json={
                    "correction_type": "wrong_value",
                    "user_explanation": "Test"
                }
            )

            assert response.status_code == 403

    def test_get_assessments_pagination(self, client: TestClient, auth_headers):
        """Test assessment pagination."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = []

            response = client.get(
                "/v1/users/user_123/assessments?limit=10&offset=20",
                headers=auth_headers
            )

            assert response.status_code == 200
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["limit"] == 10
            assert call_kwargs["offset"] == 20

    def test_get_assessments_multiple_filters(self, client: TestClient, auth_headers):
        """Test combining multiple filters."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = []

            response = client.get(
                "/v1/users/user_123/assessments?element=technical_confidence&min_confidence=0.7&limit=5",
                headers=auth_headers
            )

            assert response.status_code == 200
            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["element"] == "technical_confidence"
            assert call_kwargs["min_confidence"] == 0.7
            assert call_kwargs["limit"] == 5

    def test_get_assessments_empty_result(self, client: TestClient, auth_headers):
        """Test retrieving assessments when none exist."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            mock_get.return_value = []

            response = client.get(
                "/v1/users/user_123/assessments",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 0

    @pytest.mark.slow
    def test_assessment_temporal_analysis(self, client: TestClient, auth_headers):
        """Test temporal analysis of assessments."""
        with patch('db.supabase_client.SupabaseClient.get_assessments') as mock_get:
            # Simulate assessments over time showing improvement
            mock_get.return_value = [
                {
                    "id": "assess_1",
                    "element": "technical_confidence",
                    "value_data": {"score": 0.4},
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "assess_2",
                    "element": "technical_confidence",
                    "value_data": {"score": 0.6},
                    "created_at": "2024-01-05T00:00:00Z"
                },
                {
                    "id": "assess_3",
                    "element": "technical_confidence",
                    "value_data": {"score": 0.8},
                    "created_at": "2024-01-10T00:00:00Z"
                }
            ]

            response = client.get(
                "/v1/users/user_123/assessments?element=technical_confidence",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3

            # Verify temporal progression
            scores = [a["value_data"]["score"] for a in data]
            assert scores == [0.4, 0.6, 0.8]  # Improvement over time
