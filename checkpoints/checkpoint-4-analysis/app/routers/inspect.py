# ============================================================
# Router: /store/inspect — See what's inside the vector store
# ============================================================
# This endpoint makes the "invisible" visible. Students can
# see exactly what ChromaDB is holding:
#   - The chunk text
#   - The metadata (source file, chunk index)
#   - The embedding vector (first few dimensions + total size)
#
# This is a teaching tool — in production you wouldn't expose
# raw vector store contents via an API.
#
# DEMO:
#   GET /store/inspect                       → all chunks
#   GET /store/inspect?source=leave-policy.md → filter by file
#   GET /store/inspect?show_embeddings=true  → include vectors
# ============================================================

from fastapi import APIRouter, Query
from app.models import StoreInspectResponse, StoredChunkInfo
from app.rag.store import get_all_chunks, count

router = APIRouter(prefix="/store", tags=["Store Inspector"])


@router.get("/inspect", response_model=StoreInspectResponse)
def inspect_store(
    source: str | None = Query(
        default=None,
        description="Filter by source filename, e.g. 'leave-policy.md'.",
    ),
    show_embeddings: bool = Query(
        default=False,
        description="Include embedding vectors (first 5 dimensions). Warning: verbose!",
    ),
    limit: int = Query(
        default=50,
        description="Max chunks to return.",
        le=500,
    ),
):
    """
    Inspect the contents of the vector store.

    See what chunks are stored, their metadata, and optionally
    a preview of their embedding vectors.
    """
    raw = get_all_chunks(source=source, limit=limit, include_embeddings=show_embeddings)

    chunks = []
    for item in raw:
        chunk = StoredChunkInfo(
            id=item["id"],
            text=item["text"],
            source=item["source"],
            chunk_index=item["chunk_index"],
            doc_type=item.get("doc_type", ""),
            embedding_preview=item.get("embedding_preview"),
            embedding_dimensions=item.get("embedding_dimensions"),
        )
        chunks.append(chunk)

    # Collect unique sources
    sources = sorted(set(c.source for c in chunks))

    # total_stored is everything in the store, not just the rows returned
    return StoreInspectResponse(
        total_stored=count(),
        sources=sources,
        chunks=chunks,
    )
