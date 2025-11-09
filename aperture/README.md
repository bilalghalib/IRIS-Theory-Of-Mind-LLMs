# Aperture 🔍

**User Intelligence Middleware for AI Applications**

Aperture sits between your app and any LLM, automatically building structured, explainable user profiles from natural conversations. Get confidence-scored assessments, evidence trails, and temporal analytics without changing your chat UI.

## ✨ Features

- **LLM Proxy**: Works with OpenAI and Anthropic (bring your own API keys)
- **Auto-Assessment Extraction**: Tracks technical confidence, emotional state, help-seeking behavior, and more
- **Evidence-Based**: Every assessment is backed by actual user quotes
- **Confidence Scoring**: Know how certain each assessment is (0.0 - 1.0)
- **User Corrections**: Users can correct misunderstandings, improving accuracy over time
- **Explainable**: "Why this response?" links show users what you understand about them
- **Temporal Tracking**: Watch how user attributes change over time
- **Multi-Tenant Ready**: Built for SaaS from day one

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+
- Supabase account (free tier works)
- OpenAI or Anthropic API key (for assessment extraction)

### 2. Setup Supabase

1. Create a new Supabase project
2. Run the schema in `/db/schema.sql` in the SQL Editor
3. Get your project URL and API keys

### 3. Install Dependencies

```bash
cd aperture
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon key
- `SUPABASE_SERVICE_KEY`: Your Supabase service key
- `OPENAI_API_KEY`: For assessment extraction (internal use)
- `APERTURE_API_KEY`: Your chosen API key for customers

### 5. Run the Server

```bash
python main.py
```

Server runs on `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

## 📡 API Usage

### Send a Message (Main Endpoint)

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/conversations/conv_123/messages",
    headers={
        "X-Aperture-API-Key": "your-aperture-key",
        "Content-Type": "application/json"
    },
    json={
        "user_id": "user_456",
        "message": "I'm trying to deploy my app on AWS but keep getting errors",
        "llm_provider": "openai",
        "llm_api_key": "sk-your-openai-key",
        "llm_model": "gpt-4o-mini",
        "system_prompt": "You are a helpful assistant."
    }
)

data = response.json()
print(data["response"])  # LLM's response
print(data["aperture_link"])  # Link to "Why this response?"
```

### Query Assessments

```python
# Get all assessments for a user
assessments = requests.get(
    "http://localhost:8000/v1/users/user_456/assessments",
    headers={"X-Aperture-API-Key": "your-aperture-key"}
).json()

# Filter by element and confidence
technical_assessments = requests.get(
    "http://localhost:8000/v1/users/user_456/assessments",
    params={
        "element": "technical_confidence",
        "min_confidence": 0.7
    },
    headers={"X-Aperture-API-Key": "your-aperture-key"}
).json()
```

### Get Assessment with Evidence

```python
assessment = requests.get(
    f"http://localhost:8000/v1/users/user_456/assessments/{assessment_id}",
    headers={"X-Aperture-API-Key": "your-aperture-key"}
).json()

# See all evidence supporting this assessment
for evidence in assessment["evidence"]:
    print(f"User said: {evidence['user_message']}")
    print(f"Contribution: {evidence['confidence_contribution']}")
```

## 🎯 What Gets Tracked (MVP)

Currently extracts these assessments automatically:

| Element | Type | Description |
|---------|------|-------------|
| `technical_confidence` | Score (0-1) | How confident the user seems in technical abilities |
| `emotional_state` | Tag | frustrated, curious, excited, confused, satisfied, neutral |
| `help_seeking_behavior` | Tag | step_by_step, high_level, troubleshooting, explanation, none |

More coming soon! And you'll be able to define custom constructs.

## 🔗 User-Facing Features

### "Why This Response?" Link

Every response includes an `aperture_link`. When users click it, they see:

- Which assessments were used
- The confidence scores
- Evidence (their own quotes)
- Option to correct misunderstandings

### User Corrections

Users can flag incorrect assessments. The system will:
- Re-analyze with the correction as context
- Lower confidence in the original assessment
- Update future responses accordingly

## 🏗️ Architecture

```
Your App → Aperture API → OpenAI/Anthropic
               ↓
         [Extract Assessments]
               ↓
         Supabase Database
```

**Flow:**
1. Your app sends user message to Aperture
2. Aperture forwards to LLM provider (with your customer's API key)
3. LLM responds
4. Aperture extracts assessments in background
5. Response + Aperture metadata returned to your app

## 📊 Database Schema

- `users`: Tracks external user IDs
- `conversations`: Groups messages
- `messages`: Full conversation history
- `assessments`: Structured insights about users
- `evidence`: User quotes supporting each assessment
- `constructs`: Custom assessment configurations (coming soon)
- `response_tracking`: Links responses to assessments

## 🛣️ Roadmap

### Phase 1 (MVP - Current)
- [x] LLM proxy (OpenAI + Anthropic)
- [x] Basic assessment extraction
- [x] "Why this response?" UI
- [x] User corrections

### Phase 2 (Next)
- [ ] Auto-construct discovery
- [ ] Weekly pattern reports to operators
- [ ] Natural language construct creation
- [ ] Construct marketplace

### Phase 3 (Future)
- [ ] Multi-model consensus
- [ ] Temporal analytics dashboard
- [ ] Webhooks/triggers
- [ ] Personalization recommendation API
- [ ] Integrations (CRM, analytics)

## 🤝 Contributing

This is currently an MVP. Feedback and contributions welcome!

## 📄 License

MIT (for now - subject to change)

## 💬 Questions?

Open an issue or reach out!

---

Built with ❤️ to make AI more transparent and personalized.
