from pathlib import Path
import re, json
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
def w(rel, text):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
# ---------- 1. Open-knowledge fallback service ----------
w("apps/ai_gateway/web_knowledge.py", '''import json
import os
import urllib.parse
import urllib.request
def _get(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": "JIFUNZE-AI/1.0 (educational; contact: maintainer)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())
def openai_answer(question):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from .providers.openai_provider import OpenAIProvider
        text = OpenAIProvider().generate(
            question,
            system_prompt="Give a concise, school-appropriate, factually correct explanation in plain language.")
        return {"engine": "OpenAI", "title": "OpenAI model answer", "url": "", "text": text}
    except Exception:
        return None
def wikipedia_answer(question):
    try:
        q = urllib.parse.quote(question.strip())
        search = _get("https://en.wikipedia.org/w/rest.php/v1/search/page?q=%s&limit=1" % q)
        pages = search.get("pages") or []
        if not pages:
            return None
        title = urllib.parse.quote(pages[0]["title"].replace(" ", "_"))
        summary = _get("https://en.wikipedia.org/api/rest_v1/page/summary/%s" % title)
        extract = (summary.get("extract") or "").strip()
        if not extract:
            return None
        return {"engine": "Wikipedia", "title": summary.get("title", question),
                "url": (summary.get("content_urls") or {}).get("desktop", {}).get("page", ""),
                "text": extract}
    except Exception:
        return None
def duckduckgo_answer(question):
    try:
        q = urllib.parse.quote(question.strip())
        data = _get("https://api.duckduckgo.com/?q=%s&format=json&no_html=1&skip_disambig=1" % q)
        text = (data.get("AbstractText") or "").strip()
        url = data.get("AbstractURL") or ""
        if not text:
            rel = data.get("RelatedTopics") or []
            if rel and isinstance(rel[0], dict):
                text = (rel[0].get("Text") or "").strip()
                url = rel[0].get("FirstURL") or ""
        if not text:
            return None
        return {"engine": "DuckDuckGo", "title": data.get("Heading") or question, "url": url, "text": text}
    except Exception:
        return None
def external_answer(question):
    """Try OpenAI (if configured), then open web sources. Returns dict or None."""
    for fn in (openai_answer, wikipedia_answer, duckduckgo_answer):
        try:
            res = fn(question)
            if res and res.get("text"):
                return res
        except Exception:
            continue
    return None
''')
# ---------- 2. Ask / probe / history endpoints ----------
w("apps/learning/ask_views.py", '''import json
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
def _retrieve(institution, question, k=3):
    qt = _tokens(question)
    if not qt:
        return []
    scored = []
    for c in DocumentChunk.objects.filter(resource__institution=institution).select_related("resource")[:400]:
        ct = set(_tokens(c.chunk_text))
        hit = len([t for t in qt if t in ct])
        if hit:
            scored.append((hit / float(len(qt)), c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored if s > 0][:k]
def _membership(user):
    return Membership.objects.filter(user=user, is_active=True).first()
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
    for msg in Message.objects.filter(conversation=conv).order_by("created_at" if "created_at" in mf else "id"):
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
    chunks = _retrieve(m.institution, q)
    web = None
    if chunks:
        ctx = "\\n".join((c.chunk_text or "")[:700] for c in chunks)
        prompt = "Context from approved school materials:\\n" + ctx + "\\n\\nLearner question: " + q
    else:
        web = external_answer(q)
        if web:
            prompt = ("Context from open knowledge (" + web["engine"] + "):\\n" + web["text"][:1200] +
                      "\\n\\nLearner question: " + q)
        else:
            prompt = "Learner question: " + q
    try:
        from apps.ai_gateway.services import AIGateway
        provider = AIGateway(institution=m.institution).provider
    except Exception:
        provider = None
    if provider is None:
        from apps.ai_gateway.providers.mock_provider import MockProvider
        provider = MockProvider()
    content = provider.generate(
        prompt,
        system_prompt="You are a school tutor. Cite the supplied context. If it is insufficient, say so.",
        mode="learner", curriculum=data.get("curriculum", ""), grade_level=data.get("grade", ""),
        language=data.get("language", "en"))
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
                                  metadata={"grounded": bool(chunks), "web_engine": (web or {}).get("engine", "")})
    except Exception:
        pass
    return JsonResponse({"content": content, "sources": sources, "grounded": bool(chunks),
                         "web_source": web, "conversation_id": str(conv.id)})
''')
up = base / "config/urls.py"
uc = up.read_text(encoding="utf-8")
if "ask_views" not in uc:
    uc = "from apps.learning import ask_views\n" + uc
    uc = re.sub(r'(path\("api/resources/semantic_search/",[^)]*\),)',
                r'\1\n    path("api/learn/ask/", ask_views.ask),\n    path("api/learn/has_sources/", ask_views.has_sources),\n    path("api/learn/history/", ask_views.history),',
                uc, count=1)
    up.write_text(uc, encoding="utf-8")
