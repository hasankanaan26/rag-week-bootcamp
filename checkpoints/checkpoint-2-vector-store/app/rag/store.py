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
#   pgvector, Qdrant, FAISS, etc.). The RAG pattern stays the same
#   regardless of which store you choose.
# ============================================================

import chromadb
from app.config import CHROMA_PATH

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


# Purpose:
# Stores chunks with their embeddings in ChromaDB using upsert
# so re-ingesting updates rather than duplicates.
def add_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """
    Store chunks with their embeddings in ChromaDB.
    Each chunk needs: text, source, chunk_index.
    Returns the number of chunks stored.
    """
    collection = get_collection()

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


# Purpose:
# Searches for the most similar chunks to a query vector.
# Returns results sorted by distance (lower = more relevant).
def search(query_embedding: list[float], top_k: int = 3) -> list[dict]:
    """
    Search for the most similar chunks to a query vector.
    Returns a list of dicts with: text, source, chunk_index, distance.
    Lower distance = more similar = more relevant.
    """
    collection = get_collection()

    n_stored = collection.count()
    if n_stored == 0:
        return []
    actual_k = min(top_k, n_stored)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=actual_k,
    )

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


# Purpose:
# Retrieves stored chunks for inspection, optionally with embedding previews.
def get_all_chunks(
    source: str | None = None,
    limit: int = 50,
    include_embeddings: bool = False,
) -> list[dict]:
    """Retrieve stored chunks for inspection."""
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
        pass
