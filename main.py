from flask import Flask, request, jsonify, render_template
from theory_of_mind import TheoryOfMind
from llm_interface import get_llm_response, generate_blindspots, generate_next_steps
from visualization import generate_tom_visualization
import yaml
import traceback

app = Flask(__name__)

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

tom = TheoryOfMind()

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/initial_message', methods=['GET'])
def initial_message():
    intro_prompt = config['system_prompts']['introduction']
    try:
        intro_response = get_llm_response([], intro_prompt)
        return jsonify({'response': intro_response.choices[0].message.content.strip()})
    except Exception as e:
        print(f"Error in initial introduction: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'response': "Hello! I'm IRIS. How can I assist you today?"})


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    
    if user_input.lower() == config['commands']['show']:
        visualization = generate_tom_visualization(tom)
        return jsonify({'response': visualization})
    elif user_input.lower() == config['commands']['blindspots']:
        blindspots = generate_blindspots(tom.to_dict())
        if blindspots:
            response = "Here are some potential blindspots I've identified:\n\n"
            for i, blindspot in enumerate(blindspots, 1):
                response += f"{i}. {blindspot['description']} (Relevance: {blindspot['relevance']})\n"
        else:
            response = "I couldn't identify any specific blindspots at this time. Let's continue our conversation to gain more insights."
        return jsonify({'response': response})
    elif user_input.lower() == config['commands']['next']:
        next_steps = generate_next_steps(tom.to_dict())
        if next_steps:
            response = "Here are some suggested next steps:\n\n"
            for i, step in enumerate(next_steps, 1):
                relevance = step.get('relevance_score', step.get('relevance', 'N/A'))
                response += f"{i}. {step['description']} (Relevance: {relevance})\n"
        else:
            response = "I couldn't generate specific next steps at this time. Let's discuss your goals further to provide more targeted suggestions."
        return jsonify({'response': response})
    elif user_input.lower() == config['commands']['quit']:
        return jsonify({'response': 'Goodbye! Thank you for chatting with IRIS.'})
    
    tom_prompt = tom.generate_prompt()
    try:
        response = get_llm_response(list(tom.message_history) + [{"role": "user", "content": user_input}], tom_prompt)
        llm_response = response.choices[0].message.content.strip()
        tom.update(user_input, llm_response)
        tom.save_to_file(f"tom_{tom.user_id}.json")
        return jsonify({'response': llm_response})
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'response': "I apologize, but I encountered an error while processing your request. Please try again."})

@app.route('/get_tom', methods=['GET'])
def get_tom():
    try:
        visualization = generate_tom_visualization(tom)
        return jsonify({'visualization': visualization})
    except Exception as e:
        print(f"Error in get_tom: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'visualization': "Error generating Theory of Mind visualization."})

@app.route('/feedback', methods=['POST'])
def feedback():
    user_feedback = request.json['feedback']
    try:
        tom.handle_user_feedback(user_feedback)
        return jsonify({'response': 'Thank you for your feedback!'})
    except Exception as e:
        print(f"Error in feedback: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'response': 'Error processing feedback. Please try again.'})

if __name__ == '__main__':
    app.run(debug=True, port=5002)