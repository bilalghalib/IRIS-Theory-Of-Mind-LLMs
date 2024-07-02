from openai import OpenAI
import tiktoken
import yaml
import json
import re

client = OpenAI(api_key="your key here")

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

def truncate_conversation(conversation: list, max_tokens: int = 3800) -> list:
    truncated = []
    current_tokens = 0

    for message in reversed(conversation):
        message_tokens = len(tokenizer.encode(message['content']))
        if current_tokens + message_tokens > max_tokens:
            break
        truncated.insert(0, message)
        current_tokens += message_tokens

    return truncated

def get_llm_response(conversation: list, system_prompt: str) -> str:
    truncated_conversation = truncate_conversation(conversation)

    messages = [{"role": "system", "content": system_prompt}] + truncated_conversation

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        temperature=0.7
    )
    return response

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

def update_tom_element(category: str, current_state: dict, user_messages: list) -> dict:
    prompt = config['elements'][category]['prompt']
    context = f"Current {category} state: {json.dumps(current_state)}\n\nUser messages:\n"
    context += "\n".join([msg['content'] for msg in user_messages[-5:]])  # Last 5 user messages
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={ "type": "json_object" },
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        
        response_content = response.choices[0].message.content
        json_data = extract_json(response_content)
        
        if json_data:
            return json_data
        else:
            print(f"Error extracting JSON for {category}. Response: {response_content}")
            return current_state
    except Exception as e:
        print(f"Error updating {category}: {str(e)}")
        return current_state

def generate_blindspots(tom_dict: dict) -> list:
    prompt = config['meta_elements']['blindspots']['prompt']
    context = f"Current Theory of Mind: {json.dumps(tom_dict)}"
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={ "type": "json_object" },
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        
        response_content = response.choices[0].message.content
        json_data = json.loads(response_content)
        
        if 'blindspots' in json_data and isinstance(json_data['blindspots'], list):
            return json_data['blindspots']
        else:
            print(f"Error: Unexpected blindspots response format. Response: {response_content}")
            return []
    except Exception as e:
        print(f"Error generating blindspots: {str(e)}")
        return []

def generate_next_steps(tom_dict: dict) -> list:
    prompt = config['meta_elements']['next_steps']['prompt']
    context = f"Current Theory of Mind: {json.dumps(tom_dict)}"
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={ "type": "json_object" },
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        
        response_content = response.choices[0].message.content
        json_data = json.loads(response_content)
        
        if 'next_steps' in json_data and isinstance(json_data['next_steps'], list):
            return json_data['next_steps']
        else:
            print(f"Error: Unexpected next steps response format. Response: {response_content}")
            return []
    except Exception as e:
        print(f"Error generating next steps: {str(e)}")
        return []

def generate_conversation_summary(conversation: list) -> str:
    prompt = config['meta_elements']['conversation_summary']['prompt']
    context = f"Conversation history: {json.dumps(conversation)}"
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": context}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
            n=1,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating conversation summary: {str(e)}")
        return ""