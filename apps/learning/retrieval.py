from apps.resources.models import DocumentChunk
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)
def retrieve_context(query: str, institution_id: str, top_k: int = 5) -> list:
    """
    Hybrid retrieval: combines exact keyword match (BM25-like via Django __icontains) 
    with semantic similarity (if embeddings exist). 
    For MVP, we prioritize keyword matches and fall back to recent chunks.
    """
    # 1. Keyword search (fast, reliable for exact terms like "photosynthesis")
    keyword_matches = DocumentChunk.objects.filter(
        resource__institution_id=institution_id,
        chunk_text__icontains=query
    ).order_by("-chunk_index")[:top_k]
    if keyword_matches.exists():
        logger.info(f"Found {keyword_matches.count()} keyword matches for '{query}'")
        return list(keyword_matches)
    # 2. Fallback: If no exact keyword match, return the most recent chunks from the institution
    # (In Phase 2, this will be replaced by cosine similarity on the 'embedding' field)
    fallback_matches = DocumentChunk.objects.filter(
        resource__institution_id=institution_id
    ).order_by("-resource__created_at", "chunk_index")[:top_k]
    logger.info(f"Keyword search yielded 0 results. Falling back to {fallback_matches.count()} recent chunks.")
    return list(fallback_matches)
