# ============================================================
# Vector Store (Postgres + pgvector) — store and search chunks in SQL
# ============================================================
# Used when VECTOR_STORE=postgres. Same functions as store_chroma.py,
# so the rest of the app doesn't care which one is active.
#
# Everything lives in one table you can open in pgAdmin:
#   acme_knowledge(id, source, chunk_index, doc_type, text, embedding)
#
# TEACHING POINT:
#   A vector store is "just" a table with a vector column and a
#   distance operator. pgvector's <-> operator is Euclidean (L2)
#   distance. We square it so the numbers match ChromaDB's default
#   (squared L2), which keeps the confidence thresholds in config.py
#   valid for both stores.
#
#   The embedding column has no fixed size, so Gemini (3072) and
#   Azure (1536) vectors both fit. The trade-off: no index, so every
#   search scans all rows. That's fine for 40 chunks. In production
#   you'd fix the size, e.g. vector(1536), and add an HNSW index.
# ============================================================

import json

import psycopg

from app.config import DATABASE_URL

TABLE_NAME = "acme_knowledge"


# Purpose:
# Opens a connection and makes sure the extension and table exist.
def get_connection() -> psycopg.Connection:
    """Connect to Postgres, creating the pgvector extension and table if needed."""
    conn = psycopg.connect(DATABASE_URL)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id          TEXT PRIMARY KEY,
            source      TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text        TEXT NOT NULL,
            embedding   vector NOT NULL
        )
    """)
    # Tables created before doc types existed don't have this column yet
    conn.execute(
        f"ALTER TABLE {TABLE_NAME} ADD COLUMN IF NOT EXISTS doc_type TEXT NOT NULL DEFAULT ''"
    )
    return conn


# Purpose:
# pgvector accepts vectors as text like '[0.1,0.2,0.3]', which is JSON.
def to_vector_text(embedding: list[float]) -> str:
    """Convert a Python list to pgvector's text format."""
    return json.dumps(embedding)


def add_chunks(chunks: list[dict], embeddings: list[list[float]]) -> int:
    """
    Store chunks with their embeddings in Postgres.

    Each chunk needs: text, source, chunk_index, doc_type.
    Returns the number of chunks stored.
    """
    rows = [
        (
            f"{c['source']}_{c['chunk_index']}",
            c["source"],
            c["chunk_index"],
            c.get("doc_type", "other"),
            c["text"],
            to_vector_text(emb),
        )
        for c, emb in zip(chunks, embeddings)
    ]

    # ON CONFLICT makes re-ingesting update rows instead of duplicating
    with get_connection() as conn:
        conn.cursor().executemany(
            f"""
            INSERT INTO {TABLE_NAME} (id, source, chunk_index, doc_type, text, embedding)
            VALUES (%s, %s, %s, %s, %s, %s::vector)
            ON CONFLICT (id) DO UPDATE SET
                source = EXCLUDED.source,
                chunk_index = EXCLUDED.chunk_index,
                doc_type = EXCLUDED.doc_type,
                text = EXCLUDED.text,
                embedding = EXCLUDED.embedding
            """,
            rows,
        )

    return len(rows)


def search(
    query_embedding: list[float],
    top_k: int = 3,
    doc_type: str | None = None,
) -> list[dict]:
    """
    Search for the most similar chunks to a query vector.

    If doc_type is given, a WHERE clause limits the search to that
    doc type before the rows are ranked by distance.

    Returns a list of dicts with: text, source, chunk_index, doc_type, distance.
    Lower distance = more similar = more relevant.
    """
    query_vector = to_vector_text(query_embedding)
    where = "WHERE doc_type = %(doc_type)s" if doc_type else ""

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT text, source, chunk_index, doc_type,
                   (embedding <-> %(q)s::vector) ^ 2 AS distance
            FROM {TABLE_NAME} {where}
            ORDER BY embedding <-> %(q)s::vector
            LIMIT %(k)s
            """,
            {"q": query_vector, "k": top_k, "doc_type": doc_type},
        ).fetchall()

    return [
        {"text": r[0], "source": r[1], "chunk_index": r[2], "doc_type": r[3], "distance": r[4]}
        for r in rows
    ]


def count() -> int:
    """Count how many chunks are stored."""
    with get_connection() as conn:
        return conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]


def get_all_chunks(
    source: str | None = None,
    limit: int = 50,
    include_embeddings: bool = False,
) -> list[dict]:
    """
    Retrieve stored chunks for inspection.

    Optionally filter by source file and include embedding previews.
    """
    where = "WHERE source = %(source)s" if source else ""

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT id, text, source, chunk_index, doc_type, embedding::text
            FROM {TABLE_NAME} {where}
            ORDER BY source, chunk_index
            LIMIT %(limit)s
            """,
            {"source": source, "limit": limit},
        ).fetchall()

    items = []
    for row_id, text, src, chunk_index, doc_type, embedding_text in rows:
        item = {
            "id": row_id,
            "text": text,
            "source": src,
            "chunk_index": chunk_index,
            "doc_type": doc_type,
        }
        if include_embeddings:
            emb = json.loads(embedding_text)
            item["embedding_preview"] = emb[:5]
            item["embedding_dimensions"] = len(emb)
        items.append(item)

    return items


def get_all_embeddings() -> tuple[list[list[float]], list[str]]:
    """Return every stored vector and its source filename (for /visualize)."""
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT embedding::text, source FROM {TABLE_NAME} ORDER BY id"
        ).fetchall()

    embeddings = [json.loads(r[0]) for r in rows]
    sources = [r[1] for r in rows]
    return embeddings, sources


def clear():
    """Delete all chunks. Dropping the table also allows a new vector size."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
