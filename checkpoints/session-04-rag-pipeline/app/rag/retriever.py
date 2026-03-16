# ============================================================
# Retriever — orchestrates embedding + search in one step
# ============================================================
# This module ties together the embedder and the store:
#   1. Take a user's question (plain text)
#   2. Embed it into a vector
#   3. Search the vector store for similar chunks
#   4. Return the matching chunks with their metadata
#
# This is the "R" in RAG — the Retrieval step.
#
# WHY A SEPARATE MODULE?
#   The query router could call embedder + store directly.
#   But having a retriever function makes the flow readable:
#     retrieve(question) → chunks → build prompt → call LLM
#   Each step is one function call. Easy to follow, easy to test.
# ============================================================

from app.rag.embedder import embed_text
from app.rag.store import search, count


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """
    Find the most relevant chunks for a question.

    Steps:
      1. Embed the query into a vector
      2. Search ChromaDB for similar chunk vectors
      3. Return chunks sorted by relevance (lowest distance first)

    Args:
        query: The user's question in plain text.
        top_k: How many chunks to retrieve.

    Returns:
        List of dicts with: text, source, chunk_index, distance.
        Empty list if the store has no chunks.
    """
    stored = count()
    if stored == 0:
        return []

    # Step 1: Turn the question into a vector
    query_embedding = embed_text(query)

    # Step 2: Find similar chunks in the vector store
    results = search(query_embedding, top_k=top_k)

    return results
