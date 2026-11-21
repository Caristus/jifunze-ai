
from .base import BaseProvider
import json
class MockProvider(BaseProvider):
    provider_name = "mock"
    def generate(self, prompt, system_prompt=None, **kwargs):
        if kwargs.get("mode") == "teacher" and kwargs.get("artifact_type") == "lesson_plan":
            topic = kwargs.get("topic", "Topic")
            cur = kwargs.get("curriculum", "CBC")
            lesson = {
                "title": topic.title(),
                "subject": "Biology",
                "curriculum": cur,
                "duration": "50 minutes",
                "outcomes": [
                    f"Explain {topic.lower()} using correct terminology.",
                    f"Apply knowledge of {topic.lower()} to real life.",
                    f"Demonstrate critical thinking competencies."
                ],
                "flow": [
                    {"step": "Introduction", "duration": "5 min", "content": f"Engage learners with a question about {topic.lower()}."},
                    {"step": "Main Activity", "duration": "25 min", "content": f"Guided exploration of {topic.lower()} using school resources."},
                    {"step": "Assessment", "duration": "10 min", "content": f"Formative check on {topic.lower()}."}
                ],
                "resources": "Textbook Ch 4, Whiteboard.",
                "differentiation": "Support: Sentence starters. Extension: Case study.",
                "assessment": "1. Define process. 2. Label diagram.",
                "teacher_notes": "Ensure safety protocols."
            }
            return json.dumps(lesson)
        return "Generated content."
