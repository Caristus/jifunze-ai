from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message
from apps.resources.models import Bookmark, LearningResource
from apps.teacher_studio.models import TeachingArtifact
@login_required(login_url="/accounts/login/")
def analytics_page(request):
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    if not m:
        return render(request, "dashboard/analytics.html", {"empty": True})
    inst = m.institution
    now = timezone.localtime()
    days = []
    for i in range(13, -1, -1):
        d = (now - timedelta(days=i)).date()
        days.append({"date": d.strftime("%d/%m"),
                     "conv": Conversation.objects.filter(institution=inst, created_at__date=d).count(),
                     "art": TeachingArtifact.objects.filter(institution=inst, created_at__date=d).count()})
    by_type = {}
    for a in TeachingArtifact.objects.filter(institution=inst):
        by_type[a.artifact_type] = by_type.get(a.artifact_type, 0) + 1
    by_subject = {}
    for r in LearningResource.objects.filter(institution=inst):
        s = getattr(r, "subject", "") or "General"
        by_subject[s] = by_subject.get(s, 0) + 1
    marks = AuditEvent.objects.filter(institution=inst, action="QUIZ_AUTO_MARKED")
    pcts = [(e.metadata or {}).get("percent") for e in marks]
    pcts = [p for p in pcts if isinstance(p, (int, float))]
    week_ago = now - timedelta(days=7)
    active_users = AuditEvent.objects.filter(institution=inst, created_at__gte=week_ago).exclude(actor=None).values("actor").distinct().count()
    return render(request, "dashboard/analytics.html", {
        "days": days, "by_type": by_type, "by_subject": by_subject,
        "avg": round(sum(pcts) / len(pcts), 1) if pcts else None,
        "marks": len(pcts), "active_users": active_users,
        "resources": LearningResource.objects.filter(institution=inst).count(),
        "bookmarks": Bookmark.objects.filter(institution=inst).count(),
        "conversations": Conversation.objects.filter(institution=inst).count(),
        "messages": Message.objects.filter(conversation__institution=inst).count(),
    })
