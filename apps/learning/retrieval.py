from apps.resources.models import DocumentChunk
import logging
logger = logging.getLogger(__name__)
def retrieve_context(query: str, institution_id, top_k: int = 5) -> list:
    """Hybrid retrieval: exact keyword match first, recent-materials fallback."""
    keyword_matches = list(
        DocumentChunk.objects.filter(
            resource__institution_id=institution_id,
            chunk_text__icontains=query,
        ).order_by("-resource__created_at", "chunk_index")[:top_k]
    )
    if keyword_matches:
        logger.info("Found %d keyword matches for '%s'", len(keyword_matches), query[:40])
        return keyword_matches
    fallback = list(
        DocumentChunk.objects.filter(resource__institution_id=institution_id)
        .order_by("-resource__created_at", "chunk_index")[:top_k]
    )
    logger.info("No keyword match; using %d recent chunks as context", len(fallback))
    return fallback
