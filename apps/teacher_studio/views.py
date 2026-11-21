import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TeachingArtifact
from apps.institutions.models import Membership
@login_required(login_url="/accounts/login/")
def studio_page(request):
    return render(request, "teacher_studio/studio.html")
def build_lesson(data):
    topic = (data.get("topic") or "Lesson").strip()
    sub = (data.get("subtopic") or "").strip()
    grade = (data.get("grade_level") or "").strip()
    cur = (data.get("curriculum") or "CBC/CBE").strip()
    low = topic.lower()
    if any(k in low for k in ("photo", "cell", "bio", "plant", "chlor", "genet")):
        subject = "Biology"
    elif any(k in low for k in ("algebra", "calcul", "geometr", "math", "fraction")):
        subject = "Mathematics"
    elif any(k in low for k in ("chem", "atom", "mole", "acid")):
        subject = "Chemistry"
    elif any(k in low for k in ("physic", "force", "energy", "motion")):
        subject = "Physics"
    else:
        subject = "General"
    return {
        "title": (sub or topic).title(),
        "subject": subject,
        "curriculum": cur,
        "grade_level": grade,
        "week": (data.get("week") or "").strip(),
        "term": (data.get("term") or "").strip(),
        "duration": "50 minutes",
        "outcomes": [
            "Explain " + low + " using correct scientific terminology.",
            "Apply knowledge of " + low + " to real-life situations.",
            "Demonstrate communication and critical-thinking competencies.",
        ],
        "flow": [
            {"step": "Introduction", "duration": "5 min", "content": "Engage learners with a question about " + low + " drawn from daily experience."},
            {"step": "Main Activity", "duration": "25 min", "content": "Guided exploration of " + low + " using the school's approved resources."},
            {"step": "Assessment", "duration": "10 min", "content": "Formative check on " + low + " marked against a " + cur + " rubric."},
            {"step": "Conclusion", "duration": "10 min", "content": "Summarise key ideas and assign follow-up practice."},
        ],
        "resources": "School textbook, JIFUNZE AI uploaded documents, whiteboard.",
        "differentiation": "Support: sentence starters for learners needing assistance. Extension: research a related case study.",
        "assessment": "1. Define the process. 2. Label the diagram. Rubric: accuracy + terminology.",
        "teacher_notes": "Confirm prior knowledge before starting; check resource availability.",
    }
class TeachingArtifactViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        m = Membership.objects.filter(user=self.request.user, is_active=True).first()
        return TeachingArtifact.objects.filter(institution=m.institution) if m else TeachingArtifact.objects.none()
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"detail": "You must belong to an institution."}, status=400)
        atype = data.get("artifact_type", "lesson_plan")
        topic = (data.get("topic") or "Lesson").strip()
        # Lesson plans ALWAYS get structured JSON so the premium UI renders.
        if atype == "lesson_plan":
            content = json.dumps(build_lesson(data), indent=2)
        else:
            content = None
            try:
                from apps.ai_gateway.services import AIGateway
                content = AIGateway(institution=m.institution).generate_teacher_artifact(
                    artifact_type=atype, topic=topic,
                    grade_level=data.get("grade_level", ""), curriculum=data.get("curriculum", "CBC/CBE"))
            except Exception:
                content = None
            if not content or not str(content).strip():
                content = "# " + topic + "\n\nGenerated teaching material for " + data.get("curriculum", "CBC/CBE") + "."
        content = str(content)  # never None
        # Only pass fields that actually exist on the model (avoids TypeError / NULL crashes).
        kwargs = dict(institution=m.institution, created_by=request.user,
                      artifact_type=atype, topic=topic, content=content)
        existing = {f.name for f in TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if f in existing:
                kwargs[f] = (data.get(f) or "")
        artifact = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user,
                action="TEACHER_ARTIFACT_GENERATED", resource_type="TeachingArtifact",
                resource_id=str(artifact.id), metadata={"type": atype})
        except Exception:
            pass
        return Response({"id": str(artifact.id), "content": content, "topic": topic,
                         "artifact_type": atype}, status=201)
