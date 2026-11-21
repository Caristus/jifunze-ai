import os, django, traceback
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.test import Client
from apps.accounts.models import User
u = User.objects.get(username="Caristus_Mugendi")
c = Client()
c.force_login(u)
try:
    r = c.post(
        "/api/teacher/artifacts/generate/",
        data='{"artifact_type":"lesson_plan","topic":"Photosynthesis","grade_level":"Form 2","curriculum":"Cambridge IGCSE"}',
        content_type="application/json",
    )
    print("STATUS:", r.status_code)
    if r.status_code != 201:
        print(r.content[:3000].decode("utf-8", "ignore"))
except Exception:
    traceback.print_exc()
