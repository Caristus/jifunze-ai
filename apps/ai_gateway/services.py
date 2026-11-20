from apps.ai_gateway.providers import MockProvider, OllamaProvider
from apps.institutions.models import Institution
import logging
logger = logging.getLogger(__name__)
class AIGateway:
    """Provider-independent AI gateway with curriculum-aware prompting."""
    PROVIDERS = {"mock": MockProvider, "ollama": OllamaProvider}
    CURRICULUM_GUIDANCE = {
        "CBC/CBE": "Use competency-based language: learning outcomes, core competencies, "
                   "formative assessment, and practical activities.",
        "8-4-4": "Use knowledge-retention framing: objectives, content coverage, and "
                 "national-exam style questions.",
        "Cambridge IGCSE": "Use Cambridge terminology: learning objectives, syllabus "
                           "reference, structured questions, and mark schemes.",
        "IB": "Use inquiry-based framing: concepts, ATL skills, and global context.",
        "CAPS": "Use South African CAPS terminology: outcomes, assessments, and "
                "work schedules.",
    }
    def __init__(self, institution: Institution = None):
        self.institution = institution
        self.provider = self._get_provider()
    def _get_provider(self):
        name = getattr(self.institution, "ai_provider", "mock") or "mock"
        model = getattr(self.institution, "ai_model", None)
        if name == "ollama":
            return OllamaProvider(model=model or "llama3.2")
        return MockProvider()
    def _guidance(self, curriculum):
        return self.CURRICULUM_GUIDANCE.get(curriculum, "Align with the school's national curriculum.")
    def generate_learning_response(self, prompt, context, curriculum="CBC/CBE", grade_level=""):
        system = (f"You are a friendly educational assistant for {grade_level or 'secondary'} learners "
                  f"following the {curriculum} curriculum. {self._guidance(curriculum)} "
                  f"Answer ONLY from the provided context. If insufficient, say so honestly.")
        full = f"Context from approved school materials:\n{context}\n\nLearner question: {prompt}"
        return self.provider.generate(full, system_prompt=system,
                                      curriculum=curriculum, grade_level=grade_level, mode="learner")
    def generate_teacher_artifact(self, artifact_type, topic, grade_level, curriculum="CBC/CBE"):
        system = (f"You are an expert {curriculum} curriculum designer. {self._guidance(curriculum)} "
                  f"Create a classroom-ready {artifact_type} for {grade_level} on: {topic}. "
                  f"Include objectives, activities, and assessment.")
        return self.provider.generate(
            f"Generate a {artifact_type} on {topic} for {grade_level}.",
            system_prompt=system, artifact_type=artifact_type, topic=topic,
            grade_level=grade_level, curriculum=curriculum, mode="teacher")
