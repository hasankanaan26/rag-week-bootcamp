# ============================================================
# Router: /search — Test retrieval in isolation
# ============================================================
# This endpoint lets you search the vector store WITHOUT
# calling the LLM. It's a debugging and teaching tool.
#
# DEMO QUESTIONS TO TRY:
#   "How many vacation days do I get?"     -> should find leave-policy.md
#   "What is our Git branching strategy?"  -> should find coding-standards.md
#   "Can I work from home?"               -> should find remote-work.md
#   "quantum physics"                      -> high distances (irrelevant)
#
# Pay attention to the DISTANCE scores:
#   Low distance (< 0.5)  = strongly relevant
#   High distance (> 1.0) = probably irrelevant
# ============================================================

from fastapi import APIRouter, Query
from app.models import SearchResponse, SearchResult
from app.rag.embedder import embed_text
from app.rag.store import search, count

router = APIRouter(prefix="/search", tags=["Search"])


# Purpose:
# Embeds a query and searches ChromaDB for similar chunks.
# Returns results with distance scores — no LLM involved.
@router.get("", response_model=SearchResponse)
def search_chunks(
    q: str = Query(description="The search query text."),
    top_k: int = Query(default=3, description="Number of results to return."),
):
    """
    Search the vector store for chunks matching a query.

    This is retrieval WITHOUT generation — just finding relevant chunks.
    """
    stored = count()
    if stored == 0:
        return SearchResponse(query=q, results=[], total_results=0)

    query_embedding = embed_text(q)
    raw_results = search(query_embedding, top_k=top_k)

    results = [
        SearchResult(
            text=r["text"],
            source=r["source"],
            chunk_index=r["chunk_index"],
            distance=r["distance"],
        )
        for r in raw_results
    ]

    return SearchResponse(query=q, results=results, total_results=len(results))
