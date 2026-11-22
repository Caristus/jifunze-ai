import json
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
def build_scheme(data):
    d = _base(data, "scheme_of_work")
    low, lang, b = d["topic"].lower(), d["language"], d["band"]
    n = _count(data)
    facts = _facts(low)
    prog = (["Utangulizi na tathmini ya msingi", "Dhana kuu na istilahi", "Mazoezi ya kuongozwa na matumizi",
             "Matumizi papana na uchunguzi", "Tathmini, maona na marejeo"] if lang == "sw" else
            ["Introduction and baseline assessment", "Core concepts and terminology", "Guided practice and application",
             "Extended application and investigation", "Assessment, feedback and revision"])
    subs = ((facts["parts"] if facts else []) + prog)
    verbs = {"early": ["Identify", "Describe"], "primary": ["Describe", "Demonstrate"],
             "junior": ["Explain", "Apply"], "senior": ["Analyse", "Evaluate"]}[b]
    weeks = []
    for i in range(n):
        sub = subs[i % len(subs)]
        weeks.append({
            "week": i + 1, "subtopic": sub.title(), "lessons": 3,
            "objectives": ["%s %s in the context of %s." % (verbs[0], sub.lower(), low),
                           "%s the relationship between %s and %s." % (verbs[1], sub.lower(), low)],
            "activities": [("Group discussion and concept mapping of %s." % sub.lower()) if lang == "en" else ("Mjadala wa kikundi na ramani ya dhana ya %s." % sub.lower()),
                           ("Practical/task-based practice on %s." % sub.lower()) if lang == "en" else ("Mazoezi ya vitendo kuhusu %s." % sub.lower())],
            "assessment": ("Exit ticket + weekly quiz on %s." % sub.lower()) if lang == "en" else ("Karatasi ya kutoka + jaribio la wiki kuhusu %s." % sub.lower()),
            "resources": S[lang]["res"],
        })
    d["weeks"] = weeks
    d["coverage"] = ("100%% of %s spread across %d teaching weeks" % (low, n)) if lang == "en" else ("100%% ya %s ikisambazwa kwa wiki %d za mafundisho" % (low, n))
    d["notes"] = S[lang]["notes"]
    return d
def build_revision(data):
    d = _base(data, "revision_notes")
    low, lang = d["topic"].lower(), d["language"]
    facts = _facts(low)
    key_terms = facts["parts"] if facts else ([low] + ["definition", "structure", "function", "application"])
    d["key_terms"] = key_terms
    d["summary"] = (("%s is understood through: %s." % (low.title(), ", ".join((facts["kw"] if facts else key_terms)[:6]))) if lang == "en"
                    else ("%s inaeleweka kupitia: %s." % (low.title(), ", ".join((facts["kw"] if facts else key_terms)[:6]))))
    d["key_points"] = ([("Define %s precisely using key terms." % low),
                        ("Explain the role of each of: %s." % ", ".join(key_terms[:4])),
                        ("Apply %s to one real-life example." % low),
                        ("Practise past-paper questions under timed conditions.")] if lang == "en" else
                       [("Fafanua %s kwa usahihi kwa istilahi muhimu." % low),
                        ("Eleza dhima ya kila moja ya: %s." % ", ".join(key_terms[:4])),
                        ("Tumia %s katika mfano mmoja halisi." % low),
                        ("Fanya maswali ya mitihani iliyopita kwa muda uliopangwa.")])
    num = facts.get("numeric") if facts else None
    d["worked_example"] = (("%s Answer: %s." % (num["q"], num["answer"])) if num else
                           ("Method: (1) write what is asked, (2) list known facts, (3) apply the rule, (4) check units and reasonableness." if lang == "en"
                            else "Mbinu: (1) andika kinachoulizwa, (2) orodhesha ukweli unaojulikana, (3) tumia kanuni, (4) hakiki vitengo."))
    d["exam_questions"] = [
        {"q": ("Define %s." % low) if lang == "en" else ("Fafanua %s." % low), "a": ("A precise definition using: %s." % ", ".join(key_terms[:3]))},
        {"q": ("State two applications of %s." % low) if lang == "en" else ("Taja matumizi mawili ya %s." % low), "a": ("Any two valid, explained applications.")},
        {"q": ("Explain %s step by step." % low) if lang == "en" else ("Eleza %s hatua kwa hatua." % low), "a": ("Ordered explanation covering the key points.")},
    ]
    d["mnemonic"] = "".join(wd[0].upper() for wd in key_terms[:6]) or "REVISE"
    d["checklist"] = ([("I can define %s without notes." % low), ("I can label/draw %s." % low), ("I can answer past-paper questions on %s." % low)] if lang == "en"
                      else [("Ninaweza kufafanua %s bila madokezo." % low), ("Ninaweza kuchora/kuweka lebo %s." % low), ("Ninaweza kujibu maswali ya mitihani kuhusu %s." % low)])
    return d


