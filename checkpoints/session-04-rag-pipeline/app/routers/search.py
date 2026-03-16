# ============================================================
# Router: /search — Test retrieval in isolation
# ============================================================
# This endpoint lets you search the vector store WITHOUT
# calling the LLM. It's a debugging and teaching tool.
#
# The flow:
#   Query text → Embed → Search ChromaDB → Return matches
#
# DEMO QUESTIONS TO TRY:
#   "How many vacation days do I get?"     → should find leave-policy.md
#   "What is our Git branching strategy?"  → should find coding-standards.md
#   "Can I work from home?"               → should find remote-work.md
#   "quantum physics"                      → high distances (irrelevant)
#
# INTENTIONALLY WEAK QUERY:
#   "Tell me about the rules"             → vague, matches many docs poorly
#   Look at the distances — all high, none clearly relevant.
#   This shows why threshold-based filtering matters (Session 6).
#
# Pay attention to the DISTANCE scores:
#   Low distance (< 0.5)  = strongly relevant
#   High distance (> 1.0) = probably irrelevant
#   (Exact thresholds depend on the embedding model)
# ============================================================

from fastapi import APIRouter, Query
from app.models import SearchResponse, SearchResult
from app.rag.embedder import embed_text
from app.rag.store import search, count

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
def search_chunks(
    q: str = Query(description="The search query text."),
    top_k: int = Query(
        default=3,
        description="Number of results to return.",
    ),
):
    """
    Search the vector store for chunks matching a query.

    This is retrieval WITHOUT generation — just finding relevant chunks.
    Useful for debugging: see what the RAG system would retrieve
    before sending it to the LLM.
    """
    stored = count()
    if stored == 0:
        return SearchResponse(query=q, results=[], total_results=0)

    # Embed the query into a vector
    query_embedding = embed_text(q)

    # Search ChromaDB for similar chunks
    raw_results = search(query_embedding, top_k=top_k)

    # Convert to response model
    results = [
        SearchResult(
            text=r["text"],
            source=r["source"],
            chunk_index=r["chunk_index"],
            distance=r["distance"],
        )
        for r in raw_results
    ]

    return SearchResponse(
        query=q,
        results=results,
        total_results=len(results),
    )
