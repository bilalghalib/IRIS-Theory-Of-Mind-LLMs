# Aperture Python SDK

Official Python client for the Aperture API - User Intelligence for AI Applications.

[![PyPI version](https://badge.fury.io/py/aperture-ai.svg)](https://badge.fury.io/py/aperture-ai)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Installation

```bash
pip install aperture-ai
```

## Quick Start

```python
from aperture import Aperture

# Initialize client
client = Aperture(api_key="your-aperture-key")

# Send a message through Aperture
response = client.send_message(
    user_id="user_123",
    message="I'm trying to deploy my app on AWS but keep getting errors",
    llm_provider="openai",
    llm_api_key="sk-your-openai-key"
)

# Access the response
print(f"AI: {response.response}")
print(f"Why this response: {response.aperture_link}")
print(f"Assessments extracted: {response.assessment_count}")
```

## Features

- 🔌 **LLM Proxy** - Works with OpenAI and Anthropic
- 🧠 **Auto-Assessments** - Extracts user insights automatically
- 📊 **Pattern Discovery** - Find common patterns across users
- 🗣️ **Natural Language** - Create constructs from descriptions
- 📚 **Marketplace** - Pre-built construct templates

## Usage Examples

### Basic Conversation

```python
from aperture import Aperture

client = Aperture(api_key="aperture_xxx")

# Create conversation
conversation = client.create_conversation(
    user_id="user_123",
    metadata={"source": "web_app"}
)

# Send messages
response = client.send_message(
    user_id="user_123",
    message="How do I deploy to AWS?",
    conversation_id=conversation["id"],
    llm_provider="openai",
    llm_api_key="sk-...",
    system_prompt="You are a helpful DevOps assistant"
)

print(response.response)
```

### Query User Assessments

```python
# Get all assessments for a user
assessments = client.get_assessments("user_123")

for assessment in assessments:
    print(f"{assessment.element}: {assessment.value}")
    print(f"Confidence: {assessment.confidence}")
    print(f"Reasoning: {assessment.reasoning}")
    print()

# Filter by element
technical = client.get_assessments(
    "user_123",
    element="technical_confidence",
    min_confidence=0.7
)

# Get assessment with evidence
detail = client.get_assessment("user_123", assessment.id)
for evidence in detail.evidence:
    print(f"User said: {evidence['user_message']}")
```

### Pattern Discovery

```python
# Discover patterns across all users
patterns = client.discover_patterns(
    min_users=10,
    min_occurrence_rate=0.2,
    lookback_days=7
)

print(f"Found {patterns['patterns_found']} patterns")

for pattern in patterns["patterns"]:
    print(f"Pattern: {pattern['name']}")
    print(f"Found in: {pattern['detected_in']}")
    print(f"Confidence: {pattern['confidence']}")
    print()
```

### Natural Language Constructs

```python
# Create construct from description
result = client.create_construct_from_description(
    "I want to track if users are ready to upgrade to paid tier"
)

if result["match_type"] == "template":
    print("Found similar templates:")
    for template in result["suggested_templates"]:
        print(f"- {template['name']} (similarity: {template['similarity']})")
else:
    print("Generated custom construct:")
    print(result["custom_generated"])
```

### Browse Marketplace

```python
# Get all templates
templates = client.get_construct_templates()

for template in templates:
    print(f"{template['name']}: {template['description']}")

# Search templates
support_templates = client.get_construct_templates(
    use_case="customer support"
)
```

### User Corrections

```python
# Submit a correction
client.correct_assessment(
    user_id="user_123",
    assessment_id="assess_456",
    correction_type="wrong_value",
    user_explanation="I'm actually very confident with AWS"
)
```

## API Reference

### `Aperture(api_key, base_url="https://api.aperture.dev")`

Initialize the client.

**Parameters:**
- `api_key` (str): Your Aperture API key
- `base_url` (str, optional): API base URL
- `timeout` (int, optional): Request timeout in seconds (default: 30)

### `send_message(**kwargs)`

Send a message through Aperture.

**Parameters:**
- `user_id` (str): Your internal user identifier
- `message` (str): User's message
- `llm_provider` (str): "openai" or "anthropic"
- `llm_api_key` (str): Customer's LLM API key
- `conversation_id` (str, optional): Existing conversation ID
- `llm_model` (str, optional): Model to use
- `system_prompt` (str, optional): System prompt
- `temperature` (float, optional): LLM temperature (default: 0.7)
- `max_tokens` (int, optional): Max tokens (default: 1000)
- `metadata` (dict, optional): Optional metadata

**Returns:** `MessageResponse` object

### `get_assessments(user_id, **kwargs)`

Get assessments for a user.

**Parameters:**
- `user_id` (str): User to query
- `element` (str, optional): Filter by element
- `min_confidence` (float, optional): Minimum confidence
- `max_confidence` (float, optional): Maximum confidence
- `limit` (int, optional): Max results (default: 50)

**Returns:** List of `Assessment` objects

### `get_assessment(user_id, assessment_id)`

Get specific assessment with evidence.

**Returns:** `AssessmentWithEvidence` object

### `discover_patterns(**kwargs)`

Discover patterns across users.

**Parameters:**
- `min_users` (int, optional): Minimum users (default: 10)
- `min_occurrence_rate` (float, optional): Minimum rate (default: 0.2)
- `lookback_days` (int, optional): Days to analyze (default: 7)

**Returns:** Dict with discovered patterns

### `create_construct_from_description(description)`

Create construct from natural language.

**Parameters:**
- `description` (str): What you want to track

**Returns:** Dict with suggestions or generated config

### `get_construct_templates(**kwargs)`

Browse marketplace templates.

**Parameters:**
- `search` (str, optional): Search query
- `use_case` (str, optional): Filter by use case

**Returns:** List of templates

## Response Objects

### `MessageResponse`

Response from sending a message.

**Attributes:**
- `conversation_id` - Conversation ID
- `message_id` - Message ID
- `response` - LLM's response text
- `aperture_link` - Link to "Why this response?"
- `assessment_count` - Number of assessments extracted
- `provider` - LLM provider used
- `model` - Model used
- `usage` - Token usage stats

### `Assessment`

User assessment with confidence score.

**Attributes:**
- `id` - Assessment ID
- `user_id` - User ID
- `element` - Element name (e.g., "technical_confidence")
- `value_type` - Type: "score", "tag", "range", or "text"
- `value_data` - The actual value
- `value` - Convenience property to get the value
- `reasoning` - LLM's explanation
- `confidence` - Confidence score (0.0-1.0)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `user_corrected` - Whether user corrected this
- `observation_count` - Number of times observed

### `AssessmentWithEvidence`

Assessment with supporting evidence (extends `Assessment`).

**Additional Attributes:**
- `evidence` - List of evidence records with user quotes

## Error Handling

```python
from aperture import Aperture, ApertureError, ApertureAPIError

client = Aperture(api_key="your-key")

try:
    response = client.send_message(...)
except ApertureAPIError as e:
    print(f"API error {e.status_code}: {e.message}")
except ApertureError as e:
    print(f"SDK error: {e}")
```

## Configuration

### Environment Variables

You can set your API key via environment variable:

```bash
export APERTURE_API_KEY="your-key"
```

```python
import os
from aperture import Aperture

client = Aperture(api_key=os.getenv("APERTURE_API_KEY"))
```

### Custom Base URL

For self-hosted or development:

```python
client = Aperture(
    api_key="your-key",
    base_url="http://localhost:8000"
)
```

## Best Practices

### 1. Reuse Client Instance

```python
# Good: Create once, reuse
client = Aperture(api_key="...")

for user_message in messages:
    response = client.send_message(...)

# Bad: Creating new client each time
for user_message in messages:
    client = Aperture(api_key="...")  # Don't do this
    response = client.send_message(...)
```

### 2. Handle Errors Gracefully

```python
try:
    response = client.send_message(...)
except ApertureAPIError as e:
    if e.status_code == 429:
        # Rate limited - wait and retry
        time.sleep(60)
        response = client.send_message(...)
    else:
        # Log error and use fallback
        logger.error(f"Aperture error: {e}")
        response = fallback_llm_call(...)
```

### 3. Use Metadata for Context

```python
response = client.send_message(
    user_id="user_123",
    message="...",
    metadata={
        "source": "web_app",
        "session_id": "sess_789",
        "user_agent": "Mozilla/5.0...",
        "experiment": "variant_a"
    }
)
```

### 4. Query Assessments Efficiently

```python
# Get only what you need
recent_high_confidence = client.get_assessments(
    user_id="user_123",
    min_confidence=0.8,
    limit=10
)

# Check specific elements before making decisions
technical = client.get_assessments(
    user_id="user_123",
    element="technical_confidence"
)

if technical and technical[0].value < 0.5:
    # Route to beginner-friendly support
    pass
```

## Examples

See the `/examples` directory for:
- Flask integration
- FastAPI integration
- Next.js integration
- Streamlit chatbot
- Customer support router

## Support

- **Documentation:** https://docs.aperture.dev
- **GitHub Issues:** https://github.com/yourusername/aperture/issues
- **Discord:** [Join our community](#)
- **Email:** hello@aperture.dev

## License

MIT License - see LICENSE file for details

---

**Built with ❤️ by Aperture**

*Turn conversations into intelligence*
