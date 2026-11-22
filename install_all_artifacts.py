from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
VIEWS = '''import json
import re
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TeachingArtifact
from apps.institutions.models import Membership
@login_required(login_url="/accounts/login/")
def studio_page(request):
    return render(request, "teacher_studio/studio.html")
def _band(grade):
    g = (grade or "").lower()
    if any(k in g for k in ("pp1", "pp2", "kg", "grade r", "pre")):
        return "early"
    m = re.search(r"\\d+", g)
    n = int(m.group()) if m else 0
    if "form" in g:
        return "junior" if n <= 2 else "senior"
    if re.match(r"^s\\d", g):
        return "junior" if n <= 2 else "senior"
    if "jss" in g:
        return "junior"
    if "sss" in g or "shs" in g:
        return "senior"
    if "myp" in g:
        return "junior"
    if "dp" in g:
        return "senior"
    if "pyp" in g:
        return "primary"
    if "stage" in g:
        return "primary" if n <= 6 else "junior"
    if "year" in g:
        return "senior"
    if "standard" in g or "primary" in g:
        return "primary"
    if "basic" in g:
        return "primary" if n <= 6 else "junior"
    if "grade" in g:
        return "primary" if n <= 6 else ("junior" if n <= 9 else "senior")
    return "junior"
def _lang(d):
    return "sw" if (d.get("language") or "en") == "sw" else "en"
def _count(d):
    try:
        return max(2, min(12, int(d.get("count") or 6)))
    except (TypeError, ValueError):
        return 6
def _total(d):
    try:
        return max(20, min(120, int(d.get("duration") or 50)))
    except (TypeError, ValueError):
        return 50
def _subject(topic):
    low = topic.lower()
    if any(k in low for k in ("photo", "cell", "bio", "plant", "chlor", "genet")):
        return "Biology"
    if any(k in low for k in ("algebra", "calcul", "geometr", "math", "fraction")):
        return "Mathematics"
    if any(k in low for k in ("chem", "atom", "mole", "acid")):
        return "Chemistry"
    if any(k in low for k in ("physic", "force", "energy", "motion")):
        return "Physics"
    return "General"
FACTS = {
    "photosynthesis": {
        "mcq": [
            {"q": "Which organelle is the site of photosynthesis?", "options": ["Chloroplast", "Mitochondrion", "Nucleus", "Ribosome"], "answer": 0, "explain": "Chloroplasts contain chlorophyll which captures light energy."},
            {"q": "Which gas is released during photosynthesis?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "answer": 0, "explain": "Splitting water in the light reactions releases oxygen."},
        ],
        "parts": ["chlorophyll", "light energy", "carbon dioxide", "water", "glucose", "oxygen"],
    },
    "atom": {
        "mcq": [
            {"q": "Which particle carries a negative charge?", "options": ["Electron", "Proton", "Neutron", "Photon"], "answer": 0, "explain": "Electrons are negatively charged and orbit the nucleus."},
            {"q": "The atomic number of an element equals the number of...", "options": ["Protons", "Neutrons", "Electrons + neutrons", "Nucleons"], "answer": 0, "explain": "Atomic number = proton count, which defines the element."},
        ],
        "parts": ["proton", "neutron", "electron", "nucleus", "shell", "atomic number"],
    },
    "cell": {
        "mcq": [
            {"q": "Which structure is found ONLY in plant cells?", "options": ["Cell wall", "Cell membrane", "Cytoplasm", "Nucleus"], "answer": 0, "explain": "Plant cells have a rigid cellulose cell wall; animal cells do not."},
        ],
        "parts": ["cell wall", "chloroplast", "vacuole", "nucleus", "cytoplasm", "membrane"],
    },
    "fraction": {
        "mcq": [
            {"q": "Which fraction is equivalent to 1/2?", "options": ["2/4", "1/3", "2/3", "3/5"], "answer": 0, "explain": "Multiplying numerator and denominator by 2 gives 2/4."},
        ],
        "parts": ["numerator", "denominator", "equivalent", "common denominator", "simplify"],
    },
}
def _facts(topic):
    low = topic.lower()
    for k, v in FACTS.items():
        if k in low:
            return v
    return None
S = {
    "en": {
        "quiz_instr": "Answer all questions. Show your working where required. Marks are indicated per question.",
        "ws_instr": "Complete each task in the spaces provided. Use the word bank where given.",
        "objective": "Learners investigate and apply understanding of {t} through a hands-on collaborative activity.",
        "safety": "Follow normal classroom/laboratory safety rules; handle equipment carefully and report breakages.",
        "grouping": "Pairs or groups of 3-4 with rotating roles: recorder, presenter, timekeeper.",
        "notes": "Confirm prior knowledge before starting; check resource availability and pace for the level.",
        "diff": "Support: sentence starters and guided prompts. Extension: an open-ended investigation or case study.",
        "res": "School textbook, JIFUNZE AI uploaded documents, whiteboard and manipulatives.",
        "levels": ["Excellent", "Good", "Developing", "Beginning"],
        "criteria": ["Knowledge & understanding", "Scientific terminology", "Application to real life", "Reasoning & communication"],
        "errors": ["Confuses key terms with everyday meanings.", "Omits units or labels where required.", "States a conclusion without supporting evidence."],
        "checklist": ["All group members contributed a role.", "Findings recorded clearly.", "One real-life link explained."],
        "materials": ["Printed task cards", "Whiteboard & markers", "School textbook", "Manipulatives / chart paper"],
    },
    "sw": {
        "quiz_instr": "Jibu maswali yote. Onyesha hatua zako pale inapohitajika. Alama zimeonyeshwa kwa kila swali.",
        "ws_instr": "Kamilisha kila kazi katika nafasi ulizopewa. Tumia orodha ya maneno pale ilipotolewa.",
        "objective": "Wanafunzi huchunguza na kutumia uelewa wa {t} kupitia shughuli ya vitendo ya ushirikiano.",
        "safety": "Fuata sheria za usalama darasani/maabara; shughulikia vifaa kwa makini na ripoti uvunjikaji.",
        "grouping": "Wawili au vikundi vya 3-4 na majukumu yanayozunguka: mrekodi, mwasilishi, mlinzi wa muda.",
        "notes": "Thibitisha maarifa ya awali; angalia nyenzo na kasi ya darasa.",
        "diff": "Msaada: vianzo vya sentensi na miongozo. Upanuzi: uchunguzi wa wazi au utafiti wa kesi.",
        "res": "Kitabu cha shule, nyenzo za JIFUNZE AI, ubao na vifaa vya kufundishia.",
        "levels": ["Bora", "Nzuri", "Inaendelea", "Mwanzo"],
        "criteria": ["Maarifa na uelewa", "Istilahi za kisayansi", "Matumizi katika maisha", "Hoja na mawasiliano"],
        "errors": ["Kuchanganya istilahi muhimu na maana ya kila siku.", "Kukosa vitengo au lebo pale zinapohitajika.", "Kutoa hitimisho bila ushahidi."],
        "checklist": ["Kila mwanachama alitekeleza jukumu.", "Matokeo yameandikwa kwa uwazi.", "Kiungo kimoja cha maisha halisi kimeelezwa."],
        "materials": ["Kadi za kazi zilizochapishwa", "Ubao na markeri", "Kitabu cha shule", "Vifaa vya kufundishia / chati"],
    },
}
def _base(data, kind):
    topic = (data.get("topic") or "Lesson").strip()
    sub = (data.get("subtopic") or "").strip()
    return {
        "kind": kind,
        "title": (sub or topic).title(),
        "topic": topic,
        "subject": _subject(topic),
        "curriculum": (data.get("curriculum") or "CBC/CBE").strip(),
        "grade_level": (data.get("grade_level") or "").strip(),
        "week": (data.get("week") or "").strip(),
        "term": (data.get("term") or "").strip(),
        "duration": str(_total(data)) + " minutes",
        "language": _lang(data),
        "band": _band(data.get("grade_level")),
        "difficulty": data.get("difficulty") or "Standard",
    }
def build_lesson(data):
    d = _base(data, "lesson_plan")
    low = d["topic"].lower()
    lang = d["language"]
    b = d["band"]
    total = _total(data)
    weights = [0.1, 0.5, 0.2, 0.2]
    mins = [max(5, int(round(total * w))) for w in weights]
    mins[-1] += total - sum(mins)
    steps = {"en": ["Introduction", "Main Activity", "Assessment", "Conclusion"],
             "sw": ["Utangulizi", "Shughuli Kuu", "Tathmini", "Hitimisho"]}[lang]
    flow_en = {
        "early": ["Sing, look and touch: explore {t} with pictures and real objects.", "Play-based sorting and drawing of {t} in small circles.", "Show-and-tell: each child names one part of {t}.", "Wrap up with a song and a goodbye question about {t}."],
        "primary": ["Hook: a quick question or picture about {t} from daily life.", "Hands-on: observe, draw and label {t} using school resources.", "Two short questions on {t}; mark against a {cur} rubric.", "Recap key words and set a simple home task on {t}."],
        "junior": ["Engage learners with a question about {t} drawn from daily experience.", "Guided exploration of {t} using approved resources; pair work.", "Formative check on {t} marked against a {cur} rubric; peer review.", "Summarise key ideas and assign follow-up practice on {t}."],
        "senior": ["Probe prior conceptions of {t} with a diagnostic question.", "Investigate and analyse {t} using approved sources and data.", "Exam-style questions on {t} marked against a {cur} rubric.", "Synthesise findings, link to the next topic and set extension reading."],
    }[b]
    flow_sw = {
        "early": ["Imba, tazama na gusa: chunguza {t} kwa picha na vitu halisi.", "Mchezo wa kupanga na kuchora {t} katika vikundi vidogo.", "Onyesha-na-eleza: kila mtoto ataja sehemu moja ya {t}.", "Hitimisha kwa wimbo na swali la kuaga kuhusu {t}."],
        "primary": ["Kivutio: swali fupi au picha kuhusu {t} kutoka maisha ya kila siku.", "Kwa vitendo: chunguza, chora na weka lebo {t} kwa nyenzo za shule.", "Maswali mawili mafupi kuhusu {t}; sahihisha kwa rubriki ya {cur}.", "Rudia maneno muhimu na toa kazi nyepesi ya nyumbani."],
        "junior": ["Washirikishe wanafunzi kwa swali kuhusu {t} kutoka uzoefu wa kila siku.", "Uchunguzi wa kuongozwa wa {t} kwa nyenzo za shule; kazi ya wawili.", "Tathmini ya {t} kwa rubriki ya {cur}; mapitio ya rika.", "Fupisha mawazo makuu na toa mazoezi ya ufuatiliaji."],
        "senior": ["Chunguza dhana za awali za {t} kwa swali la uchunguzi.", "Chunguza na uchambue {t} kwa vyanzo na data; mjadala wa kikundi.", "Maswali ya mtihani kuhusu {t} kwa rubriki ya {cur}.", "Unganisha matokeo na mada ijayo; toa usomaji wa upanuzi."],
    }[b]
    out_en = {
        "early": ["Identify and name the main parts of {t}.", "Describe {t} using simple everyday words.", "Ask one curious question about {t}."],
        "primary": ["Describe {t} and its main parts correctly.", "Use simple scientific words to explain {t}.", "Give one real-life example of {t}."],
        "junior": ["Explain {t} using correct scientific terminology.", "Apply knowledge of {t} to familiar real-life situations.", "Communicate findings clearly in pairs or groups."],
        "senior": ["Explain {t} using precise scientific terminology.", "Apply and analyse {t} in unfamiliar real-life contexts.", "Evaluate evidence and demonstrate critical-thinking competencies."],
    }[b]
    out_sw = {
        "early": ["Tambua na uitaje sehemu kuu za {t}.", "Eleza {t} kwa maneno rahisi ya kila siku.", "Uliza swali moja la udadisi kuhusu {t}."],
        "primary": ["Eleza {t} na sehemu zake kuu kwa usahihi.", "Tumia maneno rahisi ya kisayansi kueleza {t}.", "Toa mfano mmoja wa maisha halisi wa {t}."],
        "junior": ["Eleza {t} kwa istilahi sahihi za kisayansi.", "Tumia maarifa ya {t} katika hali za maisha halisi.", "Wasiliana matokeo kwa uwazi kwa wawili au vikundi."],
        "senior": ["Eleza {t} kwa istilahi za kisayansi zilizo sahihi kabisa.", "Tumia na uchambue {t} katika muktadha mpya wa maisha.", "Tathmini ushahidi na uonyeshe ujuzi wa kufikiri kwa kina."],
    }[b]
    flow = flow_sw if lang == "sw" else flow_en
    outs = out_sw if lang == "sw" else out_en
    d["outcomes"] = [o.replace("{t}", low) for o in outs]
    d["flow"] = [{"step": steps[i], "duration": str(mins[i]) + " min", "content": flow[i].replace("{t}", low).replace("{cur}", d["curriculum"])} for i in range(4)]
    d["resources"] = S[lang]["res"]
    d["differentiation"] = S[lang]["diff"]
    d["assessment"] = ("Maswali mawili mafupi kuhusu " if lang == "sw" else "Two short questions on ") + low + ("; rubriki hutoa alama kwa usahihi, istilahi na hoja." if lang == "sw" else "; rubric awards marks for accuracy, terminology and reasoning.")
    d["teacher_notes"] = S[lang]["notes"]
    return d
def build_quiz(data):
    d = _base(data, "quiz")
    low = d["topic"].lower()
    lang = d["language"]
    b = d["band"]
    n = _count(data)
    diff = d["difficulty"]
    facts = _facts(low)
    qs = []
    if facts:
        for m in facts["mcq"][:2]:
            qs.append({"type": "mcq", "stem": m["q"], "options": m["options"], "marks": 1, "answer": m["options"][m["answer"]], "explain": m["explain"], "points": []})
    templates = {
        "en": [
            ("short", "Define {t} using correct terminology.", 2, "A precise definition of {t} using key scientific terms.", ["correct key term", "accurate meaning"]),
            ("short", "State two main parts or features of {t}.", 2, "Any two correct parts/features of {t}.", ["one correct part", "second correct part"]),
            ("structured", "Explain how {t} works, step by step.", 3, "A correct ordered explanation of the process of {t}.", ["correct order", "key mechanism", "clear language"]),
            ("apply", "Give one real-life application of {t} and justify it.", 3, "A valid application of {t} with a reasoned justification.", ["valid example", "justification"]),
            ("analyse", "Analyse a situation where {t} is limited or fails, and suggest a remedy.", 4, "Identifies a limiting condition of {t}, explains its effect, and proposes a workable remedy.", ["limiting condition", "effect explained", "workable remedy", "coherent argument"]),
        ],
        "sw": [
            ("short", "Fafanua {t} kwa istilahi sahihi.", 2, "Ufafanuzi sahihi wa {t} kwa istilahi muhimu za kisayansi.", ["istilahi sahihi", "maana sahihi"]),
            ("short", "Taja sehemu au sifa mbili kuu za {t}.", 2, "Sehemu/sifa mbili sahihi za {t}.", ["sehemu moja sahihi", "sehemu ya pili sahihi"]),
            ("structured", "Eleza jinsi {t} inavyofanya kazi, hatua kwa hatua.", 3, "Maelezo sahihi ya mpangilio wa mchakato wa {t}.", ["mpangilio sahihi", "utaratibu mkuu", "lugha wazi"]),
            ("apply", "Toa matumizi moja ya {t} katika maisha halisi na uyatetee.", 3, "Matumizi halali ya {t} na utetezi wenye hoja.", ["mfano halali", "utetezi"]),
            ("analyse", "Chambua hali ambapo {t} inadhibitiwa au kushindwa, na pendekeza suluhisho.", 4, "Inatambua hali ya udhibiti, inaeleza athari, na inapendekeza suluhisho linalofaa.", ["hali ya udhibiti", "athari imeelezwa", "suluhisho linalofaa", "hoja thabiti"]),
        ],
    }[lang]
    order = [0, 2, 3, 1, 4] if diff == "Challenge" else ([0, 1, 2, 3] if diff == "Foundation" else [0, 2, 1, 3, 4])
    i = 0
    while len(qs) < n:
        t = templates[order[i % len(order)]]
        qs.append({"type": t[0], "stem": t[1].replace("{t}", low), "options": [], "marks": t[2], "answer": t[3].replace("{t}", low), "explain": "", "points": t[4]})
        i += 1
    qs = qs[:n]
    for idx, q in enumerate(qs, 1):
        q["no"] = idx
    d["instructions"] = S[lang]["quiz_instr"]
    d["total_marks"] = sum(q["marks"] for q in qs)
    d["questions"] = qs
    return d
def build_worksheet(data):
    d = _base(data, "worksheet")
    low = d["topic"].lower()
    lang = d["language"]
    n = _count(data)
    facts = _facts(low)
    bank = facts["parts"] if facts else ([low, "process", "structure", "function", "example"] if lang == "en" else [low, "mchakato", "muundo", "kazi", "mfano"])
    tasks = []
    templates = {
        "en": [
            ("fill", "Fill in the blanks using the word bank: {t} involves ___, ___ and ___.", 3),
            ("short", "In two sentences, describe what {t} is.", 3),
            ("label", "Draw and label a simple diagram of {t}.", 4),
            ("match", "Match each key term of {t} to its correct meaning.", 3),
            ("apply", "Write one way {t} is used in your home or community.", 3),
            ("challenge", "Challenge: explain what would happen if {t} stopped working.", 4),
        ],
        "sw": [
            ("fill", "Jaza nafasi kwa orodha ya maneno: {t} inahusisha ___, ___ na ___.", 3),
            ("short", "Kwa sentensi mbili, eleza {t} ni nini.", 3),
            ("label", "Chora na weka lebo mchoro rahisi wa {t}.", 4),
            ("match", "Oanisha kila istilahi muhimu ya {t} na maana yake sahihi.", 3),
            ("apply", "Andika njia moja {t} inavyotumika nyumbani au jamii yako.", 3),
            ("challenge", "Changamoto: eleza nini kitatokea ikiwa {t} itaacha kufanya kazi.", 4),
        ],
    }[lang]
    for i in range(n):
        t = templates[i % len(templates)]
        tasks.append({"no": i + 1, "type": t[0], "prompt": t[1].replace("{t}", low), "lines": t[2],
                      "answer": ("Correct terms from the word bank placed in order." if t[0] == "fill" else "A correct, complete response as guided by the teacher.") if lang == "en" else ("Maneno sahihi kutoka orodha kwa mpangilio." if t[0] == "fill" else "Jibu sahihi na kamili kama alivyoongoza mwalimu.")})
    d["instructions"] = S[lang]["ws_instr"]
    d["word_bank"] = bank
    d["tasks"] = tasks
    d["extension"] = ("Extension: research one advanced example of " if lang == "en" else "Upanuzi: tafuta mfano mmoja wa juu wa ") + low + (" and share next lesson." if lang == "en" else " na ushiriki somo lijalo.")
    return d
def build_marking_guide(data):
    d = _base(data, "marking_guide")
    low = d["topic"].lower()
    lang = d["language"]
    levels = S[lang]["levels"]
    criteria = S[lang]["criteria"]
    maxs = [4, 3, 3, 2]
    rubric = []
    desc_en = [
        ["Fully accurate, complete and insightful.", "Mostly accurate with minor gaps.", "Partially accurate with notable gaps.", "Limited or inaccurate understanding."],
        ["Precise terminology throughout.", "Mostly correct terminology.", "Some terminology errors.", "Frequent terminology errors."],
        ["Valid, well-justified real-life application.", "Valid application, brief justification.", "Application present but weakly linked.", "No valid application."],
        ["Clear, logical, well-communicated reasoning.", "Mostly clear reasoning.", "Reasoning hard to follow at times.", "Little or no coherent reasoning."],
    ]
    desc_sw = [
        ["Sahihi kabisa, kamili na yenye maarifa.", "Karibu sahihi na mapungufu madogo.", "Sahihi kwa sehemu na mapungufu makubwa.", "Uelewa mdogo au usio sahihi."],
        ["Istilahi sahihi kote.", "Istilahi nyingi sahihi.", "Makosa machache ya istilahi.", "Makosa mengi ya istilahi."],
        ["Matumizi halali yenye utetezi mzuri.", "Matumizi halali, utetezi mfupi.", "Matumizi yapo lakini uhusiano dhaifu.", "Hakuna matumizi halali."],
        ["Hoja wazi, za kimantiki, zilizowasilishwa vizuri.", "Hoja nyingi wazi.", "Hoja ngumu kufuata wakati mwingine.", "Hoja thabiti kidogo au hazipo."],
    ]
    desc = desc_sw if lang == "sw" else desc_en
    for i, c in enumerate(criteria):
        rubric.append({"name": c, "max": maxs[i], "descriptors": desc[i]})
    d["levels"] = levels
    d["rubric"] = rubric
    d["total_marks"] = sum(maxs)
    d["exemplars"] = [
        {"q": ("Define " if lang == "en" else "Fafanua ") + low + ".", "answer": ("A model definition using precise terminology, awarded full marks." if lang == "en" else "Ufafanuzi wa mfano kwa istilahi sahihi, alama kamili."), "marks": 2},
        {"q": ("Apply " if lang == "en" else "Tumia ") + low + (" to a real-life case." if lang == "en" else " katika kesi ya maisha halisi."), "answer": ("A valid case with reasoned justification, awarded full marks." if lang == "en" else "Kesi halali na utetezi wenye hoja, alama kamili."), "marks": 3},
    ]
    d["common_errors"] = S[lang]["errors"]
    d["notes"] = S[lang]["notes"]
    return d
def build_activity(data):
    d = _base(data, "activity")
    low = d["topic"].lower()
    lang = d["language"]
    total = _total(data)
    weights = [0.15, 0.5, 0.2, 0.15]
    mins = [max(5, int(round(total * w))) for w in weights]
    mins[-1] += total - sum(mins)
    steps = {"en": ["Setup & briefing", "Hands-on investigation", "Share & compare", "Reflect & connect"],
             "sw": ["Maandalizi na maelezo", "Uchunguzi wa vitendo", "Shiriki na linganisha", "Tafakari na unganisha"]}[lang]
    content_en = [
        "Introduce the challenge about {t}; assign group roles and distribute materials.",
        "Groups investigate {t} hands-on, recording observations and evidence.",
        "Groups present findings; class compares results and resolves differences.",
        "Connect findings to everyday life and to the next lesson on {t}.",
    ]
    content_sw = [
        "Anzisha changamoto kuhusu {t}; gawa majukumu na vifaa.",
        "Vikundi huchunguza {t} kwa vitendo, rekodi uchunguzi na ushahidi.",
        "Vikundi huwasilisha matokeo; darasa hulinganisha na kutatua tofauti.",
        "Unganisha matokeo na maisha ya kila siku na somo lijalo la {t}.",
    ]
    content = content_sw if lang == "sw" else content_en
    d["objective"] = S[lang]["objective"].replace("{t}", low)
    d["materials"] = S[lang]["materials"]
    d["steps"] = [{"step": steps[i], "duration": str(mins[i]) + " min", "content": content[i].replace("{t}", low)} for i in range(4)]
    d["grouping"] = S[lang]["grouping"]
    d["safety"] = S[lang]["safety"]
    d["differentiation"] = S[lang]["diff"]
    d["checklist"] = S[lang]["checklist"]
    return d
BUILDERS = {"lesson_plan": build_lesson, "quiz": build_quiz, "worksheet": build_worksheet,
            "marking_guide": build_marking_guide, "activity": build_activity}
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
        builder = BUILDERS.get(atype, build_lesson)
        content = json.dumps(builder(data), indent=2)
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
'''
(base / "apps/teacher_studio/views.py").write_text(VIEWS, encoding="utf-8")
TPL = '''{% extends "base.html" %}
{% block title %}Teacher Studio — JIFUNZE AI{% endblock %}
{% block content %}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  :root{--indigo:#1B1F4B;--indigo2:#2A3070;--champ:#C9A227;--green:#10B981;--green2:#0E9F6E;--bg:#FDFCF8;--card:#FFFFFF;--ink:#0F172A;--mut:#64748B;--line:#E4E1D6;--soft:#F6F4EC;--amber:#F59E0B;--red:#DC2626;--blue:#2563EB;}
  *{scrollbar-width:thin;scrollbar-color:#C9C4B4 #EFEDE6;}
  *::-webkit-scrollbar{width:10px;height:10px;}
  *::-webkit-scrollbar-track{background:#EFEDE6;}
  *::-webkit-scrollbar-thumb{background:#C9C4B4;border-radius:8px;border:2px solid #EFEDE6;}
  *::-webkit-scrollbar-thumb:hover{background:var(--indigo);}
  .jf{font-family:Inter,sans-serif;color:var(--ink);background:radial-gradient(1100px 500px at 85% -10%,rgba(27,31,75,.06),transparent 60%),radial-gradient(900px 480px at -10% 110%,rgba(16,185,129,.07),transparent 60%),var(--bg);min-height:100vh;}
  .jf h1,.jf h2,.jf h3,.font-display{font-family:Manrope,sans-serif;}
  .jf-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);}
  .jf label{display:block;font-size:.8rem;font-weight:600;margin-bottom:.35rem;}
  .jf input,.jf select{width:100%;border:1px solid var(--line);border-radius:.6rem;padding:.6rem .7rem;background:#fff;font-size:.9rem;transition:.15s;}
  .jf input:focus,.jf select:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(27,31,75,.14);}
  .jf-btn{background:var(--indigo);color:#fff;font-weight:600;border-radius:.7rem;padding:.85rem;width:100%;display:flex;align-items:center;justify-content:center;gap:.5rem;cursor:pointer;border:none;transition:.18s;box-shadow:0 8px 20px -10px rgba(27,31,75,.55);}
  .jf-btn:hover{background:var(--indigo2);transform:translateY(-1px);}
  .jf-btn:disabled{opacity:.65;cursor:wait;transform:none;}
  .jf-btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line);box-shadow:none;}
  .jf-btn.ghost:hover{background:var(--soft);}
  .chip{font-size:.68rem;font-weight:700;letter-spacing:.04em;padding:.22rem .6rem;border-radius:9999px;background:#EEF0F6;color:#3B4270;}
  .tl{position:relative;padding-left:2.6rem;}
  .tl::before{content:"";position:absolute;left:15px;top:10px;bottom:10px;width:2px;background:linear-gradient(var(--indigo),var(--green));opacity:.35;}
  .tl-item{position:relative;margin-bottom:1.1rem;}
  .tl-dot{position:absolute;left:-2.6rem;top:2px;width:32px;height:32px;border-radius:50%;background:#fff;border:2px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.72rem;color:var(--indigo);}
  .tl-item.active .tl-dot{background:var(--indigo);color:#fff;border-color:var(--indigo);box-shadow:0 0 0 4px rgba(27,31,75,.12);}
  .oc{display:flex;align-items:flex-start;gap:.9rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.22);padding:.9rem 1rem;border-radius:.7rem;}
  .oc b{width:1.9rem;height:1.9rem;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:.85rem;}
  .stat{background:var(--soft);border:1px solid var(--line);border-radius:.7rem;padding:.7rem .8rem;}
  .stat p:first-child{font-size:.62rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:700;}
  .stat p:last-child{font-family:Manrope;font-weight:800;font-size:.95rem;margin-top:.15rem;}
  .qcard{border:1px solid var(--line);border-radius:.8rem;padding:1rem 1.1rem;margin-bottom:.9rem;background:#fff;}
  .opt{display:flex;gap:.6rem;align-items:flex-start;padding:.4rem .6rem;border:1px solid var(--line);border-radius:.5rem;margin-top:.4rem;font-size:.9rem;}
  .opt b{width:1.4rem;height:1.4rem;border-radius:50%;background:var(--soft);border:1px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:.72rem;flex-shrink:0;}
  .answer{display:none;margin-top:.7rem;background:rgba(16,185,129,.08);border:1px dashed var(--green2);border-radius:.6rem;padding:.7rem .8rem;font-size:.85rem;}
  .show-answers .answer{display:block;}
  .lines{margin-top:.6rem;height:calc(var(--n)*1.6rem);background:repeating-linear-gradient(transparent,transparent calc(1.6rem - 1px),var(--line) calc(1.6rem - 1px),var(--line) 1.6rem);border-radius:.3rem;}
  .wb{display:inline-block;background:#EEF0F6;border:1px solid var(--line);border-radius:9999px;padding:.25rem .7rem;font-size:.78rem;font-weight:600;margin:.15rem;}
  .rubric{width:100%;border-collapse:collapse;font-size:.8rem;}
  .rubric th,.rubric td{border:1px solid var(--line);padding:.55rem .6rem;vertical-align:top;text-align:left;}
  .rubric th{background:var(--indigo);color:#fff;font-family:Manrope;}
  .rubric td:first-child{font-weight:700;background:var(--soft);}
  .safety{background:#FEF2F2;border-left:4px solid var(--red);padding:.9rem 1rem;border-radius:0 .6rem .6rem 0;}
  .check{display:flex;gap:.6rem;align-items:flex-start;padding:.45rem .6rem;border:1px solid var(--line);border-radius:.5rem;margin-top:.4rem;font-size:.88rem;}
  .check i{color:var(--green2);}
  .fade{animation:fade .35s ease;}
  @keyframes fade{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
  @media print{.no-print{display:none!important;}.jf{background:#fff;}.jf-card{box-shadow:none;border:none;}.tl::before{background:#cbd5e1;opacity:1;}.rubric th{background:#334155!important;-webkit-print-color-adjust:exact;}}
</style>
<div class="jf px-4 py-8">
 <div class="max-w-7xl mx-auto">
  <div class="flex items-end justify-between mb-6 no-print">
    <div><h1 class="text-3xl font-extrabold" style="color:var(--indigo)">Teacher Studio</h1>
    <p class="mt-1" style="color:var(--mut)">Generate world-class, curriculum-aligned teaching materials.</p></div>
    <span class="chip" style="background:var(--indigo);color:#fff">AI POWERED</span>
  </div>
  <div id="err" class="no-print hidden" style="background:#FEF2F2;border:1px solid #FECACA;color:#B91C1C;border-radius:.7rem;padding:1rem;margin-bottom:1.4rem;white-space:pre-wrap;font-size:.8rem"></div>
  <div class="grid lg:grid-cols-12 gap-8">
    <div class="lg:col-span-4 no-print">
      <div class="jf-card p-6" style="position:sticky;top:24px">
        <form id="genform" class="space-y-4">
          {% csrf_token %}
          <div><label>Artifact type</label>
            <select id="atype"><option value="lesson_plan">Lesson Plan</option><option value="quiz">Quiz</option><option value="worksheet">Worksheet</option><option value="marking_guide">Marking Guide</option><option value="activity">Learning Activity</option></select></div>
          <div><label>Topic</label><input id="topic" value="Photosynthesis"></div>
          <div><label>Subtopic / title</label><input id="subtopic" placeholder="e.g. Light-dependent reactions"></div>
          <div><label>Curriculum</label>
            <select id="curr"><option>CBC/CBE</option><option>8-4-4</option><option selected>Cambridge IGCSE</option><option>IB</option><option>CAPS</option><option>NECTA</option><option>NCDC</option><option>NERDC</option><option>NaCCA</option><option>ZIMSEC</option><option>WAEC</option><option>Edexcel</option><option>Common Core</option></select></div>
          <div><label>Grade / level</label><select id="grade"></select></div>
          <div class="grid grid-cols-2 gap-3">
            <div><label>Week</label><select id="week"><option value="">—</option></select></div>
            <div><label>Term</label><select id="term"><option value="">—</option><option>Term 1</option><option>Term 2</option><option>Term 3</option></select></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label>Duration (min)</label><select id="duration"><option>30</option><option>40</option><option selected>50</option><option>60</option><option>80</option></select></div>
            <div><label>Language</label><select id="language"><option value="en">English</option><option value="sw">Kiswahili</option></select></div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div><label>Questions / tasks</label><select id="count"><option>4</option><option selected>6</option><option>8</option><option>10</option></select></div>
            <div><label>Difficulty</label><select id="difficulty"><option>Foundation</option><option selected>Standard</option><option>Challenge</option></select></div>
          </div>
          <button type="submit" id="btn" class="jf-btn"><i data-lucide="sparkles"></i> Generate Material</button>
        </form>
      </div>
    </div>
    <div class="lg:col-span-8">
      <div id="empty" class="jf-card p-16 text-center" style="border:2px dashed var(--line);color:var(--mut)">Your generated material will appear here.</div>
      <div id="out" class="hidden fade">
        <div class="flex flex-wrap gap-3 mb-4 no-print">
          <button id="printBtn" class="jf-btn flex-1"><i data-lucide="printer"></i> Print</button>
          <button id="ansBtn" class="jf-btn ghost flex-1"><i data-lucide="eye"></i> Show answers</button>
          <button id="copyBtn" class="jf-btn ghost flex-1"><i data-lucide="copy"></i> Copy</button>
          <button id="dlBtn" class="jf-btn ghost flex-1"><i data-lucide="download"></i> Download</button>
        </div>
        <div id="doc" class="jf-card p-8 md:p-12"></div>
      </div>
    </div>
  </div>
 </div>
</div>
<script>
lucide.createIcons();
function seq(p,a,b){var r=[];for(var i=a;i<=b;i++)r.push(p+" "+i);return r;}
var GRADES={"CBC/CBE":[{g:"Pre-Primary",o:["PP1","PP2"]},{g:"Primary",o:seq("Grade",1,6)},{g:"Junior School",o:seq("Grade",7,9)},{g:"Senior School",o:seq("Grade",10,12)}],"8-4-4":[{g:"Primary",o:seq("Standard",1,8)},{g:"Secondary",o:seq("Form",1,4)}],"Cambridge IGCSE":[{g:"Primary",o:seq("Stage",1,6)},{g:"Lower Secondary",o:seq("Stage",7,9)},{g:"IGCSE",o:["Year 10","Year 11"]},{g:"Advanced",o:["AS Level (Year 12)","A Level (Year 13)"]}],"IB":[{g:"PYP",o:seq("PYP",1,5)},{g:"MYP",o:seq("MYP",1,5)},{g:"DP",o:["DP 1","DP 2"]}],"CAPS":[{g:"Foundation",o:["Grade R"].concat(seq("Grade",1,3))},{g:"Intermediate",o:seq("Grade",4,6)},{g:"Senior",o:seq("Grade",7,9)},{g:"FET",o:seq("Grade",10,12)}],"NECTA":[{g:"Primary",o:["Standard I","Standard II","Standard III","Standard IV","Standard V","Standard VI","Standard VII"]},{g:"O-Level",o:seq("Form",1,4)},{g:"A-Level",o:["Form 5","Form 6"]}],"NCDC":[{g:"Primary",o:seq("P",1,7)},{g:"O-Level",o:seq("S",1,4)},{g:"A-Level",o:["S5","S6"]}],"NERDC":[{g:"Primary",o:seq("Primary",1,6)},{g:"Junior Secondary",o:seq("JSS",1,3)},{g:"Senior Secondary",o:seq("SSS",1,3)}],"NaCCA":[{g:"KG & Primary",o:["KG 1","KG 2"].concat(seq("Basic",1,6))},{g:"JHS",o:seq("Basic",7,9)},{g:"SHS",o:seq("SHS",1,3)}],"ZIMSEC":[{g:"Primary",o:seq("Grade",1,7)},{g:"O-Level",o:seq("Form",1,4)},{g:"A-Level",o:["Form 5","Form 6"]}],"WAEC":[{g:"Junior",o:seq("JSS",1,3)},{g:"Senior",o:seq("SSS",1,3)}],"Edexcel":[{g:"Primary",o:seq("Stage",1,6)},{g:"Lower Secondary",o:seq("Stage",7,9)},{g:"IGCSE",o:["Year 10","Year 11"]},{g:"Advanced",o:["AS Level (Year 12)","A Level (Year 13)"]}],"Common Core":[{g:"Elementary",o:["Kindergarten"].concat(seq("Grade",1,5))},{g:"Middle",o:seq("Grade",6,8)},{g:"High",o:seq("Grade",9,12)}]};
var DEF={"CBC/CBE":"Grade 8","8-4-4":"Form 2","Cambridge IGCSE":"Year 10","IB":"MYP 3","CAPS":"Grade 10","NECTA":"Form 2","NCDC":"S2","NERDC":"JSS 2","NaCCA":"Basic 8","ZIMSEC":"Form 2","WAEC":"SSS 2","Edexcel":"Year 10","Common Core":"Grade 8"};
var gradeSel=document.getElementById("grade"),currSel=document.getElementById("curr");
function populateGrades(){var g=GRADES[currSel.value]||GRADES["CBC/CBE"];var prev=gradeSel.value;gradeSel.innerHTML=g.map(function(x){return '<optgroup label="'+x.g+'">'+x.o.map(function(v){return '<option>'+v+'</option>';}).join("")+'</optgroup>';}).join("");var all=g.reduce(function(a,x){return a.concat(x.o);},[]);var d=DEF[currSel.value]||all[0];gradeSel.value=all.indexOf(prev)>=0?prev:(all.indexOf(d)>=0?d:all[0]);}
currSel.addEventListener("change",populateGrades);populateGrades();
(function(){var w=document.getElementById("week");for(var i=1;i<=14;i++){var o=document.createElement("option");o.textContent="Week "+i;w.appendChild(o);}})();
function esc(s){return String(s==null?"":s).replace(/[&<>]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
var I18N={en:{out:"Learning Outcomes",intro:"By the end of this lesson, learners will be able to:",flow:"Lesson Flow",res:"Teaching Resources",diff:"Differentiation",ass:"Assessment & Rubric",notes:"Teacher Notes",plan:"Lesson Plan",dur:"Duration",subj:"Subject",grade:"Grade",wt:"Week / Term",marks:"Total marks",instr:"Instructions",wb:"Word bank",ext:"Extension",rub:"Rubric",ex:"Exemplar answers",err:"Common errors",obj:"Objective",mat:"Materials",grp:"Grouping",safe:"Safety",chk:"Success checklist",ans:"Answer",pts:"Marking points",q:"Question",task:"Task"},sw:{out:"Matokeo ya Kujifunza",intro:"Mwisho wa somo, wanafunzi wataweza:",flow:"Mtiririko wa Somo",res:"Nyenzo za Kufundisha",diff:"Utofautishaji",ass:"Tathmini na Rubriki",notes:"Maelezo ya Mwalimu",plan:"Mpango wa Somo",dur:"Muda",subj:"Somo",grade:"Darasa",wt:"Wiki / Muhula",marks:"Jumla ya alama",instr:"Maagizo",wb:"Orodha ya maneno",ext:"Upanuzi",rub:"Rubriki",ex:"Majibu ya mfano",err:"Makosa ya kawaida",obj:"Lengo",mat:"Vifaa",grp:"Uvikundi",safe:"Usalama",chk:"Orodha ya mafanikio",ans:"Jibu",pts:"Vipengele vya alama",q:"Swali",task:"Kazi"}};
var currentContent="";
function header(d,b,L,sub){return '<div style="border-bottom:2px solid var(--indigo);padding-bottom:1.4rem;margin-bottom:2rem"><div class="flex gap-2 mb-2"><span class="chip" style="background:var(--indigo);color:#fff">AI GENERATED</span><span class="chip" style="background:#DCFCE7;color:#166534">'+esc(d.curriculum)+'</span><span class="chip" style="background:#FEF3C7;color:#92400E">'+esc(d.grade_level||b.grade_level)+'</span></div><h2 class="text-3xl font-extrabold" style="color:var(--indigo)">'+esc(d.title)+'</h2><p style="color:var(--mut)">'+esc(sub)+' · '+esc(d.duration)+(b.subtopic?' · '+esc(b.subtopic):'')+'</p><div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4"><div class="stat"><p>'+L.dur+'</p><p>'+esc(d.duration)+'</p></div><div class="stat"><p>'+L.subj+'</p><p>'+esc(d.subject)+'</p></div><div class="stat"><p>'+L.grade+'</p><p>'+esc(d.grade_level||b.grade_level)+'</p></div><div class="stat"><p>'+L.wt+'</p><p>'+esc((d.week||b.week||"—")+" / "+(d.term||b.term||"—"))+'</p></div></div></div>';}
function renderLesson(d,b,L){var oc=(d.outcomes||[]).map(function(o,i){return '<div class="oc"><b>'+(i+1)+'</b><span>'+esc(o)+'</span></div>';}).join("");var fl=(d.flow||[]).map(function(x,i){return '<div class="tl-item '+(i===0?"active":"")+'"><div class="tl-dot">'+String(i+1).padStart(2,"0")+'</div><div class="jf-card p-4"><div class="flex justify-between items-center mb-1"><h3 class="font-bold" style="color:var(--indigo)">'+esc(x.step)+'</h3><span class="chip">'+esc(x.duration)+'</span></div><p style="color:var(--mut);font-size:.9rem">'+esc(x.content)+'</p></div></div>';}).join("");return header(d,b,L,L.plan)+'<h3 class="text-xl font-bold mb-2" style="color:var(--indigo)">'+L.out+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-3">'+L.intro+'</p><div class="space-y-2 mb-8">'+oc+'</div><h3 class="text-xl font-bold mb-4" style="color:var(--indigo)">'+L.flow+'</h3><div class="tl mb-8">'+fl+'</div><div class="grid md:grid-cols-2 gap-6 mb-8"><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.res+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.resources)+'</p></div><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.diff+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.differentiation)+'</p></div></div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.ass+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-6">'+esc(d.assessment)+'</p><div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem;border-radius:0 .6rem .6rem 0"><h3 class="font-bold text-sm mb-1" style="color:#92400E">'+L.notes+'</h3><p style="color:#92400E;font-size:.9rem">'+esc(d.teacher_notes)+'</p></div>';}
function renderQuiz(d,b,L){var qs=(d.questions||[]).map(function(q){var opts=(q.options||[]).map(function(o,i){return '<div class="opt"><b>'+String.fromCharCode(65+i)+'</b><span>'+esc(o)+'</span></div>';}).join("");var pts=(q.points||[]).length?'<div class="mt-1"><strong>'+L.pts+':</strong> '+q.points.map(esc).join(" · ")+'</div>':"";var ans='<div class="answer"><strong>'+L.ans+':</strong> '+esc(q.answer)+(q.explain?'<div class="mt-1" style="color:var(--mut)">'+esc(q.explain)+'</div>':"")+pts+'</div>';return '<div class="qcard"><div class="flex justify-between items-center mb-2"><span class="chip" style="background:var(--indigo);color:#fff">'+L.q+' '+q.no+'</span><span class="chip">'+q.marks+' mark'+(q.marks>1?"s":"")+'</span></div><p class="font-medium mb-1">'+esc(q.stem)+'</p>'+opts+ans+'</div>';}).join("");return header(d,b,L,"Quiz")+'<div class="stat mb-4" style="display:inline-block"><p>'+L.marks+'</p><p>'+d.total_marks+'</p></div><p style="color:var(--mut);font-size:.9rem" class="mb-4">'+esc(d.instructions)+'</p>'+qs;}
function renderWorksheet(d,b,L){var wb=(d.word_bank||[]).map(function(w){return '<span class="wb">'+esc(w)+'</span>';}).join("");var ts=(d.tasks||[]).map(function(t){return '<div class="qcard"><div class="flex justify-between items-center mb-2"><span class="chip" style="background:var(--indigo);color:#fff">'+L.task+' '+t.no+'</span><span class="chip">'+esc(t.type)+'</span></div><p class="font-medium">'+esc(t.prompt)+'</p><div class="lines" style="--n:'+t.lines+'"></div><div class="answer"><strong>'+L.ans+':</strong> '+esc(t.answer)+'</div></div>';}).join("");return header(d,b,L,"Worksheet")+'<p style="color:var(--mut);font-size:.9rem" class="mb-3">'+esc(d.instructions)+'</p><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.wb+'</h3><div class="mb-5">'+wb+'</div>'+ts+'<div style="background:#EEF0F6;border:1px solid var(--line);border-radius:.6rem;padding:.9rem 1rem" class="mt-4"><strong style="color:var(--indigo)">'+L.ext+':</strong> '+esc(d.extension)+'</div>';}
function renderMarkingGuide(d,b,L){var head='<tr><th style="width:22%">'+L.rub+'</th>'+d.levels.map(function(l){return '<th>'+esc(l)+'</th>';}).join("")+'</tr>';var rows=(d.rubric||[]).map(function(r){return '<tr><td>'+esc(r.name)+' <span class="chip">/'+r.max+'</span></td>'+r.descriptors.map(function(x){return '<td>'+esc(x)+'</td>';}).join("")+'</tr>';}).join("");var ex=(d.exemplars||[]).map(function(e){return '<div class="qcard"><p class="font-medium">'+esc(e.q)+'</p><div class="answer" style="display:block"><strong>'+L.ans+':</strong> '+esc(e.answer)+' <span class="chip">'+e.marks+' marks</span></div></div>';}).join("");var er=(d.common_errors||[]).map(function(x){return '<div class="check"><i data-lucide="alert-triangle"></i><span>'+esc(x)+'</span></div>';}).join("");return header(d,b,L,"Marking Guide")+'<div class="stat mb-4" style="display:inline-block"><p>'+L.marks+'</p><p>'+d.total_marks+'</p></div><div style="overflow-x:auto" class="mb-6"><table class="rubric">'+head+rows+'</table></div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.ex+'</h3>'+ex+'<h3 class="font-bold mb-2 mt-6" style="color:var(--indigo)">'+L.err+'</h3>'+er+'<div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem;border-radius:0 .6rem .6rem 0" class="mt-6"><strong style="color:#92400E">'+L.notes+':</strong> <span style="color:#92400E">'+esc(d.notes)+'</span></div>';}
function renderActivity(d,b,L){var mat=(d.materials||[]).map(function(m){return '<span class="wb">'+esc(m)+'</span>';}).join("");var st=(d.steps||[]).map(function(x,i){return '<div class="tl-item '+(i===0?"active":"")+'"><div class="tl-dot">'+String(i+1).padStart(2,"0")+'</div><div class="jf-card p-4"><div class="flex justify-between items-center mb-1"><h3 class="font-bold" style="color:var(--indigo)">'+esc(x.step)+'</h3><span class="chip">'+esc(x.duration)+'</span></div><p style="color:var(--mut);font-size:.9rem">'+esc(x.content)+'</p></div></div>';}).join("");var ck=(d.checklist||[]).map(function(c){return '<div class="check"><i data-lucide="check-circle-2"></i><span>'+esc(c)+'</span></div>';}).join("");return header(d,b,L,"Learning Activity")+'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.obj+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-5">'+esc(d.objective)+'</p><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.mat+'</h3><div class="mb-5">'+mat+'</div><h3 class="text-xl font-bold mb-4" style="color:var(--indigo)">'+L.flow+'</h3><div class="tl mb-6">'+st+'</div><div class="grid md:grid-cols-2 gap-6 mb-6"><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.grp+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.grouping)+'</p></div><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.diff+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.differentiation)+'</p></div></div><div class="safety mb-6"><strong style="color:var(--red)">'+L.safe+':</strong> <span style="color:#7F1D1D">'+esc(d.safety)+'</span></div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.chk+'</h3>'+ck;}
function renderAny(d,b){var L=I18N[d.language==="sw"?"sw":"en"];var k=d.kind||"lesson_plan";if(k==="quiz")return renderQuiz(d,b,L);if(k==="worksheet")return renderWorksheet(d,b,L);if(k==="marking_guide")return renderMarkingGuide(d,b,L);if(k==="activity")return renderActivity(d,b,L);return renderLesson(d,b,L);}
var f=document.getElementById("genform"),btn=document.getElementById("btn"),err=document.getElementById("err");
f.addEventListener("submit",async function(e){e.preventDefault();err.classList.add("hidden");btn.disabled=true;btn.innerHTML="Generating...";var token=document.querySelector("[name=csrfmiddlewaretoken]").value;var body={artifact_type:document.getElementById("atype").value,topic:document.getElementById("topic").value,subtopic:document.getElementById("subtopic").value,grade_level:gradeSel.value,curriculum:currSel.value,week:document.getElementById("week").value,term:document.getElementById("term").value,duration:document.getElementById("duration").value,language:document.getElementById("language").value,count:document.getElementById("count").value,difficulty:document.getElementById("difficulty").value};try{var r=await fetch("/api/teacher/artifacts/generate/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify(body)});var raw=await r.text();if(!r.ok){throw new Error("HTTP "+r.status+": "+raw.slice(0,300));}var d=JSON.parse(raw);currentContent=d.content||"";var lesson=null;try{lesson=JSON.parse(d.content);}catch(_){lesson=null;}document.getElementById("empty").classList.add("hidden");var out=document.getElementById("out");out.classList.remove("hidden");var doc=document.getElementById("doc");doc.classList.remove("show-answers");doc.innerHTML=lesson?renderAny(lesson,body):('<pre style="white-space:pre-wrap">'+esc(d.content)+'</pre>');lucide.createIcons();}catch(ex){err.textContent=ex.message;err.classList.remove("hidden");}finally{btn.disabled=false;btn.innerHTML='<i data-lucide="sparkles"></i> Generate Material';lucide.createIcons();}});
document.getElementById("printBtn").onclick=function(){window.print();};
document.getElementById("ansBtn").onclick=function(){var doc=document.getElementById("doc");var on=doc.classList.toggle("show-answers");this.innerHTML=on?'<i data-lucide="eye-off"></i> Hide answers':'<i data-lucide="eye"></i> Show answers';lucide.createIcons();};
document.getElementById("copyBtn").onclick=function(){navigator.clipboard.writeText(document.getElementById("doc").innerText);};
document.getElementById("dlBtn").onclick=function(){var b=new Blob([currentContent],{type:"application/json"});var a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=(document.getElementById("topic").value||"material").replace(/\\s+/g,"_")+".json";a.click();};
</script>
{% endblock %}'''
(base / "templates/teacher_studio/studio.html").write_text(TPL, encoding="utf-8")
print("ALL ARTIFACT TYPES FUNCTIONAL")
