# ============================================================
# Router: /ingest — Load and chunk knowledge base documents
# ============================================================
# This endpoint reads files from the data/knowledge/ folder,
# splits them into chunks, and returns the results.
#
# In Session 2, chunks are NOT stored anywhere yet.
# We just inspect them to understand chunking behavior.
# In Session 3, we'll embed and store them in ChromaDB.
#
# NEW IN THIS VERSION:
#   - Supports multiple file types: .md, .txt, .csv, .pdf, .json
#   - Two chunking strategies: "fixed" (character-based with
#     overlap) and "sections" (split on headings/paragraphs)
#
# DEMO: Hit POST /ingest and look at the chunks.
#   - How many chunks per file?
#   - Where do the chunk boundaries fall?
#   - Compare fixed vs section-based chunking
#
# Try: POST /ingest?chunk_strategy=sections
# Try: POST /ingest?chunk_size=200
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

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse)
def ingest_documents(
    chunk_size: int = Query(
        default=DEFAULT_CHUNK_SIZE,
        description="Max characters per chunk (used with 'fixed' strategy). Try 200, 500, or 1000.",
    ),
    overlap: int = Query(
        default=DEFAULT_CHUNK_OVERLAP,
        description="Characters of overlap between chunks (used with 'fixed' strategy).",
    ),
    chunk_strategy: str = Query(
        default="fixed",
        description="Chunking strategy: 'fixed' (character-based with overlap) or 'sections' (split on headings/paragraphs).",
    ),
):
    """
    Load all supported files from the knowledge base and split into chunks.

    Supports: .md, .txt, .csv, .pdf, .json

    Two chunking strategies:
    - **fixed**: Split every N characters with overlap (default)
    - **sections**: Split on markdown headings or paragraph breaks
    """
    knowledge_path = Path(KNOWLEDGE_DIR)

    if not knowledge_path.exists():
        return IngestResponse(files_processed=0, total_chunks=0, chunks=[])

    all_chunks = []
    files_processed = 0

    # Read each supported file in the knowledge directory
    for filepath in sorted(knowledge_path.iterdir()):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # Use the loader to convert any format to plain text
        text = load_file(str(filepath))
        filename = filepath.name

        # Chunk using the selected strategy
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

    # Convert raw chunk dicts to Pydantic models for the response
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
        chunks=chunk_infos,
    )
