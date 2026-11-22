from .base import BaseProvider
import json
KNOWLEDGE = [
    (("atom",), "An atom is the smallest unit of an element that keeps its chemical properties. It has a nucleus (protons + neutrons) surrounded by electrons in energy levels (shells). The number of protons (atomic number) defines the element. Atoms join by bonds to form molecules."),
    (("photosynthesis",), "Photosynthesis is how green plants turn light energy into chemical energy: 6CO2 + 6H2O + light -> C6H12O6 + 6O2. It happens in chloroplasts; chlorophyll absorbs mainly red and blue light. Light-dependent reactions split water and make ATP/NADPH; the Calvin cycle then fixes CO2 into glucose."),
    (("molecule",), "A molecule is two or more atoms chemically bonded, e.g. H2O or O2. Bonds can be covalent (sharing electrons) or ionic (transferring electrons)."),
    (("cell",), "The cell is the basic unit of life. Plant cells have a cell wall, chloroplasts and a large vacuole; animal cells do not. Both have a nucleus, cytoplasm and cell membrane."),
    (("force", "newton"), "A force is a push or pull that changes motion or shape. Its unit is the newton (N). Newton's second law gives F = ma."),
    (("fraction",), "A fraction is part of a whole: numerator over denominator. To add fractions, first find a common denominator; equivalent fractions have equal value."),
]
class MockProvider(BaseProvider):
    provider_name = "mock"
    def __init__(self):
        self.model = "mock-dev-mode"
    def generate(self, prompt, system_prompt=None, **kwargs):
        mode = kwargs.get("mode", "learner")
        cur = kwargs.get("curriculum", "CBC/CBE")
        grade = kwargs.get("grade_level", "")
        lang = kwargs.get("language", "en")
        atype = kwargs.get("artifact_type", "")
        if mode == "teacher":
            topic = kwargs.get("topic", "the topic")
            if atype == "lesson_plan":
                return json.dumps({
                    "title": topic.title(), "subject": "Science", "curriculum": cur,
                    "duration": "50 minutes",
                    "outcomes": ["Explain " + topic.lower() + " correctly.", "Apply it to real life.", "Show critical thinking."],
                    "flow": [
                        {"step": "Introduction", "duration": "5 min", "content": "Hook learners with a question about " + topic.lower() + "."},
                        {"step": "Main Activity", "duration": "25 min", "content": "Guided exploration using school resources."},
                        {"step": "Assessment", "duration": "10 min", "content": "Formative check against a " + cur + " rubric."},
                    ],
                    "resources": "Textbook, uploaded documents, whiteboard.",
                    "differentiation": "Support: sentence starters. Extension: case study.",
                    "assessment": "Define + label diagram; rubric on accuracy.",
                    "teacher_notes": "Check prior knowledge first.",
                }, indent=2)
            return "# " + topic.title() + "\n\nTeaching material for " + cur + "."
        # ---- LEARNER MODE: a real, grounded, friendly answer ----
        text = prompt or ""
        if "Learner question:" in text:
            question = text.split("Learner question:")[-1].strip()
            context = text.split("Learner question:")[0].replace("Context from approved school materials:", "").strip()
        else:
            question = text.strip()
            context = ""
        q = question.lower()
        body = None
        for keys, val in KNOWLEDGE:
            if any(k in q for k in keys):
                body = val
                break
        if body is None:
            body = ("A clear way to think about \"" + question + "\":\n"
                    "1. Define the key term in your own words.\n"
                    "2. Identify the main parts or steps.\n"
                    "3. Connect it to a real-life example.\n"
                    "4. Test yourself with one practice question.")
        sw = (lang == "sw")
        lines = []
        if context:
            lines.append("Kulingana na nyenzo za shule yako:" if sw else "Based on your school's approved materials:")
            lines.append(context[:400])
            lines.append("")
        lines.append(("Kwa lugha rahisi (" if sw else "In simple terms (") + cur + ((", " + grade) if grade else "") + "):")
        lines.append(body)
        lines.append("")
        lines.append("Je, ungependa mfano au swali la mazoezi?" if sw else "Would you like a worked example or a quick practice question on this?")
        return "\n".join(lines)
