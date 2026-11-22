import json
import socket
from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.institutions.models import Institution, Membership
from apps.learning.models import Conversation, Message, MessageSource
from apps.resources.models import DocumentChunk, LearningResource
from apps.teacher_studio.views import BUILDERS
RESOURCES = [
    ("Photosynthesis - Form 2 Biology Notes", "Biology", "Form 2", "CBC/CBE",
     "Photosynthesis is the process by which green plants convert light energy into chemical energy stored in glucose. It takes place in chloroplasts, where the pigment chlorophyll absorbs mainly red and blue light. The overall equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2. The light-dependent reactions split water, releasing oxygen and producing ATP and NADPH. The Calvin cycle then uses these products to fix carbon dioxide into glucose."),
    ("Atomic Structure - Form 2 Chemistry Notes", "Chemistry", "Form 2", "CBC/CBE",
     "An atom is the smallest particle of an element that retains its chemical properties. It consists of a dense central nucleus containing protons and neutrons, surrounded by electrons arranged in energy levels or shells. Protons carry a positive charge, electrons a negative charge and neutrons are neutral. The atomic number equals the number of protons and defines the element."),
    ("Fractions and Operations - Grade 8 Mathematics", "Mathematics", "Grade 8", "CBC/CBE",
     "A fraction represents a part of a whole and is written as a numerator over a denominator. Equivalent fractions have the same value even though they look different, for example 1/2 and 2/4. To add or subtract fractions, first express them with a common denominator. To multiply fractions, multiply the numerators and multiply the denominators."),
    ("Causes of the First World War - Form 3 History", "History", "Form 3", "8-4-4",
     "The immediate cause of the First World War was the assassination of Archduke Franz Ferdinand of Austria-Hungary at Sarajevo in June 1914. Long-term causes are militarism, alliances, imperialism and nationalism. Europe was divided into two armed camps: the Triple Entente of Britain, France and Russia, and the Triple Alliance of Germany, Austria-Hungary and Italy."),
    ("Forces and Newton's Laws - Form 1 Physics", "Physics", "Form 1", "8-4-4",
     "A force is a push or a pull that can change the shape, speed or direction of motion of a body. The SI unit of force is the newton. Newton's first law states that a body remains at rest or in uniform motion unless acted on by an external force. Newton's second law gives force as mass times acceleration, F = ma."),
]
CONVERSATIONS = [
    ("Explain photosynthesis", "Biology",
     "Photosynthesis is how green plants turn light energy into chemical energy (glucose). It happens in chloroplasts, where chlorophyll absorbs mainly red and blue light. The overall equation is 6CO2 + 6H2O + light -> C6H12O6 + 6O2."),
    ("What is an atom?", "Chemistry",
     "An atom is the smallest unit of an element that keeps its chemical properties. It has a dense nucleus of protons and neutrons, with negatively charged electrons orbiting in shells."),
    ("How do I add 1/2 and 1/4?", "Mathematics",
     "To add 1/2 and 1/4, first find a common denominator, which is 4. Convert 1/2 to 2/4, then add: 2/4 + 1/4 = 3/4."),
]
def fields(model):
    return {f.name for f in model._meta.fields}
