from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import path
from apps.institutions.models import Membership
from apps.learning.models import Conversation
from apps.teacher_studio.models import TeachingArtifact
from apps.audit.models import AuditEvent
@login_required(login_url="/accounts/login/")
def home(request):
    membership = Membership.objects.filter(user=request.user, is_active=True).first()
    institution = membership.institution if membership else None
    context = {
        "membership": membership,
        "institution": institution,
        "conversations": Conversation.objects.filter(user=request.user).count(),
        "artifacts": TeachingArtifact.objects.filter(institution=institution).count() if institution else 0,
        "audit": AuditEvent.objects.filter(institution=institution).count() if institution else 0,
    }
    return render(request, "dashboards/home.html", context)
def set_theme(request, name):
    from django.shortcuts import redirect
    if name == "auto":
        request.session.pop("theme_override", None)
    elif name in ("royal", "forest", "lavender", "burgundy"):
        request.session["theme_override"] = name
    return redirect(request.META.get("HTTP_REFERER") or "/")
