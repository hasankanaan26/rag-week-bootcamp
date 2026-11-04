# ============================================================
# Retriever — with confidence scoring and no-result detection
# ============================================================
# Updated from Checkpoint 3 to add:
#   - score_confidence(): classify retrieval quality
#   - is_no_result(): detect when nothing relevant was found
#   - retrieve_with_doc_filter(): LLM picks a doc type, search only
#     that doc type, fall back to all documents if nothing good comes back
#
# TEACHING POINT:
#   The retriever retrieves. These helper functions let the
#   endpoint decide what to do with the results — show them,
#   warn the user, or say "I don't know."
# ============================================================

from app.rag.classifier import classify_question
from app.rag.embedder import embed_text
from app.rag.store import search, count
from app.config import (
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_LOW_THRESHOLD,
    NO_RESULT_DISTANCE,
)


# Purpose:
# Takes a plain-text question, embeds it, and searches the vector store
# for the most relevant chunks.
def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Find the most relevant chunks for a question.

    Returns chunks with: text, source, chunk_index, distance.
    Empty list if the store has no chunks.
    """
    stored = count()
    if stored == 0:
        return []

    query_embedding = embed_text(query)
    results = search(query_embedding, top_k=top_k)

    return results


# Purpose:
# Decides which doc type to filter on.
#   "auto" -> ask the LLM
#   "off"  -> no filter
#   any doc type label -> use it as given (handy for testing the fallback)
# Returns doc_type (or None), picked_by ("llm", "manual" or None),
# and the classifier's raw reply (only in "auto" mode).
def choose_doc_type(query: str, filter_mode: str) -> dict:
    """Resolve the filter mode into a doc type to search."""
    if filter_mode == "off":
        return {"doc_type": None, "picked_by": None, "raw_reply": None}
    if filter_mode == "auto":
        classified = classify_question(query)
        return {"doc_type": classified["doc_type"], "picked_by": "llm", "raw_reply": classified["raw_reply"]}
    return {"doc_type": filter_mode, "picked_by": "manual", "raw_reply": None}


# Purpose:
# Metadata-filtered retrieval with a safety net. Searches only the chosen
# doc type first. If that finds nothing useful (is_no_result), searches
# again across all documents so a wrong classification can't hide the answer.
def retrieve_with_doc_filter(
    query: str,
    top_k: int = 3,
    filter_mode: str = "auto",
    no_result_threshold: float | None = None,
) -> dict:
    """
    Retrieve chunks, filtered by doc type when one is chosen.

    Returns a dict with:
      chunks                 - the chunks to answer from
      doc_type               - the doc type that was tried, or None
      picked_by              - "llm", "manual" or None
      classifier_reply       - what the LLM replied (auto mode only)
      fallback_used          - True if the filtered search was too weak
                               and we searched everything instead
      filtered_best_distance - best distance inside the doc type, or None
    """
    result = {
        "chunks": [],
        "doc_type": None,
        "picked_by": None,
        "classifier_reply": None,
        "fallback_used": False,
        "filtered_best_distance": None,
    }
    if count() == 0:
        return result

    choice = choose_doc_type(query, filter_mode)
    doc_type = choice["doc_type"]
    result["doc_type"] = doc_type
    result["picked_by"] = choice["picked_by"]
    result["classifier_reply"] = choice["raw_reply"]

    # Embed once, reuse the vector for both searches
    query_embedding = embed_text(query)

    if doc_type is None:
        result["chunks"] = search(query_embedding, top_k=top_k)
        return result

    filtered = search(query_embedding, top_k=top_k, doc_type=doc_type)
    if filtered:
        result["filtered_best_distance"] = min(c["distance"] for c in filtered)

    if is_no_result(filtered, no_result_threshold=no_result_threshold):
        result["chunks"] = search(query_embedding, top_k=top_k)
        result["fallback_used"] = True
    else:
        result["chunks"] = filtered

    return result


# Purpose:
# Classifies retrieval confidence based on the best (lowest) distance score.
# Returns "high", "medium", "low", or "none".
def score_confidence(
    chunks: list[dict],
    high_threshold: float | None = None,
    low_threshold: float | None = None,
) -> str:
    """
    Score the overall confidence of retrieval results.

    Looks at the BEST (lowest) distance among retrieved chunks.
    Accepts optional threshold overrides for live experimentation.
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


# Purpose:
# Determines if retrieval found nothing useful. True when there are no chunks
# or when even the best chunk is too far away (distance exceeds threshold).
def is_no_result(
    chunks: list[dict],
    no_result_threshold: float | None = None,
) -> bool:
    """
    Determine if retrieval found nothing useful.

    This is how the system decides to say "I don't know"
    instead of giving a bad answer.
    """
    if not chunks:
        return True

    threshold = no_result_threshold if no_result_threshold is not None else NO_RESULT_DISTANCE
    best_distance = min(c["distance"] for c in chunks)
    return best_distance > threshold
