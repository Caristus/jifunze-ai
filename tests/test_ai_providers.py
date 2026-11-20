import pytest
from apps.ai_gateway.providers import MockProvider, OllamaProvider
from apps.ai_gateway.services import AIGateway
from apps.institutions.models import Institution
@pytest.fixture
def test_institution(db):
    return Institution.objects.create(name="Test School")
@pytest.mark.django_db
def test_mock_provider_generates_response():
    provider = MockProvider()
    response = provider.generate("What is photosynthesis?")
    assert "photosynthesis" in response.lower()
    assert len(response) > 50
@pytest.mark.django_db
def test_ollama_provider_handles_connection_error():
    provider = OllamaProvider(base_url="http://localhost:99999")
    response = provider.generate("test")
    assert "not available" in response.lower() or "error" in response.lower()
@pytest.mark.django_db
def test_ai_gateway_uses_institution_config(test_institution):
    test_institution.ai_provider = "mock"
    test_institution.save()
    gateway = AIGateway(institution=test_institution)
    assert gateway.provider.provider_name == "mock"
    response = gateway.generate_learning_response("Test question")
    assert len(response) > 0
