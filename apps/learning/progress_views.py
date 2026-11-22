from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message, MessageSource
def fields(model):
    return {f.name for f in model._meta.fields}
@login_required(login_url="/accounts/login/")
def progress(request):
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    if not m:
        return JsonResponse({"sessions": 0, "messages": 0, "sources": 0, "days": [], "topics": []})
    cf = fields(Conversation)
    convs = Conversation.objects.filter(institution=m.institution)
    if "user" in cf:
        convs = convs.filter(user=request.user)
    mf = fields(Message)
    msgs = Message.objects.filter(conversation__in=convs)
    learner = msgs.filter(role="user") if "role" in mf else msgs
    sources = MessageSource.objects.filter(message__in=msgs).count() if "message" in fields(MessageSource) else 0
    now = timezone.localtime()
    days = []
    for i in range(6, -1, -1):
        d = (now - timedelta(days=i)).date()
        n = 0
        if "created_at" in cf:
            n += convs.filter(created_at__date=d).count()
        if "created_at" in mf:
            n += msgs.filter(created_at__date=d).count()
        days.append({"date": d.strftime("%a"), "count": n})
    topics = []
    if "title" in cf:
        topics = [t for t in convs.values_list("title", flat=True) if t][:6]
    return JsonResponse({"sessions": convs.count(), "messages": learner.count(), "sources": sources,
                         "active_days": sum(1 for d in days if d["count"]), "days": days, "topics": topics})
