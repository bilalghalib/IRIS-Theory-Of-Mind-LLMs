"""
Flask + Aperture Chat Example

A simple Flask application that integrates Aperture to build user understanding.
Shows how to use the Python SDK in a web application.
"""

import os
from flask import Flask, render_template, request, jsonify, session
from aperture import Aperture, ApertureAPIError
from dotenv import load_dotenv
import secrets

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Initialize Aperture client
aperture = Aperture(
    api_key=os.getenv('APERTURE_API_KEY'),
    base_url=os.getenv('APERTURE_BASE_URL', 'https://api.aperture.dev')
)


@app.route('/')
def index():
    """Render the chat interface."""
    # Generate or retrieve user ID from session
    if 'user_id' not in session:
        session['user_id'] = f"user_{secrets.token_hex(8)}"

    return render_template('chat.html', user_id=session['user_id'])


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages through Aperture.

    Request body:
        {
            "message": "User's message",
            "conversation_id": "optional_conv_id"
        }

    Returns:
        {
            "message": "AI response",
            "conversation_id": "conv_123",
            "message_id": "msg_456",
            "aperture_link": "https://aperture.dev/c/abc",
            "assessment_count": 3
        }
    """
    try:
        data = request.get_json()
        user_message = data.get('message')
        conversation_id = data.get('conversation_id')

        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User session not found'}), 401

        # Send message through Aperture
        response = aperture.send_message(
            user_id=user_id,
            message=user_message,
            conversation_id=conversation_id,
            llm_provider='openai',
            llm_api_key=os.getenv('OPENAI_API_KEY'),
            system_prompt='You are a helpful assistant that provides clear, concise answers.',
            temperature=0.7,
            metadata={
                'source': 'flask_app',
                'user_agent': request.headers.get('User-Agent'),
                'ip_address': request.remote_addr
            }
        )

        return jsonify({
            'message': response.response,
            'conversation_id': response.conversation_id,
            'message_id': response.message_id,
            'aperture_link': response.aperture_link,
            'assessment_count': response.assessment_count
        })

    except ApertureAPIError as e:
        app.logger.error(f'Aperture API error: {e.status_code} - {e.message}')
        return jsonify({
            'error': 'Failed to process message',
            'detail': e.message
        }), e.status_code

    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return jsonify({
            'error': 'Internal server error',
            'detail': str(e)
        }), 500


@app.route('/api/assessments', methods=['GET'])
def get_assessments():
    """
    Get assessments for the current user.

    Query parameters:
        - element: Filter by element name
        - min_confidence: Minimum confidence threshold (0.0-1.0)

    Returns:
        {
            "assessments": [
                {
                    "element": "technical_confidence",
                    "value": 0.8,
                    "confidence": 0.9,
                    "reasoning": "User demonstrated strong understanding...",
                    ...
                }
            ]
        }
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User session not found'}), 401

        element = request.args.get('element')
        min_confidence = request.args.get('min_confidence', type=float)

        assessments = aperture.get_assessments(
            user_id=user_id,
            element=element,
            min_confidence=min_confidence,
            limit=50
        )

        return jsonify({
            'assessments': [
                {
                    'id': a.id,
                    'element': a.element,
                    'value': a.value,
                    'confidence': a.confidence,
                    'reasoning': a.reasoning,
                    'created_at': a.created_at,
                    'user_corrected': a.user_corrected
                }
                for a in assessments
            ]
        })

    except ApertureAPIError as e:
        return jsonify({'error': e.message}), e.status_code

    except Exception as e:
        app.logger.error(f'Error getting assessments: {str(e)}')
        return jsonify({'error': 'Failed to get assessments'}), 500


@app.route('/api/assessments/<assessment_id>/correct', methods=['POST'])
def correct_assessment(assessment_id):
    """
    Submit a user correction for an assessment.

    Request body:
        {
            "correction_type": "wrong_value",
            "user_explanation": "I'm actually very confident with AWS"
        }
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User session not found'}), 401

        data = request.get_json()

        result = aperture.correct_assessment(
            user_id=user_id,
            assessment_id=assessment_id,
            correction_type=data.get('correction_type'),
            user_explanation=data.get('user_explanation')
        )

        return jsonify({
            'success': True,
            'message': 'Correction submitted successfully'
        })

    except ApertureAPIError as e:
        return jsonify({'error': e.message}), e.status_code

    except Exception as e:
        app.logger.error(f'Error correcting assessment: {str(e)}')
        return jsonify({'error': 'Failed to submit correction'}), 500


if __name__ == '__main__':
    # Check for required environment variables
    required_vars = ['APERTURE_API_KEY', 'OPENAI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        exit(1)

    print("✅ Starting Flask app with Aperture integration")
    app.run(debug=True, port=5000)
