from pathlib import Path
base = Path(r"C:\Users\ESTHER M\Documents\jifunze_ai")
# ---------- 1. Rewrite the mock provider to answer DIRECTLY (not dump passages) ----------
mp = base / "apps/ai_gateway/providers/mock_provider.py"
mp.write_text('''from .base import BaseProvider
import json
import re as _re
KNOWLEDGE = [
    (("photosynthesis",), "Photosynthesis is how green plants turn light energy into chemical energy (glucose). It happens in chloroplasts, where chlorophyll absorbs mainly red and blue light. The overall equation is 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂. The process has two stages: the light-dependent reactions split water and produce ATP and NADPH, then the Calvin cycle uses those to fix CO₂ into glucose."),
    (("brownian",), "Brownian motion is the random, jittery movement of tiny suspended particles caused by collisions with the molecules of the surrounding fluid. You see it when, for example, smoke particles under a microscope wiggle unpredictably — that wiggle is evidence that the fluid molecules themselves are moving, which helped prove the existence of atoms."),
    (("activation energy",), "Activation energy is the minimum energy that reacting particles must have for a reaction to start. Think of it as the hill a reaction must climb before it can roll down. Catalysts work by lowering that hill, so more particles have enough energy and the reaction speeds up."),
    (("atom",), "An atom is the smallest unit of an element that keeps its chemical properties. It has a dense nucleus of protons (positive) and neutrons (neutral), with negatively charged electrons orbiting in shells. The number of protons (the atomic number) defines the element."),
    (("molecule",), "A molecule is two or more atoms chemically bonded together, like H₂O or O₂. Bonds can be covalent (sharing electrons) or ionic (transferring electrons)."),
    (("cell",), "The cell is the basic unit of life. Plant cells have a cell wall, chloroplasts and a large permanent vacuole; animal cells do not. Both have a nucleus, cytoplasm and cell membrane."),
    (("force", "newton"), "A force is a push or pull that can change an object's motion or shape. Its unit is the newton (N). Newton's second law gives F = ma."),
    (("fraction",), "A fraction is a part of a whole: numerator over denominator. To add fractions, first find a common denominator; equivalent fractions (like 1/2 and 2/4) have equal value."),
    (("first world war", "ww1", "wwi"), "The First World War (1914–1918) was triggered by the assassination of Archduke Franz Ferdinand of Austria-Hungary in Sarajevo. Deeper causes included militarism, the alliance system (Triple Entente vs Triple Alliance), imperialism and nationalism. It ended with the Treaty of Versailles in 1919."),
    (("kenya", "independence"), "Kenya gained independence from Britain on 12 December 1963 after the Mau Mau uprising and years of political struggle led by Jomo Kenyatta and others."),
    (("equation", "algebra"), "An equation states that two expressions are equal. To solve, isolate the unknown by applying inverse operations to both sides until the variable stands alone."),
]
def _level_band(grade):
    g = (grade or "").lower()
    if any(k in g for k in ("pp1", "pp2", "kg", "grade r", "pre")):
        return "early"
    m = _re.search(r"\\d+", g)
    n = int(m.group()) if m else 0
    if "form" in g or _re.match(r"^s\\d", g):
        return "junior" if n <= 2 else "senior"
    if "jss" in g or "myp" in g:
        return "junior"
    if "sss" in g or "shs" in g or "dp" in g or "year" in g:
        return "senior"
    if "stage" in g:
        return "primary" if n <= 6 else "junior"
    if "standard" in g or "primary" in g:
        return "primary"
    if "basic" in g:
        return "primary" if n <= 6 else "junior"
    if "grade" in g:
        return "primary" if n <= 6 else ("junior" if n <= 9 else "senior")
    return "junior"
LEVEL_STYLE = {
    "early": {
        "en": {"tone": "Let's explore this together!",
               "close": "Can you draw a picture of what we just talked about?",
               "len": 3},
        "sw": {"tone": "Tuchunguze hili pamoja!",
               "close": "Je, unaweza kuchora picha ya tulichozungumza?",
               "len": 3},
    },
    "primary": {
        "en": {"tone": "Here's a clear way to think about it.",
               "close": "Want a quick practice question to check you've got it?",
               "len": 4},
        "sw": {"tone": "Hii hapa ni njia wazi ya kufikiria.",
               "close": "Ungependa swali fupi la mazoezi?",
               "len": 4},
    },
    "junior": {
        "en": {"tone": "Let me break this down properly.",
               "close": "Want me to show a worked example or set a past-paper question?",
               "len": 5},
        "sw": {"tone": "Niruhusu nikufafanulie vizuri.",
               "close": "Ungependa mfano uliofanywa au swali la mtihani uliopita?",
               "len": 5},
    },
    "senior": {
        "en": {"tone": "Here's a precise, exam-ready explanation.",
               "close": "Want an exam-style question with a mark scheme, or a deeper extension?",
               "len": 6},
        "sw": {"tone": "Huu hapa ni ufafanuzi sahihi wa mtihani.",
               "close": "Ungependa swali la mtihani na rubriki, au mada ya upanuzi?",
               "len": 6},
    },
}
def _match(q):
    ql = q.lower()
    for keys, val in KNOWLEDGE:
        if any(k in ql for k in keys):
            return val
    return None
def _style_from_context(context, question):
    """Pull a couple of useful facts out of raw context without dumping it."""
    text = (context or "") + " " + (question or "")
    sents = [s.strip() for s in _re.split(r"[.!?]\\n?|\\n", text) if len(s.strip()) > 20]
    low = question.lower()
    ranked = sorted(sents, key=lambda s: -sum(1 for w in _re.findall(r"\\w+", low) if len(w) > 3 and w in s.lower()))
    return ranked[:2]
class MockProvider(BaseProvider):
    provider_name = "mock"
    def __init__(self):
        self.model = "mock-dev-mode"
    def generate(self, prompt, system_prompt=None, **kwargs):
        mode = kwargs.get("mode", "learner")
        cur = kwargs.get("curriculum", "CBC/CBE")
        grade = kwargs.get("grade_level", "")
        lang = kwargs.get("language", "en")
        atype = kwargs.get("artifact_type", "")
        subject = kwargs.get("subject", "General")
        if mode == "teacher":
            topic = kwargs.get("topic", "the topic")
            if atype == "lesson_plan":
                return json.dumps({
                    "title": topic.title(), "subject": "Science", "curriculum": cur,
                    "duration": "50 minutes",
                    "outcomes": ["Explain " + topic.lower() + " correctly.", "Apply it to real life.", "Show critical thinking."],
                    "flow": [
                        {"step": "Introduction", "duration": "5 min", "content": "Hook learners with a question about " + topic.lower() + "."},
                        {"step": "Main Activity", "duration": "25 min", "content": "Guided exploration using school resources."},
                        {"step": "Assessment", "duration": "10 min", "content": "Formative check against a " + cur + " rubric."},
                    ],
                    "resources": "Textbook, uploaded documents, whiteboard.",
                    "differentiation": "Support: sentence starters. Extension: case study.",
                    "assessment": "Define + label diagram; rubric on accuracy.",
                    "teacher_notes": "Check prior knowledge first.",
                }, indent=2)
            return "# " + topic.title() + "\\n\\nTeaching material for " + cur + "."
        # ---------- LEARNER MODE: direct, conversational, level-aware ----------
        text = prompt or ""
        if "Learner question:" in text:
            question = text.split("Learner question:")[-1].strip()
            raw_context = text.split("Learner question:")[0].split("Context")[0].strip()
        else:
            question = text.strip()
            raw_context = ""
        sw = (lang == "sw")
        band = _level_band(grade)
        style = LEVEL_STYLE.get(band, LEVEL_STYLE["junior"])
        st = style["sw"] if sw else style["en"]
        body = _match(question)
        if body is None:
            hints = _style_from_context(raw_context, question)
            if hints:
                body = hints[0] + (" " + hints[1] if len(hints) > 1 else "")
            else:
                q_clean = question.strip("? ").strip(".")
                body = (
                    "A good way to think about " + q_clean + " is to start with the definition, then identify the key parts, then connect it to a real-life example."
                    if not sw else
                    "Njia nzuri ya kufikiria " + q_clean + " ni kuanza na ufafanuzi, kisha kutambua sehemu muhimu, kisha kuiunganisha na mfano wa maisha halisi."
                )
        lines = [
            st["tone"],
            "",
            body,
        ]
        if subject and subject != "General":
            lines.append("")
            lines.append(
                ("(Somo: " + subject + " · " if sw else "(" + subject + " · ") + cur + " · " + str(grade or "—" ) + ")"
            )
        else:
            lines.append("")
            lines.append("(" + cur + " · " + str(grade or "—") + ")")
        lines.append("")
        lines.append(st["close"])
        return "\\n".join(lines)
''', encoding="utf-8")
# ---------- 2. Fallback in ask_views: compose an answer from context instead of dumping it ----------
av = base / "apps/learning/ask_views.py"
avs = av.read_text(encoding="utf-8")
OLD_FALLBACK = '''def _fallback_answer(chunks, web, grade, curriculum, subject, lang):
    """Direct RAG answer when the AI provider is unavailable."""
    sw = lang == "sw"
    head = ("Kutoka nyenzo za shule yako:" if sw else "From your school's approved materials:")
    if chunks:
        passage = (chunks[0].chunk_text or "")[:700]
        body = head + "\\n" + passage
    elif web:
        body = ("Kutoka vyanzo huria (" + web["engine"] + "):" if sw else "From open knowledge (" + web["engine"] + "):") + "\\n" + web["text"][:700]
    else:
        body = ("Sijapata nyenzo za kutosha. Jaribu:" if sw else "I could not find enough material. Try:") + "\\n1. " + \\
               ("Eleza istilahi kuu." if sw else "Define the key term.") + "\\n2. " + \\
               ("Toa mfano halisi." if sw else "Give a real-life example.") + "\\n3. " + \\
               ("Wasiliana na mwalimu." if sw else "Ask your teacher for the textbook section.")
    note = ("\\n\\nKiwango: " if sw else "\\n\\nLevel: ") + str(grade or "—") + " · " + str(curriculum or "") + \\
           (" · Somo: " if sw else " · Subject: ") + str(subject or "General") + "."
    return body + note'''