BUILDERS = {"lesson_plan": build_lesson, "scheme_of_work": build_scheme, "revision_notes": build_revision, "quiz": build_quiz, "worksheet": build_worksheet,
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
def _advice(pct, pending, lang):
    if lang == "sw":
        if pct >= 80:
            return ["Bora sana — endeleza kwa maswali ya changamoto zaidi."]
        if pct >= 65:
            return ["Nzuri — fanya marejeo madogo ya dhana zilizokosewa."]
        if pct >= 50:
            return ["Inakaribia — rudia mada hii kwa mifano zaidi ya vitendo."]
        return ["Rudia mafundisho ya msingi ya mada hii kwa msaada wa mwalimu."]
    if pct >= 80:
        return ["Excellent mastery — extend with challenge questions and peer teaching."]
    if pct >= 65:
        return ["Good grasp — brief revision of the missed concepts will close the gap."]
    if pct >= 50:
        return ["Approaching competence — reteach the topic with worked examples before retesting."]
    return ["Foundational gaps — schedule supported reteaching and a diagnostic retake."]
def grade_question(q, ans, lang="en"):
    t = q.get("type")
    marks = float(q.get("marks") or 0)
    awarded, status, fb, conf = 0.0, "wrong", "", 1.0
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
            hits, misses = len(sel & correct), len(sel - correct)
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
    elif t == "essay":
        text = str(ans or "")
        words = len(text.split())
        low = _norm(text)
        pts = q.get("points") or []
        hit = sum(1 for p in pts if any(_norm(k) and _norm(k) in low for k in (p.get("keywords") or [])))
        kw_cov = hit / max(1, len(pts))
        struct = sum(1 for w in ("because", "therefore", "example", "first", "second", "however", "kwa sababu", "kwa hivyo", "mfano") if w in low) / 5.0
        length = min(1.0, words / 120.0)
        prov = round(marks * (0.45 * kw_cov + 0.30 * struct + 0.25 * length), 2)
        awarded, status, conf = prov, "review", 0.55
        fb = ("Provisional %s/%s from rubric (content %.0f%%, structure %.0f%%, development %.0f%%). Confirm with teacher judgement."
              % (prov, int(marks), kw_cov * 100, struct * 100, length * 100))
        if not words:
            awarded, status, fb = 0.0, "blank", "No response written."
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
            conf = 0.9 if hit_labels else 0.5
            if q.get("review"):
                fb += " (keyword match — confirm with teacher judgement)"
    else:
        status, fb, conf = "review", "Extended response — requires teacher judgement against the rubric.", 0.5
    return {"no": q.get("no"), "type": t, "marks": marks, "awarded": awarded, "status": status,
            "feedback": fb, "expected": q.get("answer"), "points": q.get("points") or [], "confidence": conf}
def _renumber_recompute(d):
    qs = d.get("questions") or []
    for i, q in enumerate(qs, 1):
        q["no"] = i
    d["total_marks"] = sum(q.get("marks") or 0 for q in qs)
    d["auto_markable"] = sum(q.get("marks") or 0 for q in qs if q.get("auto"))
    d["review_marks"] = sum(q.get("marks") or 0 for q in qs if not q.get("auto"))
    return d
def _apply_improve(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    if not d.get("misconceptions"):
        d["misconceptions"] = (["Wanafunzi huchanganya " + low + " na dhana za kila siku.",
                                "Hutumia kanuni hata pale isipotumika.",
                                "Hukosa vitengo au lebo katika majibu."] if lang == "sw" else
                               ["Learners confuse " + low + " with everyday intuitions.",
                                "The rule is over-generalised to cases where it does not hold.",
                                "Units or labels are omitted in responses."])
    if not d.get("bloom"):
        d["bloom"] = (["Kumbuka", "Elewa", "Tumia", "Chambua"] if lang == "sw" else
                      ["Remember", "Understand", "Apply", "Analyse"])
    for q in (d.get("questions") or []):
        if not q.get("explain"):
            q["explain"] = ("Award credit per marking point; accept equivalent correct phrasing." if lang == "en"
                            else "Toa alama kwa kila kipengele; kubali majibu sawia sahihi.")
    d["improved"] = True
    return d
def _apply_expand(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    kw = (_facts(low) or {}).get("kw") or [low]
    kind = d.get("kind")
    if kind == "quiz":
        specs = [("structured", 4), ("essay", 6), ("short", 2), ("match", 4)]
        extra = []
        for ty, mk in specs:
            if ty == "match":
                pairs = (_facts(low) or {}).get("pairs")
                if not pairs:
                    continue
                extra.append({"type": "match", "stem": ("Match each term to its meaning." if lang == "en" else "Oanisha kila istilahi na maana yake."),
                              "pairs": [{"term": p[0], "meaning": p[1]} for p in pairs], "meanings": [p[1] for p in pairs],
                              "marks": len(pairs), "answer": "; ".join(p[0] + " = " + p[1] for p in pairs),
                              "explain": "", "points": [], "auto": True})
                continue
            extra.append({"type": ty,
                          "stem": (("Discuss " if lang == "en" else "Jadili ") + low + (" giving examples." if lang == "en" else " ukitoa mifano.")) if ty == "essay"
                          else (("Explain how " if lang == "en" else "Eleza jinsi ") + low + (" works in detail." if lang == "en" else " inavyofanya kazi kwa kina.")),
                          "marks": mk,
                          "answer": ("Teacher judgement against rubric." if ty == "essay" else "A detailed correct explanation covering: " + ", ".join(kw[:4])),
                          "explain": "", "points": _points(kw, mk, lang), "auto": ty != "essay", "review": ty == "essay"})
        d["questions"] = (d.get("questions") or []) + extra
        _renumber_recompute(d)
    elif kind == "lesson_plan":
        d["flow"] = (d.get("flow") or []) + [{"step": ("Extension / Homework" if lang == "en" else "Upanuzi / Kazi ya nyumbani"),
                                              "duration": "10 min",
                                              "content": ("Investigate one real-world case of " + low + " and present findings next lesson." if lang == "en" else "Chunguza kesi moja halisi ya " + low + " na uwasilishe somo lijalo.")}]
        d["homework"] = ("Write a one-page summary of " + low + " including a labelled diagram and two exam-style questions." if lang == "en"
                         else "Andika muhtasari wa ukurasa mmoja wa " + low + " pamoja na mchoro wenye lebo na maswali mawili ya mtihani.")
    elif kind == "worksheet":
        n0 = len(d.get("tasks") or [])
        d["tasks"] = (d.get("tasks") or []) + [
            {"no": n0 + 1, "type": "apply", "prompt": ("List two ways " + low + " matters in your community." if lang == "en" else "Orodhesha njia mbili " + low + " inavyoleta faida jamii."), "lines": 3,
             "answer": "Any two valid, explained ways."},
            {"no": n0 + 2, "type": "challenge", "prompt": ("Design a simple investigation for " + low + "." if lang == "en" else "Buni uchunguzi rahisi wa " + low + "."), "lines": 4,
             "answer": "A workable method with variables identified."}]
    elif kind == "activity":
        d["steps"] = (d.get("steps") or []) + [{"step": ("Extension" if lang == "en" else "Upanuzi"), "duration": "10 min",
                                                "content": ("Groups design a follow-up investigation on " + low + "." if lang == "en" else "Vikundi vibuni uchunguzi wa ufuatiliaji kuhusu " + low + ".")}]
    elif kind == "marking_guide":
        d["rubric"] = (d.get("rubric") or []) + [{"name": ("Use of evidence / data" if lang == "en" else "Matumizi ya ushahidi / data"), "max": 2,
                                                  "descriptors": (["Strong, relevant evidence.", "Adequate evidence.", "Limited evidence.", "No evidence."] if lang == "en" else ["Ushahidi imara.", "Ushahidi wa kutosha.", "Ushahidi mdogo.", "Hakuna ushahidi."])}]
        d["total_marks"] = sum(r.get("max") or 0 for r in d["rubric"])
    d["expanded"] = True
    return d
def _apply_simplify(d):
    lang = d.get("language", "en")
    low = (d.get("topic") or "the topic").lower()
    parts = (_facts(low) or {}).get("parts") or [low, "process", "structure", "function"]
    kind = d.get("kind")
    if kind == "quiz":
        keep = [q for q in (d.get("questions") or []) if q.get("type") in ("mcq", "tf", "fill", "short")]
        keep = keep[:max(4, (len(keep) + 1) // 2)] or (d.get("questions") or [])[:4]
        for q in keep:
            q["marks"] = min(q.get("marks") or 1, 2)
            q["hint"] = ("Hint: recall the key term for " + low + "." if lang == "en" else "Dokezo: kumbuka istilahi muhimu ya " + low + ".")
        d["questions"] = keep
        d["word_bank"] = parts
        _renumber_recompute(d)
    elif kind == "lesson_plan":
        d["outcomes"] = [o.replace("Explain", "Describe").replace("Analyse", "Name").replace("Evaluate", "Match")
                         .replace("Eleza", "Eleza kwa ufupi").replace("Chambua", "Taja") for o in (d.get("outcomes") or [])]
        d["word_bank"] = parts
    elif kind == "worksheet":
        for t in (d.get("tasks") or []):
            t["lines"] = max(2, (t.get("lines") or 3) - 1)
        d["word_bank"] = parts
    d["simplified"] = True
    return d


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
        lang = lesson.get("language", "en")
        answers = data.get("answers") or {}
        results = [grade_question(q, answers.get(str(q.get("no")), answers.get(q.get("no"))), lang) for q in questions]
        total = sum(r["marks"] for r in results)
        awarded = round(sum(r["awarded"] for r in results), 2)
        pending = [r["no"] for r in results if r["status"] == "review"]
        pct = round(100.0 * awarded / total, 1) if total else 0.0
        by_type = {}
        for r in results:
            e = by_type.setdefault(r["type"], {"marks": 0.0, "awarded": 0.0})
            e["marks"] += r["marks"]; e["awarded"] += r["awarded"]
        report = {
            "total_marks": total, "awarded": awarded, "percentage": pct, "band": _grade_band(pct),
            "pending": pending, "results": results, "advice": _advice(pct, pending, lang),
            "by_type": {k: {"marks": v["marks"], "awarded": round(v["awarded"], 2),
                            "pct": round(100.0 * v["awarded"] / v["marks"], 1) if v["marks"] else 0.0} for k, v in by_type.items()},
            "topic": art.topic, "grade_level": lesson.get("grade_level", ""), "curriculum": lesson.get("curriculum", ""),
        }
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="QUIZ_AUTO_MARKED",
                                      resource_type="TeachingArtifact", resource_id=str(art.id),
                                      metadata={"awarded": awarded, "total": total, "percent": pct,
                                                "band": report["band"], "pending": pending, "topic": art.topic})
        except Exception:
            pass
        return Response(report)
    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response([])
        from apps.audit.models import AuditEvent
        rows = []
        for e in AuditEvent.objects.filter(institution=m.institution, action="QUIZ_AUTO_MARKED").order_by("-id")[:12]:
            meta = e.metadata or {}
            art = TeachingArtifact.objects.filter(id=e.resource_id).first()
            rows.append({
                "date": e.created_at.strftime("%d %b %Y, %H:%M") if e.created_at else "",
                "topic": meta.get("topic") or (art.topic if art else ""),
                "awarded": meta.get("awarded", 0), "total": meta.get("total", 0),
                "percent": meta.get("percent", 0), "band": meta.get("band", ""),
            })
        return Response(rows)

    @action(detail=False, methods=["post"], url_path="transform")
    def transform(self, request):
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
            return Response({"detail": "Artifact content is not transformable."}, status=400)
        act = data.get("action")
        params = dict(lesson.get("_params") or {})
        params.setdefault("artifact_type", art.artifact_type)
        params.setdefault("topic", art.topic)
        if act == "save":
            from apps.resources.models import LearningResource, DocumentChunk
            lr_fields = {f.name for f in LearningResource._meta.fields}
            kwargs = {"institution": m.institution, "title": (lesson.get("title") or art.topic) + " (AI-generated)",
                      "status": "ready", "uploaded_by": request.user}
            for f, v in (("subject", lesson.get("subject")), ("grade_level", lesson.get("grade_level")),
                         ("curriculum", lesson.get("curriculum")), ("topic", lesson.get("topic")),
                         ("provenance_tier", "A"), ("license", "Original - AI-generated, school-owned"),
                         ("source_url", ""), ("attribution", "JIFUNZE AI Teacher Studio")):
                if f in lr_fields:
                    kwargs[f] = v or ""
            res, _ = LearningResource.objects.update_or_create(
                institution=m.institution, title=kwargs["title"],
                defaults={k: v for k, v in kwargs.items() if k not in ("institution", "title")})
            dc_fields = {f.name for f in DocumentChunk._meta.fields}
            DocumentChunk.objects.filter(resource=res).delete()
            blobs = [lesson.get("title", "")] + list(lesson.get("outcomes") or []) + \
                    [s.get("content", "") for s in (lesson.get("flow") or [])] + \
                    [q.get("stem", "") for q in (lesson.get("questions") or [])] + \
                    [lesson.get("assessment", ""), lesson.get("resources", ""), lesson.get("teacher_notes", "")]
            text = " ".join(x for x in blobs if x)
            for i in range(0, len(text), 900):
                ck = {"resource": res, "chunk_index": i // 900, "chunk_text": text[i:i + 900]}
                DocumentChunk.objects.create(**{k: v for k, v in ck.items() if k in dc_fields or k == "resource"})
            try:
                from apps.audit.models import AuditEvent
                AuditEvent.objects.create(institution=m.institution, actor=request.user, action="ARTIFACT_SAVED_TO_LIBRARY",
                                          resource_type="LearningResource", resource_id=str(res.id),
                                          metadata={"from_artifact": str(art.id)})
            except Exception:
                pass
            return Response({"saved": True, "resource_id": str(res.id), "title": kwargs["title"]})
        if act == "regenerate":
            params["variation"] = (params.get("variation") or 0) + 1
            new = BUILDERS.get(params.get("artifact_type"), build_lesson)(params)
        elif act == "translate":
            params["language"] = "sw" if (lesson.get("language") == "en") else "en"
            new = BUILDERS.get(params.get("artifact_type"), build_lesson)(params)
        elif act == "improve":
            new = _apply_improve(json.loads(json.dumps(lesson)))
        elif act == "expand":
            new = _apply_expand(json.loads(json.dumps(lesson)))
        elif act == "simplify":
            new = _apply_simplify(json.loads(json.dumps(lesson)))
        else:
            return Response({"detail": "Unknown action."}, status=400)
        new["_params"] = params
        content = json.dumps(new, indent=2)
        kwargs = dict(institution=m.institution, created_by=request.user,
                      artifact_type=params.get("artifact_type", art.artifact_type),
                      topic=params.get("topic", art.topic), content=content)
        existing = {f.name for f in TeachingArtifact._meta.fields}
        for f in ("grade_level", "curriculum", "subtopic", "week", "term", "subject"):
            if f in existing:
                kwargs[f] = (params.get(f) or "")
        newart = TeachingArtifact.objects.create(**kwargs)
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="ARTIFACT_TRANSFORMED",
                                      resource_type="TeachingArtifact", resource_id=str(newart.id),
                                      metadata={"action": act, "from": str(art.id)})
        except Exception:
            pass
        return Response({"id": str(newart.id), "content": content, "action": act})

    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        rows = []
        for a in self.get_queryset().order_by("-created_at")[:20]:
            try:
                lesson = json.loads(a.content)
            except Exception:
                lesson = {}
            rows.append({
                "id": str(a.id), "artifact_type": a.artifact_type, "topic": a.topic,
                "title": lesson.get("title") or a.topic, "grade_level": lesson.get("grade_level", ""),
                "curriculum": lesson.get("curriculum", ""), "language": lesson.get("language", "en"),
                "created_at": a.created_at.strftime("%d %b, %H:%M") if a.created_at else "",
                "content": a.content,
            })
        return Response(rows)
    @action(detail=False, methods=["post"], url_path="notes")
    def notes(self, request):
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
            return Response({"detail": "Artifact content is not editable."}, status=400)
        lesson["teacher_notes"] = str(data.get("notes") or "")
        art.content = json.dumps(lesson, indent=2)
        art.save(update_fields=["content"])
        try:
            from apps.audit.models import AuditEvent
            AuditEvent.objects.create(institution=m.institution, actor=request.user, action="TEACHER_NOTES_EDITED",
                                      resource_type="TeachingArtifact", resource_id=str(art.id), metadata={})
        except Exception:
            pass
        return Response({"saved": True})

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        from datetime import timedelta
        from django.utils import timezone
        m = Membership.objects.filter(user=request.user, is_active=True).first()
        if not m:
            return Response({"total": 0, "by_type": {}, "by_curr": [], "by_lang": {}, "days": [],
                             "marks_count": 0, "avg_percent": None, "pending_review": 0,
                             "transforms": {}, "saved": 0, "top_topics": [], "by_grade": {}})
        qs = TeachingArtifact.objects.filter(institution=m.institution)
        total = qs.count()
        by_type, by_curr, by_grade, by_lang, topics = {}, {}, {}, {}, {}
        for a in qs.order_by("-created_at")[:300]:
            by_type[a.artifact_type] = by_type.get(a.artifact_type, 0) + 1
            if a.curriculum:
                by_curr[a.curriculum] = by_curr.get(a.curriculum, 0) + 1
            if a.grade_level:
                by_grade[a.grade_level] = by_grade.get(a.grade_level, 0) + 1
            topics[a.topic] = topics.get(a.topic, 0) + 1
            try:
                lesson = json.loads(a.content)
                lg = lesson.get("language", "en")
                by_lang[lg] = by_lang.get(lg, 0) + 1
            except Exception:
                pass
        now = timezone.localtime()
        days = []
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).date()
            days.append({"date": d.strftime("%a"), "count": qs.filter(created_at__date=d).count()})
        from apps.audit.models import AuditEvent
        marks = AuditEvent.objects.filter(institution=m.institution, action="QUIZ_AUTO_MARKED")
        pcts = [(e.metadata or {}).get("percent") for e in marks]
        pcts = [p for p in pcts if isinstance(p, (int, float))]
        avg = round(sum(pcts) / len(pcts), 1) if pcts else None
        pending = sum(len((e.metadata or {}).get("pending") or []) for e in marks)
        transforms = {}
        for e in AuditEvent.objects.filter(institution=m.institution, action="ARTIFACT_TRANSFORMED"):
            k = (e.metadata or {}).get("action") or "other"
            transforms[k] = transforms.get(k, 0) + 1
        saved = AuditEvent.objects.filter(institution=m.institution, action="ARTIFACT_SAVED_TO_LIBRARY").count()
        return Response({
            "total": total,
            "by_type": by_type,
            "by_curr": sorted(by_curr.items(), key=lambda kv: -kv[1])[:4],
            "by_grade": by_grade,
            "by_lang": by_lang,
            "days": days,
            "marks_count": len(pcts),
            "avg_percent": avg,
            "pending_review": pending,
            "transforms": transforms,
            "saved": saved,
            "top_topics": sorted(topics.items(), key=lambda kv: -kv[1])[:5],
        })
