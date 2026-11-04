# ============================================================
# Router: /store/inspect — See what's inside the vector store
# ============================================================
# This endpoint makes the "invisible" visible. Students can
# see exactly what ChromaDB is holding.
#
# DEMO:
#   GET /store/inspect                       -> all chunks
#   GET /store/inspect?source=leave-policy.md -> filter by file
#   GET /store/inspect?show_embeddings=true  -> include vectors
# ============================================================

from fastapi import APIRouter, Query
from app.models import StoreInspectResponse, StoredChunkInfo
from app.rag.store import get_all_chunks

router = APIRouter(prefix="/store", tags=["Store Inspector"])


# Purpose:
# Returns the contents of the vector store for inspection.
# Shows chunk text, metadata, and optionally embedding previews.
@router.get("/inspect", response_model=StoreInspectResponse)
def inspect_store(
    source: str | None = Query(
        default=None,
        description="Filter by source filename, e.g. 'leave-policy.md'.",
    ),
    show_embeddings: bool = Query(
        default=False,
        description="Include embedding vectors (first 5 dimensions).",
    ),
    limit: int = Query(default=50, description="Max chunks to return.", le=500),
):
    """Inspect the contents of the vector store."""
    raw = get_all_chunks(source=source, limit=limit, include_embeddings=show_embeddings)

    chunks = []
    for item in raw:
        chunk = StoredChunkInfo(
            id=item["id"],
            text=item["text"],
            source=item["source"],
            chunk_index=item["chunk_index"],
            embedding_preview=item.get("embedding_preview"),
            embedding_dimensions=item.get("embedding_dimensions"),
        )
        chunks.append(chunk)

    sources = sorted(set(c.source for c in chunks))

    return StoreInspectResponse(
        total_stored=len(chunks),
        sources=sources,
        chunks=chunks,
    )
