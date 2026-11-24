import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
inst = Institution.objects.filter(name="Jifunze Test School").first() or Institution.objects.first()
ROWS = [
    ("admin",            "admin12345!",   "platform_admin", True,  True),
    ("Caristus_Mugendi", "admin12345!",   "platform_admin", True,  True),
    ("jifunze.admin",    "Jifunze@2026!", "platform_admin", True,  True),
    ("teacher.demo",     "teach12345!",   "teacher",        False, False),
    ("learner.demo",     "learn12345!",   "learner",        False, False),
    ("parent.demo",      "parent12345!",  "parent",         False, False),
]
for un, pw, role, staff, superuser in ROWS:
    u, created = User.objects.get_or_create(username=un, defaults={"role": role})
    u.role = role
    u.is_staff = staff
    u.is_superuser = superuser
    u.is_active = True
    u.set_password(pw)
    if hasattr(u, "otp_secret"):
        u.otp_secret = ""
    if hasattr(u, "email_verified"):
        u.email_verified = True
    if not u.email:
        u.email = un.replace(".", "_") + "@jifunze.local"
    u.save()
    if inst:
        Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": role, "is_active": True})
    print("reset:", un, "/", pw, "| staff" if staff else "| app-only")
learner = User.objects.filter(username="learner.demo").first()
parent = User.objects.filter(username="parent.demo").first()
if learner and parent and hasattr(parent, "ward"):
    parent.ward = learner
    parent.save()
    print("parent.demo linked to learner.demo")
print("ACCESS RESET COMPLETE")
