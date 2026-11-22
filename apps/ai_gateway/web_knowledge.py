import json
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
