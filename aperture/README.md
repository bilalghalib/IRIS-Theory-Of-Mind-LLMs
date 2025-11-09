# Aperture 🔍

**User Intelligence Middleware for AI Applications**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)

> Turn conversations into structured, queryable user intelligence. The analytics layer for LLM applications.

Aperture sits between your app and any LLM, automatically building structured, explainable user profiles from natural conversations. Get confidence-scored assessments, evidence trails, and pattern discovery without changing your chat UI.

---

## 🎯 Why Aperture?

Just like every web app needs analytics (Mixpanel, Amplitude), every AI app needs **conversational intelligence**.

| What Teams Do Now | With Aperture |
|-------------------|---------------|
| Chat logs are write-only | **Structured, queryable profiles** |
| Manual user profiling via forms | **Auto-extracted from conversations** |
| Context windows as "memory" | **Persistent, confidence-scored insights** |
| Black-box AI responses | **Explainable with evidence trails** |
| Generic responses for all users | **Personalized based on understanding** |
| Guess what users need | **Auto-discover patterns across users** |

---

## ✨ Features

### Core Intelligence
- 🔌 **Universal LLM Proxy** - Works with OpenAI, Anthropic, and more (BYOK - Bring Your Own Key)
- 🧠 **Auto-Assessment Extraction** - Tracks technical confidence, emotional state, help-seeking behavior, skills, and custom attributes
- 📊 **Confidence Scoring** - Every assessment includes certainty level (0.0 - 1.0)
- 📝 **Evidence Trails** - All insights backed by actual user quotes
- 🔍 **Explainability** - "Why this response?" links show users your understanding

### Phase 2 (New!)
- 🎯 **Pattern Discovery** - Automatically finds common patterns across all users
- 🗣️ **Natural Language Constructs** - "I want to track purchase intent" → auto-generates config
- 📚 **Construct Marketplace** - Pre-built templates for customer support, sales, edtech, and more
- ✏️ **User Corrections** - Users can fix misunderstandings, system re-learns
- 📧 **Email Notifications** - Weekly digests of discovered patterns
- 🔄 **Temporal Analytics** - Track how attributes change over time

### Developer Experience
- 🐳 **Docker Ready** - One-command local setup
- 🧪 **Testing Infrastructure** - pytest with async support
- 🤖 **CI/CD** - Automated linting, testing, security scans
- 📖 **Auto-Generated Docs** - Interactive API docs at `/docs`
- 🛠️ **Multi-Tenant** - Built for SaaS from day one

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/yourusername/aperture.git
cd aperture
cp .env.example .env
# Edit .env with your credentials
docker-compose up
```

Visit http://localhost:8000

### Option 2: Python

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/aperture.git
cd aperture
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials

# 4. Setup database
# Run db/schema.sql in your Supabase SQL Editor

# 5. Run server
python main.py
```

Visit:
- **Landing Page:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

**Detailed setup guide:** See [SETUP.md](SETUP.md)

---

## 📡 API Overview

### 1. Core Message Proxy

Send messages through Aperture to automatically extract assessments:

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
        "llm_provider": "openai",  # or "anthropic"
        "llm_api_key": "sk-your-openai-key",  # Customer's own key
        "llm_model": "gpt-4o-mini"
    }
)

data = response.json()
print(data["response"])        # LLM's response
print(data["aperture_link"])   # Link to "Why this response?"
print(data["assessment_count"]) # Number of assessments extracted
```

**What gets extracted automatically:**
- `technical_confidence`: 0.4 (struggling with deployment)
- `emotional_state`: "frustrated"
- `help_seeking_behavior`: "troubleshooting"
- Evidence: "keep getting errors"

### 2. Query Assessments

```python
# Get all assessments for a user
assessments = requests.get(
    "http://localhost:8000/v1/users/user_456/assessments",
    headers={"X-Aperture-API-Key": "your-key"}
).json()

# Filter by element and confidence
technical = requests.get(
    "http://localhost:8000/v1/users/user_456/assessments",
    params={
        "element": "technical_confidence",
        "min_confidence": 0.7
    },
    headers={"X-Aperture-API-Key": "your-key"}
).json()

# Get assessment with evidence
detail = requests.get(
    f"http://localhost:8000/v1/users/user_456/assessments/{assessment_id}",
    headers={"X-Aperture-API-Key": "your-key"}
).json()

for evidence in detail["evidence"]:
    print(f"User said: {evidence['user_message']}")
    print(f"Confidence: {evidence['confidence_contribution']}")
```

### 3. Pattern Discovery (NEW!)

Automatically discover what patterns exist across your users:

```python
# Analyze conversations to find patterns
patterns = requests.post(
    "http://localhost:8000/v1/admin/discover-patterns",
    headers={"X-Aperture-API-Key": "your-key"},
    json={
        "min_users": 10,
        "min_occurrence_rate": 0.2,
        "lookback_days": 7
    }
).json()

