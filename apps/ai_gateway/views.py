from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.institutions.models import Institution, Membership
@login_required
def ai_config(request):
    """Configure AI provider for the user's institution."""
    membership = Membership.objects.filter(user=request.user, is_active=True).first()
    if not membership:
        messages.error(request, "You must be a member of an institution to configure AI.")
        return redirect("dashboard")
    institution = membership.institution
    if request.method == "POST":
        institution.ai_provider = request.POST.get("ai_provider", "mock")
        if institution.ai_provider == "ollama":
            institution.ai_model = request.POST.get("ai_model", "llama3.2")
        else:
            institution.ai_model = ""
        institution.save()
        messages.success(request, f"AI provider updated to {institution.get_ai_provider_display()}")
        return redirect("ai_config")
    context = {
        "institution": institution,
        "provider_choices": Institution.AI_PROVIDER_CHOICES,
    }
    return render(request, "ai_gateway/config.html", context)
