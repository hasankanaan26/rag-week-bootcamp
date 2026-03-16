# ============================================================
# Retriever — embed a query, search the store, score confidence
# ============================================================
# Session 7: Added query rewriting and metadata filtering.
#
# Query rewriting asks the LLM to rephrase vague questions
# with synonyms and specific terms, improving retrieval quality.
#
# Metadata filtering lets you restrict search to specific
# source documents, useful for targeted Q&A.
# ============================================================

import logging
from app.rag.embedder import embed_text
from app.rag.store import search, count
from app.llm import call_llm
from app.prompts.rewrite_query import REWRITE_PROMPT
from app.config import (
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_LOW_THRESHOLD,
    NO_RESULT_DISTANCE,
)

logger = logging.getLogger("rag.retriever")


def rewrite_query(question: str) -> str:
    """
    Use the LLM to rewrite a vague question into a more specific
    search query with synonyms and formal terms.
    """
    prompt = REWRITE_PROMPT.format(question=question)
    rewritten = call_llm(user_prompt=prompt)
    return rewritten.strip()


def retrieve(
    query: str,
    top_k: int = 3,
    rewrite: bool = False,
    where: dict | None = None,
) -> tuple[list[dict], str | None]:
    """
    Find the most relevant chunks for a question.

    Args:
        query: The user question.
        top_k: Number of chunks to retrieve.
        rewrite: If True, rewrite the query before embedding.
        where: Optional metadata filter (e.g. {"source": "leave-policy.md"}).

    Returns:
        Tuple of (chunks, rewritten_query or None).
    """
    stored = count()
    if stored == 0:
        return [], None

    rewritten = None
    search_query = query
    if rewrite:
        rewritten = rewrite_query(query)
        search_query = rewritten
        logger.info("Query rewritten | original=%r → rewritten=%r", query, rewritten)

    query_embedding = embed_text(search_query)
    results = search(query_embedding, top_k=top_k, where=where)

    return results, rewritten


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