# Returns:
{
    "patterns_found": 3,
    "patterns": [
        {
            "name": "deployment_platform_preference",
            "detected_in": "47 users (47%)",
            "confidence": 0.82,
            "value_proposition": "Track which platforms users prefer for deployment",
            "example_values": ["aws", "vercel", "heroku"]
        }
    ]
}
```

### 4. Natural Language Construct Creation (NEW!)

Describe what you want to track in plain English:

```python
# Create construct from description
result = requests.post(
    "http://localhost:8000/v1/constructs/from-description",
    headers={"X-Aperture-API-Key": "your-key"},
    json={
        "description": "I want to know if users are ready to upgrade to paid tier"
    }
).json()

# Returns:
{
    "match_type": "template",  # or "custom"
    "suggested_templates": [
        {
            "name": "purchase_intent",
            "description": "Track buyer readiness (BANT)",
            "similarity": 0.89,
            "elements": ["budget", "authority", "need", "timeline"]
        }
    ]
}
```

### 5. Construct Marketplace (NEW!)

Browse pre-built construct templates:

```python
# Get all templates
templates = requests.get(
    "http://localhost:8000/v1/constructs/templates",
    headers={"X-Aperture-API-Key": "your-key"}
).json()

# Search by use case
support_templates = requests.get(
    "http://localhost:8000/v1/constructs/templates?use_case=customer support",
    headers={"X-Aperture-API-Key": "your-key"}
).json()
```

**Available Templates:**
- `customer_support_tier` - Classify technical expertise for routing
- `purchase_intent` - Track buyer readiness (BANT)
- `student_knowledge_tracker` - Learning progress and understanding
- `developer_skill_profiler` - Tech stack and experience level

---

## 🎯 What Gets Tracked (Built-in)

| Assessment | Type | Example Values | Use Case |
|------------|------|----------------|----------|
| **technical_confidence** | Score (0-1) | 0.3 (struggling), 0.7 (competent), 0.9 (expert) | Route to appropriate support tier |
| **emotional_state** | Tag | frustrated, curious, excited, confused, satisfied | Detect when to escalate |
| **help_seeking_behavior** | Tag | step_by_step, high_level, troubleshooting, explanation | Personalize response style |

**All assessments include:**
- Confidence score (how certain)
- Evidence (user's actual quotes)
- Reasoning (why this assessment)
- Observation count (how many times seen)
- Timestamps (when detected)

---

## 🏗️ Architecture

```
┌─────────────┐
│  Your App   │
└──────┬──────┘
       │ POST /v1/conversations/{id}/messages
       │ {user_id, message, llm_api_key, ...}
       ▼
┌─────────────────────────────────────────┐
│          APERTURE MIDDLEWARE            │
│                                         │
│  1. Forward to OpenAI/Anthropic        │
│  2. Get LLM response                   │
│  3. Store conversation                 │
│  4. Generate short link                │
│  5. Return response + metadata         │
│                                         │
│  Background (async):                    │
│  6. Extract assessments                │
│  7. Discover patterns                  │
│  8. Store in database                  │
└────────────┬────────────────────────────┘
             │
             ▼
      ┌─────────────┐
      │  Supabase   │
      │  (Postgres) │
      └─────────────┘
```

**Key Components:**
- `main.py` - FastAPI application (9+ endpoints)
- `services/llm_proxy.py` - Multi-provider LLM support
- `services/assessment_extractor.py` - Intelligence extraction
- `services/pattern_discovery.py` - Cross-user pattern analysis
- `services/construct_creator.py` - NL construct generation
- `db/supabase_client.py` - Database operations
- `web/templates/` - User-facing explainability UI

---

## 📊 Database Schema

7 tables with proper relationships and indexes:

1. **users** - External user IDs from your app
2. **conversations** - Groups messages together
3. **messages** - Full conversation history
4. **assessments** - Structured user insights
5. **evidence** - User quotes supporting each assessment
6. **constructs** - Custom assessment configurations
7. **response_tracking** - Links short IDs to assessments

**See:** `db/schema.sql` for complete schema

---

## 🎯 Use Cases

### Customer Support
```python
# Auto-classify user expertise
assessment = get_assessment(user_id, "technical_confidence")
if assessment["value_data"]["score"] < 0.5:
    route_to_tier_1_support()
else:
    route_to_tier_2_support()
```

### EdTech
```python
# Track student understanding
progress = get_assessments(student_id, "topic_understanding")
if progress[-1]["confidence"] > 0.8 and progress[-1]["value_data"]["score"] > 0.9:
    suggest_advanced_material()
