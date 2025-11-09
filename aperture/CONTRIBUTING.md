# Contributing to Aperture

Thank you for your interest in contributing to Aperture! This guide will help you get started.

## 🚀 Quick Start

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/aperture.git
cd aperture

# Option 1: Python venv (recommended for quick testing)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Option 2: Docker (recommended for consistency)
docker-compose up
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Required:**
- Supabase project (or use local postgres via docker-compose)
- OpenAI or Anthropic API key (for assessment extraction)

**Optional:**
- Redis (for caching/background jobs - future)

### Run Locally

```bash
# With Python
python main.py

# With Docker
docker-compose up

# With auto-reload
uvicorn main:app --reload
```

Visit:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Run specific test file
pytest tests/test_api/test_messages.py

# Run tests matching pattern
pytest -k "test_assessment"

# Watch mode (requires pytest-watch)
ptw
```

## 📋 Code Standards

### Linting & Formatting

We use:
- **ruff** - Fast Python linter (replaces flake8, isort, etc.)
- **black** - Code formatter
- **mypy** - Type checking

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy .

# Run all checks
./scripts/lint.sh  # (we'll create this)
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## 🏗️ Architecture

### Project Structure

```
aperture/
├── main.py              # FastAPI app
├── config.py            # Settings
├── db/                  # Database layer
├── services/            # Business logic
├── schemas/             # Pydantic models
├── web/                 # UI templates
├── tests/               # Test suite
└── scripts/             # Utility scripts
```

### Key Patterns

1. **Service Layer**: Business logic lives in `services/`
2. **DB Abstraction**: All DB calls go through `db/supabase_client.py`
3. **Type Safety**: Use Pydantic models for all API I/O
4. **Async**: Use `async/await` for I/O operations
5. **Error Handling**: Catch exceptions, return proper HTTP status codes

### Adding a New Endpoint

1. Define Pydantic schema in `schemas/`
2. Add business logic to appropriate service
3. Create endpoint in `main.py` or new router
4. Add tests in `tests/test_api/`
5. Update OpenAPI docs (automatic with FastAPI)

Example:
```python
# schemas/new_feature.py
class NewFeatureRequest(BaseModel):
    field: str

# services/new_service.py
async def process_new_feature(data: NewFeatureRequest):
    # Business logic here
    pass

# main.py
@app.post("/v1/new-feature")
async def new_feature(
    request: NewFeatureRequest,
    api_key: str = Header(..., alias="X-Aperture-API-Key")
):
    await verify_api_key(api_key)
    result = await new_service.process_new_feature(request)
    return result

# tests/test_api/test_new_feature.py
async def test_new_feature():
    response = client.post("/v1/new-feature", json={"field": "value"})
    assert response.status_code == 200
```

## 🔄 Development Workflow

### 1. Pick an Issue

- Check [GitHub Issues](https://github.com/yourusername/aperture/issues)
- Look for `good-first-issue` or `help-wanted` labels
- Comment on issue to claim it

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write code
- Add tests
- Update docs if needed
- Run linters/tests locally

### 4. Commit

Use conventional commits:

```bash
git commit -m "feat: add natural language construct creation"
git commit -m "fix: handle missing API key error"
git commit -m "docs: update README with new endpoint"
git commit -m "test: add assessment extraction tests"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`

### 5. Push & Create PR

```bash
git push origin feature/your-feature-name
```

Create PR on GitHub with:
- Clear description of changes
- Link to related issue
- Screenshots (if UI changes)
- Test results

### 6. Code Review

- Address review comments
- Keep commits clean
- Squash if needed before merge

## 🐛 Debugging

### Enable Debug Logging

```python
# In config.py or .env
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Use FastAPI Debug Mode

```bash
uvicorn main:app --reload --log-level debug
```

### Common Issues

**"Connection refused" to Supabase:**
- Check `SUPABASE_URL` in .env
- Verify internet connection
- Try local postgres: `docker-compose up postgres`

**Assessment extraction not working:**
- Verify `OPENAI_API_KEY` is set
- Check API quota/billing
- Look at server logs for errors

**Tests failing:**
- Ensure test database is clean
- Check for port conflicts
- Run `pytest -v` for verbose output

## 📚 Documentation

When contributing, please update:

1. **Code comments**: Docstrings for functions/classes
2. **README.md**: If adding major features
3. **API docs**: Automatic via FastAPI, but add examples
4. **CHANGELOG.md**: Note your changes

## 🎯 Areas for Contribution

### High Priority
- [ ] Pattern discovery algorithm (Phase 2)
- [ ] More assessment types (skill profiling, purchase intent)
- [ ] Temporal analytics (track changes over time)
- [ ] Multi-model consensus

### Medium Priority
- [ ] Webhooks/triggers
- [ ] Dashboard UI
- [ ] Integration examples (Next.js, React)
- [ ] Performance optimizations

### Good First Issues
- [ ] Add more tests
- [ ] Improve error messages
- [ ] Add type hints
- [ ] Documentation improvements
- [ ] Example applications

## 💬 Getting Help

- **Discord**: [Join our Discord](#)
- **GitHub Discussions**: Ask questions
- **Issues**: Report bugs
- **Email**: support@aperture.dev

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## 🙏 Thank You!

Every contribution, no matter how small, makes Aperture better. We appreciate your time and effort!

---

**Happy coding!** 🚀
