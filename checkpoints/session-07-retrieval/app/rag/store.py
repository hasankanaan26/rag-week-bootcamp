# ============================================================
# Vector Store — ChromaDB wrapper for storing and searching chunks
# ============================================================
# ChromaDB stores our chunks alongside their vector embeddings.
# When we search, it finds the chunks whose vectors are closest
# to the query vector — that means "most similar in meaning."
#
# This module is intentionally thin: just a few functions
# around ChromaDB's Python API. No abstraction layers.
#
# TEACHING POINT:
#   ChromaDB is one of many vector stores (Pinecone, Weaviate,
#   pgvector, Qdrant, etc.). The RAG pattern stays the same
#   regardless of which store you choose.
# ============================================================

import chromadb
from app.config import CHROMA_PATH

# One collection for our knowledge base
COLLECTION_NAME = "acme_knowledge"


def get_client() -> chromadb.ClientAPI:
    """Create a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    """Get or create the knowledge base collection."""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Acme Corp knowledge base chunks"},
    )


def add_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """
    Store chunks with their embeddings in ChromaDB.

    Each chunk needs: text, source, chunk_index.
    Returns the number of chunks stored.
    """
    collection = get_collection()

    # Build unique IDs so re-ingesting updates instead of duplicates
    ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def search(
    query_embedding: list[float],
    top_k: int = 3,
    where: dict | None = None,
) -> list[dict]:
    """
    Search for the most similar chunks to a query vector.

    Args:
        query_embedding: The query vector.
        top_k: Number of results to return.
        where: Optional ChromaDB metadata filter (e.g. {"source": "leave-policy.md"}).

    Returns a list of dicts with: text, source, chunk_index, distance.
    Lower distance = more similar = more relevant.
    """
    collection = get_collection()

    # Don't request more results than we have stored
    n_stored = collection.count()
    if n_stored == 0:
        return []
    actual_k = min(top_k, n_stored)

    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": actual_k,
    }
    if where:
        query_kwargs["where"] = where

    results = collection.query(**query_kwargs)

    # Unpack ChromaDB's nested response format into flat dicts
    items = []
    for i in range(len(results["ids"][0])):
        items.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i],
        })

    return items


def count() -> int:
    """Count how many chunks are stored."""
    return get_collection().count()


def get_all_chunks(
    source: str | None = None,
    limit: int = 50,
    include_embeddings: bool = False,
) -> list[dict]:
    """
    Retrieve stored chunks for inspection.

    Optionally filter by source file and include embedding previews.
    """
    collection = get_collection()

    if collection.count() == 0:
        return []

    includes = ["documents", "metadatas"]
    if include_embeddings:
        includes.append("embeddings")

    kwargs = {"limit": limit, "include": includes}
    if source:
        kwargs["where"] = {"source": source}

    data = collection.get(**kwargs)

    items = []
    for i in range(len(data["ids"])):
        item = {
            "id": data["ids"][i],
            "text": data["documents"][i],
            "source": data["metadatas"][i]["source"],
            "chunk_index": data["metadatas"][i]["chunk_index"],
        }
        if include_embeddings and data.get("embeddings") is not None:
            emb = list(data["embeddings"][i])
            item["embedding_preview"] = emb[:5]
            item["embedding_dimensions"] = len(emb)
        items.append(item)

    return items


def clear():
    """Delete all chunks. Useful for re-ingesting from scratch."""
    client = get_client()
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except ValueError:
        pass  # Collection didn't exist
