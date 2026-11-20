from apps.institutions.models import Institution
from apps.accounts.models import User
from apps.resources.models import LearningResource, DocumentChunk
inst = Institution.objects.first()
user = User.objects.first()
if not inst or not user:
    print("ERROR: Please create an Institution and a User first in the Django Admin panel.")
else:
    res = LearningResource.objects.create(
        institution=inst, 
        uploaded_by=user,
        title="Photosynthesis Notes - Form 2", 
        subject="Biology",
        grade_level="Form 2", 
        status="ready",
    )
    DocumentChunk.objects.create(
        resource=res, 
        chunk_index=0,
        chunk_text=(
            "Photosynthesis is the process by which green plants use sunlight to convert "
            "carbon dioxide and water into glucose and oxygen. It occurs in the chloroplasts, "
            "which contain the green pigment chlorophyll. The light-dependent reactions happen "
            "in the thylakoid membranes, while the Calvin cycle occurs in the stroma. "
            "Overall equation: 6CO2 + 6H2O -> C6H12O6 + 6O2."
        ),
    )
    print(f"SUCCESS! Seeded resource '{res.title}' for institution '{inst.name}'")