# ---------- 3. Companion UI with progressive search status ----------
w("templates/learning/companion.html", '''{% extends "base.html" %}
{% block title %}Learning Companion — JIFUNZE AI{% endblock %}
{% block content %}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<style>
  :root{--indigo:#1B1F4B;--green:#10B981;--green2:#0E9F6E;--bg:#FDFCF8;--card:#fff;--ink:#0F172A;--mut:#64748B;--line:#E4E1D6;--soft:#F6F4EC;}
  .cp{font-family:Inter,sans-serif;color:var(--ink);display:grid;grid-template-columns:280px 1fr;gap:1.2rem;height:calc(100vh - 190px);min-height:480px;}
  @media(max-width:900px){.cp{grid-template-columns:1fr;height:auto;}.cp-side{display:none;}}
  .cp-side{background:var(--card);border:1px solid var(--line);border-radius:1rem;padding:1rem;overflow-y:auto;}
  .cp-main{background:var(--card);border:1px solid var(--line);border-radius:1rem;display:flex;flex-direction:column;overflow:hidden;}
  .cp-msgs{flex:1;overflow-y:auto;padding:1.2rem;display:flex;flex-direction:column;gap:1rem;}
  .bub{max-width:78%;padding:.8rem 1rem;border-radius:1rem;font-size:.92rem;line-height:1.55;white-space:pre-wrap;}
  .bub.user{align-self:flex-end;background:var(--green2);color:#fff;border-bottom-right-radius:.3rem;}
  .bub.ai{align-self:flex-start;background:#EAF7F0;color:var(--ink);border-bottom-left-radius:.3rem;}
  .bub.status{align-self:flex-start;background:var(--soft);color:var(--mut);font-size:.82rem;display:flex;align-items:center;gap:.5rem;border:1px dashed var(--line);}
  .spin{width:14px;height:14px;border:2px solid var(--line);border-top-color:var(--indigo);border-radius:50%;animation:sp 0.8s linear infinite;flex-shrink:0;}
  @keyframes sp{to{transform:rotate(360deg);}}
  .src{display:inline-flex;align-items:center;gap:.35rem;font-size:.7rem;font-weight:600;background:#DCFCE7;color:#166534;border:1px solid #BBF7D0;border-radius:9999px;padding:.18rem .6rem;margin:.15rem .2rem 0 0;text-decoration:none;}
  .src.web{background:#E0E7FF;color:#3730A3;border-color:#C7D2FE;}
  .cp-input{display:flex;gap:.6rem;padding:.9rem;border-top:1px solid var(--line);background:#fff;}
  .cp-input textarea{flex:1;border:1px solid var(--line);border-radius:.7rem;padding:.7rem .8rem;font:inherit;font-size:.92rem;resize:none;min-height:46px;max-height:120px;}
  .cp-input textarea:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(27,31,75,.12);}
  .cp-send{background:var(--green2);color:#fff;border:none;border-radius:.7rem;padding:0 1.1rem;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:.4rem;}
  .cp-send:disabled{opacity:.6;cursor:wait;}
  .cv-item{display:block;width:100%;text-align:left;border:1px solid var(--line);border-radius:.6rem;padding:.5rem .65rem;margin-top:.4rem;background:#fff;cursor:pointer;font-size:.8rem;font-weight:600;color:var(--ink);}
  .cv-item:hover{background:var(--soft);}
  .cp select{width:100%;border:1px solid var(--line);border-radius:.6rem;padding:.5rem;font-size:.82rem;background:#fff;margin-top:.4rem;}
</style>
<div class="max-w-7xl mx-auto px-4 py-6">
  <h1 class="text-2xl font-extrabold mb-4" style="font-family:Manrope;color:var(--indigo)">Learning Companion</h1>
  <div class="cp">
    <aside class="cp-side">
      <button id="newBtn" class="cp-send" style="width:100%;padding:.6rem;justify-content:center">+ New conversation</button>
      <label style="font-size:.72rem;font-weight:700;color:var(--mut);display:block;margin-top:.9rem">SUBJECT</label>
      <select id="subj"><option>Biology</option><option>Chemistry</option><option>Physics</option><option>Mathematics</option><option>General</option></select>
      <label style="font-size:.72rem;font-weight:700;color:var(--mut);display:block;margin-top:.6rem">CURRICULUM</label>
      <select id="curr"><option>CBC/CBE</option><option>8-4-4</option><option>Cambridge IGCSE</option><option>IB</option><option>CAPS</option></select>
      <label style="font-size:.72rem;font-weight:700;color:var(--mut);display:block;margin-top:.6rem">GRADE</label>
      <select id="grade"><option>Form 2</option><option>Grade 8</option><option>Year 10</option><option>Standard 4</option></select>
      <label style="font-size:.72rem;font-weight:700;color:var(--mut);display:block;margin-top:.9rem">HISTORY</label>
      <div id="cvList">{% for c in conversations %}<button class="cv-item" data-id="{{ c.id }}">{{ c.title|truncatechars:34 }}</button>{% endfor %}</div>
    </aside>
    <section class="cp-main">
      <div class="cp-msgs" id="msgs">
        <div class="bub ai">Karibu! Ask me anything about your school subjects. I answer from your school's approved materials first, and from open knowledge (Wikipedia / OpenAI) when the library doesn't cover it — always telling you which.</div>
      </div>
      <div class="cp-input">
        <textarea id="q" rows="1" placeholder="Ask anything about your school subjects…"></textarea>
        <button id="send" class="cp-send">Send</button>
      </div>
    </section>
  </div>
</div>
<script>
(function(){
  var msgs=document.getElementById("msgs"),q=document.getElementById("q"),send=document.getElementById("send");
  var convId=null;
  function csrf(){return (document.cookie.match(/csrftoken=([^;]+)/)||[])[1]||"";}
  function scroll(){msgs.scrollTop=msgs.scrollHeight;}
  function bub(cls,text){var d=document.createElement("div");d.className="bub "+cls;d.textContent=text;msgs.appendChild(d);scroll();return d;}
  function chips(node,sources,web){
    (sources||[]).forEach(function(t){var a=document.createElement("span");a.className="src";a.textContent="📄 "+t;node.parentNode.insertBefore(a,node.nextSibling);});
    if(web){var a=document.createElement("a");a.className="src web";a.textContent="🌐 "+web.engine+" · "+web.title;a.href=web.url||"#";a.target="_blank";node.parentNode.insertBefore(a,node.nextSibling);}
  }
  function statusBubble(){var d=document.createElement("div");d.className="bub status";d.innerHTML='<span class="spin"></span><span class="st">Searching your school library…</span>';msgs.appendChild(d);scroll();return d;}
  function setStatus(sb,text,done){var s=sb.querySelector(".st");s.textContent=text;if(done){var sp=sb.querySelector(".spin");if(sp)sp.remove();}}
  function ask(){
    var text=q.value.trim();if(!text)return;
    q.value="";send.disabled=true;
    bub("user",text);
    var sb=statusBubble();
    fetch("/api/learn/has_sources/?q="+encodeURIComponent(text),{credentials:"same-origin"})
      .then(function(r){return r.json();}).then(function(p){
        setStatus(sb, p.count? ("Found "+p.count+" school source"+(p.count>1?"s":"")+" — composing answer…") : "Not in your school library — consulting open knowledge (Wikipedia / OpenAI)…");
      }).catch(function(){});
    fetch("/api/learn/ask/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":csrf(),"Content-Type":"application/json"},
      body:JSON.stringify({question:text,conversation_id:convId,subject:document.getElementById("subj").value,
        curriculum:document.getElementById("curr").value,grade:document.getElementById("grade").value})})
      .then(function(r){return r.json();}).then(function(d){
        sb.remove();
        var node=bub("ai",d.content||"");
        var wrap=document.createElement("div");wrap.style.alignSelf="flex-start";
        node.parentNode.insertBefore(wrap,node.nextSibling);
        (d.sources||[]).forEach(function(t){var a=document.createElement("span");a.className="src";a.textContent="📄 "+t;wrap.appendChild(a);});
        if(d.web_source){var a=document.createElement("a");a.className="src web";a.textContent="🌐 "+d.web_source.engine+" · "+d.web_source.title;a.href=d.web_source.url||"#";a.target="_blank";wrap.appendChild(a);}
        convId=d.conversation_id;scroll();
      }).catch(function(e){sb.remove();bub("ai","Sorry — something went wrong: "+e.message);})
      .finally(function(){send.disabled=false;q.focus();});
  }
  send.onclick=ask;
  q.addEventListener("keydown",function(e){if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();ask();}});
  document.getElementById("newBtn").onclick=function(){convId=null;msgs.innerHTML="";bub("ai","New conversation started. Ask me anything!");};
  Array.prototype.forEach.call(document.querySelectorAll(".cv-item"),function(b){
    b.onclick=function(){
      convId=b.dataset.id;msgs.innerHTML="";
      fetch("/api/learn/history/?id="+convId,{credentials:"same-origin"}).then(function(r){return r.json();}).then(function(j){
        (j.messages||[]).forEach(function(m){bub(m.role==="user"?"user":"ai",m.content);
          (m.sources||[]).forEach(function(t){var a=document.createElement("span");a.className="src";a.textContent="📄 "+t;msgs.appendChild(a);});});
        if(!(j.messages||[]).length)bub("ai","(empty conversation)");
      });
    };
  });
})();
</script>
{% endblock %}''')
print("COMPANION: PROGRESSIVE SEARCH STATUS + WEB FALLBACK INSTALLED")
