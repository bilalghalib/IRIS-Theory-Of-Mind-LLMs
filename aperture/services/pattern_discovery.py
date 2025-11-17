from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from openai import OpenAI
from collections import Counter, defaultdict
import json
from config import settings
from db.supabase_client import db
from services.embeddings import embedding_service


class PatternDiscoveryService:
    """Service for discovering common patterns across user conversations."""

    def __init__(self):
        if settings.openai_api_key:
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.llm_client = None

    async def discover_patterns(
        self,
        min_users: int = 10,
        min_occurrence_rate: float = 0.2,
        lookback_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Discover common patterns across all user conversations.

        Args:
            min_users: Minimum number of users that must exhibit a pattern
            min_occurrence_rate: Minimum percentage of users (0.0-1.0)
            lookback_days: How many days back to analyze

        Returns:
            List of discovered patterns
        """
        # Get all assessments from the past N days
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)

        # This would use the actual DB query in production
        # For now, return structure showing what we'd discover

        print(f"Analyzing assessments from the past {lookback_days} days...")

        # Step 1: Analyze assessment frequency
        element_frequencies = await self._analyze_element_frequencies()

        # Step 2: Cluster similar assessment values
        clustered_patterns = await self._cluster_assessment_values(element_frequencies)

        # Step 3: Generate construct suggestions
        discovered_constructs = await self._generate_construct_suggestions(
            clustered_patterns,
            min_users,
            min_occurrence_rate
        )

        return discovered_constructs

    async def _analyze_element_frequencies(self) -> Dict[str, Any]:
        """
        Analyze which assessment elements appear most frequently across users.

        Returns:
            Dict mapping element names to frequency data
        """
        # In production, this would query the database
        # For demonstration, showing the structure:

        frequencies = {
            "technical_confidence": {
                "total_users": 47,
                "total_assessments": 142,
                "avg_confidence": 0.78,
                "common_values": [0.3, 0.5, 0.7, 0.9]
            },
            "emotional_state": {
                "total_users": 89,
                "total_assessments": 267,
                "avg_confidence": 0.82,
                "common_values": ["frustrated", "curious", "satisfied"]
            },
            "help_seeking_behavior": {
                "total_users": 61,
                "total_assessments": 183,
                "avg_confidence": 0.85,
                "common_values": ["step_by_step", "troubleshooting"]
            }
        }

        return frequencies

    async def _cluster_assessment_values(
        self,
        frequencies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Cluster similar assessment values to find common patterns.

        Args:
            frequencies: Element frequency data

        Returns:
            List of clustered patterns
        """
        clusters = []

        for element, data in frequencies.items():
            # For each element, look for patterns in the values
            if data["total_users"] < 10:
                continue

            clusters.append({
                "element": element,
                "user_count": data["total_users"],
                "occurrence_rate": data["total_users"] / 100,  # Assuming 100 total users
                "avg_confidence": data["avg_confidence"],
                "common_values": data["common_values"]
            })

        return clusters

    async def _generate_construct_suggestions(
        self,
        patterns: List[Dict[str, Any]],
        min_users: int,
        min_occurrence_rate: float
    ) -> List[Dict[str, Any]]:
        """
        Generate construct suggestions from discovered patterns.

        Args:
            patterns: Clustered patterns
            min_users: Minimum user threshold
            min_occurrence_rate: Minimum occurrence rate

        Returns:
            List of construct suggestions
        """
        if not self.llm_client:
            return []

        suggestions = []

        for pattern in patterns:
            if pattern["user_count"] < min_users:
                continue
            if pattern["occurrence_rate"] < min_occurrence_rate:
                continue

            # Use LLM to generate construct suggestion
            prompt = f"""Based on this discovered pattern in user conversations, suggest a construct definition.

Pattern:
- Element: {pattern['element']}
- Found in {pattern['user_count']} users ({pattern['occurrence_rate']*100:.1f}%)
- Average confidence: {pattern['avg_confidence']}
- Common values: {pattern['common_values']}

Generate a construct suggestion with:
1. A descriptive name
2. What this measures/tracks
3. Why it's valuable
4. Suggested element configuration

Return as JSON:
{{
  "name": "construct_name",
  "description": "What this measures",
  "value_proposition": "Why operators should track this",
  "elements": [
    {{
      "name": "element_name",
      "value_type": "score|tag|range|text",
      "description": "What this element captures"
    }}
  ],
  "example_use_cases": ["use case 1", "use case 2"]
}}
"""

            try:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing user behavior patterns."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=500
                )

                suggestion = json.loads(response.choices[0].message.content)
                suggestion["detected_in"] = f"{pattern['user_count']} users ({pattern['occurrence_rate']*100:.0f}%)"
                suggestion["confidence"] = pattern["avg_confidence"]
                suggestion["sample_values"] = pattern["common_values"]

                suggestions.append(suggestion)

            except Exception as e:
                print(f"Error generating suggestion for {pattern['element']}: {e}")
                continue

        return suggestions

    async def analyze_user_messages_for_patterns(
        self,
        user_messages: List[str],
        existing_elements: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Analyze user messages to suggest additional elements to track.

        Args:
            user_messages: List of recent user messages
            existing_elements: Elements already being tracked

        Returns:
            Suggested new elements
        """
        if not self.llm_client or not user_messages:
            return []

        # Take sample of messages
        sample_messages = user_messages[:20]
        messages_text = "\n".join([f"- {msg}" for msg in sample_messages])

        prompt = f"""Analyze these user messages and identify potential new elements to track beyond what's already tracked.

Currently tracking: {', '.join(existing_elements)}

User messages:
{messages_text}

Identify 2-3 new elements that would be valuable to track. For each:
1. What you'd call it
2. What type of value (score, tag, range, text)
3. Why it would be valuable
4. Example values you see in the messages

Return as JSON array of suggestions.
"""

        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing conversations for patterns."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("suggestions", [])

        except Exception as e:
            print(f"Error analyzing messages: {e}")
            return []

    async def find_correlations(
        self,
        assessments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find correlations between different assessment types.

        Args:
            assessments: List of assessments for a user

        Returns:
            List of detected correlations
        """
        # Group assessments by element
        by_element = defaultdict(list)
        for assessment in assessments:
            by_element[assessment["element"]].append(assessment)

        correlations = []

        # Simple correlation detection
        # In production, use proper statistical methods
        if "emotional_state" in by_element and "help_seeking_behavior" in by_element:
            emotional_values = [a["value_data"] for a in by_element["emotional_state"]]
            help_values = [a["value_data"] for a in by_element["help_seeking_behavior"]]

            # Example: Frustrated users often seek step-by-step help
            frustrated_count = sum(1 for v in emotional_values if v.get("tag") == "frustrated")
            step_by_step_count = sum(1 for v in help_values if v.get("tag") == "step_by_step")

            if frustrated_count > 0 and step_by_step_count > 0:
                correlation_strength = min(frustrated_count, step_by_step_count) / max(frustrated_count, step_by_step_count)

                if correlation_strength > 0.6:
                    correlations.append({
                        "element1": "emotional_state",
                        "value1": "frustrated",
                        "element2": "help_seeking_behavior",
                        "value2": "step_by_step",
                        "strength": correlation_strength,
                        "insight": "Frustrated users tend to need step-by-step guidance"
                    })

        return correlations


# Singleton instance
pattern_discovery = PatternDiscoveryService()
