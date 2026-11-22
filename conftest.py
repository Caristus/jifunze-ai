import pytest
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
def _make_school(suffix, role="teacher"):
    inst = Institution.objects.create(name="School %s" % suffix, country="Kenya")
    user = User.objects.create_user(username="user_%s" % suffix, password="pass12345!")
    user.role = role
    user.save()
    Membership.objects.create(user=user, institution=inst, role=role, is_active=True)
    return inst, user
@pytest.fixture
def school_a(db):
    return _make_school("a")
@pytest.fixture
def school_b(db):
    return _make_school("b")
@pytest.fixture
def client_a(client, school_a):
    client.force_login(school_a[1])
    return client
