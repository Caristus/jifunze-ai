import pytest
from apps.governance.models import DataRequest
from apps.learning.models import Conversation
@pytest.mark.django_db
def test_api_requires_authentication(client, db):
    resp = client.get("/api/learning/conversations/")
    assert resp.status_code in (401, 403)
@pytest.mark.django_db
def test_learner_cannot_resolve_data_request(two_schools, client):
    inst_a, inst_b, user_a, user_b = two_schools
    dr = DataRequest.objects.create(institution=inst_a, requested_by=user_a, request_type="deletion")
    client.force_login(user_a)
    resp = client.post(
        f"/api/governance/requests/{dr.id}/resolve/",
        {"decision": "completed"}, content_type="application/json")
    assert resp.status_code == 403
@pytest.mark.django_db
def test_admin_completion_executes_real_deletion(two_schools, client):
    inst_a, inst_b, user_a, user_b = two_schools
    user_a.role = "school_admin"
    user_a.save()
    Conversation.objects.create(institution=inst_a, user=user_a, title="doomed")
    dr = DataRequest.objects.create(institution=inst_a, requested_by=user_a, request_type="deletion")
    client.force_login(user_a)
    resp = client.post(
        f"/api/governance/requests/{dr.id}/resolve/",
        {"decision": "completed"}, content_type="application/json")
    assert resp.status_code == 200
    assert Conversation.objects.filter(user=user_a, institution=inst_a).count() == 0
