from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import asyncio

from config import settings
from schemas import (
    MessageRequest,
    MessageResponse,
    ConversationCreate,
    ConversationResponse,
    Assessment,
    AssessmentWithEvidence,
    AssessmentQuery,
    UserCorrection,
    ConstructCreate,
    Construct
)
from db.supabase_client import db
from services.llm_proxy import llm_proxy
from services.assessment_extractor import assessment_extractor
from services.short_link import generate_short_id, create_aperture_link, create_embedded_footer

app = FastAPI(
    title="Aperture API",
    description="User Intelligence Middleware for AI Applications",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates for web UI
templates = Jinja2Templates(directory="web/templates")


# ==================== AUTH MIDDLEWARE ====================

async def verify_api_key(x_aperture_api_key: str = Header(...)):
    """Verify the Aperture API key."""
    # For MVP, simple key check. Later: JWT, rate limiting, etc.
    if x_aperture_api_key != settings.aperture_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_aperture_api_key


# ==================== CORE ENDPOINTS ====================

@app.post("/v1/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: MessageRequest,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    """
    Send a message through the Aperture proxy.

    This is the main endpoint that:
    1. Forwards the message to the LLM provider
    2. Extracts assessments in the background
    3. Returns the response with Aperture metadata
    """
    await verify_api_key(api_key)

    # Get or create user
    user = await db.get_or_create_user(request.user_id)

    # Get or create conversation
    conversation = await db.get_conversation(conversation_id)
    if not conversation:
        conversation = await db.create_conversation(
            user_id=user["id"],
            metadata=request.metadata
        )

    # Get conversation history
    history = await db.get_conversation_messages(conversation["id"])
    formatted_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]

    # Add current user message to history
    formatted_history.append({"role": "user", "content": request.message})

    # Forward to LLM provider
    try:
        response_text, llm_metadata = await llm_proxy.send_message(
            provider=request.llm_provider,
            api_key=request.llm_api_key,
            messages=formatted_history,
            model=request.llm_model,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM provider error: {str(e)}")

    # Generate short link
    short_id = generate_short_id()
    aperture_link = create_aperture_link(short_id)

    # Store user message
    user_msg = await db.add_message(
        conversation_id=conversation["id"],
        role="user",
        content=request.message
    )

    # Store assistant message with Aperture link
    assistant_msg = await db.add_message(
        conversation_id=conversation["id"],
        role="assistant",
        content=response_text,
        aperture_link=aperture_link
    )

    # Extract assessments in background (async)
    asyncio.create_task(
        extract_and_store_assessments(
            user_id=user["id"],
            user_message=request.message,
            assistant_response=response_text,
            conversation_history=formatted_history[:-1],  # Exclude current message
            short_id=short_id,
            conversation_id=conversation["id"],
            message_id=assistant_msg["id"]
        )
    )

    # Return response (with embedded footer if desired)
    # For now, we'll keep response clean and provide link separately
    return MessageResponse(
        conversation_id=conversation["id"],
        message_id=assistant_msg["id"],
        response=response_text,
        aperture_link=aperture_link,
        assessment_count=0,  # Will be updated async
        provider=llm_metadata["provider"],
        model=llm_metadata["model"],
        usage=llm_metadata.get("usage")
    )


async def extract_and_store_assessments(
    user_id: str,
    user_message: str,
    assistant_response: str,
    conversation_history: List[dict],
    short_id: str,
    conversation_id: str,
    message_id: str
):
    """Background task to extract and store assessments."""
    try:
        # Extract assessments
        assessments = await assessment_extractor.extract_basic_assessments(
            user_message=user_message,
            assistant_response=assistant_response,
            conversation_history=conversation_history
        )

        assessment_ids = []

        # Store each assessment
        for assessment_data in assessments:
            # Check if similar assessment exists
            existing = await db.get_assessments(
                user_id=user_id,
                element=assessment_data["element"],
                limit=1
            )

            if existing:
                # Update existing assessment
                existing_assessment = existing[0]
                updated = await db.update_assessment(
                    assessment_id=existing_assessment["id"],
                    updates={
                        "value_data": assessment_data["value_data"],
                        "reasoning": assessment_data["reasoning"],
                        "confidence": assessment_data["confidence"],
                        "observation_count": existing_assessment.get("observation_count", 1) + 1
                    }
                )
                assessment_id = existing_assessment["id"]
            else:
                # Create new assessment
                assessment_data["user_id"] = user_id
                created = await db.create_assessment(assessment_data)
                assessment_id = created["id"]

            # Add evidence
            await db.add_evidence(
                assessment_id=assessment_id,
                user_message=user_message,
                context=assistant_response[:200],
                confidence_contribution=assessment_data["confidence"]
            )

            assessment_ids.append(assessment_id)

        # Store response tracking
        await db.create_response_record(
            short_id=short_id,
            conversation_id=conversation_id,
            message_id=message_id,
            assessment_ids=assessment_ids
        )

    except Exception as e:
        print(f"Error in background assessment extraction: {e}")


@app.post("/v1/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    """Create a new conversation."""
    await verify_api_key(api_key)

    user = await db.get_or_create_user(request.user_id)
    conversation = await db.create_conversation(
        user_id=user["id"],
        metadata=request.metadata
    )

    return ConversationResponse(
        id=conversation["id"],
        user_id=user["external_id"],
        created_at=conversation["created_at"],
        message_count=0,
        metadata=conversation["metadata"]
    )


# ==================== ASSESSMENT ENDPOINTS ====================

@app.get("/v1/users/{user_id}/assessments", response_model=List[Assessment])
async def get_assessments(
    user_id: str,
    element: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    limit: int = 50,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    """Query assessments for a user."""
    await verify_api_key(api_key)

    user = await db.get_or_create_user(user_id)

    assessments = await db.get_assessments(
        user_id=user["id"],
        element=element,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        limit=limit
    )

    return assessments


@app.get("/v1/users/{user_id}/assessments/{assessment_id}", response_model=AssessmentWithEvidence)
async def get_assessment_with_evidence(
    user_id: str,
    assessment_id: str,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    """Get a specific assessment with all its evidence."""
    await verify_api_key(api_key)

    assessment = await db.get_assessment_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    evidence = await db.get_evidence_for_assessment(assessment_id)

    return AssessmentWithEvidence(**assessment, evidence=evidence)


@app.put("/v1/users/{user_id}/assessments/{assessment_id}/correct")
async def correct_assessment(
    user_id: str,
    assessment_id: str,
    correction: UserCorrection,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    """User correction of an assessment."""
    await verify_api_key(api_key)

    # Get assessment
    assessment = await db.get_assessment_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Get evidence
    evidence = await db.get_evidence_for_assessment(assessment_id)

    # Re-analyze with correction
    updated_data = await assessment_extractor.re_analyze_with_correction(
        assessment_id=assessment_id,
        original_assessment=assessment,
        user_correction=correction.dict(),
        evidence_list=evidence
    )

    # Update assessment
    updates = {
        "user_corrected": True,
        **updated_data
    }

    updated_assessment = await db.update_assessment(assessment_id, updates)

    return {"status": "corrected", "assessment": updated_assessment}


# ==================== WEB UI ENDPOINTS ====================

@app.get("/c/{short_id}", response_class=HTMLResponse)
async def why_this_response(short_id: str, request: Request):
    """Show 'Why this response?' page."""
    # Get response tracking data
    tracking = await db.get_response_record(short_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Response not found")

    # Get assessments used for this response
    assessments_data = []
    for assessment_id in tracking.get("assessment_ids", []):
        assessment = await db.get_assessment_by_id(assessment_id)
        if assessment:
            evidence = await db.get_evidence_for_assessment(assessment_id)
            assessment["evidence"] = evidence
            assessments_data.append(assessment)

    # Get the message
    message = await db.get_conversation_messages(tracking["conversation_id"], limit=100)
    target_msg = next((m for m in message if m["id"] == tracking["message_id"]), None)

    return templates.TemplateResponse(
        "why_response.html",
        {
            "request": request,
            "short_id": short_id,
            "message": target_msg,
            "assessments": assessments_data
        }
    )


@app.get("/c/{short_id}/edit", response_class=HTMLResponse)
async def edit_understanding(short_id: str, request: Request):
    """Show correction form."""
    tracking = await db.get_response_record(short_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Response not found")

    assessments_data = []
    for assessment_id in tracking.get("assessment_ids", []):
        assessment = await db.get_assessment_by_id(assessment_id)
        if assessment:
            assessments_data.append(assessment)

    return templates.TemplateResponse(
        "edit_understanding.html",
        {
            "request": request,
            "short_id": short_id,
            "assessments": assessments_data
        }
    )


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Aperture API",
        "tagline": "User Intelligence Middleware for AI Applications",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