```

### Sales
```python
# Detect buying signals
intent = get_assessment(lead_id, "purchase_intent")
if intent["elements"]["timeline"]["value"] == "immediate":
    notify_sales_team()
```

### Developer Tools
```python
# Personalize code suggestions
skills = get_assessments(dev_id, "programming_languages")
if "typescript" in [s["value_data"]["tag"] for s in skills]:
    suggest_typescript_solution()
```

---

## 🔗 User-Facing Features

### "Why This Response?" Page

Every LLM response includes an `aperture_link`. When users click:

```
┌─ Why You Got This Response ──────────────┐
│                                           │
│ I suggested TypeScript because:           │
│                                           │
│ ✓ You prefer TypeScript (confidence: 0.9)│
│   Evidence: "I use TS for all projects"  │
│   From: 2 days ago                        │
│                                           │
│ [This is accurate ✓]  [Correct this ✗]   │
└───────────────────────────────────────────┘
```

### User Correction Flow

1. User clicks "Correct this"
2. Chooses correction type (wrong value, misinterpretation, etc.)
3. Provides explanation (optional)
4. System re-analyzes with correction as new ground truth
5. Future responses adjust accordingly

**Result:** Personalized AI that gets better over time with transparency.

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Run specific tests
pytest tests/test_api/test_messages.py

# Watch mode (requires pytest-watch)
ptw
```

**Test Structure:**
```
tests/
├── conftest.py              # Fixtures and mocks
├── test_api/                # API endpoint tests
│   ├── test_health.py
│   ├── test_auth.py
│   └── test_messages.py
├── test_services/           # Service layer tests
│   ├── test_llm_proxy.py
│   └── test_embeddings.py
└── test_integration/        # End-to-end tests
    └── test_full_flow.py
```

---

## 🚢 Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Docker

```bash
# Build
docker build -t aperture .

# Run
docker run -p 8000:8000 --env-file .env aperture
```

**See:** Deployment guides in [docs/deployment/](docs/deployment/)

---

## 🛣️ Roadmap

### ✅ Phase 1: MVP (Completed)
- Core LLM proxy
- Basic assessment extraction
- User correction flow
- "Why this response?" UI

### ✅ Phase 2: Auto-Discovery (Completed)
- Pattern discovery across users
- Natural language construct creation
- Construct marketplace
- Email notifications

### 🚧 Phase 3: Advanced Features (Next)
- [ ] Multi-model consensus (GPT-4 + Claude)
- [ ] Temporal analytics dashboard
- [ ] Webhooks & triggers
- [ ] Real-time pattern alerts

### 📅 Phase 4: Enterprise (Future)
- [ ] SSO / RBAC
- [ ] On-premise deployment
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Advanced analytics dashboard

**See:** [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed roadmap

---

## 💰 Pricing

| Tier | Price | Assessments/mo | Features |
|------|-------|----------------|----------|
| **Free** | $0 | 1,000 | Basic constructs, API access, Community support |
| **Pro** | $49 | 10,000 | Custom constructs, Pattern discovery, Webhooks, Email support |
| **Business** | $199 | 50,000 | Multi-model consensus, Analytics dashboard, Priority support |
| **Enterprise** | Custom | Unlimited | On-prem, SSO, SLA, Dedicated support |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code standards
- Testing requirements
- PR process

**Quick start for contributors:**
```bash
# Setup
git clone https://github.com/yourusername/aperture.git
cd aperture
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install

# Develop
python main.py

# Test
pytest

# Lint
./scripts/lint.sh

# Auto-fix
./scripts/fix.sh
```

---

## 📚 Documentation

- **Quick Start:** [SETUP.md](SETUP.md) - 5-minute setup guide
- **API Reference:** http://localhost:8000/docs - Auto-generated
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- **Testing:** [TESTING.md](TESTING.md) - Test strategy
- **Roadmap:** [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) - Full product plan
- **Architecture:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical overview

---

## 🏆 Built With

- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Supabase](https://supabase.com) - PostgreSQL database
- [OpenAI](https://openai.com) & [Anthropic](https://anthropic.com) - LLM providers
- [Pydantic](https://docs.pydantic.dev) - Data validation
- [pytest](https://pytest.org) - Testing framework

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 💬 Support

- **Documentation:** https://docs.aperture.dev
- **GitHub Issues:** https://github.com/yourusername/aperture/issues
- **Discord:** [Join our community](#)
- **Email:** hello@aperture.dev

---

## 🌟 Star History

If you find Aperture useful, please consider giving it a star! ⭐

---

**Built with ❤️ to make AI more transparent and personalized.**

*Turn conversations into intelligence. Start understanding your users today.*
