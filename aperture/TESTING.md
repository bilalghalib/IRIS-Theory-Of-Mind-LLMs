# Aperture Testing Guide

Complete guide to testing the Aperture platform, including unit tests, integration tests, E2E tests, and visual regression testing.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Types](#test-types)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

---

## Testing Philosophy

Aperture uses a comprehensive testing strategy with multiple layers:

1. **Unit Tests** - Fast, isolated tests for individual functions and classes
2. **Integration Tests** - Test API endpoints and service interactions
3. **E2E Tests** - Browser-based tests using Puppeteer for user flows
4. **Visual Regression** - Screenshot comparison for UI consistency

**Coverage Goals:**
- Unit Tests: 80%+ coverage for services
- Integration Tests: 100% API endpoint coverage
- E2E Tests: All critical user flows
- Visual Regression: All public-facing pages

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

Test individual services in isolation with mocked dependencies.

**Technologies:**
- pytest
- pytest-asyncio
- unittest.mock

**Location:** `aperture/tests/unit/`

**Example:**
```python
@pytest.mark.unit
class TestLLMProxy:
    @pytest.mark.asyncio
    async def test_send_message_openai(self):
        with patch('httpx.AsyncClient.post') as mock_post:
            # Test OpenAI integration
            ...
```

### 2. Integration Tests (`tests/integration/`)

Test API endpoints with mocked external services (LLMs, database).

**Technologies:**
- pytest
- FastAPI TestClient
- unittest.mock

**Location:** `aperture/tests/integration/`

**Example:**
```python
@pytest.mark.integration
@pytest.mark.api
class TestMessagesAPI:
    def test_send_message_success(self, client, auth_headers):
        response = client.post("/v1/conversations/conv_123/messages", ...)
        assert response.status_code == 200
```

### 3. E2E Tests (`tests/e2e/`)

Browser automation tests for user-facing features.

**Technologies:**
- Puppeteer
- Jest
- TypeScript

**Location:** `aperture/tests/e2e/`

**Example:**
```typescript
describe('Landing Page', () => {
  test('should display main headline', async () => {
    await browser.goto(`${BASE_URL}/`);
    const headline = await browser.getText('.hero h1');
    expect(headline).toContain('Stop Guessing');
  });
});
```

### 4. Visual Regression (`tests/e2e/visual-regression.test.ts`)

Screenshot comparison tests to catch UI regressions.

**Technologies:**
- Puppeteer
- jest-image-snapshot

**Example:**
```typescript
test('should match landing page snapshot', async () => {
  const screenshot = await page.screenshot({ fullPage: true });
  expect(screenshot).toMatchImageSnapshot({
    customSnapshotIdentifier: 'landing-page-desktop',
    failureThreshold: 0.01
  });
});
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (optional, for integration tests)

### Setup

1. **Install Python dependencies:**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Install E2E test dependencies:**

```bash
cd tests/e2e
npm install
```

3. **Set environment variables:**

```bash
export APERTURE_API_KEY="test-api-key"
export OPENAI_API_KEY="sk-test-key"
export BASE_URL="http://localhost:8000"
```

### Run All Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
cd tests/e2e && npm test

# Visual regression
cd tests/e2e && npm run test:visual
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run specific test file
pytest tests/unit/test_llm_proxy.py -v

# Run with coverage
pytest tests/unit/ --cov=services --cov-report=html

# Run tests matching pattern
pytest tests/unit/ -k "test_send_message" -v

# Run only unit tests (skip slow integration tests)
pytest tests/unit/ -v -m unit
```

### Integration Tests

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific API test suite
pytest tests/integration/test_api_messages.py -v

# Run with markers
pytest tests/integration/ -v -m integration

# Skip slow tests
pytest tests/integration/ -v -m "not slow"

# Run with detailed output
pytest tests/integration/ -vv --tb=short
```

### E2E Tests

```bash
cd tests/e2e

# Run all E2E tests
npm test

# Run in headed mode (see browser)
HEADLESS=false npm test

# Run specific test file
npm test -- landing-page.test.ts

# Run with slow motion (debugging)
SLOWMO=100 npm test

# Run in watch mode
npm run test:watch
```

### Visual Regression Tests

```bash
cd tests/e2e

# Run visual tests
npm run test:visual

# Update baseline screenshots
npm run update:screenshots

# Run visual tests in headed mode
HEADLESS=false npm run test:visual
```

---

## Test Structure

```
aperture/
├── tests/
│   ├── unit/                          # Unit tests
│   │   ├── test_llm_proxy.py
│   │   ├── test_embeddings.py
│   │   └── test_assessment_extractor.py
│   ├── integration/                   # Integration tests
│   │   ├── conftest.py               # Fixtures & mocks
│   │   ├── test_api_messages.py
│   │   ├── test_api_assessments.py
│   │   └── test_api_patterns.py
│   └── e2e/                           # E2E tests
│       ├── package.json
│       ├── jest.config.js
│       ├── helpers/
│       │   └── browser.ts            # Browser helper
│       ├── landing-page.test.ts
│       ├── pricing-calculator.test.ts
│       └── visual-regression.test.ts
```

---

## CI/CD Integration

Aperture uses GitHub Actions for automated testing on every push and pull request.

### Workflow Overview

```
┌─────────────────┐
│   Push/PR       │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Lint    │  ruff, black, mypy
    └────┬─────┘
         │
    ┌────▼─────────┐
    │  Unit Tests  │  pytest tests/unit/
    └────┬─────────┘
         │
    ┌────▼────────────────┐
    │ Integration Tests  │  pytest tests/integration/
    └────┬────────────────┘
         │
    ┌────▼─────────┐
    │  E2E Tests   │  Puppeteer + Jest
    └────┬─────────┘
         │
    ┌────▼────────────────┐
    │ Visual Regression   │  (PRs only)
    └────┬────────────────┘
         │
    ┌────▼─────────┐
    │  Security    │  bandit
    └────┬─────────┘
         │
    ┌────▼─────────┐
    │  Docker      │  Build image
    └──────────────┘
```

### Test Coverage Requirements

- Unit tests: 80%+ coverage required
- Integration tests: 100% endpoint coverage
- E2E tests: All critical user flows
- PRs failing tests will be blocked from merging

---

## Troubleshooting

### Common Issues

#### 1. E2E Tests Failing with "Browser not launched"

**Problem:** Puppeteer can't find Chromium.

**Solution:**
```bash
cd tests/e2e
npm install
npx puppeteer browsers install chrome
```

#### 2. Visual Tests Failing with Minor Pixel Differences

**Problem:** Font rendering differences across environments.

**Solution:**
Update failure threshold in test:
```typescript
expect(screenshot).toMatchImageSnapshot({
  failureThreshold: 0.05, // Allow 5% difference
  failureThresholdType: 'percent'
});
```

#### 3. Integration Tests Timing Out

**Problem:** Slow external API calls.

**Solution:**
Ensure all external calls are mocked:
```python
@patch('httpx.AsyncClient.post')
def test_with_mock(mock_post):
    mock_post.return_value = AsyncMock(...)
```

---

## Best Practices

### DO ✅

- Write tests before fixing bugs (TDD)
- Keep tests fast (< 1s for unit, < 5s for integration)
- Use descriptive test names (`test_send_message_with_invalid_api_key`)
- Mock external dependencies
- Test edge cases and error conditions
- Use fixtures for common setup
- Clean up resources in teardown

### DON'T ❌

- Test implementation details
- Write flaky tests with sleeps
- Skip tests without good reason
- Commit failing tests
- Test third-party code
- Use production data in tests
- Share state between tests

---

**For more help, see:**
- [README.md](./README.md) - Project overview
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guide
- [CLAUDE.md](./CLAUDE.md) - AI assistant context
