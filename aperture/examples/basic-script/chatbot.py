"""
Basic Aperture Example - Simple Command-Line Chatbot

This example shows the simplest possible integration with Aperture.
A command-line chatbot that builds user understanding over time.
"""

import os
from aperture import Aperture, ApertureAPIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Aperture client
client = Aperture(
    api_key=os.getenv('APERTURE_API_KEY'),
    base_url=os.getenv('APERTURE_BASE_URL', 'https://api.aperture.dev')
)

def main():
    """Run the chatbot."""
    print("🤖 Welcome to Aperture-powered Chatbot!")
    print("=" * 50)
    print("This chatbot builds understanding about you as you chat.")
    print("Type 'quit' to exit, 'insights' to see what I know about you.\n")

    # Simple user ID (in production, use your auth system)
    user_id = input("Enter your name (or user ID): ").strip() or "demo_user"
    print(f"\nHello {user_id}! Let's chat.\n")

    conversation_id = None

    while True:
        # Get user input
        user_message = input("You: ").strip()

        if not user_message:
            continue

        # Handle special commands
        if user_message.lower() == 'quit':
            print("\n👋 Goodbye! Your conversation has been saved.")
            break

        if user_message.lower() == 'insights':
            show_insights(user_id)
            continue

        try:
            # Send message through Aperture
            response = client.send_message(
                user_id=user_id,
                message=user_message,
                conversation_id=conversation_id,
                llm_provider='openai',
                llm_api_key=os.getenv('OPENAI_API_KEY'),
                system_prompt='You are a helpful, friendly assistant.',
                temperature=0.7
            )

            # Save conversation ID for continuity
            if not conversation_id:
                conversation_id = response.conversation_id

            # Display response
            print(f"\nAssistant: {response.response}")

            # Show Aperture link (optional)
            if response.assessment_count > 0:
                print(f"🔍 Why this response: {response.aperture_link}")

            print()

        except ApertureAPIError as e:
            print(f"\n❌ API Error ({e.status_code}): {e.message}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break

        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def show_insights(user_id: str):
    """Show what Aperture knows about the user."""
    print("\n" + "=" * 50)
    print("📊 What I know about you:")
    print("=" * 50)

    try:
        assessments = client.get_assessments(
            user_id=user_id,
            min_confidence=0.5,
            limit=20
        )

        if not assessments:
            print("\nNo insights yet. Keep chatting!")
        else:
            for assessment in assessments:
                print(f"\n🔹 {assessment.element.replace('_', ' ').title()}")
                print(f"   Value: {assessment.value}")
                print(f"   Confidence: {assessment.confidence:.0%}")
                print(f"   Why: {assessment.reasoning[:100]}...")

        print("\n" + "=" * 50 + "\n")

    except ApertureAPIError as e:
        print(f"\n❌ Could not fetch insights: {e.message}\n")


if __name__ == '__main__':
    # Check for required environment variables
    required_vars = ['APERTURE_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease create a .env file with:")
        print("  APERTURE_API_KEY=your_aperture_key")
        print("  OPENAI_API_KEY=your_openai_key")
        exit(1)

    main()
