"""
Aperture Python SDK

Official Python client for the Aperture API.

Installation:
    pip install aperture-ai

Usage:
    from aperture import Aperture

    client = Aperture(api_key="your-key")

    response = client.send_message(
        user_id="user_123",
        message="Hello!",
        llm_provider="openai",
        llm_api_key="sk-..."
    )
"""

from typing import Optional, Dict, Any, List
import requests
from datetime import datetime


class ApertureError(Exception):
    """Base exception for Aperture SDK."""
    pass


class ApertureAPIError(ApertureError):
    """API returned an error."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class Aperture:
    """
    Aperture API Client

    Args:
        api_key: Your Aperture API key
        base_url: API base URL (default: https://api.aperture.dev)
        timeout: Request timeout in seconds (default: 30)

    Example:
        client = Aperture(api_key="aperture_xxx")

        response = client.send_message(
            user_id="user_123",
            message="I'm deploying on AWS",
            llm_provider="openai",
            llm_api_key="sk-..."
        )

        print(response.response)
        print(response.aperture_link)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.aperture.dev",
        timeout: int = 30
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "X-Aperture-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "aperture-python/0.1.0"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                timeout=self.timeout
            )

            if response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                raise ApertureAPIError(response.status_code, error_detail)

            return response.json()

        except requests.RequestException as e:
            raise ApertureError(f"Request failed: {str(e)}")

    # ==================== Messages ====================

    def send_message(
        self,
        user_id: str,
        message: str,
        llm_provider: str,
        llm_api_key: str,
        conversation_id: Optional[str] = None,
        llm_model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'MessageResponse':
        """
        Send a message through Aperture.

        Args:
            user_id: Your internal user identifier
            message: User's message
            llm_provider: "openai" or "anthropic"
            llm_api_key: Customer's LLM API key
            conversation_id: Optional existing conversation ID
            llm_model: Model to use (defaults based on provider)
            system_prompt: System prompt for the LLM
            temperature: LLM temperature (0.0-2.0)
            max_tokens: Max tokens in response
            metadata: Optional metadata dict

        Returns:
            MessageResponse object with response, link, and metadata

        Example:
            response = client.send_message(
                user_id="user_123",
                message="Help me deploy to AWS",
                llm_provider="openai",
                llm_api_key="sk-..."
            )

            print(f"AI: {response.response}")
            print(f"Why: {response.aperture_link}")
        """
        if not conversation_id:
            # Create conversation first
            conv = self.create_conversation(user_id, metadata or {})
            conversation_id = conv["id"]

        data = {
            "user_id": user_id,
            "message": message,
            "llm_provider": llm_provider,
            "llm_api_key": llm_api_key,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if llm_model:
            data["llm_model"] = llm_model
        if system_prompt:
            data["system_prompt"] = system_prompt
        if metadata:
            data["metadata"] = metadata

        result = self._request(
            "POST",
            f"/v1/conversations/{conversation_id}/messages",
            json=data
        )

        return MessageResponse(result)

    def create_conversation(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new conversation."""
        return self._request(
            "POST",
            "/v1/conversations",
            json={"user_id": user_id, "metadata": metadata or {}}
        )

    # ==================== Assessments ====================

    def get_assessments(
        self,
        user_id: str,
        element: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        limit: int = 50
    ) -> List['Assessment']:
        """
        Get assessments for a user.

        Args:
            user_id: User to query
            element: Filter by element (e.g., "technical_confidence")
            min_confidence: Minimum confidence threshold
            max_confidence: Maximum confidence threshold
            limit: Max results to return

        Returns:
            List of Assessment objects

        Example:
            # Get all assessments
            assessments = client.get_assessments("user_123")

            # Get high-confidence technical assessments
            tech = client.get_assessments(
                "user_123",
                element="technical_confidence",
                min_confidence=0.8
            )
        """
        params = {"limit": limit}
        if element:
            params["element"] = element
        if min_confidence is not None:
            params["min_confidence"] = min_confidence
        if max_confidence is not None:
            params["max_confidence"] = max_confidence

        results = self._request(
            "GET",
            f"/v1/users/{user_id}/assessments",
            params=params
        )

        return [Assessment(a) for a in results]

    def get_assessment(
        self,
        user_id: str,
        assessment_id: str
    ) -> 'AssessmentWithEvidence':
        """Get a specific assessment with evidence."""
        result = self._request(
            "GET",
            f"/v1/users/{user_id}/assessments/{assessment_id}"
        )
        return AssessmentWithEvidence(result)

    def correct_assessment(
        self,
        user_id: str,
        assessment_id: str,
        correction_type: str,
        corrected_value: Optional[Dict] = None,
        user_explanation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit a user correction for an assessment.

        Args:
            user_id: User ID
            assessment_id: Assessment to correct
            correction_type: "wrong_value", "wrong_interpretation", "not_applicable", "other"
            corrected_value: Optional corrected value
            user_explanation: Optional explanation

        Returns:
            Updated assessment
        """
        return self._request(
            "PUT",
            f"/v1/users/{user_id}/assessments/{assessment_id}/correct",
            json={
                "correction_type": correction_type,
                "corrected_value": corrected_value,
                "user_explanation": user_explanation
            }
        )

    # ==================== Pattern Discovery ====================

    def discover_patterns(
        self,
        min_users: int = 10,
        min_occurrence_rate: float = 0.2,
        lookback_days: int = 7
    ) -> Dict[str, Any]:
        """
        Discover common patterns across all users.

        Args:
            min_users: Minimum users that must exhibit pattern
            min_occurrence_rate: Minimum percentage (0.0-1.0)
            lookback_days: Days to analyze

        Returns:
            Discovered patterns with suggestions

        Example:
            patterns = client.discover_patterns(
                min_users=20,
                min_occurrence_rate=0.25
            )

            for pattern in patterns["patterns"]:
                print(f"{pattern['name']}: {pattern['detected_in']}")
        """
        return self._request(
            "POST",
            "/v1/admin/discover-patterns",
            json={
                "min_users": min_users,
                "min_occurrence_rate": min_occurrence_rate,
                "lookback_days": lookback_days
            }
        )

    # ==================== Constructs ====================

    def create_construct_from_description(
        self,
        description: str
    ) -> Dict[str, Any]:
        """
        Create a construct from natural language description.

        Args:
            description: What you want to track (e.g., "purchase intent")

        Returns:
            Suggested templates or generated construct

        Example:
            result = client.create_construct_from_description(
                "I want to track if users are ready to upgrade"
            )

            if result["match_type"] == "template":
                print("Found similar template:")
                print(result["suggested_templates"][0]["name"])
        """
        return self._request(
            "POST",
            "/v1/constructs/from-description",
            json={"description": description}
        )

    def get_construct_templates(
        self,
        search: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Browse construct templates from the marketplace.

        Args:
            search: Search query
            use_case: Filter by use case

        Returns:
            List of templates
        """
        params = {}
        if search:
            params["search"] = search
        if use_case:
            params["use_case"] = use_case

        result = self._request(
            "GET",
            "/v1/constructs/templates",
            params=params
        )
        return result.get("templates", [])

    def validate_construct(
        self,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a construct configuration."""
        return self._request(
            "POST",
            "/v1/constructs/validate",
            json=config
        )


# ==================== Response Objects ====================

class MessageResponse:
    """Response from sending a message."""

    def __init__(self, data: Dict[str, Any]):
        self.conversation_id = data["conversation_id"]
        self.message_id = data["message_id"]
        self.response = data["response"]
        self.aperture_link = data["aperture_link"]
        self.assessment_count = data["assessment_count"]
        self.provider = data["provider"]
        self.model = data["model"]
        self.usage = data.get("usage")
        self._raw = data

    def __repr__(self):
        return f"<MessageResponse conversation_id={self.conversation_id}>"


class Assessment:
    """User assessment with confidence score."""

    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.element = data["element"]
        self.value_type = data["value_type"]
        self.value_data = data["value_data"]
        self.reasoning = data["reasoning"]
        self.confidence = data["confidence"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.user_corrected = data.get("user_corrected", False)
        self.observation_count = data.get("observation_count", 0)
        self._raw = data

    @property
    def value(self):
        """Get the actual value (score, tag, etc.)."""
        if self.value_type == "score":
            return self.value_data.get("score")
        elif self.value_type == "tag":
            return self.value_data.get("tag")
        elif self.value_type == "range":
            return self.value_data.get("range")
        else:
            return self.value_data.get("text")

    def __repr__(self):
        return f"<Assessment {self.element}={self.value} confidence={self.confidence}>"


class AssessmentWithEvidence(Assessment):
    """Assessment with supporting evidence."""

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.evidence = data.get("evidence", [])

    def __repr__(self):
        return f"<Assessment {self.element}={self.value} evidence_count={len(self.evidence)}>"


__version__ = "0.1.0"
__all__ = ["Aperture", "ApertureError", "ApertureAPIError", "MessageResponse", "Assessment", "AssessmentWithEvidence"]
