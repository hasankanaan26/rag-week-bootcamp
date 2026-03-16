# ============================================================
# CHECKPOINT: Session 3 — Embeddings and Vector Storage
# ============================================================
# After this session, students have:
#   - Everything from Sessions 1-2 (plain chat, grounded demo, chunking)
#   - An embedder that turns text into vectors
#   - A ChromaDB store that persists chunks with their embeddings
#   - An updated /ingest endpoint that embeds + stores chunks
#   - A /search endpoint for testing retrieval in isolation
#
# Key question for students:
#   "Search for 'vacation days'. Now search for 'annual leave'.
#   Both find the same chunks — how? They don't share any words!"
#   Answer: Embeddings capture MEANING, not keywords.
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.inspect import router as inspect_router
from app.routers.embed import router as embed_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="Week 3: RAG Done Properly — Session 3 checkpoint",
    version="0.3.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(inspect_router)
app.include_router(embed_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 3}
