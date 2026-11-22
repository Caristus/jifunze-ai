from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from apps.institutions.models import Membership
from apps.resources.models import DocumentChunk, LearningResource
@login_required(login_url="/accounts/login/")
def library_page(request):
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    fields = {f.name for f in LearningResource._meta.fields}
    base_qs = LearningResource.objects.filter(institution=m.institution) if m else LearningResource.objects.none()
    qs = base_qs
    q = request.GET.get("q", "").strip()
    cur = request.GET.get("curriculum", "").strip()
    grade = request.GET.get("grade", "").strip()
    subj = request.GET.get("subject", "").strip()
    tier = request.GET.get("tier", "").strip()
    if q:
        cond = Q(title__icontains=q)
        if "topic" in fields:
            cond |= Q(topic__icontains=q)
        if "subject" in fields:
            cond |= Q(subject__icontains=q)
        qs = qs.filter(cond)
    if cur and "curriculum" in fields:
        qs = qs.filter(curriculum=cur)
    if grade and "grade_level" in fields:
        qs = qs.filter(grade_level=grade)
    if subj and "subject" in fields:
        qs = qs.filter(subject=subj)
    if tier and "provenance_tier" in fields:
        qs = qs.filter(provenance_tier=tier)
    order = "-created_at" if "created_at" in fields else "-id"
    rows = []
    for r in qs.order_by(order)[:200]:
        file_url = ""
        try:
            if getattr(r, "file", None):
                file_url = r.file.url
        except Exception:
            file_url = ""
        rows.append({
            "title": r.title,
            "subject": getattr(r, "subject", ""),
            "grade": getattr(r, "grade_level", ""),
            "curriculum": getattr(r, "curriculum", ""),
            "topic": getattr(r, "topic", ""),
            "tier": getattr(r, "provenance_tier", "A"),
            "license": getattr(r, "license", ""),
            "attribution": getattr(r, "attribution", ""),
            "source_url": getattr(r, "source_url", ""),
            "chunks": DocumentChunk.objects.filter(resource=r).count(),
            "file_url": file_url,
        })
    def distinct(field):
        if not m or field not in fields:
            return []
        return sorted({v for v in base_qs.values_list(field, flat=True) if v})
    counts = {"A": 0, "B": 0, "C": 0}
    for row in rows:
        counts[row["tier"]] = counts.get(row["tier"], 0) + 1
    return render(request, "resources/library.html", {
        "rows": rows, "q": q, "counts": counts,
        "curricula": distinct("curriculum"), "grades": distinct("grade_level"), "subjects": distinct("subject"),
        "sel": {"curriculum": cur, "grade": grade, "subject": subj, "tier": tier},
        "institution": m.institution if m else None,
    })
