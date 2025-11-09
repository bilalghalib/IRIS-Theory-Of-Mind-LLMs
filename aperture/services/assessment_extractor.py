from typing import List, Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic
import json
from config import settings
from schemas.assessments import ValueType


class AssessmentExtractor:
    """Service for extracting assessments from conversations."""

    def __init__(self):
        # Use internal API keys for assessment extraction
        self.openai_client = None
        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)

        self.anthropic_client = None
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

    async def extract_basic_assessments(
        self,
        user_message: str,
        assistant_response: str,
        conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Extract basic assessments from a conversation turn.

        For MVP, we'll extract:
        - technical_confidence
        - emotional_state
        - help_seeking_behavior

        Returns list of assessment dictionaries ready for DB insertion.
        """
        if not self.openai_client:
            return []

        # Build context
        context = self._build_context(user_message, assistant_response, conversation_history)

        # Call LLM for extraction
        prompt = self._build_extraction_prompt()

        try:
            response = self.openai_client.chat.completions.create(
                model=settings.default_assessment_model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                temperature=settings.assessment_temperature,
                max_tokens=500
            )

            result = json.loads(response.choices[0].message.content)
            assessments = self._format_assessments(result, user_message)
            return assessments

        except Exception as e:
            print(f"Error extracting assessments: {e}")
            return []

    def _build_context(
        self,
        user_message: str,
        assistant_response: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build context string for assessment extraction."""
        context_parts = []

        # Add recent history (last 5 messages)
        if conversation_history:
            context_parts.append("Recent conversation:")
            for msg in conversation_history[-5:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")

        # Add current exchange
        context_parts.append("\nCurrent exchange:")
        context_parts.append(f"user: {user_message}")
        context_parts.append(f"assistant: {assistant_response}")

        return "\n".join(context_parts)

    def _build_extraction_prompt(self) -> str:
        """Build the system prompt for assessment extraction."""
        return """You are an expert at analyzing conversations to extract structured insights about users.

Analyze the conversation and extract the following assessments:

1. **technical_confidence**: How confident does the user seem in their technical abilities?
   - score: 0.0 (very uncertain) to 1.0 (very confident)
   - reasoning: Why you assigned this score
   - evidence: Specific quote from user's message

2. **emotional_state**: What is the user's current emotional state?
   - value: one of ["frustrated", "neutral", "curious", "excited", "confused", "satisfied"]
   - reasoning: Why you chose this emotion
   - evidence: Specific quote from user's message

3. **help_seeking_behavior**: What type of help is the user seeking?
   - value: one of ["step_by_step", "high_level", "troubleshooting", "explanation", "none"]
   - reasoning: Why you identified this behavior
   - evidence: Specific quote from user's message

Return a JSON object in this exact format:
{
  "assessments": [
    {
      "element": "technical_confidence",
      "value_type": "score",
      "value": 0.7,
      "reasoning": "User asks specific questions about deployment, suggesting moderate familiarity",
      "confidence": 0.8,
      "evidence": "I'm trying to deploy this on AWS"
    },
    {
      "element": "emotional_state",
      "value_type": "tag",
      "value": "frustrated",
      "reasoning": "User mentions 'keep getting errors', indicating frustration",
      "confidence": 0.9,
      "evidence": "keep getting errors"
    },
    {
      "element": "help_seeking_behavior",
      "value_type": "tag",
      "value": "troubleshooting",
      "reasoning": "User is trying to solve a specific error",
      "confidence": 0.95,
      "evidence": "I'm trying to deploy this on AWS but keep getting errors"
    }
  ]
}

IMPORTANT:
- Only extract assessments if there's clear evidence in the user's message
- If you can't confidently assess something, omit it from the response
- Keep evidence quotes short and relevant
- Confidence should reflect how certain you are about the assessment"""

    def _format_assessments(
        self,
        extraction_result: Dict,
        user_message: str
    ) -> List[Dict[str, Any]]:
        """Format extracted assessments for database insertion."""
        formatted = []

        for assessment in extraction_result.get("assessments", []):
            # Map value_type string to enum
            value_type = assessment.get("value_type", "text")
            if value_type == "score":
                value_data = {"score": assessment["value"]}
            elif value_type == "tag":
                value_data = {"tag": assessment["value"]}
            elif value_type == "range":
                value_data = {"range": assessment["value"]}
            else:
                value_data = {"text": str(assessment["value"])}

            formatted_assessment = {
                "element": assessment["element"],
                "value_type": value_type,
                "value_data": value_data,
                "reasoning": assessment.get("reasoning", ""),
                "confidence": assessment.get("confidence", 0.5),
                "metadata": {
                    "extraction_model": settings.default_assessment_model,
                    "raw_evidence": assessment.get("evidence", user_message[:200])
                }
            }

            formatted.append(formatted_assessment)

        return formatted

    async def re_analyze_with_correction(
        self,
        assessment_id: str,
        original_assessment: Dict,
        user_correction: Dict,
        evidence_list: List[Dict]
    ) -> Dict[str, Any]:
        """
        Re-analyze an assessment given user correction.

        This updates the assessment based on user feedback.
        """
        if not self.openai_client:
            return original_assessment

        # Build prompt with correction
        prompt = f"""The user has corrected an assessment we made about them.

Original Assessment:
- Element: {original_assessment['element']}
- Value: {original_assessment['value_data']}
- Reasoning: {original_assessment['reasoning']}
- Confidence: {original_assessment['confidence']}

Evidence from conversation:
{json.dumps([e.get('user_message', '') for e in evidence_list[:5]], indent=2)}

User Correction:
- Type: {user_correction.get('correction_type')}
- New Value: {user_correction.get('corrected_value', 'N/A')}
- Explanation: {user_correction.get('user_explanation', 'None provided')}

Based on this correction, provide an updated assessment. Return JSON:
{{
  "value_data": {{"score": 0.5}} or {{"tag": "value"}} etc,
  "reasoning": "Updated reasoning incorporating user feedback",
  "confidence": 0.0-1.0 (lower confidence since user corrected us)
}}"""

        try:
            response = self.openai_client.chat.completions.create(
                model=settings.default_assessment_model,
                messages=[
                    {"role": "system", "content": "You are analyzing user corrections to improve assessment accuracy."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=300
            )

            updated = json.loads(response.choices[0].message.content)
            return updated

        except Exception as e:
            print(f"Error re-analyzing with correction: {e}")
            # Return lower confidence version
            return {
                "confidence": max(0.0, original_assessment['confidence'] - 0.3),
                "reasoning": f"{original_assessment['reasoning']} (User corrected this assessment)"
            }


# Singleton instance
assessment_extractor = AssessmentExtractor()
