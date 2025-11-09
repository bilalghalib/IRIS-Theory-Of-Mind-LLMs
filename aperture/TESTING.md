# Testing Strategy

## Test Coverage Goals
- Unit tests: 80%+
- Integration tests: Key API flows
- E2E tests: Full conversation flow

## Stack
- pytest (test runner)
- pytest-asyncio (async tests)
- httpx (API testing)
- Factory Boy (test data generation)
- pytest-cov (coverage reporting)

## Test Structure

```
aperture/
├── tests/
│   ├── conftest.py              # Fixtures
│   ├── test_api/
│   │   ├── test_messages.py     # Message endpoint tests
│   │   ├── test_assessments.py  # Assessment endpoint tests
│   │   └── test_corrections.py  # Correction flow tests
│   ├── test_services/
│   │   ├── test_llm_proxy.py
│   │   ├── test_assessment_extractor.py
│   │   └── test_pattern_discovery.py
│   └── test_integration/
│       └── test_full_conversation.py
```

## Key Test Cases

### 1. Message Flow
- Send message → LLM responds → assessments extracted
- Conversation history maintained correctly
- Short links generated

### 2. Assessment Extraction
- Correct elements extracted
- Confidence scores reasonable
- Evidence captured

### 3. User Corrections
- Correction updates assessment
- Re-analysis with new context
- Future assessments influenced

### 4. Error Handling
- Invalid API keys
- LLM provider failures
- Database connection issues

## Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest tests/test_api/test_messages.py

# Watch mode (with pytest-watch)
ptw
```

## CI Integration

GitHub Actions will run on every PR:
- Linting (ruff)
- Type checking (mypy)
- Tests with coverage
- Security scanning (bandit)
