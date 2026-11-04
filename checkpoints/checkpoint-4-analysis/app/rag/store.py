# ============================================================
# Vector Store — picks ChromaDB or Postgres based on VECTOR_STORE
# ============================================================
# The rest of the app imports from here and never needs to know
# which database is behind it:
#   VECTOR_STORE=chroma    -> store_chroma.py   (default, local files)
#   VECTOR_STORE=postgres  -> store_postgres.py (pgvector in Docker)
#
# TEACHING POINT:
#   ChromaDB is one of many vector stores (Pinecone, Weaviate,
#   pgvector, Qdrant, etc.). The RAG pattern stays the same
#   regardless of which store you choose. This file proves it:
#   both stores expose the exact same six functions.
# ============================================================

from app.config import VECTOR_STORE

if VECTOR_STORE == "postgres":
    from app.rag import store_postgres as backend
else:
    from app.rag import store_chroma as backend


def add_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """Store chunks with their embeddings. Returns how many were stored."""
    return backend.add_chunks(chunks, embeddings)


def search(
    query_embedding: list[float],
    top_k: int = 3,
    doc_type: str | None = None,
) -> list[dict]:
    """Return the top_k closest chunks, optionally only from one doc_type."""
    return backend.search(query_embedding, top_k, doc_type)


def count() -> int:
    """Count how many chunks are stored."""
    return backend.count()


def get_all_chunks(
    source: str | None = None,
    limit: int = 50,
    include_embeddings: bool = False,
) -> list[dict]:
    """Retrieve stored chunks for inspection."""
    return backend.get_all_chunks(source, limit, include_embeddings)


def get_all_embeddings() -> tuple[list[list[float]], list[str]]:
    """Return every stored vector and its source filename."""
    return backend.get_all_embeddings()


def clear():
    """Delete all chunks. Useful for re-ingesting from scratch."""
    backend.clear()
