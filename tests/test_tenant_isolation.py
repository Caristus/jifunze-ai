import json
import pytest
from apps.teacher_studio.models import TeachingArtifact
pytestmark = pytest.mark.django_db
def _artifact(inst, user, topic):
    return TeachingArtifact.objects.create(
        institution=inst, created_by=user, artifact_type="lesson_plan",
        topic=topic, content=json.dumps({"kind": "lesson_plan", "title": topic}))
def test_school_cannot_see_other_school_artifacts(client_a, school_a, school_b):
    _artifact(school_a[0], school_a[1], "Photosynthesis")
    _artifact(school_b[0], school_b[1], "Secret B topic")
    r = client_a.get("/api/teacher/artifacts/recent/")
    assert r.status_code == 200
    titles = [x["title"] for x in r.json()]
    assert "Photosynthesis" in titles
    assert "Secret B topic" not in titles
def test_automark_rejects_foreign_artifact(client_a, school_b):
    foreign = _artifact(school_b[0], school_b[1], "Foreign quiz")
    r = client_a.post("/api/teacher/artifacts/automark/",
                      {"artifact_id": str(foreign.id), "answers": {}},
                      content_type="application/json")
    assert r.status_code == 404
