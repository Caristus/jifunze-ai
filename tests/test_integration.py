import json
import pytest
pytestmark = pytest.mark.django_db
def test_generate_then_automark_quiz(client_a):
    r = client_a.post("/api/teacher/artifacts/generate/", {
        "artifact_type": "quiz", "topic": "Photosynthesis", "grade_level": "Form 2",
        "curriculum": "CBC/CBE", "count": 6, "mix": "balanced", "language": "en",
        "duration": 50, "difficulty": "Standard"}, content_type="application/json")
    assert r.status_code == 201
    art = r.json()
    lesson = json.loads(art["content"])
    assert lesson["kind"] == "quiz" and lesson["questions"]
    answers = {str(q["no"]): (q.get("correct") if q["type"] == "mcq" else
                              (q.get("answer") if q["type"] in ("short", "structured") else None))
               for q in lesson["questions"]}
    m = client_a.post("/api/teacher/artifacts/automark/",
                      {"artifact_id": art["id"], "answers": answers},
                      content_type="application/json")
    assert m.status_code == 200
    rep = m.json()
    assert rep["total_marks"] > 0 and 0 <= rep["percentage"] <= 100
def test_transform_improve_creates_version(client_a):
    r = client_a.post("/api/teacher/artifacts/generate/", {
        "artifact_type": "lesson_plan", "topic": "Photosynthesis", "grade_level": "Form 2",
        "curriculum": "CBC/CBE", "language": "en", "duration": 50}, content_type="application/json")
    art = r.json()
    t = client_a.post("/api/teacher/artifacts/transform/",
                      {"artifact_id": art["id"], "action": "improve"},
                      content_type="application/json")
    assert t.status_code == 200
    assert json.loads(t.json()["content"]).get("misconceptions")
