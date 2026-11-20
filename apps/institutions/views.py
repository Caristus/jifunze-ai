import csv
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from apps.institutions.models import Institution, Membership
User = get_user_model()
@login_required(login_url="/accounts/login/")
def bulk_onboard(request):
    membership = Membership.objects.filter(user=request.user, is_active=True, role__in=["school_admin", "admin"]).first()
    if not membership:
        messages.error(request, "Only School Administrators can perform bulk onboarding.")
        return redirect("home")
    institution = membership.institution
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)
        success_count = 0
        error_count = 0
        for row in reader:
            username = row.get("username", "").strip()
            email = row.get("email", "").strip()
            role = row.get("role", "learner").strip().lower()
            if not username or role not in ["learner", "teacher", "school_admin"]:
                error_count += 1
                continue
            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"email": email, "role": role}
                )
                Membership.objects.get_or_create(
                    user=user,
                    institution=institution,
                    defaults={"role": role, "is_active": True}
                )
                success_count += 1
            except Exception:
                error_count += 1
        messages.success(request, f"Bulk onboarded {success_count} users. {error_count} errors/skipped.")
        return redirect("bulk_onboard")
    return render(request, "institutions/bulk_onboard.html", {"institution": institution})
