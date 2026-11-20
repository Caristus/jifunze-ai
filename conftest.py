import pytest
from django.contrib.auth import get_user_model
from apps.institutions.models import Institution, Membership
User = get_user_model()
@pytest.fixture
def two_schools(db):
    inst_a = Institution.objects.create(name="School A", country="Kenya")
    inst_b = Institution.objects.create(name="School B", country="Kenya")
    user_a = User.objects.create_user(username="learner_a", password="pass12345!", role="learner")
    user_b = User.objects.create_user(username="learner_b", password="pass12345!", role="learner")
    Membership.objects.create(user=user_a, institution=inst_a, role="learner")
    Membership.objects.create(user=user_b, institution=inst_b, role="learner")
    return inst_a, inst_b, user_a, user_b
