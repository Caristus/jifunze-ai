import csv
import io
import random
import string
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
def _parse(text):
    rows = []
    reader = csv.reader(io.StringIO(text or ""))
    for r in reader:
        r = [c.strip() for c in r if c.strip()]
        if not r:
            continue
        if r[0].lower() in ("username", "name"):
            continue
        username = r[0]
        role = r[1] if len(r) > 1 else "learner"
        grade = r[2] if len(r) > 2 else ""
        rows.append((username, role, grade))
    return rows
@login_required(login_url="/accounts/login/")
def onboard_page(request):
    results = request.session.pop("onboard_results", None)
    return render(request, "accounts/onboard.html", {"results": results})
@login_required(login_url="/accounts/login/")
def onboard_run(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    inst = m.institution if m else Institution.objects.first()
    text = request.POST.get("csv", "")
    if request.FILES.get("file"):
        text = request.FILES["file"].read().decode("utf-8-sig", errors="ignore")
    rows = _parse(text)
    results = []
    for username, role, grade in rows:
        password = "Jif!" + "".join(random.choices(string.digits, k=4))
        u, created = User.objects.get_or_create(username=username, defaults={"role": role})
        if created:
            u.set_password(password)
            u.save()
        else:
            password = "(existing user)"
        Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": role, "is_active": True})
        results.append({"username": username, "role": role, "grade": grade, "password": password, "created": created})
    request.session["onboard_results"] = results
    return redirect("/onboard/")
@login_required(login_url="/accounts/login/")
def onboard_csv(request):
    results = request.session.get("onboard_results") or []
    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = 'attachment; filename="jifunze_credentials.csv"'
    writer = csv.writer(resp)
    writer.writerow(["username", "role", "grade", "temporary_password"])
    for r in results:
        writer.writerow([r["username"], r["role"], r["grade"], r["password"]])
    return resp
