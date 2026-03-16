# ============================================================
# Router: /ingest — Load, chunk, embed, and store documents
# ============================================================
# UPDATED in Session 3: Now embeds chunks and stores them in
# ChromaDB (in Session 2, chunks were only returned for inspection).
#
# The flow is now:
#   Read files → Chunk → Embed → Store in ChromaDB → Return summary
#
# DEMO:
#   1. POST /ingest — load all documents into the vector store
#   2. Check the response: how many chunks were stored?
#   3. POST /ingest again — notice it re-indexes (upsert, not duplicates)
# ============================================================

from pathlib import Path
from fastapi import APIRouter, Query
from app.config import (
    KNOWLEDGE_DIR,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    SUPPORTED_EXTENSIONS,
)
from app.models import IngestResponse, ChunkInfo
from app.rag.chunker import chunk_document, chunk_by_sections
from app.rag.loader import load_file
from app.rag.embedder import embed_texts
from app.rag.store import add_chunks, clear

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse)
def ingest_documents(
    chunk_size: int = Query(
        default=DEFAULT_CHUNK_SIZE,
        description="Max characters per chunk (used with 'fixed' strategy).",
    ),
    overlap: int = Query(
        default=DEFAULT_CHUNK_OVERLAP,
        description="Characters of overlap between chunks (used with 'fixed' strategy).",
    ),
    chunk_strategy: str = Query(
        default="fixed",
        description="Chunking strategy: 'fixed' or 'sections'.",
    ),
    fresh: bool = Query(
        default=False,
        description="Set to true to clear the store before ingesting.",
    ),
):
    """
    Load all supported files, chunk them, embed them, and store in ChromaDB.
    """
    if fresh:
        clear()

    knowledge_path = Path(KNOWLEDGE_DIR)

    if not knowledge_path.exists():
        return IngestResponse(
            files_processed=0, total_chunks=0, chunks_stored=0, chunks=[]
        )

    all_chunks = []
    files_processed = 0

    for filepath in sorted(knowledge_path.iterdir()):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = load_file(str(filepath))
        filename = filepath.name

        if chunk_strategy == "sections":
            doc_chunks = chunk_by_sections(text=text, source=filename)
        else:
            doc_chunks = chunk_document(
                text=text,
                source=filename,
                chunk_size=chunk_size,
                overlap=overlap,
            )

        all_chunks.extend(doc_chunks)
        files_processed += 1

    # Embed all chunks in one batch
    chunk_texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(chunk_texts)

    # Store chunks + embeddings in ChromaDB
    chunks_stored = add_chunks(all_chunks, embeddings)

    # Build response with chunk details
    chunk_infos = [
        ChunkInfo(
            text=chunk["text"],
            source=chunk["source"],
            chunk_index=chunk["chunk_index"],
        )
        for chunk in all_chunks
    ]

    return IngestResponse(
        files_processed=files_processed,
        total_chunks=len(chunk_infos),
        chunks_stored=chunks_stored,
        chunks=chunk_infos,
    )
