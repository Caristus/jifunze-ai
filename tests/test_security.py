import pytest
from django.urls import reverse
pytestmark = pytest.mark.django_db
def test_anonymous_redirected_from_studio(client):
    r = client.get("/studio/")
    assert r.status_code in (302, 403)
    assert "/accounts/login/" in r.get("Location", "/accounts/login/")
def test_anonymous_api_rejected(client):
    r = client.get("/api/teacher/artifacts/recent/")
    assert r.status_code in (401, 403)
def test_library_requires_login(client):
    r = client.get("/library/")
    assert r.status_code in (302, 403)
def test_health_requires_login(client):
    r = client.get("/health/")
    assert r.status_code in (302, 403)
