from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ConstructType(str, Enum):
    """Pre-defined construct types."""
    THEORY_OF_MIND = "theory_of_mind"
    SKILL_PROFILE = "skill_profile"
    SENTIMENT_TRACKER = "sentiment_tracker"
    PURCHASE_INTENT = "purchase_intent"
    CUSTOM = "custom"


class ConstructElement(BaseModel):
    """Configuration for a single element within a construct."""
    name: str
    description: str
    value_type: str  # "score", "range", "tag", "text"
    extraction_prompt: Optional[str] = None  # Custom prompt for extracting this element


class ConstructConfig(BaseModel):
    """Configuration for how a construct works."""
    elements: List[ConstructElement]
    update_frequency: str = "every_message"  # or "every_3_messages", "daily", etc.
    llm_model: str = "gpt-4o-mini"
    enabled: bool = True


class ConstructCreate(BaseModel):
    """Create a new construct."""
    user_id: str
    type: ConstructType
    name: str = Field(..., description="Human-readable name")
    description: Optional[str] = None
    config: ConstructConfig


class Construct(BaseModel):
    """Full construct definition."""
    id: str
    user_id: str
    type: ConstructType
    name: str
    description: Optional[str]
    config: ConstructConfig
    created_at: datetime
    updated_at: datetime
    assessment_count: int = 0  # How many assessments have been made


class ConstructFromDescription(BaseModel):
    """Natural language request to create a construct."""
    description: str = Field(
        ...,
        description="What you want to track",
        examples=["I want to know if users are ready to upgrade to paid tier"]
    )
