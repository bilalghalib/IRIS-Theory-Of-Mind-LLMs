from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MessageRequest(BaseModel):
    """Request to send a message through the proxy."""
    user_id: str = Field(..., description="Your internal user identifier")
    message: str = Field(..., description="User's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")

    # LLM Provider config (BYOK - Bring Your Own Key)
    llm_provider: str = Field("openai", description="LLM provider: 'openai' or 'anthropic'")
    llm_api_key: str = Field(..., description="Customer's LLM API key")
    llm_model: Optional[str] = Field(None, description="Model to use (defaults based on provider)")

    # Optional parameters
    system_prompt: Optional[str] = Field(None, description="System prompt for the LLM")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=4096)

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    """Response from the LLM with Aperture enhancements."""
    conversation_id: str
    message_id: str
    response: str

    # Aperture additions
    aperture_link: str = Field(..., description="Short link to 'Why this response?'")
    assessment_count: int = Field(..., description="Number of assessments extracted")

    # LLM metadata
    provider: str
    model: str
    usage: Optional[Dict[str, int]] = None


class ConversationCreate(BaseModel):
    """Create a new conversation."""
    user_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    """Conversation details."""
    id: str
    user_id: str
    created_at: datetime
    message_count: int
    metadata: Dict[str, Any]


class Message(BaseModel):
    """Individual message in a conversation."""
    id: str
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    created_at: datetime
    aperture_link: Optional[str] = None
