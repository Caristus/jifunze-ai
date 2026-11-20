import pytest
from apps.learning.models import Conversation
@pytest.mark.django_db
def test_learner_sees_only_own_school_conversations(two_schools, client):
    inst_a, inst_b, user_a, user_b = two_schools
    Conversation.objects.create(institution=inst_a, user=user_a, title="School A secret")
    client.force_login(user_b)
    resp = client.get("/api/learning/conversations/")
    assert resp.status_code == 200
    assert resp.json()["count"] == 0
@pytest.mark.django_db
def test_conversation_detail_blocked_across_schools(two_schools, client):
    inst_a, inst_b, user_a, user_b = two_schools
    conv = Conversation.objects.create(institution=inst_a, user=user_a, title="private")
    client.force_login(user_b)
    resp = client.get(f"/api/learning/conversations/{conv.id}/")
    assert resp.status_code == 404
