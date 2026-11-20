from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
from apps.resources.models import LearningResource, DocumentChunk
from apps.learning.models import Conversation, Message, MessageSource
from apps.teacher_studio.models import TeachingArtifact
from apps.audit.models import AuditEvent
# Clear demo content (keeps institution + users)
MessageSource.objects.all().delete()
Message.objects.all().delete()
Conversation.objects.all().delete()
TeachingArtifact.objects.all().delete()
DocumentChunk.objects.all().delete()
LearningResource.objects.all().delete()
AuditEvent.objects.all().delete()
inst, _ = Institution.objects.get_or_create(name="Jifunze Test School", defaults={"country": "Kenya"})
admin, _ = User.objects.get_or_create(username="Caristus_Mugendi", defaults={"role": "school_admin"})
Membership.objects.get_or_create(user=admin, institution=inst, defaults={"role": "school_admin"})
r = LearningResource.objects.create(
    institution=inst, uploaded_by=admin,
    title="Photosynthesis Chapter - Form 2 Biology",
    subject="Biology", grade_level="Form 2", topic="Biology > Form 2",
    curriculum="CBC/CBE", status=LearningResource.Status.READY)
chunks = [
    DocumentChunk.objects.create(resource=r, chunk_index=0, chunk_text=(
        "Photosynthesis is the process by which green plants use sunlight to convert carbon dioxide "
        "and water into glucose and oxygen. It occurs in the chloroplasts, which contain the green "
        "pigment chlorophyll. The overall equation is 6CO2 + 6H2O -> C6H12O6 + 6O2.")),
    DocumentChunk.objects.create(resource=r, chunk_index=1, chunk_text=(
        "Chlorophyll absorbs light energy, mainly red and blue wavelengths, and uses it to split "
        "water molecules in the light-dependent reactions. This energy is then used to fix carbon "
        "dioxide into glucose during the light-independent reactions (Calvin cycle).")),
]
c = Conversation.objects.create(institution=inst, user=admin, title="Photosynthesis - Form 2")
Message.objects.create(conversation=c, role=Message.Role.USER, content="What is the role of chlorophyll in photosynthesis?")
m = Message.objects.create(conversation=c, role=Message.Role.ASSISTANT,
    content=("Based on your school's approved Form 2 Biology materials (CBC/CBE curriculum): "
             "Chlorophyll is the green pigment in chloroplasts that absorbs light energy, mainly "
             "red and blue wavelengths. It uses this energy to split water molecules in the "
             "light-dependent reactions, releasing oxygen and providing energy to fix carbon "
             "dioxide into glucose in the Calvin cycle."),
    model_provider="mock")
for ch in chunks:
    MessageSource.objects.create(message=m, resource=r, chunk=ch, relevance_score=1.0)
TeachingArtifact.objects.create(institution=inst, created_by=admin,
    artifact_type=TeachingArtifact.ArtifactType.LESSON_PLAN, topic="Photosynthesis",
    grade_level="Form 2", curriculum="CBC/CBE",
    content=("# Lesson Plan: Photosynthesis (Form 2)\n\n## Learning Outcomes\n"
             "By the end of the lesson the learner will:\n1. Explain photosynthesis using correct terminology.\n"
             "2. Describe the role of chlorophyll.\n3. Write the word equation.\n\n"
             "## Activities\nIntroduction (5 min), guided exploration (25 min), formative assessment (10 min)."))
AuditEvent.objects.create(institution=inst, actor=admin, action="AI_LEARNING_QUERY",
    resource_type="Conversation", resource_id=str(c.id), metadata={"provider": "mock", "chunks_used": 2})
AuditEvent.objects.create(institution=inst, actor=admin, action="TEACHER_ARTIFACT_GENERATED",
    resource_type="TeachingArtifact", metadata={"type": "lesson_plan"})
print("GOLDEN PATH SEEDED: 1 resource, 2 chunks, 1 conversation with sources, 1 artifact, 2 audit events.")
