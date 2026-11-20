from apps.ai_gateway.providers import MockProvider, OllamaProvider
from apps.institutions.models import Institution
import logging
logger = logging.getLogger(__name__)
class AIGateway:
    """Central AI orchestration layer with provider abstraction."""
    PROVIDERS = {
        "mock": MockProvider,
        "ollama": OllamaProvider,
    }
    def __init__(self, institution: Institution = None):
        self.institution = institution
        self.provider = self._get_provider()
    def _get_provider(self):
        """Get provider based on institution configuration."""
        if self.institution and hasattr(self.institution, "ai_provider"):
            provider_name = self.institution.ai_provider or "mock"
            model = getattr(self.institution, "ai_model", None)
        else:
            provider_name = "mock"
            model = None
        provider_class = self.PROVIDERS.get(provider_name, MockProvider)
        if provider_name == "ollama":
            return provider_class(model=model or "llama3.2")
        return provider_class()
    def generate_learning_response(self, message: str, context: str = None) -> str:
        """Generate grounded learning response."""
        system_prompt = """You are a helpful educational assistant for African schools.
You answer questions based ONLY on the provided context from the school's approved materials.
If the context doesn't contain the answer, say so clearly rather than guessing.
Keep responses age-appropriate and aligned with local curricula (CBC/CBE, Cambridge)."""
        full_prompt = message
        if context:
            full_prompt = f"Context from school materials:\n{context}\n\nQuestion: {message}"
        return self.provider.generate(
            prompt=full_prompt,
            system_prompt=system_prompt,
            context_preview=context
        )
    def generate_teacher_artifact(self, artifact_type: str, topic: str, grade_level: str, curriculum: str = None) -> str:
        """Generate teaching materials."""
        curriculum_context = f" for {curriculum}" if curriculum else ""
        system_prompt = f"""You are an expert curriculum designer{curriculum_context}.
Create high-quality {artifact_type}s that are:
- Age-appropriate for {grade_level}
- Aligned with {curriculum or 'local educational standards'}
- Engaging and practical for classroom use"""
        prompt = f"""Create a {artifact_type} for {grade_level} on the topic: {topic}
Include:
- Clear learning objectives
- Structured content with examples
- Assessment questions or activities
- Teacher notes or facilitation guidance"""
        return self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )
