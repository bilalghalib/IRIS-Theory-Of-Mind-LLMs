# CLAUDE.md - AI Assistant Context

This file provides context for AI assistants (Claude, GPT-4, etc.) working on the Aperture project.

---

## Project Overview

**Aperture** is a User Intelligence Middleware API for AI applications. It sits between chat applications and LLM providers (OpenAI, Anthropic), automatically extracting structured, explainable user profiles from conversations.

**Think of it as:** "Mixpanel/Amplitude for LLM applications" or "ChatGPT Memory 2.0 but structured, queryable, and explainable"

---

## Core Innovation

### The Problem
- Chat logs are unstructured and write-only
- LLMs have no persistent memory beyond context windows
- No way to query "what do we know about this user?"
- Black-box AI responses with no explainability
- Every user gets generic responses

### The Solution
Aperture automatically extracts and structures insights like:
- Technical confidence (score 0-1)
- Emotional state (frustrated, curious, etc.)
- Help-seeking behavior (step-by-step, high-level, etc.)
- Custom constructs (purchase intent, skill level, etc.)

Each assessment includes:
- **Value** (the actual insight)
- **Confidence** (how certain, 0-1)
- **Evidence** (user's actual quotes)
- **Reasoning** (LLM's explanation)

### Unique Features
1. **Pattern Discovery** - Finds common patterns across ALL users automatically
2. **Natural Language Constructs** - "I want to track purchase intent" → generates config
3. **User Corrections** - Users can fix misunderstandings, system re-learns
4. **Explainability** - "Why this response?" pages show transparency

---

## Architecture

```
User's App → Aperture (Proxy) → OpenAI/Anthropic
                 ↓
        [Extract Assessments]
                 ↓
          Supabase (Postgres)
```

**Tech Stack:**
- FastAPI (async Python web framework)
- Supabase (PostgreSQL with real-time)
- OpenAI + Anthropic (LLM providers)
- Pydantic (data validation)
- NumPy (embeddings similarity)

**Key Services:**
- `llm_proxy.py` - Multi-provider LLM forwarding
- `assessment_extractor.py` - Intelligence extraction from conversations
- `pattern_discovery.py` - Cross-user pattern analysis
- `construct_creator.py` - Natural language → construct configuration
- `embeddings.py` - Semantic similarity for pattern matching
- `email_notifications.py` - Operator alerts

---

## Project Structure

```
aperture/
├── main.py                  # FastAPI app with all endpoints
├── config.py                # Pydantic settings
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
│
├── db/
│   ├── schema.sql           # Supabase/Postgres schema
│   └── supabase_client.py   # Database service layer
│
├── services/                # Business logic
│   ├── llm_proxy.py
│   ├── assessment_extractor.py
│   ├── pattern_discovery.py
│   ├── construct_creator.py
│   ├── embeddings.py
│   ├── email_notifications.py
│   └── short_link.py
│
├── schemas/                 # Pydantic models
│   ├── messages.py
│   ├── assessments.py
│   └── constructs.py
│
├── web/
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── why_response.html
│   │   └── edit_understanding.html
│   └── landing.html         # Marketing landing page
│
├── tests/                   # pytest test suite
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_integration/
│
├── .github/workflows/       # CI/CD
│   └── ci.yml
│
└── scripts/                 # Helper scripts
    ├── lint.sh
    └── fix.sh
```

---

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/conversations/{id}/messages` | POST | Main proxy endpoint - sends message, extracts assessments |
| `/v1/users/{id}/assessments` | GET | Query user assessments with filters |
| `/v1/users/{id}/assessments/{id}` | GET | Get assessment with evidence |
| `/v1/users/{id}/assessments/{id}/correct` | PUT | User correction of assessment |
| `/v1/admin/discover-patterns` | POST | Run pattern discovery across users |
| `/v1/constructs/from-description` | POST | Create construct from NL description |
| `/v1/constructs/templates` | GET | Browse construct marketplace |
| `/v1/constructs/validate` | POST | Validate construct config |
| `/c/{short_id}` | GET | "Why this response?" page |
| `/c/{short_id}/edit` | GET | User correction form |

---

## Database Schema

**7 tables:**

1. **users** - External user IDs (from customer's app)
2. **conversations** - Groups messages together
3. **messages** - Full conversation history
4. **assessments** - Structured insights with confidence scores
5. **evidence** - User quotes supporting each assessment
6. **constructs** - Custom assessment configurations
7. **response_tracking** - Maps short IDs to assessments

**Key relationships:**
- User → Many Conversations
- Conversation → Many Messages
- User → Many Assessments
- Assessment → Many Evidence records

---

## Development Workflow

### Local Setup

```bash
# Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env  # Edit with credentials
python main.py

# OR Docker
docker-compose up
```

### Testing

```bash
pytest                              # All tests
pytest --cov=. --cov-report=html   # With coverage
pytest tests/test_api/              # Specific directory
./scripts/lint.sh                   # Linting
./scripts/fix.sh                    # Auto-fix formatting
```

### Code Quality

- **Linting:** ruff (fast Python linter)
- **Formatting:** black
- **Type checking:** mypy
- **Pre-commit hooks:** Configured in `.pre-commit-config.yaml`

---

## Common Tasks

### Adding a New Assessment Type

1. Update `services/assessment_extractor.py`:
   - Add element to extraction prompt
   - Define value type (score, tag, range, text)
   - Add extraction logic

2. Test extraction works:
   ```python
   pytest tests/test_services/test_assessment_extractor.py
   ```

3. Document in README.md

### Adding a New Endpoint

1. Define Pydantic schema in `schemas/`
2. Add business logic to appropriate `services/` file
3. Create endpoint in `main.py`
4. Add tests in `tests/test_api/`
5. FastAPI auto-generates docs at `/docs`

### Adding a Construct Template

1. Edit `services/construct_creator.py`
2. Add to `self.templates` list:
   ```python
   {
       "name": "template_name",
       "description": "What it measures",
       "use_cases": ["use case 1", "use case 2"],
       "elements": [...]
   }
   ```

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use FastAPI debug mode
uvicorn main:app --reload --log-level debug
```

---

## Important Patterns

### Async/Await
Most functions are `async def` for performance:
```python
async def my_function():
    result = await db.query(...)
    return result
```

### Error Handling
Always catch and log exceptions:
```python
try:
    result = await risky_operation()
except Exception as e:
    print(f"Error: {e}")
    return fallback_value
```

### Type Hints
Use Pydantic models for validation:
```python
from schemas import MessageRequest

async def endpoint(request: MessageRequest):
    # request is validated automatically
    pass
```

### Background Tasks
Long-running tasks use `asyncio.create_task`:
```python
asyncio.create_task(extract_assessments(...))
# Returns immediately, task runs in background
```

---

## Phase Completion Status

### ✅ Phase 1: MVP (Complete)
- LLM proxy (OpenAI + Anthropic)
- Basic assessment extraction
- User correction flow
- "Why this response?" UI
- Evidence trails

### ✅ Phase 2: Auto-Discovery (Complete)
- Embedding service for semantic similarity
- Pattern discovery across users
- Natural language construct creation
- Construct marketplace (4 templates)
- Email notification system
- Admin discovery endpoints

### 🚧 Phase 3: Advanced Features (Next)
- Multi-model consensus
- Temporal analytics
- Webhooks & triggers
- Real-time pattern alerts

### 📅 Phase 4: Enterprise (Planned)
- SSO / RBAC
- On-premise deployment
- CRM integrations
- Advanced analytics dashboard

---

## Key Design Decisions

### Why FastAPI?
- Async support (better performance)
- Auto-generated API docs
- Pydantic integration
- Modern Python features

### Why Supabase?
- Managed Postgres (reliable)
- Real-time capabilities (future)
- Auth built-in (future)
- Free tier generous for MVP

### Why BYOK (Bring Your Own Key)?
- Privacy: Customer's data never touches our LLM keys
- Cost: Customers pay their own LLM costs
- Flexibility: Works with any provider
- Trust: No vendor lock-in

### Why Assessments vs Raw Logs?
- **Queryable:** "Find frustrated users" vs grepping logs
- **Structured:** Can aggregate, analyze, visualize
- **Confident:** Know certainty of each insight
- **Explainable:** Evidence trail for every assessment
- **Temporal:** Track changes over time

---

## Common Gotchas

1. **Missing imports:** Services are singletons, import carefully
   ```python
   from services import llm_proxy  # Good
   from services.llm_proxy import llm_proxy  # Also good
   ```

2. **Async without await:**
   ```python
   # BAD
   result = async_function()

   # GOOD
   result = await async_function()
   ```

3. **API key validation:** All endpoints need `verify_api_key()`

4. **Environment variables:** Always use `settings` object:
   ```python
   from config import settings
   api_key = settings.openai_api_key  # Good
   api_key = os.getenv("OPENAI_API_KEY")  # Avoid
   ```

5. **Database IDs:** Use UUIDs (from Supabase), not integers

---

## Testing Strategy

### Unit Tests
- Test individual functions in `services/`
- Mock external dependencies (DB, LLM)
- Fast, no network calls

### Integration Tests
- Test full endpoint flows
- Use test database or mocks
- Verify request/response formats

### E2E Tests
- Full conversation flow
- Real database (test instance)
- Slower but comprehensive

**Coverage goal:** 80%+

---

## Deployment Notes

### Environment Variables Required

```bash
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
OPENAI_API_KEY=...
APERTURE_API_KEY=...
```

### Health Check
GET `/health` should return `{"status": "healthy"}`

### Monitoring
- Errors logged to console (add Sentry in production)
- API latency tracked via FastAPI middleware
- Database connection pooling via Supabase

### Scaling Considerations
- Stateless API (can horizontal scale)
- Database is bottleneck (Supabase handles this)
- Background tasks could use Celery + Redis (future)

---

## When to Ask for Clarification

1. **Business logic unclear:** "Should this assessment be scored or tagged?"
2. **Edge cases:** "What if user has no conversation history?"
3. **Security concerns:** "Is this API key validation sufficient?"
4. **Performance:** "Will this query scale to 10,000 users?"

---

## Useful Commands

```bash
# Run server
python main.py

# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest -v

# Run linting
./scripts/lint.sh

# Format code
./scripts/fix.sh

# Check coverage
pytest --cov=. --cov-report=term

# Build Docker
docker build -t aperture .

# Run Docker
docker-compose up

# View API docs
# Visit http://localhost:8000/docs
```

---

## Resources

- **README.md** - User-facing documentation
- **CONTRIBUTING.md** - Developer guide
- **DEVELOPMENT_PLAN.md** - Product roadmap
- **SETUP.md** - Detailed setup guide
- **TESTING.md** - Testing strategy
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Supabase Docs:** https://supabase.com/docs
- **OpenAI API:** https://platform.openai.com/docs
- **Anthropic API:** https://docs.anthropic.com

---

## Project Philosophy

1. **Transparency First:** Users should know what we know about them
2. **Evidence-Based:** Every assessment backed by real quotes
3. **Correctable:** Users can fix misunderstandings
4. **Privacy-Focused:** BYOK, minimal data retention
5. **Developer-Friendly:** Great docs, auto-generated API reference
6. **Production-Ready:** Tests, linting, CI/CD from day one

---

## Quick Reference: What to Update When...

### Adding a new LLM provider
- Update `services/llm_proxy.py`
- Add to `_send_<provider>` method
- Update README.md

### Changing assessment logic
- Update `services/assessment_extractor.py`
- Update prompt in `_build_extraction_prompt()`
- Add tests
- Update docs

### Modifying database schema
- Edit `db/schema.sql`
- Update migration script
- Update `db/supabase_client.py` methods
- Test locally

### New API endpoint
- Add to `main.py`
- Create Pydantic schema in `schemas/`
- Add tests in `tests/test_api/`
- FastAPI auto-docs will update

---

## Current Version

**v0.2.0** - Phase 2 Complete

**Total Lines of Code:** ~8,000
**Total Tests:** 10+ (more coming)
**API Endpoints:** 13
**Database Tables:** 7
**Construct Templates:** 4

**Last Updated:** 2025-01-09

---

## For Future AI Assistants

This project was built iteratively across multiple sessions:

1. **Session 1:** MVP (Core proxy, assessments, UI)
2. **Session 2:** Phase 2 (Pattern discovery, NL constructs, marketplace)

The code is well-structured and follows best practices. When working on this:
- Read the relevant service file first
- Check existing tests for examples
- Follow established patterns
- Update documentation
- Ask clarifying questions when unsure

**Core principle:** Make AI transparent and personalizable. Every feature should serve that goal.

---

**Happy coding! 🚀**

*Built to make AI more transparent and personalized.*
