from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
VIEWS = r'''import json
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
    m = re.search(r"\d+", g)
    n = int(m.group()) if m else 0
    if "form" in g:
        return "junior" if n <= 2 else "senior"
    if re.match(r"^s\d", g):
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
        return max(2, min(20, int(d.get("count") or 6)))
    except (TypeError, ValueError):
        return 6
def _total(d):
    try:
        return max(20, min(120, int(d.get("duration") or 50)))
    except (TypeError, ValueError):
        return 50
def _subject(topic):
    low = topic.lower()
    if any(k in low for k in ("photo", "cell", "bio", "plant", "chlor", "genet", "respir")):
        return "Biology"
    if any(k in low for k in ("algebra", "calcul", "geometr", "math", "fraction", "equation")):
        return "Mathematics"
    if any(k in low for k in ("chem", "atom", "mole", "acid", "molecule")):
        return "Chemistry"
    if any(k in low for k in ("physic", "force", "energy", "motion", "newton")):
        return "Physics"
    return "General"
FACTS = {
    "photosynthesis": {
        "kw": ["light", "energy", "chlorophyll", "carbon dioxide", "water", "glucose", "oxygen", "chloroplast"],
        "parts": ["chlorophyll", "chloroplast", "carbon dioxide", "water", "glucose", "oxygen"],
        "mcq": [
            {"q": "Which organelle is the site of photosynthesis?", "options": ["Chloroplast", "Mitochondrion", "Nucleus", "Ribosome"], "answer": 0, "explain": "Chloroplasts contain chlorophyll which captures light energy."},
            {"q": "Which gas is released during photosynthesis?", "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "answer": 0, "explain": "Splitting water in the light reactions releases oxygen."},
        ],
        "pairs": [["Chlorophyll", "Green pigment that absorbs light"], ["Chloroplast", "Organelle where photosynthesis occurs"], ["Glucose", "Sugar product stored as chemical energy"], ["Stomata", "Pores allowing gas exchange"]],
        "tf": {"s": "Photosynthesis stores light energy as chemical energy in glucose.", "a": True, "e": "Light energy is converted into chemical energy in glucose."},
        "numeric": {"q": "How many molecules of CO2 are needed to make one molecule of glucose (6CO2 + 6H2O -> C6H12O6 + 6O2)?", "value": 6, "tol": 0, "unit": "molecules", "e": "The balanced equation requires 6 CO2 molecules."},
        "labels": ["leaf", "chloroplast", "sunlight", "carbon dioxide", "oxygen"],
    },
    "atom": {
        "kw": ["nucleus", "proton", "neutron", "electron", "charge", "shell", "atomic number", "smallest"],
        "parts": ["proton", "neutron", "electron", "nucleus", "shell", "atomic number"],
        "mcq": [
            {"q": "Which particle carries a negative charge?", "options": ["Electron", "Proton", "Neutron", "Photon"], "answer": 0, "explain": "Electrons are negatively charged and occupy shells."},
            {"q": "The atomic number of an element equals the number of...", "options": ["Protons", "Neutrons", "Electrons + neutrons", "Nucleons"], "answer": 0, "explain": "Atomic number = proton count."},
        ],
        "pairs": [["Proton", "Positively charged particle in the nucleus"], ["Neutron", "Neutral particle in the nucleus"], ["Electron", "Negatively charged particle in shells"], ["Atomic number", "Number of protons in an atom"]],
        "tf": {"s": "Neutrons carry a positive charge.", "a": False, "e": "Neutrons are neutral; protons are positive."},
        "numeric": {"q": "Carbon has atomic number 6. How many protons does a carbon atom have?", "value": 6, "tol": 0, "unit": "protons", "e": "Atomic number equals proton number."},
        "labels": ["nucleus", "proton", "neutron", "electron", "shell"],
    },
    "cell": {
        "kw": ["membrane", "cytoplasm", "nucleus", "cell wall", "chloroplast", "vacuole", "basic unit", "life"],
        "parts": ["cell wall", "chloroplast", "vacuole", "nucleus", "cytoplasm", "membrane"],
        "mcq": [{"q": "Which structure is found ONLY in plant cells?", "options": ["Cell wall", "Cell membrane", "Cytoplasm", "Nucleus"], "answer": 0, "explain": "Plant cells have a cellulose cell wall."}],
        "pairs": [["Nucleus", "Controls cell activities and holds DNA"], ["Cytoplasm", "Jelly-like medium where reactions occur"], ["Cell membrane", "Controls movement of substances in and out"], ["Vacuole", "Stores cell sap and maintains turgor"]],
        "tf": {"s": "Animal cells contain a large permanent vacuole.", "a": False, "e": "Large permanent vacuoles are a plant cell feature."},
        "labels": ["cell wall", "nucleus", "cytoplasm", "vacuole", "chloroplast"],
    },
    "fraction": {
        "kw": ["numerator", "denominator", "equal parts", "whole", "equivalent", "common denominator"],
        "parts": ["numerator", "denominator", "equivalent", "common denominator", "simplify"],
        "mcq": [{"q": "Which fraction is equivalent to 1/2?", "options": ["2/4", "1/3", "2/3", "3/5"], "answer": 0, "explain": "Multiply numerator and denominator by 2."}],
        "pairs": [["Numerator", "Top number showing parts taken"], ["Denominator", "Bottom number showing total equal parts"], ["Equivalent fractions", "Different forms of the same value"], ["Simplify", "Divide top and bottom by a common factor"]],
        "tf": {"s": "3/6 and 1/2 are equivalent fractions.", "a": True, "e": "3/6 simplifies to 1/2."},
        "numeric": {"q": "Compute 1/2 + 1/4. Give your answer as a decimal.", "value": 0.75, "tol": 0.01, "unit": "", "e": "1/2 = 0.5 and 1/4 = 0.25, so the sum is 0.75."},
        "labels": ["numerator", "denominator", "whole", "equal parts"],
    },
    "force": {
        "kw": ["push", "pull", "newton", "mass", "acceleration", "motion", "shape"],
        "parts": ["push", "pull", "newton", "mass", "acceleration", "resultant"],
        "mcq": [{"q": "The SI unit of force is the...", "options": ["Newton", "Joule", "Watt", "Pascal"], "answer": 0, "explain": "Force is measured in newtons (N)."}],
        "pairs": [["Newton", "SI unit of force"], ["Mass", "Amount of matter in a body"], ["Acceleration", "Rate of change of velocity"], ["Resultant force", "Single force with the same effect as all forces"]],
        "tf": {"s": "Force equals mass multiplied by acceleration.", "a": True, "e": "Newton's second law: F = ma."},
        "numeric": {"q": "A 5 kg mass accelerates at 3 m/s2. Calculate the force in newtons.", "value": 15, "tol": 0.1, "unit": "N", "e": "F = ma = 5 x 3 = 15 N."},
        "labels": ["applied force", "friction", "weight", "normal reaction"],
    },
}
DISTRACTORS = ["ribosome", "mitochondrion", "vacuole", "neutron", "denominator", "friction", "stomata", "acceleration"]
def _facts(topic):
    low = topic.lower()
    for k, v in FACTS.items():
        if k in low:
            return v
    return None
S = {
    "en": {
        "quiz_instr": "Answer ALL questions. For multiple choice, select one option unless stated otherwise. Show working for calculations. Marks are shown per question.",
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
        "quiz_instr": "Jibu maswali YOTE. Kwa chaguo, chagua jibu moja isipokuwa kuelekezwa vinginevyo. Onyesha hatua za hesabu. Alama zimeonyeshwa kwa kila swali.",
        "ws_instr": "Kamilisha kila kazi katika nafasi ulizopewa. Tumia orodha ya maneno pale ilipotolewa.",
        "objective": "Wanafunzi huchunguza na kutumia uelewa wa {t} kupitia shughuli ya vitendo ya ushirikiano.",
        "safety": "Fuata sheria za usalama darasani/maabara; shughulikia vifaa kwa makini na ripoti uvunjikaji.",
        "grouping": "Wawili au vikundi vya 3-4 na majukumu yanayozunguka: mrekodi, mwasilishi, mlinzi wa muda.",
        "notes": "Thibitisha maarifa ya awali; angalia nyenzo na kasi ya darasa.",
        "diff": "Msaada: vianzo vya sentensi na miongozo. Upanuzi: uchunguzi wa wazi au utafiti wa kesi.",
        "res": "Kitabu cha shule, nyenzo za JIFUNZE AI, ubao na vifaa vya kufundishia.",
        "levels": ["Bora", "Nzuri", "Inaendelea", "Mwanzo"],
        "criteria": ["Maarifa na uelewa", "Istilahi za kisayansi", "Matumizi katika maisha", "Hoja na mawasiliano"],
        "errors": ["Kuchanganya istilahi muhimu na maana ya kila siku.", "Kukosa vitengo au lebo.", "Kutoa hitimisho bila ushahidi."],
        "checklist": ["Kila mwanachama alitekeleza jukumu.", "Matokeo yameandikwa kwa uwazi.", "Kiungo kimoja cha maisha halisi kimeelezwa."],
        "materials": ["Kadi za kazi", "Ubao na markeri", "Kitabu cha shule", "Vifaa vya kufundishia / chati"],
    },
}
MIXES = {
    "balanced": ["mcq", "tf", "fill", "short", "match", "multi", "structured", "numeric", "diagram", "essay"],
    "mcq": ["mcq", "mcq", "tf", "multi", "mcq", "numeric", "mcq", "tf"],
    "short": ["short", "fill", "tf", "short", "match", "short", "structured", "fill"],
    "structured": ["structured", "short", "structured", "numeric", "essay", "structured", "short", "diagram"],
    "practical": ["diagram", "match", "fill", "numeric", "short", "diagram", "structured", "match"],
}
def _base(data, kind):
    topic = (data.get("topic") or "Lesson").strip()
    sub = (data.get("subtopic") or "").strip()
    return {
        "kind": kind, "title": (sub or topic).title(), "topic": topic,
        "subject": _subject(topic), "curriculum": (data.get("curriculum") or "CBC/CBE").strip(),
        "grade_level": (data.get("grade_level") or "").strip(),
        "week": (data.get("week") or "").strip(), "term": (data.get("term") or "").strip(),
        "duration": str(_total(data)) + " minutes", "language": _lang(data),
        "band": _band(data.get("grade_level")), "difficulty": data.get("difficulty") or "Standard",
        "mix": data.get("mix") or "balanced",
    }
def build_lesson(data):
    d = _base(data, "lesson_plan")
    low, lang, b = d["topic"].lower(), d["language"], d["band"]
    total = _total(data)
    mins = [max(5, int(round(total * w))) for w in (0.1, 0.5, 0.2, 0.2)]
    mins[-1] += total - sum(mins)
    steps = {"en": ["Introduction", "Main Activity", "Assessment", "Conclusion"], "sw": ["Utangulizi", "Shughuli Kuu", "Tathmini", "Hitimisho"]}[lang]
    flow_en = {"early": ["Sing, look and touch: explore {t} with pictures and real objects.", "Play-based sorting and drawing of {t}.", "Show-and-tell: each child names one part of {t}.", "Wrap up with a song and a goodbye question."],
               "primary": ["Hook: a quick question or picture about {t} from daily life.", "Hands-on: observe, draw and label {t}.", "Two short questions on {t} marked on a {cur} rubric.", "Recap key words and set a simple home task."],
               "junior": ["Engage learners with a question about {t} from daily experience.", "Guided exploration of {t} using approved resources; pair work.", "Formative check on {t} against a {cur} rubric; peer review.", "Summarise key ideas and assign follow-up practice."],
               "senior": ["Probe prior conceptions of {t} with a diagnostic question.", "Investigate and analyse {t} using approved sources and data.", "Exam-style questions on {t} against a {cur} rubric.", "Synthesise findings and set extension reading."]}[b]
    flow_sw = {"early": ["Imba, tazama na gusa: chunguza {t} kwa picha na vitu halisi.", "Mchezo wa kupanga na kuchora {t}.", "Onyesha-na-eleza: kila mtoto ataja sehemu ya {t}.", "Hitimisha kwa wimbo na swali la kuaga."],
               "primary": ["Kivutio: swali au picha kuhusu {t} kutoka maisha ya kila siku.", "Kwa vitendo: chunguza, chora na weka lebo {t}.", "Maswali mawili mafupi kwa rubriki ya {cur}.", "Rudia maneno muhimu na toa kazi ya nyumbani."],
               "junior": ["Washirikishe wanafunzi kwa swali kuhusu {t}.", "Uchunguzi wa kuongozwa wa {t}; kazi ya wawili.", "Tathmini ya {t} kwa rubriki ya {cur}; mapitio ya rika.", "Fupisha mawazo makuu na toa mazoezi."],
               "senior": ["Chunguza dhana za awali za {t}.", "Chunguza na uchambue {t} kwa vyanzo na data.", "Maswali ya mtihani kwa rubriki ya {cur}.", "Unganisha matokeo na toa usomaji wa upanuzi."]}[b]
    out_en = {"early": ["Identify and name the main parts of {t}.", "Describe {t} using simple everyday words.", "Ask one curious question about {t}."],
              "primary": ["Describe {t} and its main parts correctly.", "Use simple scientific words to explain {t}.", "Give one real-life example of {t}."],
              "junior": ["Explain {t} using correct scientific terminology.", "Apply knowledge of {t} to familiar real-life situations.", "Communicate findings clearly in pairs or groups."],
              "senior": ["Explain {t} using precise scientific terminology.", "Apply and analyse {t} in unfamiliar contexts.", "Evaluate evidence and demonstrate critical thinking."]}[b]
    out_sw = {"early": ["Tambua na uitaje sehemu kuu za {t}.", "Eleza {t} kwa maneno rahisi.", "Uliza swali moja la udadisi kuhusu {t}."],
              "primary": ["Eleza {t} na sehemu zake kwa usahihi.", "Tumia maneno rahisi ya kisayansi kueleza {t}.", "Toa mfano mmoja wa maisha halisi."],
              "junior": ["Eleza {t} kwa istilahi sahihi za kisayansi.", "Tumia maarifa ya {t} katika maisha halisi.", "Wasiliana matokeo kwa uwazi."],
              "senior": ["Eleza {t} kwa istilahi sahihi kabisa.", "Tumia na uchambue {t} katika muktadha mpya.", "Tathmini ushahidi na onyesha kufikiri kwa kina."]}[b]
    flow = flow_sw if lang == "sw" else flow_en
    outs = out_sw if lang == "sw" else out_en
    d["outcomes"] = [o.replace("{t}", low) for o in outs]
    d["flow"] = [{"step": steps[i], "duration": str(mins[i]) + " min", "content": flow[i].replace("{t}", low).replace("{cur}", d["curriculum"])} for i in range(4)]
    d["resources"] = S[lang]["res"]; d["differentiation"] = S[lang]["diff"]
    d["assessment"] = ("Maswali mawili mafupi kuhusu " if lang == "sw" else "Two short questions on ") + low + ("; rubriki hutoa alama kwa usahihi na istilahi." if lang == "sw" else "; rubric awards marks for accuracy and terminology.")
    d["teacher_notes"] = S[lang]["notes"]
    return d
def _points(kw, marks, lang):
    pool = kw or []
    n = max(1, min(marks, len(pool))) or 1
    pts = []
    for i in range(n):
        group = pool[i::n] or pool
        pts.append({"label": "M%d" % (i + 1), "keywords": [g.lower() for g in group], "mark": 1,
                    "desc": ("Alama kwa wazo sahihi: " if lang == "sw" else "Award for correct idea: ") + ", ".join(group[:3])})
    extra = marks - sum(p["mark"] for p in pts)
    if extra > 0 and pts:
        pts[-1]["mark"] += extra
    return pts
def build_quiz(data):
    d = _base(data, "quiz")
    low, lang, b = d["topic"].lower(), d["language"], d["band"]
    n, mix = _count(data), (data.get("mix") or "balanced")
    facts = _facts(low)
    cycle = MIXES.get(mix, MIXES["balanced"])
    kw = facts["kw"] if facts else [low]
    parts = facts["parts"] if facts else [low, "structure", "function", "example"]
    pairs = facts["pairs"] if facts else [[low.title(), "Key concept under study"], ["Structure", "Physical arrangement of parts"], ["Function", "What it does"], ["Example", "A real-life instance"]]
    labels = facts["labels"] if facts else parts[:4]
    qs = []
    mcq_i = 0
    for i in range(n):
        t = cycle[i % len(cycle)]
        if t in ("mcq", "multi", "tf", "numeric") and not facts:
            t = "short" if i % 2 else "structured"
        if t == "mcq" and facts:
            src = facts["mcq"][mcq_i % len(facts["mcq"])]
            mcq_i += 1
            qs.append({"type": "mcq", "stem": src["q"], "options": src["options"], "correct": src["answer"],
                       "marks": 1, "answer": src["options"][src["answer"]], "explain": src["explain"], "points": [], "auto": True})
        elif t == "multi" and facts:
            correct_terms = parts[:3]
            dis = [x for x in DISTRACTORS if x not in parts][:2]
            opts = correct_terms + dis
            qs.append({"type": "multi", "stem": ("Select ALL terms associated with " if lang == "en" else "Chagua maneno YOTE yanayohusiana na ") + low + ".",
                       "options": opts, "correct_multi": [0, 1, 2], "marks": 3,
                       "answer": ", ".join(correct_terms), "explain": ("Each correct term scores 1; wrong selections cancel credit." if lang == "en" else "Kila neno sahihi hupata 1; chaguo zisizo sahihi hupunguza alama."),
                       "points": [], "auto": True})
        elif t == "tf" and facts:
            f = facts["tf"]
            qs.append({"type": "tf", "stem": f["s"], "options": ["True", "False"], "tf_answer": f["a"], "marks": 1,
                       "answer": "True" if f["a"] else "False", "explain": f["e"], "points": [], "auto": True})
        elif t == "numeric" and facts and facts.get("numeric"):
            f = facts["numeric"]
            qs.append({"type": "numeric", "stem": f["q"], "marks": 2, "numeric": {"value": f["value"], "tol": f["tol"], "unit": f["unit"]},
                       "answer": str(f["value"]) + (" " + f["unit"] if f["unit"] else ""), "explain": f["e"],
                       "points": [{"label": "M1", "keywords": [], "mark": 1, "desc": "Correct method / substitution"}, {"label": "A1", "keywords": [], "mark": 1, "desc": "Correct final answer with unit"}], "auto": True})
        elif t == "fill":
            chosen = parts[:3]
            stem = ("Complete the statement: " if lang == "en" else "Kamilisha sentensi: ") + low.title() + " involves ___, ___ and ___."
            qs.append({"type": "fill", "stem": stem, "blanks": 3, "blanks_accept": [[c.lower()] for c in chosen],
                       "marks": 3, "answer": ", ".join(chosen), "explain": "", "points": [], "auto": True})
        elif t == "match":
            meanings = [p[1] for p in pairs]
            qs.append({"type": "match", "stem": ("Match each term to its correct meaning." if lang == "en" else "Oanisha kila istilahi na maana yake sahihi."),
                       "pairs": [{"term": p[0], "meaning": p[1]} for p in pairs], "meanings": meanings,
                       "marks": len(pairs), "answer": "; ".join(p[0] + " = " + p[1] for p in pairs), "explain": "", "points": [], "auto": True})
        elif t == "diagram":
            qs.append({"type": "diagram", "stem": ("Label the numbered parts of the diagram of " if lang == "en" else "Weka lebo sehemu zenye namba za mchoro wa ") + low + ".",
                       "labels_expected": [x.lower() for x in labels], "marks": len(labels),
                       "answer": ", ".join(labels), "explain": ("Award 1 mark per correct label." if lang == "en" else "Toa alama 1 kwa kila lebo sahihi."), "points": [], "auto": True})
        elif t == "essay":
            qs.append({"type": "essay", "stem": ("Discuss " if lang == "en" else "Jadili ") + low + (", giving examples and evaluating its importance in everyday life." if lang == "en" else ", ukitoa mifano na kutathmini umuhimu wake katika maisha ya kila siku."),
                       "marks": 6, "answer": ("Teacher judgement against the rubric: content, terminology, application, reasoning." if lang == "en" else "Uamuzi wa mwalimu kwa rubriki: maudhui, istilahi, matumizi, hoja."),
                       "explain": "", "points": _points(kw, 6, lang), "auto": False, "review": True})
        elif t == "structured":
            marks = 4 if b == "senior" else 3
            qs.append({"type": "structured", "stem": ("Explain how " if lang == "en" else "Eleza jinsi ") + low + (" works, step by step, using correct terminology." if lang == "en" else " inavyofanya kazi, hatua kwa hatua, kwa istilahi sahihi."),
                       "marks": marks, "answer": ("A correct ordered explanation covering: " if lang == "en" else "Maelezo sahihi ya mpangilio yanayojumuisha: ") + ", ".join(kw[:4]),
                       "explain": "", "points": _points(kw, marks, lang), "auto": True, "review": not bool(facts)})
        else:
            marks = 2
            qs.append({"type": "short", "stem": ("Define " if lang == "en" else "Fafanua ") + low + (" using correct terminology." if lang == "en" else " kwa istilahi sahihi."),
                       "marks": marks, "answer": ("A precise definition including: " if lang == "en" else "Ufafanuzi sahihi unaojumuisha: ") + ", ".join(kw[:4]),
                       "explain": "", "points": _points(kw, marks, lang), "auto": True, "review": not bool(facts)})
    for idx, q in enumerate(qs, 1):
        q["no"] = idx
    d["instructions"] = S[lang]["quiz_instr"]
    d["total_marks"] = sum(q["marks"] for q in qs)
    d["questions"] = qs
    d["auto_markable"] = sum(q["marks"] for q in qs if q.get("auto"))
    d["review_marks"] = sum(q["marks"] for q in qs if not q.get("auto"))
    return d
def build_worksheet(data):
    d = _base(data, "worksheet")
    low, lang, n = d["topic"].lower(), d["language"], _count(data)
    facts = _facts(low)
    bank = facts["parts"] if facts else [low, "process", "structure", "function", "example"]
    tpl = {"en": [("fill", "Fill in the blanks using the word bank: {t} involves ___, ___ and ___.", 3),
                  ("short", "In two sentences, describe what {t} is.", 3),
                  ("label", "Draw and label a simple diagram of {t}.", 4),
                  ("match", "Match each key term of {t} to its correct meaning.", 3),
                  ("apply", "Write one way {t} is used in your home or community.", 3),
                  ("challenge", "Challenge: explain what would happen if {t} stopped working.", 4)],
           "sw": [("fill", "Jaza nafasi kwa orodha ya maneno: {t} inahusisha ___, ___ na ___.", 3),
                  ("short", "Kwa sentensi mbili, eleza {t} ni nini.", 3),
                  ("label", "Chora na weka lebo mchoro rahisi wa {t}.", 4),
                  ("match", "Oanisha kila istilahi ya {t} na maana yake.", 3),
                  ("apply", "Andika njia moja {t} inavyotumika nyumbani au jamii yako.", 3),
                  ("challenge", "Changamoto: eleza nini kitatokea ikiwa {t} itaacha kufanya kazi.", 4)]}[lang]
    tasks = []
    for i in range(n):
        t = tpl[i % len(tpl)]
        tasks.append({"no": i + 1, "type": t[0], "prompt": t[1].replace("{t}", low), "lines": t[2],
                      "answer": ("Correct terms from the word bank placed in order." if t[0] == "fill" else "A correct, complete response as guided by the teacher.") if lang == "en" else ("Maneno sahihi kutoka orodha kwa mpangilio." if t[0] == "fill" else "Jibu sahihi na kamili kama alivyoongoza mwalimu.")})
    d["instructions"] = S[lang]["ws_instr"]; d["word_bank"] = bank; d["tasks"] = tasks
    d["extension"] = ("Extension: research one advanced example of " if lang == "en" else "Upanuzi: tafuta mfano mmoja wa juu wa ") + low + (" and share next lesson." if lang == "en" else " na ushiriki somo lijalo.")
    return d
def build_marking_guide(data):
    d = _base(data, "marking_guide")
    lang = d["language"]
    levels, criteria, maxs = S[lang]["levels"], S[lang]["criteria"], [4, 3, 3, 2]
    desc_en = [["Fully accurate, complete and insightful.", "Mostly accurate with minor gaps.", "Partially accurate with notable gaps.", "Limited or inaccurate understanding."],
               ["Precise terminology throughout.", "Mostly correct terminology.", "Some terminology errors.", "Frequent terminology errors."],
               ["Valid, well-justified real-life application.", "Valid application, brief justification.", "Application present but weakly linked.", "No valid application."],
               ["Clear, logical, well-communicated reasoning.", "Mostly clear reasoning.", "Reasoning hard to follow at times.", "Little or no coherent reasoning."]]
    desc_sw = [["Sahihi kabisa, kamili na yenye maarifa.", "Karibu sahihi na mapungufu madogo.", "Sahihi kwa sehemu.", "Uelewa mdogo au usio sahihi."],
               ["Istilahi sahihi kote.", "Istilahi nyingi sahihi.", "Makosa machache ya istilahi.", "Makosa mengi ya istilahi."],
               ["Matumizi halali yenye utetezi mzuri.", "Matumizi halali, utetezi mfupi.", "Matumizi yenye uhusiano dhaifu.", "Hakuna matumizi halali."],
               ["Hoja wazi na za kimantiki.", "Hoja nyingi wazi.", "Hoja ngumu kufuata.", "Hoja thabiti kidogo."]]
    desc = desc_sw if lang == "sw" else desc_en
    d["levels"] = levels
    d["rubric"] = [{"name": c, "max": maxs[i], "descriptors": desc[i]} for i, c in enumerate(criteria)]
    d["total_marks"] = sum(maxs)
    low = d["topic"].lower()
    d["exemplars"] = [{"q": ("Define " if lang == "en" else "Fafanua ") + low + ".", "answer": "A model definition using precise terminology, awarded full marks." if lang == "en" else "Ufafanuzi wa mfano kwa istilahi sahihi, alama kamili.", "marks": 2},
                      {"q": ("Apply " if lang == "en" else "Tumia ") + low + (" to a real-life case." if lang == "en" else " katika kesi halisi."), "answer": "A valid case with reasoned justification, awarded full marks." if lang == "en" else "Kesi halali na utetezi wenye hoja, alama kamili.", "marks": 3}]
    d["common_errors"] = S[lang]["errors"]; d["notes"] = S[lang]["notes"]
    d["auto_policy"] = ("Objective items (MCQ, true/false, numeric, matching, blanks, labels) are marked automatically. Open responses earn credit per matched marking point and are flagged for teacher confirmation. Essays require full teacher judgement." if lang == "en" else "Maswali ya objective husahihishwa kiotomatiki. Majibu ya wazi hupata alama kwa kila kipengele kinacholingana na huthibitishwa na mwalimu. Insha zinahitaji uamuzi wa mwalimu.")
    return d
def build_activity(data):
    d = _base(data, "activity")
    low, lang, total = d["topic"].lower(), d["language"], _total(data)
    mins = [max(5, int(round(total * w))) for w in (0.15, 0.5, 0.2, 0.15)]
    mins[-1] += total - sum(mins)
    steps = {"en": ["Setup & briefing", "Hands-on investigation", "Share & compare", "Reflect & connect"], "sw": ["Maandalizi na maelezo", "Uchunguzi wa vitendo", "Shiriki na linganisha", "Tafakari na unganisha"]}[lang]
    c_en = ["Introduce the challenge about {t}; assign roles and distribute materials.", "Groups investigate {t} hands-on, recording observations.", "Groups present findings; class compares results.", "Connect findings to everyday life and the next lesson."]
    c_sw = ["Anzisha changamoto kuhusu {t}; gawa majukumu na vifaa.", "Vikundi huchunguza {t} kwa vitendo, rekodi uchunguzi.", "Vikundi huwasilisha matokeo; darasa hulinganisha.", "Unganisha matokeo na maisha ya kila siku."]
    content = c_sw if lang == "sw" else c_en
    d["objective"] = S[lang]["objective"].replace("{t}", low)
    d["materials"] = S[lang]["materials"]
    d["steps"] = [{"step": steps[i], "duration": str(mins[i]) + " min", "content": content[i].replace("{t}", low)} for i in range(4)]
    d["grouping"] = S[lang]["grouping"]; d["safety"] = S[lang]["safety"]
    d["differentiation"] = S[lang]["diff"]; d["checklist"] = S[lang]["checklist"]
    return d
BUILDERS = {"lesson_plan": build_lesson, "quiz": build_quiz, "worksheet": build_worksheet,
            "marking_guide": build_marking_guide, "activity": build_activity}
def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\.\-/ ]+", " ", str(s or "").lower())).strip()
def _grade_band(pct):
    if pct >= 80:
        return "A · Exceeding expectation"
    if pct >= 65:
        return "B · Meeting expectation"
    if pct >= 50:
        return "C · Approaching expectation"
    if pct >= 40:
        return "D · Below expectation"
    return "E · Needs support"
def grade_question(q, ans):
    t = q.get("type")
    marks = float(q.get("marks") or 0)
    awarded, status, fb = 0.0, "wrong", ""
    if t == "mcq":
        try:
            sel = int(ans)
        except (TypeError, ValueError):
            sel = -1
        if sel == q.get("correct"):
            awarded, status, fb = marks, "correct", "Correct option selected."
        elif sel < 0:
            status, fb = "blank", "No option selected."
        else:
            fb = "Correct answer: " + str(q.get("answer"))
    elif t == "multi":
        correct = set(q.get("correct_multi") or [])
        try:
            sel = set(int(x) for x in (ans or []))
        except (TypeError, ValueError):
            sel = set()
        if not sel:
            status, fb = "blank", "No options selected."
        else:
            hits = len(sel & correct)
            misses = len(sel - correct)
            per = marks / max(1, len(correct))
            awarded = max(0.0, round((hits - misses) * per, 2))
            status = "correct" if awarded >= marks else ("partial" if awarded > 0 else "wrong")
            fb = "%d correct, %d incorrect selections." % (hits, misses)
    elif t == "tf":
        if ans in (None, ""):
            status, fb = "blank", "No choice made."
        else:
            truth = str(ans).lower() in ("true", "1", "yes")
            if truth == bool(q.get("tf_answer")):
                awarded, status, fb = marks, "correct", "Correct judgement."
            else:
                fb = "Correct answer: " + str(q.get("answer"))
    elif t == "numeric":
        spec = q.get("numeric") or {}
        m = re.search(r"-?\d+(?:\.\d+)?", str(ans or ""))
        if not m:
            status, fb = "blank", "No numeric answer given."
        else:
            val = float(m.group())
            if abs(val - float(spec.get("value", 0))) <= float(spec.get("tol", 0)) + 1e-9:
                awarded, status, fb = marks, "correct", "Correct value (method + answer marks)."
            else:
                awarded, status, fb = round(marks / 2, 2), "partial", "Method credit only. Expected " + str(spec.get("value")) + " " + str(spec.get("unit") or "")
    elif t == "fill":
        vals = ans if isinstance(ans, list) else [ans]
        accept = q.get("blanks_accept") or []
        hits = 0
        for i, group in enumerate(accept):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and any(got == _norm(a) or _norm(a) in got for a in group):
                hits += 1
        awarded = round(marks * hits / max(1, len(accept)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(accept) else ("partial" if hits else "wrong"))
        fb = "%d of %d blanks correct." % (hits, len(accept))
    elif t == "match":
        pairs = q.get("pairs") or []
        vals = ans if isinstance(ans, list) else []
        hits = 0
        for i, p in enumerate(pairs):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and got == _norm(p.get("meaning")):
                hits += 1
        awarded = round(marks * hits / max(1, len(pairs)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(pairs) else ("partial" if hits else "wrong"))
        fb = "%d of %d matches correct." % (hits, len(pairs))
    elif t == "diagram":
        expected = q.get("labels_expected") or []
        vals = ans if isinstance(ans, list) else []
        hits = 0
        for i, exp in enumerate(expected):
            got = _norm(vals[i]) if i < len(vals) else ""
            if got and (got == _norm(exp) or _norm(exp) in got):
                hits += 1
        awarded = round(marks * hits / max(1, len(expected)), 2)
        status = "blank" if not any(vals) else ("correct" if hits == len(expected) else ("partial" if hits else "wrong"))
        fb = "%d of %d labels correct." % (hits, len(expected))
    elif t in ("short", "structured"):
        text = _norm(ans)
        pts = q.get("points") or []
        if not text:
            status, fb = "blank", "No response written."
        else:
            hit_labels = []
            for p in pts:
                if any(_norm(k) and _norm(k) in text for k in (p.get("keywords") or [])):
                    awarded += float(p.get("mark") or 0)
                    hit_labels.append(p.get("label"))
            awarded = round(min(awarded, marks), 2)
            status = "correct" if awarded >= marks else ("partial" if awarded > 0 else "review")
            fb = ("Credit for: " + ", ".join(hit_labels)) if hit_labels else "No marking points detected — teacher review advised."
            if q.get("review"):
                status = "review" if awarded < marks else status
                fb += " (keyword match — confirm with teacher judgement)"
    else:
        status, fb = "review", "Extended response — requires teacher judgement against the rubric."
    return {"no": q.get("no"), "type": t, "marks": marks, "awarded": awarded, "status": status,
            "feedback": fb, "expected": q.get("answer"), "points": q.get("points") or []}
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
        content = json.dumps(BUILDERS.get(atype, build_lesson)(data), indent=2)
        kwargs = dict(institution=m.institution, created_by=request.user, artifact_type=atype, topic=topic, content=content)
        existing = {f.name for f in TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if f in existing:
                kwargs[f] = (data.get(f) or "")
        artifact = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="TEACHER_ARTIFACT_GENERATED",
                                      resource_type="TeachingArtifact", resource_id=str(artifact.id), metadata={"type": atype})
        except Exception:
            pass
        return Response({"id": str(artifact.id), "content": content, "topic": topic, "artifact_type": atype}, status=201)
    @action(detail=False, methods=["post"], url_path="automark")
    def automark(self, request):
        data = request.data if isinstance(request.data, dict) else {}
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"detail": "You must belong to an institution."}, status=400)
        art = TeachingArtifact.objects.filter(id=data.get("artifact_id"), institution=m.institution).first()
        if not art:
            return Response({"detail": "Artifact not found."}, status=404)
        try:
            lesson = json.loads(art.content)
        except Exception:
            return Response({"detail": "Artifact is not a markable quiz."}, status=400)
        questions = lesson.get("questions") or []
        if not questions:
            return Response({"detail": "This artifact has no questions."}, status=400)
        answers = data.get("answers") or {}
        results = [grade_question(q, answers.get(str(q.get("no")), answers.get(q.get("no")))) for q in questions]
        total = sum(r["marks"] for r in results)
        awarded = round(sum(r["awarded"] for r in results), 2)
        pending = [r["no"] for r in results if r["status"] == "review"]
        pct = round(100.0 * awarded / total, 1) if total else 0.0
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="QUIZ_AUTO_MARKED",
                                      resource_type="TeachingArtifact", resource_id=str(art.id),
                                      metadata={"awarded": awarded, "total": total, "percent": pct, "pending": pending})
        except Exception:
            pass
        return Response({"total_marks": total, "awarded": awarded, "percentage": pct,
                         "band": _grade_band(pct), "pending": pending, "results": results})
'''
(base / "apps/teacher_studio/views.py").write_text(VIEWS, encoding="utf-8")
TPL = r'''{% extends "base.html" %}
{% block title %}Teacher Studio — JIFUNZE AI{% endblock %}
{% block content %}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<script src="https://unpkg.com/lucide@latest"></script>
<script src="/static/js/vendor/jspdf.umd.min.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js'"></script>
<script src="/static/js/vendor/jspdf.plugin.autotable.min.js" onerror="this.onerror=null;this.src='https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js'"></script>
<style>
  :root{--indigo:#1B1F4B;--indigo2:#2A3070;--champ:#C9A227;--green:#10B981;--green2:#0E9F6E;--bg:#FDFCF8;--card:#FFFFFF;--ink:#0F172A;--mut:#64748B;--line:#E4E1D6;--soft:#F6F4EC;--amber:#F59E0B;--red:#DC2626;}
  *{scrollbar-width:thin;scrollbar-color:#C9C4B4 #EFEDE6;}
  *::-webkit-scrollbar{width:10px;height:10px;}
  *::-webkit-scrollbar-track{background:#EFEDE6;}
  *::-webkit-scrollbar-thumb{background:#C9C4B4;border-radius:8px;border:2px solid #EFEDE6;}
  *::-webkit-scrollbar-thumb:hover{background:var(--indigo);}
  .jf{font-family:Inter,sans-serif;color:var(--ink);background:radial-gradient(1100px 500px at 85% -10%,rgba(27,31,75,.06),transparent 60%),radial-gradient(900px 480px at -10% 110%,rgba(16,185,129,.07),transparent 60%),var(--bg);min-height:100vh;}
  .jf h1,.jf h2,.jf h3{font-family:Manrope,sans-serif;}
  .jf-card{background:var(--card);border:1px solid var(--line);border-radius:1rem;box-shadow:0 6px 18px -8px rgba(27,31,75,.14);}
  .jf label{display:block;font-size:.8rem;font-weight:600;margin-bottom:.35rem;}
  .jf input,.jf select,.jf textarea{width:100%;border:1px solid var(--line);border-radius:.6rem;padding:.6rem .7rem;background:#fff;font-size:.9rem;font-family:inherit;transition:.15s;}
  .jf input:focus,.jf select:focus,.jf textarea:focus{outline:none;border-color:var(--indigo);box-shadow:0 0 0 3px rgba(27,31,75,.14);}
  .jf-btn{background:var(--indigo);color:#fff;font-weight:600;border-radius:.7rem;padding:.8rem;width:100%;display:flex;align-items:center;justify-content:center;gap:.5rem;cursor:pointer;border:none;transition:.18s;box-shadow:0 8px 20px -10px rgba(27,31,75,.55);font-size:.88rem;}
  .jf-btn:hover{background:var(--indigo2);transform:translateY(-1px);}
  .jf-btn:disabled{opacity:.65;cursor:wait;transform:none;}
  .jf-btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line);box-shadow:none;}
  .jf-btn.ghost:hover{background:var(--soft);}
  .jf-btn.green{background:var(--green2);}
  .jf-btn.green:hover{background:#0b8457;}
  .chip{font-size:.68rem;font-weight:700;letter-spacing:.04em;padding:.22rem .6rem;border-radius:9999px;background:#EEF0F6;color:#3B4270;}
  .tl{position:relative;padding-left:2.6rem;}
  .tl::before{content:"";position:absolute;left:15px;top:10px;bottom:10px;width:2px;background:linear-gradient(var(--indigo),var(--green));opacity:.35;}
  .tl-item{position:relative;margin-bottom:1.1rem;}
  .tl-dot{position:absolute;left:-2.6rem;top:2px;width:32px;height:32px;border-radius:50%;background:#fff;border:2px solid var(--line);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.72rem;color:var(--indigo);}
  .tl-item.active .tl-dot{background:var(--indigo);color:#fff;border-color:var(--indigo);}
  .oc{display:flex;gap:.9rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.22);padding:.9rem 1rem;border-radius:.7rem;}
  .oc b{width:1.9rem;height:1.9rem;border-radius:50%;background:var(--green);color:#fff;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:.85rem;}
  .stat{background:var(--soft);border:1px solid var(--line);border-radius:.7rem;padding:.7rem .8rem;}
  .stat p:first-child{font-size:.62rem;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);font-weight:700;}
  .stat p:last-child{font-family:Manrope;font-weight:800;font-size:.95rem;margin-top:.15rem;}
  .qcard{border:1px solid var(--line);border-radius:.8rem;padding:1rem 1.1rem;margin-bottom:.9rem;background:#fff;}
  .optrow{display:flex;gap:.6rem;align-items:flex-start;padding:.45rem .6rem;border:1px solid var(--line);border-radius:.5rem;margin-top:.4rem;font-size:.9rem;cursor:pointer;}
  .optrow:hover{background:var(--soft);}
  .optrow input{width:auto;margin-top:.2rem;}
  .answer{display:none;margin-top:.7rem;background:rgba(16,185,129,.08);border:1px dashed var(--green2);border-radius:.6rem;padding:.7rem .8rem;font-size:.85rem;}
  .show-answers .answer{display:block;}
  .fb{display:none;margin-top:.6rem;border-radius:.55rem;padding:.55rem .75rem;font-size:.82rem;font-weight:600;}
  .fb.correct{display:block;background:#DCFCE7;color:#166534;}
  .fb.partial{display:block;background:#FEF3C7;color:#92400E;}
  .fb.wrong{display:block;background:#FEE2E2;color:#991B1B;}
  .fb.review{display:block;background:#E0E7FF;color:#3730A3;}
  .fb.blank{display:block;background:#F1F5F9;color:#475569;}
  .lines{margin-top:.6rem;height:calc(var(--n)*1.6rem);background:repeating-linear-gradient(transparent,transparent calc(1.6rem - 1px),var(--line) calc(1.6rem - 1px),var(--line) 1.6rem);}
  .wb{display:inline-block;background:#EEF0F6;border:1px solid var(--line);border-radius:9999px;padding:.25rem .7rem;font-size:.78rem;font-weight:600;margin:.15rem;}
  .rubric{width:100%;border-collapse:collapse;font-size:.8rem;}
  .rubric th,.rubric td{border:1px solid var(--line);padding:.55rem .6rem;text-align:left;vertical-align:top;}
  .rubric th{background:var(--indigo);color:#fff;font-family:Manrope;}
  .rubric td:first-child{font-weight:700;background:var(--soft);}
  .safety{background:#FEF2F2;border-left:4px solid var(--red);padding:.9rem 1rem;border-radius:0 .6rem .6rem 0;}
  .check{display:flex;gap:.6rem;padding:.45rem .6rem;border:1px solid var(--line);border-radius:.5rem;margin-top:.4rem;font-size:.88rem;}
  .diagram{border:1px dashed var(--line);border-radius:.7rem;background:var(--soft);padding:1rem;margin-top:.6rem;}
  .score{background:linear-gradient(135deg,var(--indigo),#343C86);color:#fff;border-radius:1rem;padding:1.2rem 1.4rem;margin-bottom:1.4rem;}
  .score .big{font-family:Manrope;font-size:2.2rem;font-weight:800;line-height:1;}
  .fade{animation:fade .35s ease;}
  @keyframes fade{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
  @media print{.no-print{display:none!important;}.jf{background:#fff;}.jf-card{box-shadow:none;border:none;}.score{background:#334155!important;-webkit-print-color-adjust:exact;}.rubric th{background:#334155!important;-webkit-print-color-adjust:exact;}}
</style>
<div class="jf px-4 py-8">
 <div class="max-w-7xl mx-auto">
  <div class="flex items-end justify-between mb-6 no-print">
    <div><h1 class="text-3xl font-extrabold" style="color:var(--indigo)">Teacher Studio</h1>
    <p class="mt-1" style="color:var(--mut)">Generate, auto-mark and export curriculum-aligned materials.</p></div>
    <span class="chip" style="background:var(--indigo);color:#fff">AI POWERED</span>
  </div>
  <div id="err" class="no-print hidden" style="background:#FEF2F2;border:1px solid #FECACA;color:#B91C1C;border-radius:.7rem;padding:1rem;margin-bottom:1.4rem;white-space:pre-wrap;font-size:.8rem"></div>
  <div class="grid lg:grid-cols-12 gap-8">
    <div class="lg:col-span-4 no-print">
      <div class="jf-card p-6" style="position:sticky;top:24px;max-height:calc(100vh - 60px);overflow:auto">
        <form id="genform" class="space-y-4">
          {% csrf_token %}
          <div><label>Artifact type</label>
            <select id="atype"><option value="lesson_plan">Lesson Plan</option><option value="quiz">Quiz / Assessment</option><option value="worksheet">Worksheet</option><option value="marking_guide">Marking Guide</option><option value="activity">Learning Activity</option></select></div>
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
            <div><label>Questions / tasks</label><select id="count"><option>4</option><option selected>6</option><option>8</option><option>10</option><option>12</option><option>15</option><option>20</option></select></div>
            <div><label>Difficulty</label><select id="difficulty"><option>Foundation</option><option selected>Standard</option><option>Challenge</option></select></div>
          </div>
          <div><label>Question mix</label>
            <select id="mix"><option value="balanced">Balanced (all types)</option><option value="mcq">Objective-heavy (MCQ / T-F)</option><option value="short">Short answer &amp; blanks</option><option value="structured">Structured exam-style</option><option value="practical">Illustrative / practical</option></select></div>
          <button type="submit" id="btn" class="jf-btn"><i data-lucide="sparkles"></i> Generate Material</button>
        </form>
      </div>
    </div>
    <div class="lg:col-span-8">
      <div id="empty" class="jf-card p-16 text-center" style="border:2px dashed var(--line);color:var(--mut)">Your generated material will appear here.</div>
      <div id="out" class="hidden fade">
        <div class="flex flex-wrap gap-3 mb-4 no-print">
          <button id="markBtn" class="jf-btn green flex-1 hidden"><i data-lucide="check-check"></i> Auto-mark</button>
          <button id="ansBtn" class="jf-btn ghost flex-1"><i data-lucide="eye"></i> Marking scheme</button>
          <button id="printBtn" class="jf-btn ghost flex-1"><i data-lucide="printer"></i> Print</button>
          <button id="dlBtn" class="jf-btn ghost flex-1"><i data-lucide="file-down"></i> Download PDF</button>
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
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
var I18N={en:{out:"Learning Outcomes",intro:"By the end of this lesson, learners will be able to:",flow:"Lesson Flow",res:"Teaching Resources",diff:"Differentiation",ass:"Assessment & Rubric",notes:"Teacher Notes",plan:"Lesson Plan",dur:"Duration",subj:"Subject",grade:"Grade",wt:"Week / Term",marks:"Total marks",instr:"Instructions",wb:"Word bank",ext:"Extension",rub:"Rubric",ex:"Exemplar answers",err:"Common errors",obj:"Objective",mat:"Materials",grp:"Grouping",safe:"Safety",chk:"Success checklist",ans:"Answer",pts:"Marking points",q:"Question",task:"Task",scheme:"Marking scheme",auto:"Auto-markable",review:"Teacher review"},sw:{out:"Matokeo ya Kujifunza",intro:"Mwisho wa somo, wanafunzi wataweza:",flow:"Mtiririko wa Somo",res:"Nyenzo za Kufundisha",diff:"Utofautishaji",ass:"Tathmini na Rubriki",notes:"Maelezo ya Mwalimu",plan:"Mpango wa Somo",dur:"Muda",subj:"Somo",grade:"Darasa",wt:"Wiki / Muhula",marks:"Jumla ya alama",instr:"Maagizo",wb:"Orodha ya maneno",ext:"Upanuzi",rub:"Rubriki",ex:"Majibu ya mfano",err:"Makosa ya kawaida",obj:"Lengo",mat:"Vifaa",grp:"Uvikundi",safe:"Usalama",chk:"Orodha ya mafanikio",ans:"Jibu",pts:"Vipengele vya alama",q:"Swali",task:"Kazi",scheme:"Mpango wa alama",auto:"Kiotomatiki",review:"Mapitio ya mwalimu"}};
var currentContent="",currentLesson=null,currentArtifactId=null,lastMark=null;
var TYPE_LABEL={mcq:"Multiple choice",multi:"Multi-select",tf:"True / False",numeric:"Calculation",fill:"Fill in the blanks",match:"Matching",short:"Short answer",structured:"Structured",diagram:"Illustrative / labelling",essay:"Extended response"};
function header(d,b,L,sub){return '<div style="border-bottom:2px solid var(--indigo);padding-bottom:1.4rem;margin-bottom:1.6rem"><div class="flex flex-wrap gap-2 mb-2"><span class="chip" style="background:var(--indigo);color:#fff">AI GENERATED</span><span class="chip" style="background:#DCFCE7;color:#166534">'+esc(d.curriculum)+'</span><span class="chip" style="background:#FEF3C7;color:#92400E">'+esc(d.grade_level)+'</span></div><h2 class="text-3xl font-extrabold" style="color:var(--indigo)">'+esc(d.title)+'</h2><p style="color:var(--mut)">'+esc(sub)+' · '+esc(d.duration)+(b.subtopic?' · '+esc(b.subtopic):'')+'</p><div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4"><div class="stat"><p>'+L.dur+'</p><p>'+esc(d.duration)+'</p></div><div class="stat"><p>'+L.subj+'</p><p>'+esc(d.subject)+'</p></div><div class="stat"><p>'+L.grade+'</p><p>'+esc(d.grade_level)+'</p></div><div class="stat"><p>'+L.wt+'</p><p>'+esc((d.week||"—")+" / "+(d.term||"—"))+'</p></div></div></div>';}
function schemeBlock(q,L){var pts=(q.points||[]).map(function(p){return '<div>'+esc(p.label)+' ('+p.mark+'): '+esc(p.desc)+'</div>';}).join("");return '<div class="answer"><strong>'+L.ans+':</strong> '+esc(q.answer)+(q.explain?'<div class="mt-1" style="color:var(--mut)">'+esc(q.explain)+'</div>':'')+(pts?'<div class="mt-2"><strong>'+L.pts+':</strong>'+pts+'</div>':'')+'</div>';}
function answerInput(q){var n=q.no;
 if(q.type==="mcq"||q.type==="tf"){var opts=q.type==="tf"?["True","False"]:q.options;return opts.map(function(o,i){return '<label class="optrow"><input type="radio" name="q'+n+'" value="'+(q.type==="tf"?o.toLowerCase():i)+'"><span><b>'+String.fromCharCode(65+i)+'.</b> '+esc(o)+'</span></label>';}).join("");}
 if(q.type==="multi"){return q.options.map(function(o,i){return '<label class="optrow"><input type="checkbox" name="q'+n+'" value="'+i+'"><span>'+esc(o)+'</span></label>';}).join("");}
 if(q.type==="numeric"){return '<input class="mt-2" data-q="'+n+'" placeholder="Your answer'+(q.numeric&&q.numeric.unit?' in '+esc(q.numeric.unit):'')+'">';}
 if(q.type==="fill"){var h='';for(var i=0;i<(q.blanks||3);i++)h+='<input class="mt-2" data-q="'+n+'" data-i="'+i+'" placeholder="Blank '+(i+1)+'">';return h;}
 if(q.type==="diagram"){var h='<div class="diagram"><p class="text-xs mb-2" style="color:var(--mut)">Label each numbered part.</p>';(q.labels_expected||[]).forEach(function(x,i){h+='<div class="flex items-center gap-2 mt-2"><span class="chip">'+(i+1)+'</span><input data-q="'+n+'" data-i="'+i+'" placeholder="Label '+(i+1)+'"></div>';});return h+'</div>';}
 if(q.type==="match"){var h='<div class="mt-2">';(q.pairs||[]).forEach(function(p,i){h+='<div class="grid grid-cols-2 gap-2 items-center mt-2"><span class="text-sm font-semibold">'+esc(p.term)+'</span><select data-q="'+n+'" data-i="'+i+'"><option value="">— choose —</option>'+q.meanings.map(function(m){return '<option>'+esc(m)+'</option>';}).join("")+'</select></div>';});return h+'</div>';}
 if(q.type==="essay"){return '<textarea class="mt-2" rows="6" data-q="'+n+'" placeholder="Write your extended response..."></textarea>';}
 if(q.type==="structured"){return '<textarea class="mt-2" rows="4" data-q="'+n+'" placeholder="Step-by-step explanation..."></textarea>';}
 return '<textarea class="mt-2" rows="2" data-q="'+n+'" placeholder="Your answer..."></textarea>';}
function renderQuiz(d,b,L){var qs=(d.questions||[]).map(function(q){return '<div class="qcard" id="qc'+q.no+'"><div class="flex flex-wrap justify-between items-center gap-2 mb-2"><span class="chip" style="background:var(--indigo);color:#fff">'+L.q+' '+q.no+'</span><div class="flex gap-2"><span class="chip">'+esc(TYPE_LABEL[q.type]||q.type)+'</span><span class="chip" style="background:#FEF3C7;color:#92400E">'+q.marks+' marks</span>'+(q.auto?'':'<span class="chip" style="background:#E0E7FF;color:#3730A3">'+L.review+'</span>')+'</div></div><p class="font-medium mb-1">'+esc(q.stem)+'</p>'+answerInput(q)+schemeBlock(q,L)+'<div class="fb" id="fb'+q.no+'"></div></div>';}).join("");
 return header(d,b,L,"Quiz")+'<div class="flex flex-wrap gap-3 mb-4"><div class="stat"><p>'+L.marks+'</p><p>'+d.total_marks+'</p></div><div class="stat"><p>'+L.auto+'</p><p>'+d.auto_markable+'</p></div><div class="stat"><p>'+L.review+'</p><p>'+d.review_marks+'</p></div></div><p style="color:var(--mut);font-size:.9rem" class="mb-4">'+esc(d.instructions)+'</p>'+qs;}
function renderLesson(d,b,L){var oc=(d.outcomes||[]).map(function(o,i){return '<div class="oc"><b>'+(i+1)+'</b><span>'+esc(o)+'</span></div>';}).join("");var fl=(d.flow||[]).map(function(x,i){return '<div class="tl-item '+(i===0?"active":"")+'"><div class="tl-dot">'+String(i+1).padStart(2,"0")+'</div><div class="jf-card p-4"><div class="flex justify-between mb-1"><h3 class="font-bold" style="color:var(--indigo)">'+esc(x.step)+'</h3><span class="chip">'+esc(x.duration)+'</span></div><p style="color:var(--mut);font-size:.9rem">'+esc(x.content)+'</p></div></div>';}).join("");return header(d,b,L,L.plan)+'<h3 class="text-xl font-bold mb-2" style="color:var(--indigo)">'+L.out+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-3">'+L.intro+'</p><div class="space-y-2 mb-8">'+oc+'</div><h3 class="text-xl font-bold mb-4" style="color:var(--indigo)">'+L.flow+'</h3><div class="tl mb-8">'+fl+'</div><div class="grid md:grid-cols-2 gap-6 mb-8"><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.res+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.resources)+'</p></div><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.diff+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.differentiation)+'</p></div></div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.ass+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-6">'+esc(d.assessment)+'</p><div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem"><strong style="color:#92400E">'+L.notes+':</strong> <span style="color:#92400E">'+esc(d.teacher_notes)+'</span></div>';}
function renderWorksheet(d,b,L){var wb=(d.word_bank||[]).map(function(w){return '<span class="wb">'+esc(w)+'</span>';}).join("");var ts=(d.tasks||[]).map(function(t){return '<div class="qcard"><div class="flex justify-between mb-2"><span class="chip" style="background:var(--indigo);color:#fff">'+L.task+' '+t.no+'</span><span class="chip">'+esc(t.type)+'</span></div><p class="font-medium">'+esc(t.prompt)+'</p><div class="lines" style="--n:'+t.lines+'"></div><div class="answer"><strong>'+L.ans+':</strong> '+esc(t.answer)+'</div></div>';}).join("");return header(d,b,L,"Worksheet")+'<p style="color:var(--mut);font-size:.9rem" class="mb-3">'+esc(d.instructions)+'</p><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.wb+'</h3><div class="mb-5">'+wb+'</div>'+ts+'<div style="background:#EEF0F6;border:1px solid var(--line);border-radius:.6rem;padding:.9rem 1rem" class="mt-4"><strong style="color:var(--indigo)">'+L.ext+':</strong> '+esc(d.extension)+'</div>';}
function renderMarkingGuide(d,b,L){var head='<tr><th style="width:22%">'+L.rub+'</th>'+d.levels.map(function(l){return '<th>'+esc(l)+'</th>';}).join("")+'</tr>';var rows=(d.rubric||[]).map(function(r){return '<tr><td>'+esc(r.name)+' <span class="chip">/'+r.max+'</span></td>'+r.descriptors.map(function(x){return '<td>'+esc(x)+'</td>';}).join("")+'</tr>';}).join("");var ex=(d.exemplars||[]).map(function(e){return '<div class="qcard"><p class="font-medium">'+esc(e.q)+'</p><div class="answer" style="display:block"><strong>'+L.ans+':</strong> '+esc(e.answer)+' <span class="chip">'+e.marks+' marks</span></div></div>';}).join("");var er=(d.common_errors||[]).map(function(x){return '<div class="check"><span>'+esc(x)+'</span></div>';}).join("");return header(d,b,L,"Marking Guide")+'<div class="stat mb-4" style="display:inline-block"><p>'+L.marks+'</p><p>'+d.total_marks+'</p></div><div style="overflow-x:auto" class="mb-6"><table class="rubric">'+head+rows+'</table></div><div style="background:#EEF0F6;border:1px solid var(--line);border-radius:.6rem;padding:.9rem 1rem" class="mb-6"><strong style="color:var(--indigo)">Auto-marking policy:</strong> '+esc(d.auto_policy)+'</div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.ex+'</h3>'+ex+'<h3 class="font-bold mb-2 mt-6" style="color:var(--indigo)">'+L.err+'</h3>'+er+'<div style="background:#FFFBEB;border-left:4px solid var(--amber);padding:1rem" class="mt-6"><strong style="color:#92400E">'+L.notes+':</strong> <span style="color:#92400E">'+esc(d.notes)+'</span></div>';}
function renderActivity(d,b,L){var mat=(d.materials||[]).map(function(m){return '<span class="wb">'+esc(m)+'</span>';}).join("");var st=(d.steps||[]).map(function(x,i){return '<div class="tl-item '+(i===0?"active":"")+'"><div class="tl-dot">'+String(i+1).padStart(2,"0")+'</div><div class="jf-card p-4"><div class="flex justify-between mb-1"><h3 class="font-bold" style="color:var(--indigo)">'+esc(x.step)+'</h3><span class="chip">'+esc(x.duration)+'</span></div><p style="color:var(--mut);font-size:.9rem">'+esc(x.content)+'</p></div></div>';}).join("");var ck=(d.checklist||[]).map(function(c){return '<div class="check"><span>'+esc(c)+'</span></div>';}).join("");return header(d,b,L,"Learning Activity")+'<h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.obj+'</h3><p style="color:var(--mut);font-size:.9rem" class="mb-5">'+esc(d.objective)+'</p><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.mat+'</h3><div class="mb-5">'+mat+'</div><h3 class="text-xl font-bold mb-4" style="color:var(--indigo)">'+L.flow+'</h3><div class="tl mb-6">'+st+'</div><div class="grid md:grid-cols-2 gap-6 mb-6"><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.grp+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.grouping)+'</p></div><div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.diff+'</h3><p style="color:var(--mut);font-size:.9rem">'+esc(d.differentiation)+'</p></div></div><div class="safety mb-6"><strong style="color:var(--red)">'+L.safe+':</strong> <span style="color:#7F1D1D">'+esc(d.safety)+'</span></div><h3 class="font-bold mb-2" style="color:var(--indigo)">'+L.chk+'</h3>'+ck;}
function renderAny(d,b){var L=I18N[d.language==="sw"?"sw":"en"];var k=d.kind||"lesson_plan";if(k==="quiz")return renderQuiz(d,b,L);if(k==="worksheet")return renderWorksheet(d,b,L);if(k==="marking_guide")return renderMarkingGuide(d,b,L);if(k==="activity")return renderActivity(d,b,L);return renderLesson(d,b,L);}
function collect(){var out={};(currentLesson.questions||[]).forEach(function(q){var n=q.no;
 if(q.type==="mcq"||q.type==="tf"){var el=document.querySelector('input[name="q'+n+'"]:checked');out[n]=el?el.value:null;}
 else if(q.type==="multi"){out[n]=Array.prototype.slice.call(document.querySelectorAll('input[name="q'+n+'"]:checked')).map(function(x){return x.value;});}
 else if(q.type==="fill"||q.type==="diagram"||q.type==="match"){out[n]=Array.prototype.slice.call(document.querySelectorAll('[data-q="'+n+'"]')).map(function(x){return x.value;});}
 else{var t=document.querySelector('[data-q="'+n+'"]');out[n]=t?t.value:"";}});return out;}
function showResults(r){var doc=document.getElementById("doc");var old=document.getElementById("scorecard");if(old)old.remove();
 var card=document.createElement("div");card.id="scorecard";card.className="score";
 card.innerHTML='<div class="flex flex-wrap items-center justify-between gap-4"><div><p class="text-xs uppercase tracking-widest opacity-80">Auto-marked result</p><p class="big">'+r.awarded+' / '+r.total_marks+'</p></div><div><p class="text-xs uppercase tracking-widest opacity-80">Percentage</p><p class="big">'+r.percentage+'%</p></div><div><p class="text-xs uppercase tracking-widest opacity-80">Performance</p><p class="font-bold text-lg">'+esc(r.band)+'</p></div><div><p class="text-xs uppercase tracking-widest opacity-80">Teacher review</p><p class="font-bold text-lg">'+(r.pending.length?r.pending.length+" item(s)":"None")+'</p></div></div>';
 doc.insertBefore(card,doc.firstChild);
 r.results.forEach(function(x){var fb=document.getElementById("fb"+x.no);if(!fb)return;fb.className="fb "+x.status;fb.textContent=x.awarded+" / "+x.marks+" — "+x.feedback;});
 lucide.createIcons();}
var f=document.getElementById("genform"),btn=document.getElementById("btn"),err=document.getElementById("err");
f.addEventListener("submit",async function(e){e.preventDefault();err.classList.add("hidden");btn.disabled=true;btn.innerHTML="Generating...";
 var token=document.querySelector("[name=csrfmiddlewaretoken]").value;
 var body={artifact_type:document.getElementById("atype").value,topic:document.getElementById("topic").value,subtopic:document.getElementById("subtopic").value,grade_level:gradeSel.value,curriculum:currSel.value,week:document.getElementById("week").value,term:document.getElementById("term").value,duration:document.getElementById("duration").value,language:document.getElementById("language").value,count:document.getElementById("count").value,difficulty:document.getElementById("difficulty").value,mix:document.getElementById("mix").value};
 try{var r=await fetch("/api/teacher/artifacts/generate/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify(body)});
 var raw=await r.text();if(!r.ok)throw new Error("HTTP "+r.status+": "+raw.slice(0,300));
 var d=JSON.parse(raw);currentContent=d.content||"";currentArtifactId=d.id;lastMark=null;
 try{currentLesson=JSON.parse(d.content);}catch(_){currentLesson=null;}
 document.getElementById("empty").classList.add("hidden");document.getElementById("out").classList.remove("hidden");
 var doc=document.getElementById("doc");doc.classList.remove("show-answers");
 doc.innerHTML=currentLesson?renderAny(currentLesson,body):('<pre style="white-space:pre-wrap">'+esc(d.content)+'</pre>');
 document.getElementById("markBtn").classList.toggle("hidden",!(currentLesson&&currentLesson.kind==="quiz"));
 lucide.createIcons();
 }catch(ex){err.textContent=ex.message;err.classList.remove("hidden");}
 finally{btn.disabled=false;btn.innerHTML='<i data-lucide="sparkles"></i> Generate Material';lucide.createIcons();}});
document.getElementById("markBtn").onclick=async function(){if(!currentArtifactId)return;var b=this;b.disabled=true;b.innerHTML="Marking...";
 try{var token=document.querySelector("[name=csrfmiddlewaretoken]").value;
 var r=await fetch("/api/teacher/artifacts/automark/",{method:"POST",credentials:"same-origin",headers:{"X-CSRFToken":token,"Content-Type":"application/json"},body:JSON.stringify({artifact_id:currentArtifactId,answers:collect()})});
 var raw=await r.text();if(!r.ok)throw new Error(raw.slice(0,200));lastMark=JSON.parse(raw);showResults(lastMark);
 }catch(ex){err.textContent=ex.message;err.classList.remove("hidden");}
 finally{b.disabled=false;b.innerHTML='<i data-lucide="check-check"></i> Auto-mark';lucide.createIcons();}};
document.getElementById("ansBtn").onclick=function(){var doc=document.getElementById("doc");var on=doc.classList.toggle("show-answers");this.innerHTML=on?'<i data-lucide="eye-off"></i> Hide scheme':'<i data-lucide="eye"></i> Marking scheme';lucide.createIcons();};
document.getElementById("printBtn").onclick=function(){window.print();};
</script>
<script src="/static/js/studio_pdf.js"></script>
{% endblock %}'''
(base / "templates/teacher_studio/studio.html").write_text(TPL, encoding="utf-8")
print("20-QUESTION MIX + MARKING SCHEME + AUTO-MARKING INSTALLED")
