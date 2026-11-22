BLOCKED_TOPICS = (
    "weapon", "bomb", "exploit", "malware", "self-harm", "suicide method",
    "illegal drug synthesis", "child personal data", "bypass security",
)
def screen_prompt(text):
    """Return (allowed, reason). Blocks unsafe or privacy-violating requests."""
    low = (text or "").lower()
    for topic in BLOCKED_TOPICS:
        if topic in low:
            return False, "This request is outside the educational safety policy of JIFUNZE AI."
    return True, ""
def learning_guardrail():
    return ("You are a school tutor. If the provided sources do not support an answer, say so "
            "clearly instead of guessing. Never request or reveal personal data about children.")
