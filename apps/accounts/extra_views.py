import json
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.signing import BadSignature, TimestampSigner
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from apps.accounts.totp import gen_secret, otpauth_uri, totp, verify
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message
from apps.resources.models import Bookmark, LearningResource
def _m(user):
    return Membership.objects.filter(user=user, is_active=True).first()
@login_required(login_url="/accounts/login/")
def approvals_page(request):
    m = _m(request.user)
    qs = LearningResource.objects.filter(institution=m.institution).order_by("-id") if m else LearningResource.objects.none()
    return render(request, "accounts/approvals.html", {
        "pending": qs.filter(approval_status="pending"),
        "recent": qs.exclude(approval_status="pending")[:15],
        "require": getattr(m.institution, "require_approval", False) if m else False})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def approval_action(request):
    m = _m(request.user)
    data = json.loads(request.body or "{}")
    res = LearningResource.objects.filter(id=data.get("id"), institution=m.institution).first()
    if not res:
        return JsonResponse({"detail": "not found"}, status=404)
    res.approval_status = data.get("status", "approved")
    res.save(update_fields=["approval_status"])
    return JsonResponse({"status": res.approval_status})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def require_approval_toggle(request):
    m = _m(request.user)
    data = json.loads(request.body or "{}")
    if hasattr(m.institution, "require_approval"):
        m.institution.require_approval = bool(data.get("on"))
        m.institution.save()
    return JsonResponse({"on": m.institution.require_approval})
@login_required(login_url="/accounts/login/")
def community_page(request):
    qs = LearningResource.objects.filter(shared_public=True, approval_status="approved").select_related("institution").order_by("-id")[:40]
    return render(request, "accounts/community.html", {"rows": qs})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def share_toggle(request):
    m = _m(request.user)
    data = json.loads(request.body or "{}")
    res = LearningResource.objects.filter(id=data.get("id"), institution=m.institution).first()
    if not res:
        return JsonResponse({"detail": "not found"}, status=404)
    res.shared_public = bool(data.get("on"))
    res.save(update_fields=["shared_public"])
    return JsonResponse({"on": res.shared_public})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def bookmark_toggle(request):
    m = _m(request.user)
    data = json.loads(request.body or "{}")
    res = LearningResource.objects.filter(id=data.get("id"), institution=m.institution).first()
    if not res:
        return JsonResponse({"detail": "not found"}, status=404)
    b = Bookmark.objects.filter(user=request.user, resource=res).first()
    if b:
        b.delete(); on = False
    else:
        Bookmark.objects.create(user=request.user, institution=m.institution, resource=res); on = True
    return JsonResponse({"on": on})
@login_required(login_url="/accounts/login/")
def parent_page(request):
    ward = getattr(request.user, "ward", None)
    data = {"ward": ward, "conversations": [], "topics": []}
    if ward:
        convs = Conversation.objects.filter(user=ward).order_by("-id")[:10]
        data["conversations"] = convs
        data["topics"] = [c.title for c in convs if c.title]
        data["count"] = Conversation.objects.filter(user=ward).count()
        data["messages"] = Message.objects.filter(conversation__user=ward, role="user").count()
    return render(request, "accounts/parent.html", data)
@login_required(login_url="/accounts/login/")
def twofa_page(request):
    u = request.user
    msg = ""
    if request.method == "POST":
        code = request.POST.get("code", "")
        if not u.otp_secret:
            u.otp_secret = gen_secret(); u.save()
            msg = "Secret created. Enter a code from your authenticator to confirm."
        if verify(u.otp_secret, code):
            request.session["2fa_ok"] = True
            return redirect("/")
        msg = "Invalid code. Try again (codes rotate every 30s)."
    uri = otpauth_uri(u.otp_secret, u.username) if u.otp_secret else ""
    return render(request, "accounts/twofa.html", {"secret": u.otp_secret, "uri": uri, "msg": msg,
                                                   "current": totp(u.otp_secret) if u.otp_secret else ""})
@login_required(login_url="/accounts/login/")
def verify_send(request):
    u = request.user
    if not u.email:
        return JsonResponse({"detail": "no email on account"}, status=400)
    token = TimestampSigner().sign(u.email)
    link = request.build_absolute_uri("/accounts/verify/%s/" % token)
    send_mail("Verify your JIFUNZE AI email", "Click to verify: %s" % link, "no-reply@jifunze.ai", [u.email], fail_silently=True)
    return JsonResponse({"sent": True, "link": link})
def verify_confirm(request, token):
    try:
        email = TimestampSigner().unsign(token, max_age=60 * 60 * 48)
    except BadSignature:
        return render(request, "accounts/twofa.html", {"msg": "Invalid or expired verification link.", "secret": "", "uri": "", "current": ""})
    from apps.accounts.models import User
    u = User.objects.filter(email=email).first()
    if u:
        u.email_verified = True; u.save()
    return redirect("/")
