import hashlib
import math
import re
DIM = 64
def _tokens(text):
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", (text or "").lower()).split() if len(w) > 2]
def encode(text, dim=DIM):
    """Deterministic hashed bag-of-words vector. Swap for sentence-transformers / pgvector in production."""
    v = [0.0] * dim
    for tok in _tokens(text):
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        v[h % dim] += 1.0 + ((h >> 8) % 7) / 7.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [round(x / norm, 5) for x in v]
def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))
def pgvector_available():
    from django.db import connection
    if connection.vendor != "postgresql":
        return False
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1 FROM pg_extension WHERE extname='vector'")
            return c.fetchone() is not None
    except Exception:
        return False
def semantic_search(institution, query, k=8):
    from apps.resources.models import DocumentChunk
    qv = encode(query)
    rows = []
    qs = DocumentChunk.objects.filter(resource__institution=institution).select_related("resource")
    for c in qs[:500]:
        emb = c.embedding if isinstance(c.embedding, list) else None
        if not emb:
            continue
        rows.append((cosine(qv, emb), c))
    rows.sort(key=lambda x: -x[0])
    out = []
    for score, c in rows[:k]:
        out.append({"score": round(score, 3), "title": c.resource.title,
                    "subject": getattr(c.resource, "subject", ""), "grade": getattr(c.resource, "grade_level", ""),
                    "chunk": (c.chunk_text or "")[:300]})
    return out
