from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.institutions.models import Membership
from apps.learning.semantic import semantic_search
@login_required(login_url="/accounts/login/")
def search(request):
    q = (request.GET.get("q") or "").strip()
    m = Membership.objects.filter(user=request.user, is_active=True).first()
    if not m or not q:
        return JsonResponse({"results": []})
    return JsonResponse({"results": semantic_search(m.institution, q, 8)})
