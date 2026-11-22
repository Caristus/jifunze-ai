import json
import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message
def _m(user):
    return Membership.objects.filter(user=user, is_active=True).first()
@login_required(login_url="/accounts/login/")
def centre_page(request):
    m = _m(request.user)
    inst = m.institution if m else None
    consent = []
    requests_ = []
    try:
        from apps.governance.models import ConsentRecord, DataRequest
        consent = list(ConsentRecord.objects.filter(institution=inst).order_by("-id")[:20]) if inst else []
        requests_ = list(DataRequest.objects.filter(institution=inst).order_by("-id")[:20]) if inst else []
    except Exception:
        pass
    audit = list(AuditEvent.objects.filter(institution=inst).order_by("-id")[:30]) if inst else []
    provider = getattr(inst, "ai_provider", "") or os.environ.get("AI_PROVIDER", "mock")
    model = getattr(inst, "ai_model", "") or os.environ.get("OPENAI_MODEL", os.environ.get("OLLAMA_MODEL", "mock-dev-mode"))
    retention = getattr(inst, "retention_days", 365)
    return render(request, "governance/centre.html", {
        "consent": consent, "requests": requests_, "audit": audit,
        "provider": provider, "model": model, "retention": retention, "institution": inst})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def centre_action(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    m = _m(request.user)
    if not m:
        return JsonResponse({"detail": "no institution"}, status=400)
    data = json.loads(request.body or "{}")
    act = data.get("action")
    if act == "retention":
        if hasattr(m.institution, "retention_days"):
            m.institution.retention_days = int(data.get("days", 365))
            m.institution.save()
        return JsonResponse({"saved": True})
    if act == "request":
        try:
            from apps.governance.models import DataRequest
            drf = {f.name for f in DataRequest._meta.fields}
            dk = {"institution": m.institution, "user": request.user}
            for f in ("request_type", "type"):
                if f in drf:
                    dk[f] = data.get("type", "export")
            for f in ("status",):
                if f in drf:
                    dk[f] = "pending"
            DataRequest.objects.create(**{k: v for k, v in dk.items() if k in drf})
            return JsonResponse({"created": True})
        except Exception as e:
            return JsonResponse({"detail": str(e)}, status=400)
    if act == "delete":
        convs = Conversation.objects.filter(user=request.user, institution=m.institution)
        Message.objects.filter(conversation__in=convs).delete()
        n = convs.count()
        convs.delete()
        AuditEvent.objects.create(institution=m.institution, actor=request.user, action="DATA_DELETED",
                                  resource_type="User", resource_id=str(request.user.id),
                                  metadata={"conversations": n})
        return JsonResponse({"deleted": n})
    return JsonResponse({"detail": "unknown action"}, status=400)
@login_required(login_url="/accounts/login/")
def centre_export(request):
    m = _m(request.user)
    convs = Conversation.objects.filter(user=request.user, institution=m.institution) if m else Conversation.objects.none()
    payload = {
        "user": request.user.username,
        "institution": m.institution.name if m else "",
        "conversations": [
            {"title": c.title, "messages": [{"role": getattr(msg, "role", ""), "content": msg.content}
                                            for msg in Message.objects.filter(conversation=c).order_by("id")]}
            for c in convs],
    }
    resp = HttpResponse(json.dumps(payload, indent=2), content_type="application/json")
    resp["Content-Disposition"] = 'attachment; filename="jifunze_my_data.json"'
    return resp
