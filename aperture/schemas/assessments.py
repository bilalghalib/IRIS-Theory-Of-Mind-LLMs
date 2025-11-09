from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from enum import Enum


class ValueType(str, Enum):
    """Type of assessment value."""
    SCORE = "score"  # 0.0 - 1.0
    RANGE = "range"  # e.g., "low", "medium", "high"
    TAG = "tag"  # e.g., "python", "react", "aws"
    TEXT = "text"  # Free-form text


class Evidence(BaseModel):
    """Evidence supporting an assessment."""
    id: str
    assessment_id: str
    user_message: str
    context: Optional[str] = None  # Surrounding conversation context
    timestamp: datetime
    confidence_contribution: float = Field(..., ge=0.0, le=1.0)


class AssessmentCreate(BaseModel):
    """Create a new assessment."""
    user_id: str
    construct_id: Optional[str] = None  # Links to a construct (optional for now)
    element: str = Field(..., description="What aspect is being assessed (e.g., 'technical_confidence')")

    value_type: ValueType
    value_data: Dict[str, Any] = Field(..., description="The actual value (format depends on value_type)")

    reasoning: str = Field(..., description="LLM's explanation for this assessment")
    confidence: float = Field(..., ge=0.0, le=1.0)

    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AssessmentUpdate(BaseModel):
    """Update an existing assessment."""
    value_data: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    user_corrected: Optional[bool] = None


class Assessment(BaseModel):
    """Assessment with all details."""
    id: str
    user_id: str
    construct_id: Optional[str] = None
    element: str

    value_type: ValueType
    value_data: Dict[str, Any]

    reasoning: str
    confidence: float

    created_at: datetime
    updated_at: datetime

    user_corrected: bool = False
    observation_count: int = 0

    metadata: Dict[str, Any]


class AssessmentWithEvidence(Assessment):
    """Assessment with its supporting evidence."""
    evidence: List[Evidence] = []


class AssessmentQuery(BaseModel):
    """Query parameters for filtering assessments."""
    user_id: str
    element: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    user_corrected: Optional[bool] = None
    limit: int = Field(50, ge=1, le=500)


class UserCorrection(BaseModel):
    """User feedback to correct an assessment."""
    correction_type: Literal["wrong_value", "wrong_interpretation", "not_applicable", "other"]
    corrected_value: Optional[Dict[str, Any]] = None
    user_explanation: Optional[str] = None