class Command(BaseCommand):
    help = "Populate the platform with realistic demo data."
    def handle(self, *args, **o):
        inst, _ = Institution.objects.get_or_create(name="Jifunze Test School", defaults={"country": "Kenya"})
        admin, _ = User.objects.get_or_create(username="admin", defaults={"role": "platform_admin"})
        admin.set_password("admin12345!"); admin.save()
        caristus, _ = User.objects.get_or_create(username="Caristus_Mugendi", defaults={"role": "school_admin"})
        caristus.set_password("admin12345!"); caristus.save()
        teacher, _ = User.objects.get_or_create(username="teacher.demo", defaults={"role": "teacher"})
        teacher.set_password("teach12345!"); teacher.save()
        learner, _ = User.objects.get_or_create(username="learner.demo", defaults={"role": "learner"})
        learner.set_password("learn12345!"); learner.save()
        for u, r in ((admin, "platform_admin"), (caristus, "school_admin"), (teacher, "teacher"), (learner, "learner")):
            Membership.objects.get_or_create(user=u, institution=inst, defaults={"role": r, "is_active": True})
        lr_f, dc_f = fields(LearningResource), fields(DocumentChunk)
        chunks_by_title = {}
        for title, subj, grade, curr, text in RESOURCES:
            kwargs = {"institution": inst, "title": title, "status": "ready", "uploaded_by": teacher}
            for f, v in (("subject", subj), ("grade_level", grade), ("curriculum", curr), ("topic", title.split(" - ")[0]),
                         ("provenance_tier", "A"), ("license", "CC0 demo"), ("source_url", ""),
                         ("attribution", "JIFUNZE AI demo")):
                if f in lr_f:
                    kwargs[f] = v
            res, _ = LearningResource.objects.update_or_create(institution=inst, title=title,
                                                                defaults={k: v for k, v in kwargs.items() if k not in ("institution", "title")})
            DocumentChunk.objects.filter(resource=res).delete()
            halves = [text[:len(text)//2], text[len(text)//2:]]
            cl = []
            for i, half in enumerate(halves):
                ck = {"resource": res, "chunk_index": i, "chunk_text": half.strip()}
                cl.append(DocumentChunk.objects.create(**{k: v for k, v in ck.items() if k in dc_f or k == "resource"}))
            chunks_by_title[title] = cl
        made_art = 0
        specs = [("lesson_plan", "Photosynthesis", "Form 2", "CBC/CBE"),
                 ("quiz", "Atomic Structure", "Form 2", "CBC/CBE"),
                 ("worksheet", "Fractions", "Grade 8", "CBC/CBE"),
                 ("marking_guide", "Photosynthesis", "Form 2", "CBC/CBE"),
                 ("scheme_of_work", "Forces and Motion", "Form 1", "8-4-4")]
        from apps.teacher_studio.models import TeachingArtifact
        for kind, topic, grade, curr in specs:
            params = {"artifact_type": kind, "topic": topic, "grade_level": grade, "curriculum": curr,
                      "language": "en", "duration": 50, "count": 8, "mix": "balanced", "difficulty": "Standard"}
            content = json.dumps(BUILDERS[kind](params), indent=2)
            kwargs = {"institution": inst, "created_by": teacher, "artifact_type": kind, "topic": topic, "content": content}
            ex = {f.name for f in TeachingArtifact._meta.fields}
            for f in ("grade_level", "curriculum"):
                if f in ex:
                    kwargs[f] = grade if f == "grade_level" else curr
            if not TeachingArtifact.objects.filter(institution=inst, topic=topic, artifact_type=kind).exists():
                TeachingArtifact.objects.create(**kwargs)
                made_art += 1
        cf, mf, sf = fields(Conversation), fields(Message), fields(MessageSource)
        made_conv = 0
        for title, subj, answer in CONVERSATIONS:
            if Conversation.objects.filter(institution=inst, title=title).exists():
                continue
            ck = {"institution": inst, "title": title}
            if "user" in cf:
                ck["user"] = learner
            if "subject" in cf:
                ck["subject"] = subj
            conv = Conversation.objects.create(**ck)
            mk = {"conversation": conv, "content": title}
            if "role" in mf:
                mk["role"] = "user"
            Message.objects.create(**mk)
            ak = {"conversation": conv, "content": answer}
            if "role" in mf:
                ak["role"] = "assistant"
            am = Message.objects.create(**ak)
            match = [t for t in chunks_by_title if t.lower().split(" ")[0] in title.lower() or title.lower().split(" ")[-1] in t.lower()]
            src_title = match[0] if match else RESOURCES[0][0]
            if "message" in sf:
                sk = {"message": am}
                if "resource" in sf:
                    sk["resource"] = chunks_by_title[src_title][0].resource
                if "chunk" in sf:
                    sk["chunk"] = chunks_by_title[src_title][0]
                MessageSource.objects.create(**sk)
            made_conv += 1
        try:
            from apps.governance.models import ConsentRecord, DataRequest
            crf = fields(ConsentRecord)
            ck2 = {"institution": inst, "user": learner}
            for f in ("policy_version", "version"):
                if f in crf:
                    ck2[f] = "v1.0"
            for f in ("granted", "consent", "accepted"):
                if f in crf:
                    ck2[f] = True
            if not ConsentRecord.objects.filter(institution=inst, user=learner).exists():
                ConsentRecord.objects.create(**{k: v for k, v in ck2.items() if k in crf})
            drf = fields(DataRequest)
            dk = {"institution": inst, "user": learner}
            for f in ("request_type", "type"):
                if f in drf:
                    dk[f] = "export"
            for f in ("status",):
                if f in drf:
                    dk[f] = "pending"
            if not DataRequest.objects.filter(institution=inst, user=learner).exists():
                DataRequest.objects.create(**{k: v for k, v in dk.items() if k in drf})
        except Exception as e:
            self.stdout.write("governance seed skipped: %s" % e)
        try:
            ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip.connect(("8.8.8.8", 80)); lan = ip.getsockname()[0]; ip.close()
        except Exception:
            lan = "127.0.0.1"
        self.stdout.write(self.style.SUCCESS("DEMO DATA READY  artifacts+=%d conversations+=%d" % (made_art, made_conv)))
        self.stdout.write("Logins: admin/admin12345!  Caristus_Mugendi/admin12345!  teacher.demo/teach12345!  learner.demo/learn12345!")
        self.stdout.write("Mobile test: python manage.py runserver 0.0.0.0:8000  then http://%s:8000 on your phone" % lan)
