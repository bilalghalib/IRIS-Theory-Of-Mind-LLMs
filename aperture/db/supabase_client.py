from supabase import create_client, Client
from config import settings
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class SupabaseService:
    """Service for interacting with Supabase database."""

    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Use service key for backend operations
        )

    # ==================== USERS ====================

    async def get_or_create_user(self, external_id: str, metadata: Optional[Dict] = None) -> Dict:
        """Get existing user or create new one."""
        # Check if user exists
        result = self.client.table("users").select("*").eq("external_id", external_id).execute()

        if result.data:
            return result.data[0]

        # Create new user
        user_data = {
            "external_id": external_id,
            "metadata": metadata or {}
        }
        result = self.client.table("users").insert(user_data).execute()
        return result.data[0]

    # ==================== CONVERSATIONS ====================

    async def create_conversation(self, user_id: str, metadata: Optional[Dict] = None) -> Dict:
        """Create a new conversation."""
        conv_data = {
            "user_id": user_id,
            "metadata": metadata or {}
        }
        result = self.client.table("conversations").insert(conv_data).execute()
        return result.data[0]

    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get conversation by ID."""
        result = self.client.table("conversations").select("*").eq("id", conversation_id).execute()
        return result.data[0] if result.data else None

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        aperture_link: Optional[str] = None
    ) -> Dict:
        """Add a message to a conversation."""
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "aperture_link": aperture_link
        }
        result = self.client.table("messages").insert(message_data).execute()
        return result.data[0]

    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a conversation."""
        result = (
            self.client.table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return result.data

    # ==================== ASSESSMENTS ====================

    async def create_assessment(self, assessment_data: Dict) -> Dict:
        """Create a new assessment."""
        result = self.client.table("assessments").insert(assessment_data).execute()
        return result.data[0]

    async def update_assessment(self, assessment_id: str, updates: Dict) -> Dict:
        """Update an existing assessment."""
        updates["updated_at"] = datetime.utcnow().isoformat()
        result = (
            self.client.table("assessments")
            .update(updates)
            .eq("id", assessment_id)
            .execute()
        )
        return result.data[0] if result.data else None

    async def get_assessments(
        self,
        user_id: str,
        element: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Query assessments for a user."""
        query = self.client.table("assessments").select("*").eq("user_id", user_id)

        if element:
            query = query.eq("element", element)
        if min_confidence is not None:
            query = query.gte("confidence", min_confidence)
        if max_confidence is not None:
            query = query.lte("confidence", max_confidence)

        result = query.order("updated_at", desc=True).limit(limit).execute()
        return result.data

    async def get_assessment_by_id(self, assessment_id: str) -> Optional[Dict]:
        """Get a specific assessment."""
        result = self.client.table("assessments").select("*").eq("id", assessment_id).execute()
        return result.data[0] if result.data else None

    # ==================== EVIDENCE ====================

    async def add_evidence(
        self,
        assessment_id: str,
        user_message: str,
        context: Optional[str] = None,
        confidence_contribution: float = 0.5
    ) -> Dict:
        """Add evidence to an assessment."""
        evidence_data = {
            "assessment_id": assessment_id,
            "user_message": user_message,
            "context": context,
            "confidence_contribution": confidence_contribution
        }
        result = self.client.table("evidence").insert(evidence_data).execute()
        return result.data[0]

    async def get_evidence_for_assessment(self, assessment_id: str) -> List[Dict]:
        """Get all evidence for an assessment."""
        result = (
            self.client.table("evidence")
            .select("*")
            .eq("assessment_id", assessment_id)
            .order("timestamp", desc=True)
            .execute()
        )
        return result.data

    # ==================== CONSTRUCTS ====================

    async def create_construct(self, construct_data: Dict) -> Dict:
        """Create a new construct."""
        result = self.client.table("constructs").insert(construct_data).execute()
        return result.data[0]

    async def get_user_constructs(self, user_id: str) -> List[Dict]:
        """Get all constructs for a user."""
        result = (
            self.client.table("constructs")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return result.data

    # ==================== RESPONSE TRACKING (for short links) ====================

    async def create_response_record(
        self,
        short_id: str,
        conversation_id: str,
        message_id: str,
        assessment_ids: List[str]
    ) -> Dict:
        """Create a record for tracking 'Why this response?' links."""
        record_data = {
            "short_id": short_id,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "assessment_ids": assessment_ids
        }
        result = self.client.table("response_tracking").insert(record_data).execute()
        return result.data[0]

    async def get_response_record(self, short_id: str) -> Optional[Dict]:
        """Get response tracking data by short ID."""
        result = (
            self.client.table("response_tracking")
            .select("*")
            .eq("short_id", short_id)
            .execute()
        )
        return result.data[0] if result.data else None


# Singleton instance
db = SupabaseService()
