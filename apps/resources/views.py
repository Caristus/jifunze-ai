import os
import logging
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import LearningResource, DocumentChunk
from .processors import extract_text, chunk_text
from apps.audit.models import AuditEvent
from apps.institutions.models import Membership
logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md")
@login_required(login_url="/accounts/login/")
def upload_resource(request):
    if request.method == "POST":
        membership = Membership.objects.filter(user=request.user, is_active=True).first()
        if not membership:
            return JsonResponse({"error": "You must belong to an institution to upload resources."}, status=403)
        files = request.FILES.getlist("files")
        paths = request.POST.getlist("paths")
        default_subject = request.POST.get("subject", "").strip()
        default_grade = request.POST.get("grade_level", "").strip()
        default_curriculum = request.POST.get("curriculum", "CBC/CBE").strip()
        results = []
        for index, uploaded in enumerate(files):
            rel = (paths[index] if index < len(paths) else uploaded.name).replace("\\", "/")
            parts = [p for p in rel.split("/") if p]
            filename = parts[-1] if parts else uploaded.name
            folders = parts[:-1]
            topic = " > ".join(folders)
            title = os.path.splitext(filename)[0]
            subject = default_subject or (folders[0] if folders else "")
            grade = default_grade or (folders[1] if len(folders) > 1 else "")
            if not filename.lower().endswith(ALLOWED_EXTENSIONS):
                results.append({"name": rel, "topic": topic, "status": "Skipped (unsupported type)", "chunks": 0})
                continue
            resource = LearningResource.objects.create(
                institution=membership.institution, uploaded_by=request.user,
                title=title, subject=subject, grade_level=grade, topic=topic, curriculum=default_curriculum,
                file=uploaded, status=LearningResource.Status.PROCESSING,
            )
            try:
                text = extract_text(uploaded)
                chunks = chunk_text(text) if text else []
                for i, chunk in enumerate(chunks):
                    DocumentChunk.objects.create(resource=resource, chunk_index=i, chunk_text=chunk)
                resource.status = LearningResource.Status.READY if chunks else LearningResource.Status.FAILED
                resource.save()
                results.append({"name": rel, "topic": topic,
                                "status": "Processed" if chunks else "No text extracted",
                                "chunks": len(chunks)})
            except Exception as e:
                resource.status = LearningResource.Status.FAILED
                resource.save()
                logger.exception("Bulk upload failed for %s", filename)
                results.append({"name": rel, "topic": topic, "status": f"Failed: {e}", "chunks": 0})
        processed = sum(1 for r in results if r["status"] == "Processed")
        AuditEvent.objects.create(
            institution=membership.institution, actor=request.user,
            action="RESOURCE_BULK_UPLOAD", resource_type="LearningResource",
            metadata={"files": len(files), "processed": processed})
        return JsonResponse({"results": results, "processed": processed, "total": len(files)})
    return render(request, "resources/upload.html")
@login_required(login_url="/accounts/login/")
def resource_library(request):
    membership = Membership.objects.filter(user=request.user, is_active=True).first()
    resources = (
        LearningResource.objects.filter(institution=membership.institution)
        .select_related("uploaded_by") if membership else LearningResource.objects.none()
    )
    return render(request, "resources/library.html",
                  {"resources": resources, "institution": membership.institution if membership else None})


