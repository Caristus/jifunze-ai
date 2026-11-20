import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.resources.models import DocumentChunk
@pytest.mark.django_db
def test_full_learning_workflow(two_schools, client):
    inst_a, inst_b, user_a, user_b = two_schools
    client.force_login(user_a)
    upload = SimpleUploadedFile("notes.txt", b"Photosynthesis converts light energy into chemical energy in chloroplasts.", content_type="text/plain")
    resp = client.post("/upload/", {"files": [upload], "paths": ["Biology/Form 2/notes.txt"], "subject": "", "grade_level": ""})
    assert resp.status_code == 200
    assert DocumentChunk.objects.filter(resource__institution=inst_a).count() >= 1
    resp = client.post("/api/learning/conversations/", {"title": "Biology help"}, content_type="application/json")
    assert resp.status_code == 201
    conv_id = resp.json()["id"]
    resp = client.post(
        f"/api/learning/conversations/{conv_id}/chat/",
        {"prompt": "What is photosynthesis?"}, content_type="application/json")
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "assistant"
    assert len(body["sources"]) >= 1, "AI answer must cite school resources"
