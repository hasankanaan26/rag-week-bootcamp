# ============================================================
# Retriever — embed a query, search the store, score confidence
# ============================================================
# The retriever ties embedding and search together:
#   retrieve(query) → embed → search → ranked chunks
#
# Also provides confidence helpers used by the query endpoint:
#   score_confidence(chunks) → "high" / "medium" / "low" / "none"
#   is_no_result(chunks)     → True if nothing useful was found
#
# TEACHING POINT:
#   The retriever retrieves; the endpoint decides what to do
#   with the results. Keeping this separation makes each piece
#   easy to test and reason about independently.
# ============================================================

from app.rag.embedder import embed_text
from app.rag.store import search, count
from app.config import (
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_LOW_THRESHOLD,
    NO_RESULT_DISTANCE,
)


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Find the most relevant chunks for a question.

    Returns chunks sorted by relevance (lowest distance first).
    Each chunk dict includes: text, source, chunk_index, distance.
    """
    stored = count()
    if stored == 0:
        return []

    query_embedding = embed_text(query)
    results = search(query_embedding, top_k=top_k)

    return results


def score_confidence(
    chunks: list[dict],
    high_threshold: float | None = None,
    low_threshold: float | None = None,
) -> str:
    """
    Score the overall confidence of retrieval results.

    Looks at the BEST (lowest) distance among retrieved chunks.
    Accepts optional threshold overrides for experimentation.

    Returns: "high", "medium", "low", or "none"
    """
    if not chunks:
        return "none"

    high = high_threshold if high_threshold is not None else CONFIDENCE_HIGH_THRESHOLD
    low = low_threshold if low_threshold is not None else CONFIDENCE_LOW_THRESHOLD
    best_distance = min(c["distance"] for c in chunks)

    if best_distance <= high:
        return "high"
    elif best_distance <= low:
        return "medium"
    else:
        return "low"


def is_no_result(
    chunks: list[dict],
    no_result_threshold: float | None = None,
) -> bool:
    """
    Determine if retrieval found nothing useful.

    Accepts an optional threshold override for experimentation.
    """
    if not chunks:
        return True

    threshold = no_result_threshold if no_result_threshold is not None else NO_RESULT_DISTANCE
    best_distance = min(c["distance"] for c in chunks)
    return best_distance > threshold