NEW_FALLBACK = '''def _fallback_answer(chunks, web, grade, curriculum, subject, lang):
    """Composes a direct tutor-style answer from retrieved context (never dumps passages)."""
    import re as _re
    sw = lang == "sw"
    tone = ("Hii hapa ni jibu moja kwa moja:" if sw else "Here's a direct answer:")
    body = ""
    if chunks:
        sents = [s.strip() for c in chunks for s in _re.split(r"[.!?]\\n?|\\n", c.chunk_text or "") if len(s.strip()) > 20]
        body = ". ".join(sents[:2]) + "." if sents else (chunks[0].chunk_text or "")[:300]
    elif web:
        sents = [s.strip() for s in _re.split(r"[.!?]\\n?|\\n", web["text"]) if len(s.strip()) > 20]
        body = ". ".join(sents[:2]) + "." if sents else web["text"][:300]
    else:
        body = ("Sitakuwa na nyenzo za kutosha kujibu moja kwa moja — tafadhali jaribu istilahi nyingine au uliza mwalimu wako."
                if sw else
                "I don't have enough material to answer directly — try a different term or ask your teacher.")
    sig = "(" + (curriculum or "") + " · " + str(grade or "—") + (" · " + subject if subject and subject != "General" else "") + ")"
    return tone + "\\n\\n" + body + "\\n\\n" + sig'''
if OLD_FALLBACK in avs:
    avs = avs.replace(OLD_FALLBACK, NEW_FALLBACK, 1)
    av.write_text(avs, encoding="utf-8")
    print("FALLBACK: now composes a direct answer")
else:
    print("WARNING: fallback block not found exactly")
print("MOCK PROVIDER: direct, conversational, level-aware answers installed")
