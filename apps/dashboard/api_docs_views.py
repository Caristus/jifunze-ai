from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import get_resolver
def _walk(resolver, prefix=""):
    out = []
    for p in resolver.url_patterns:
        pat = prefix + str(p.pattern)
        if hasattr(p, "url_patterns"):
            out += _walk(p, pat)
        else:
            out.append((pat, getattr(p, "name", "")))
    return out
@login_required(login_url="/accounts/login/")
def api_docs_page(request):
    rows = [(pat, name) for pat, name in _walk(get_resolver()) if pat.startswith("api/")]
    rows.sort()
    return render(request, "dashboard/api_docs.html", {"rows": rows})
