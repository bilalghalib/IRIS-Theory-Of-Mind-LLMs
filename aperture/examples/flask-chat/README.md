# Flask + Aperture Chat Example

A simple Flask application that integrates Aperture to build user understanding over time.

## Features

- 💬 Real-time chat interface
- 🧠 Automatic user intelligence extraction
- 🔍 "Why this response?" links for transparency
- 🎨 Beautiful gradient UI with pure CSS
- 📊 API endpoints for querying assessments
- ✅ User correction support

## Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set environment variables:**

Create `.env` file:

```bash
APERTURE_API_KEY=your_aperture_key
OPENAI_API_KEY=your_openai_key
FLASK_SECRET_KEY=your_random_secret_key
```

3. **Run the application:**

```bash
python app.py
```

4. **Open your browser:**

Navigate to [http://localhost:5000](http://localhost:5000)

## How It Works

1. User types a message in the chat interface
2. Frontend sends POST request to `/api/chat`
3. Flask backend proxies message through Aperture
4. Aperture extracts user insights in the background
5. LLM response is returned to the user
6. User can click "Why this response?" to see what Aperture learned

## Project Structure

```
flask-chat/
├── app.py                    # Main Flask application
├── templates/
│   └── chat.html            # Chat interface
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## API Endpoints

### `POST /api/chat`

Send a message through Aperture.

**Request:**
```json
{
  "message": "User's message",
  "conversation_id": "optional_conv_id"
}
```

**Response:**
```json
{
  "message": "AI response",
  "conversation_id": "conv_123",
  "message_id": "msg_456",
  "aperture_link": "https://aperture.dev/c/abc",
  "assessment_count": 3
}
```

### `GET /api/assessments`

Get assessments for the current user.

**Query Parameters:**
- `element` (optional): Filter by element name
- `min_confidence` (optional): Minimum confidence threshold (0.0-1.0)

**Response:**
```json
{
  "assessments": [
    {
      "element": "technical_confidence",
      "value": 0.8,
      "confidence": 0.9,
      "reasoning": "User demonstrated strong understanding...",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### `POST /api/assessments/<assessment_id>/correct`

Submit a correction for an assessment.

**Request:**
```json
{
  "correction_type": "wrong_value",
  "user_explanation": "I'm actually very confident with AWS"
}
```

## Customization

### Change LLM Provider

In `app.py`, update the `send_message` call:

```python
response = aperture.send_message(
    user_id=user_id,
    message=user_message,
    llm_provider='anthropic',  # Changed from 'openai'
    llm_api_key=os.getenv('ANTHROPIC_API_KEY'),
    # ... rest of parameters
)
```

### Add User Authentication

Replace session-based user ID with your auth system:

```python
from flask_login import login_required, current_user

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    user_id = current_user.id
    # ... rest of the code
```

### Add Assessments Dashboard

Create a new route to display what Aperture knows:

```python
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    assessments = aperture.get_assessments(user_id, min_confidence=0.7)

    return render_template('dashboard.html', assessments=assessments)
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:

```bash
docker build -t flask-aperture .
docker run -p 8000:8000 --env-file .env flask-aperture
```

### Deployment Platforms

Works on any Python-compatible platform:
- Heroku
- Railway
- Render
- Fly.io
- DigitalOcean App Platform

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APERTURE_API_KEY` | Your Aperture API key | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | Yes |
| `APERTURE_BASE_URL` | Aperture API base URL | No (defaults to production) |

## Development

### Running with Debug Mode

```bash
export FLASK_DEBUG=1
python app.py
```

### Adding Tests

Create `test_app.py`:

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_chat_endpoint(client):
    response = client.post('/api/chat', json={
        'message': 'Hello'
    })
    assert response.status_code == 200
```

## Learn More

- [Aperture Documentation](https://docs.aperture.dev)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Aperture Python SDK](https://github.com/yourusername/aperture/tree/main/sdk/python)

## License

MIT
