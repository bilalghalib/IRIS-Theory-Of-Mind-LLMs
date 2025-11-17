from typing import List, Dict, Any, Optional
from openai import OpenAI
import json
from config import settings
from services.embeddings import embedding_service
from schemas.constructs import ConstructConfig, ConstructElement


class ConstructCreatorService:
    """Service for creating constructs from natural language descriptions."""

    def __init__(self):
        if settings.openai_api_key:
            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None

        # Pre-defined construct templates (marketplace)
        self.templates = [
            {
                "name": "customer_support_tier",
                "description": "Classify customer technical expertise for routing",
                "use_cases": ["customer support", "technical support", "help desk"],
                "elements": [
                    {
                        "name": "expertise_level",
                        "value_type": "tag",
                        "description": "Customer's technical skill level",
                        "possible_values": ["beginner", "intermediate", "advanced", "expert"]
                    },
                    {
                        "name": "self_sufficiency",
                        "value_type": "score",
                        "description": "How independently they can solve problems"
                    }
                ]
            },
            {
                "name": "purchase_intent",
                "description": "Track buyer readiness and qualification (BANT)",
                "use_cases": ["sales", "lead qualification", "enterprise sales"],
                "elements": [
                    {
                        "name": "budget",
                        "value_type": "tag",
                        "description": "Budget availability",
                        "possible_values": ["mentioned", "not_mentioned", "constrained", "flexible"]
                    },
                    {
                        "name": "authority",
                        "value_type": "tag",
                        "description": "Decision-making authority",
                        "possible_values": ["decision_maker", "influencer", "user", "unknown"]
                    },
                    {
                        "name": "need",
                        "value_type": "score",
                        "description": "Urgency and strength of need"
                    },
                    {
                        "name": "timeline",
                        "value_type": "tag",
                        "description": "Purchase timeline",
                        "possible_values": ["immediate", "this_quarter", "exploring", "no_timeline"]
                    }
                ]
            },
            {
                "name": "student_knowledge_tracker",
                "description": "Track student understanding and learning progress",
                "use_cases": ["edtech", "online learning", "tutoring"],
                "elements": [
                    {
                        "name": "topic_understanding",
                        "value_type": "score",
                        "description": "Understanding level for current topic"
                    },
                    {
                        "name": "learning_style",
                        "value_type": "tag",
                        "description": "Preferred learning approach",
                        "possible_values": ["visual", "hands_on", "reading", "discussion", "mixed"]
                    },
                    {
                        "name": "struggle_points",
                        "value_type": "text",
                        "description": "Specific concepts causing difficulty"
                    }
                ]
            },
            {
                "name": "developer_skill_profiler",
                "description": "Track developer skills and technology preferences",
                "use_cases": ["developer tools", "code assistants", "technical education"],
                "elements": [
                    {
                        "name": "programming_languages",
                        "value_type": "tag",
                        "description": "Primary programming languages used",
                        "possible_values": ["python", "javascript", "typescript", "java", "go", "rust", "other"]
                    },
                    {
                        "name": "frameworks",
                        "value_type": "tag",
                        "description": "Frameworks and libraries used"
                    },
                    {
                        "name": "experience_level",
                        "value_type": "tag",
                        "description": "Overall development experience",
                        "possible_values": ["junior", "mid", "senior", "lead"]
                    }
                ]
            }
        ]

    async def create_from_description(
        self,
        description: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Create a construct from a natural language description.

        Args:
            description: What the user wants to track
            user_id: ID of the user creating the construct

        Returns:
            Construct suggestion with similar templates and/or custom config
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        # Step 1: Generate embedding for the description
        description_embedding = await embedding_service.generate_embedding(description)

        # Step 2: Find similar templates
        template_embeddings = []
        for template in self.templates:
            template_text = f"{template['name']} {template['description']} {' '.join(template['use_cases'])}"
            embedding = await embedding_service.generate_embedding(template_text)
            template_embeddings.append({
                **template,
                "embedding": embedding
            })

        similar_templates = await embedding_service.find_similar(
            description_embedding,
            template_embeddings,
            top_k=3,
            min_similarity=0.6
        )

        # Step 3: If good matches found, suggest them
        if similar_templates and similar_templates[0]["similarity"] > 0.75:
            return {
                "match_type": "template",
                "suggested_templates": similar_templates,
                "custom_generated": None,
                "message": "Found similar existing constructs. You can use these as-is or customize them."
            }

        # Step 4: No good match, generate custom construct
        custom_construct = await self._generate_custom_construct(description)

        return {
            "match_type": "custom",
            "suggested_templates": similar_templates if similar_templates else [],
            "custom_generated": custom_construct,
            "message": "Generated a custom construct based on your description."
        }

    async def _generate_custom_construct(self, description: str) -> Dict[str, Any]:
        """
        Generate a custom construct configuration from description.

        Args:
            description: User's description of what they want to track

        Returns:
            Custom construct configuration
        """
        prompt = f"""Create a construct definition for tracking the following:

"{description}"

Generate a complete construct configuration with:
1. A clear, descriptive name (snake_case)
2. Description of what it measures
3. 2-4 elements to track
4. For each element:
   - name (snake_case)
   - value_type (score, tag, range, or text)
   - description
   - If tag or range, suggest possible values
5. Example use cases

Return as JSON:
{{
  "name": "construct_name",
  "description": "What this construct measures",
  "elements": [
    {{
      "name": "element_name",
      "value_type": "score",
      "description": "What this element captures",
      "extraction_prompt": "Instructions for LLM to extract this element",
      "possible_values": ["optional", "list", "for", "tags"]
    }}
  ],
  "use_cases": ["use case 1", "use case 2"],
  "update_frequency": "every_message"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at designing user analytics constructs. Create practical, useful configurations."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=800
            )

            construct_config = json.loads(response.choices[0].message.content)
            construct_config["generated_from"] = description
            construct_config["confidence"] = 0.8  # Confidence in the generated config

            return construct_config

        except Exception as e:
            print(f"Error generating custom construct: {e}")
            raise

    async def validate_construct_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a construct configuration for completeness and correctness.

        Args:
            config: Construct configuration to validate

        Returns:
            Validation result with any issues found
        """
        issues = []
        warnings = []

        # Check required fields
        required_fields = ["name", "description", "elements"]
        for field in required_fields:
            if field not in config:
                issues.append(f"Missing required field: {field}")

        # Validate elements
        if "elements" in config:
            if not isinstance(config["elements"], list):
                issues.append("'elements' must be a list")
            elif len(config["elements"]) == 0:
                issues.append("Construct must have at least one element")
            else:
                for i, element in enumerate(config["elements"]):
                    # Check required element fields
                    if "name" not in element:
                        issues.append(f"Element {i}: missing 'name'")
                    if "value_type" not in element:
                        issues.append(f"Element {i}: missing 'value_type'")
                    elif element["value_type"] not in ["score", "tag", "range", "text"]:
                        issues.append(f"Element {i}: invalid value_type '{element['value_type']}'")

                    # Check for extraction prompt
                    if "extraction_prompt" not in element:
                        warnings.append(f"Element {i} ({element.get('name', 'unnamed')}): no extraction_prompt provided")

        # Check name format
        if "name" in config:
            if not config["name"].replace("_", "").isalnum():
                issues.append("Construct name should be snake_case alphanumeric")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    async def get_templates(
        self,
        search_query: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available construct templates.

        Args:
            search_query: Optional search query
            use_case: Optional use case filter

        Returns:
            List of matching templates
        """
        templates = self.templates.copy()

        # Filter by use case
        if use_case:
            templates = [
                t for t in templates
                if use_case.lower() in [uc.lower() for uc in t.get("use_cases", [])]
            ]

        # Search by query
        if search_query:
            query_lower = search_query.lower()
            templates = [
                t for t in templates
                if query_lower in t["name"].lower()
                or query_lower in t["description"].lower()
                or any(query_lower in uc.lower() for uc in t.get("use_cases", []))
            ]

        return templates


# Singleton instance
construct_creator = ConstructCreatorService()
