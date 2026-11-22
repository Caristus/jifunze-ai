import json
import os
import time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from django.core.cache import cache
from django.test import Client
from apps.accounts.models import User
from apps.accounts.totp import gen_secret, totp
from apps.institutions.models import Institution, Membership
from apps.resources.models import LearningResource
inst, _ = Institution.objects.get_or_create(name="Verify School", defaults={"country": "Kenya"})
def mkuser(un, role):
    u, _ = User.objects.get_or_create(username=un, defaults={"role": role})
    u.role = role
    u.set_password("pass12345!")
    u.save()
    Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": role, "is_active": True})
    return u
admin = mkuser("verify_admin", "school_admin")
teacher = mkuser("verify_teacher", "teacher")
learner = mkuser("verify_learner", "learner")
parent = mkuser("verify_parent", "parent")
parent.ward = learner
parent.save()
res, _ = LearningResource.objects.get_or_create(institution=inst, title="Verify Resource",
                                                defaults={"status": "ready", "uploaded_by": teacher})
if hasattr(res, "approval_status"):
    res.approval_status = "pending"
if hasattr(res, "shared_public"):
    res.shared_public = False
res.save()
c_admin, c_teacher, c_learner, c_parent = Client(), Client(), Client(), Client()
c_admin.force_login(admin); c_teacher.force_login(teacher)
c_learner.force_login(learner); c_parent.force_login(parent)
results = []
def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, "EXCEPTION: %s" % e
    results.append((name, ok, detail))
def f_parent():
    r = c_parent.get("/parent/")
    d = r.content.decode()
    return (r.status_code == 200 and ("Progress" in d or learner.username in d or "topics" in d.lower())), "status=%s" % r.status_code
def f_approvals():
    before = "Verify Resource" in c_learner.get("/library/").content.decode()
    r = c_admin.post("/approvals/action/", data=json.dumps({"id": str(res.id), "status": "approved"}), content_type="application/json")
    after = "Verify Resource" in c_learner.get("/library/").content.decode()
    return (not before and r.status_code == 200 and after), "hidden_before=%s approve=%s visible_after=%s" % (not before, r.status_code, after)
def f_sharing():
    res.refresh_from_db()
    res.shared_public = True
    res.save()
    res.refresh_from_db()
    d = c_teacher.get("/community/").content.decode()
    found = "Verify Resource" in d
    return found, ("found=%s approval=%s shared=%s" % (found, res.approval_status, res.shared_public))
def f_bookmarks():
    r = c_learner.post("/bookmark/toggle/", data=json.dumps({"id": str(res.id)}), content_type="application/json")
    on = r.json().get("on")
    d = c_learner.get("/library/?bookmarks=1").content.decode()
    listed = "Verify Resource" in d
    from apps.resources.models import Bookmark
    bm_count = Bookmark.objects.filter(user=learner, resource=res).count()
    c_learner.post("/bookmark/toggle/", data=json.dumps({"id": str(res.id)}), content_type="application/json")
    return (on is True and listed), ("toggled=%s listed=%s bookmark_count=%s" % (on, listed, bm_count))
def f_analytics():
    r = c_admin.get("/analytics/")
    return (r.status_code == 200), "status=%s" % r.status_code
def f_2fa():
    admin.otp_secret = gen_secret()
    admin.save()
    c2 = Client(); c2.force_login(admin)
    r = c2.get("/")
    redirected = r.status_code == 302 and "/accounts/2fa/" in r.get("Location", "")
    r2 = c2.post("/accounts/2fa/", {"code": totp(admin.otp_secret)})
    verified = r2.status_code == 302
    r3 = c2.get("/")
    inside = r3.status_code == 200
    admin.otp_secret = ""
    admin.save()
    return (redirected and verified and inside), "redirect=%s verify=%s inside=%s" % (redirected, verified, inside)
def f_email():
    learner.email = "verify_learner@example.com"
    learner.email_verified = False
    learner.save()
    r = c_learner.get("/accounts/verify/send/")
    link = r.json().get("link", "")
    token = link.rstrip("/").split("/")[-1]
    Client().get("/accounts/verify/%s/" % token)
    learner.refresh_from_db()
    return (learner.email_verified is True), "verified=%s" % learner.email_verified
def f_ratelimit():
    key = "rl:%s:%d" % (learner.id, int(time.time() // 60))
    cache.set(key, 60, 60)
    r = c_learner.post("/api/learn/ask/", data="{}", content_type="application/json")
    cache.delete(key)
    return (r.status_code == 429), "status=%s (expect 429)" % r.status_code
def f_apidocs():
    r = c_admin.get("/api/docs/")
    d = r.content.decode()
    return (r.status_code == 200 and "api/" in d), "status=%s" % r.status_code
check("1 Parent/guardian portal", f_parent)
check("2 Resource approval workflow", f_approvals)
check("3 Teacher resource sharing", f_sharing)
check("4 Bookmarking / favorites", f_bookmarks)
check("5 Advanced analytics dashboard", f_analytics)
check("6 Two-factor auth for admins", f_2fa)
check("7 Email verification", f_email)
check("8 API rate limiting", f_ratelimit)
check("9 API documentation", f_apidocs)
print("")
print("=" * 64)
passed = 0
for name, ok, detail in results:
    passed += 1 if ok else 0
    print("%-38s %s   %s" % (name, "PASS" if ok else "FAIL", detail))
print("=" * 64)
print("CONFIRMED %d / 9 PHASE-2 FEATURES" % passed)
