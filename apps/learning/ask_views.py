import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.ai_gateway.web_knowledge import external_answer
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
from apps.learning.models import Conversation, Message, MessageSource
from apps.resources.models import DocumentChunk
def fields(model):
    return {f.name for f in model._meta.fields}
def _tokens(text):
    return [t for t in "".join(ch if ch.isalnum() else " " for ch in (text or "").lower()).split() if len(t) > 2]
def _retrieve(institution, question, k=3, subject="", approved_only=False):
    qt = _tokens(question)
    if not qt:
        return []
    scored = []
    qs = DocumentChunk.objects.filter(resource__institution=institution).select_related("resource")
    if approved_only:
        qs = qs.filter(resource__approval_status="approved")
    for c in qs[:400]:
        ct = set(_tokens(c.chunk_text))
        hit = len([t for t in qt if t in ct])
        if hit:
            score = hit / float(len(qt))
            if subject and subject != "General" and getattr(c.resource, "subject", "") == subject:
                score *= 1.6
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored if s > 0][:k]
def _membership(user):
    return Membership.objects.filter(user=user, is_active=True).first()
def _fallback_answer(chunks, web, grade, curriculum, subject, lang):
    """Composes a direct tutor-style answer from retrieved context (never dumps passages)."""
    import re as _re
    sw = lang == "sw"
    tone = ("Hii hapa ni jibu moja kwa moja:" if sw else "Here's a direct answer:")
    body = ""
    if chunks:
        sents = [s.strip() for c in chunks for s in _re.split(r"[.!?]\n?|\n", c.chunk_text or "") if len(s.strip()) > 20]
        body = ". ".join(sents[:2]) + "." if sents else (chunks[0].chunk_text or "")[:300]
    elif web:
        sents = [s.strip() for s in _re.split(r"[.!?]\n?|\n", web["text"]) if len(s.strip()) > 20]
        body = ". ".join(sents[:2]) + "." if sents else web["text"][:300]
    else:
        body = ("Sitakuwa na nyenzo za kutosha kujibu moja kwa moja — tafadhali jaribu istilahi nyingine au uliza mwalimu wako."
                if sw else
                "I don't have enough material to answer directly — try a different term or ask your teacher.")
    sig = "(" + (curriculum or "") + " · " + str(grade or "—") + (" · " + subject if subject and subject != "General" else "") + ")"
    return tone + "\n\n" + body + "\n\n" + sig
@login_required(login_url="/accounts/login/")
def has_sources(request):
    m = _membership(request.user)
    q = (request.GET.get("q") or "").strip()
    if not m or not q:
        return JsonResponse({"count": 0, "titles": []})
    chunks = _retrieve(m.institution, q)
    return JsonResponse({"count": len(chunks), "titles": [c.resource.title for c in chunks]})
@login_required(login_url="/accounts/login/")
def history(request):
    m = _membership(request.user)
    cid = request.GET.get("id")
    conv = Conversation.objects.filter(id=cid, institution=m.institution).first() if m and cid else None
    if not conv:
        return JsonResponse({"messages": []})
    mf, sf = fields(Message), fields(MessageSource)
    out = []
    order = "created_at" if "created_at" in mf else "id"
    for msg in Message.objects.filter(conversation=conv).order_by(order):
        srcs = []
        if "message" in sf:
            for s in MessageSource.objects.filter(message=msg):
                srcs.append(getattr(getattr(s, "resource", None), "title", ""))
        out.append({"role": getattr(msg, "role", "assistant"), "content": msg.content, "sources": [x for x in srcs if x]})
    return JsonResponse({"messages": out})
@csrf_exempt
@login_required(login_url="/accounts/login/")
def ask(request):
    if request.method != "POST":
        return JsonResponse({"detail": "POST only"}, status=405)
    try:
        data = json.loads(request.body or "{}")
    except Exception:
        data = {}
    m = _membership(request.user)
    if not m:
        return JsonResponse({"detail": "You must belong to an institution."}, status=400)
    q = (data.get("question") or "").strip()
    if not q:
        return JsonResponse({"detail": "Empty question."}, status=400)
    lang = data.get("language", "en")
    subject = (data.get("subject") or "General").strip()
    grade = (data.get("grade") or "").strip()
    curriculum = (data.get("curriculum") or "").strip()
    cf, mf, sf = fields(Conversation), fields(Message), fields(MessageSource)
    conv = None
    if data.get("conversation_id"):
        conv = Conversation.objects.filter(id=data["conversation_id"], institution=m.institution).first()
    if not conv:
        ckwargs = {"institution": m.institution, "title": q[:60]}
        if "user" in cf:
            ckwargs["user"] = request.user
        for f in ("subject", "curriculum", "grade_level"):
            if f in cf and data.get(f):
                ckwargs[f] = data[f]
        conv = Conversation.objects.create(**ckwargs)
    mkwargs = {"conversation": conv, "content": q}
    if "role" in mf:
        mkwargs["role"] = "user"
    Message.objects.create(**mkwargs)
    chunks = _retrieve(m.institution, q, 3, subject, approved_only=(request.user.role in ("learner", "parent")))
    web = None
    if chunks:
        ctx = "\n".join((c.chunk_text or "")[:700] for c in chunks)
        prompt = "Context from approved school materials:\n" + ctx + "\n\nLearner question: " + q
    else:
        web = external_answer(q)
        if web:
            prompt = "Context from open knowledge (" + web["engine"] + "):\n" + web["text"][:1200] + "\n\nLearner question: " + q
        else:
            prompt = "Learner question: " + q
    debug = ""
    content = None
    try:
        provider = None
        try:
            from apps.ai_gateway.services import AIGateway
            provider = AIGateway(institution=m.institution).provider
        except Exception as e1:
            debug = "gateway:%s" % e1
        if provider is None:
            from apps.ai_gateway.providers.mock_provider import MockProvider
            provider = MockProvider()
        content = provider.generate(
            prompt,
            system_prompt="You are a school tutor. Cite the supplied context. If it is insufficient, say so.",
            mode="learner", curriculum=curriculum, grade_level=grade, language=lang, subject=subject)
    except Exception as e2:
        debug = (debug + " | generate:%s" % e2).strip(" |")
        content = None
    if not content or not str(content).strip():
        content = _fallback_answer(chunks, web, grade, curriculum, subject, lang)
        if debug:
            content += "\n\n[provider debug: " + debug + "]"
    content = str(content)
    akwargs = {"conversation": conv, "content": content}
    if "role" in mf:
        akwargs["role"] = "assistant"
    amsg = Message.objects.create(**akwargs)
    sources = []
    if chunks and "message" in sf:
        for c in chunks:
            skwargs = {"message": amsg}
            if "resource" in sf:
                skwargs["resource"] = c.resource
            if "chunk" in sf:
                skwargs["chunk"] = c
            try:
                MessageSource.objects.create(**skwargs)
            except Exception:
                pass
            sources.append(c.resource.title)
    try:
        AuditEvent.objects.create(institution=m.institution, actor=request.user, action="LEARN_ASK",
                                  resource_type="Conversation", resource_id=str(conv.id),
                                  metadata={"grounded": bool(chunks), "web_engine": (web or {}).get("engine", ""),
                                            "provider_debug": debug})
    except Exception:
        pass
    return JsonResponse({"content": content, "sources": sources, "grounded": bool(chunks),
                         "web_source": web, "conversation_id": str(conv.id)})
