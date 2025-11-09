"""
Example client application demonstrating Aperture API usage.

This simulates a simple chat application that uses Aperture
to proxy LLM calls and automatically build user profiles.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
APERTURE_BASE_URL = "http://localhost:8000"
APERTURE_API_KEY = os.getenv("APERTURE_API_KEY", "your-secret-api-key-for-testing")
USER_ID = "demo_user_001"
LLM_PROVIDER = "openai"  # or "anthropic"
LLM_API_KEY = os.getenv("OPENAI_API_KEY")  # Customer's own key
LLM_MODEL = "gpt-4o-mini"


class ApertureClient:
    """Simple client for interacting with Aperture API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {
            "X-Aperture-API-Key": api_key,
            "Content-Type": "application/json"
        }
        self.conversation_id = None

    def create_conversation(self, user_id: str):
        """Create a new conversation."""
        response = requests.post(
            f"{self.base_url}/v1/conversations",
            headers=self.headers,
            json={"user_id": user_id, "metadata": {}}
        )
        response.raise_for_status()
        data = response.json()
        self.conversation_id = data["id"]
        return data

    def send_message(
        self,
        user_id: str,
        message: str,
        llm_provider: str,
        llm_api_key: str,
        llm_model: str = None,
        system_prompt: str = None
    ):
        """Send a message through Aperture."""
        if not self.conversation_id:
            self.create_conversation(user_id)

        response = requests.post(
            f"{self.base_url}/v1/conversations/{self.conversation_id}/messages",
            headers=self.headers,
            json={
                "user_id": user_id,
                "message": message,
                "llm_provider": llm_provider,
                "llm_api_key": llm_api_key,
                "llm_model": llm_model,
                "system_prompt": system_prompt,
                "temperature": 0.7,
                "max_tokens": 500
            }
        )
        response.raise_for_status()
        return response.json()

    def get_assessments(self, user_id: str, element: str = None):
        """Get assessments for a user."""
        params = {}
        if element:
            params["element"] = element

        response = requests.get(
            f"{self.base_url}/v1/users/{user_id}/assessments",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()


def main():
    """Demo conversation with Aperture."""
    print("🔍 Aperture API Demo\n")

    if not LLM_API_KEY:
        print("❌ Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env")
        return

    client = ApertureClient(APERTURE_BASE_URL, APERTURE_API_KEY)

    # System prompt
    system_prompt = "You are a helpful AI assistant specializing in software development."

    # Simulated conversation
    messages = [
        "Hi! I'm trying to deploy my React app to AWS but I keep getting CORS errors.",
        "I'm not very familiar with AWS. Can you explain step by step?",
        "That's helpful! I'm feeling more confident now. Let me try that.",
    ]

    print(f"User: {USER_ID}")
    print(f"Provider: {LLM_PROVIDER}\n")
    print("-" * 60)

    for user_message in messages:
        print(f"\n💬 USER: {user_message}\n")

        # Send message through Aperture
        response = client.send_message(
            user_id=USER_ID,
            message=user_message,
            llm_provider=LLM_PROVIDER,
            llm_api_key=LLM_API_KEY,
            llm_model=LLM_MODEL,
            system_prompt=system_prompt
        )

        print(f"🤖 ASSISTANT: {response['response']}\n")
        print(f"🔗 Aperture Link: {response['aperture_link']}")
        print(f"📊 Model: {response['model']}")

        if response.get("usage"):
            print(f"📈 Tokens: {response['usage']['total_tokens']}")

        print("-" * 60)

    # Wait a moment for background assessment extraction
    print("\n⏳ Waiting for assessments to be extracted...")
    import time
    time.sleep(3)

    # Fetch assessments
    print("\n📊 User Assessments:\n")
    assessments = client.get_assessments(USER_ID)

    if assessments:
        for assessment in assessments:
            element = assessment["element"].replace("_", " ").title()
            confidence = int(assessment["confidence"] * 100)

            value_str = ""
            if assessment["value_type"] == "score":
                value_str = f"{int(assessment['value_data']['score'] * 100)}/100"
            elif assessment["value_type"] == "tag":
                value_str = assessment["value_data"]["tag"]

            print(f"✓ {element}: {value_str} ({confidence}% confident)")
            print(f"  Reason: {assessment['reasoning']}")
            print(f"  Observed: {assessment['observation_count']} time(s)")
            print()
    else:
        print("No assessments extracted yet. They may still be processing.")

    print("\n✨ Demo complete! Check the Aperture links to see 'Why this response?'\n")


if __name__ == "__main__":
    main()
