import json
import uuid
from typing import List, Dict, Any
import yaml
from collections import deque
from llm_interface import update_tom_element, generate_blindspots, generate_next_steps, generate_conversation_summary

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class Element:
    def __init__(self, content: str, evidence: List[str] = None, confidence: float = 0.5, questions: List[str] = None):
        self.content = content
        self.evidence = evidence or []
        self.confidence = confidence
        self.questions = questions or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "questions": self.questions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Element':
        return cls(
            content=data["content"],
            evidence=data["evidence"],
            confidence=data["confidence"],
            questions=data["questions"]
        )

    def update(self, category: str, user_messages: List[Dict[str, str]]):
        updated_data = update_tom_element(category, self.to_dict(), user_messages)
        self.content = updated_data.get('content', self.content)
        self.evidence = updated_data.get('evidence', self.evidence)
        self.confidence = updated_data.get('confidence', self.confidence)
        self.questions = updated_data.get('questions', self.questions)

class TheoryOfMind:
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())[:8]
        self.frame = {category: [Element("")] for category in config['elements']}
        self.blindspots: List[str] = []
        self.next_steps: List[str] = []
        self.conversation_summary = ""
        self.message_history = deque(maxlen=config['sliding_window_size'])
        self.interaction_count = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "frame": {k: [e.to_dict() for e in v] for k, v in self.frame.items()},
            "blindspots": self.blindspots,
            "next_steps": self.next_steps,
            "conversation_summary": self.conversation_summary,
            "message_history": list(self.message_history),
            "interaction_count": self.interaction_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TheoryOfMind':
        tom = cls(user_id=data["user_id"])
        tom.frame = {k: [Element.from_dict(e) for e in v] for k, v in data["frame"].items()}
        tom.blindspots = data.get("blindspots", [])
        tom.next_steps = data.get("next_steps", [])
        tom.conversation_summary = data["conversation_summary"]
        tom.message_history = deque(data["message_history"], maxlen=config['sliding_window_size'])
        tom.interaction_count = data["interaction_count"]
        return tom

    def save_to_file(self, filename: str):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'TheoryOfMind':
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def update(self, user_input: str, llm_response: str):
        self.message_history.append({"role": "user", "content": user_input})
        self.message_history.append({"role": "assistant", "content": llm_response})
        self.interaction_count += 1

        user_messages = [msg for msg in self.message_history if msg['role'] == 'user']
        for category, elements in self.frame.items():
            for element in elements:
                element.update(category, user_messages)

        if self.interaction_count % config['update_frequency']['blindspots'] == 0:
            self.blindspots = generate_blindspots(self.to_dict())

        if self.interaction_count % config['update_frequency']['next_steps'] == 0:
            self.next_steps = generate_next_steps(self.to_dict())

        if self.interaction_count % config['update_frequency']['conversation_summary'] == 0:
            self.conversation_summary = generate_conversation_summary(list(self.message_history))

    def generate_prompt(self) -> str:
        tom_summary = json.dumps(self.to_dict(), indent=2)
        return config['system_prompts']['main_interaction'].format(tom=tom_summary)

    def handle_user_feedback(self, feedback: str):
        # Implement logic to adjust TOM based on user feedback
        pass