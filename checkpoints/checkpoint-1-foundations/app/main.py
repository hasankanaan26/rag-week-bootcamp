# ============================================================
# CHECKPOINT 1 — Foundations of RAG
# ============================================================
# After this checkpoint, students have:
#   - A running FastAPI app with /health and /ask endpoints
#   - A plain LLM call that answers questions (no retrieval)
#   - A /ask/grounded demo showing what "grounded" answers look like
#   - A /ingest endpoint that loads and chunks documents
#   - An understanding of WHY plain LLM answers aren't enough
#   - An understanding of how chunking works and why it matters
#
# Key demo:
#   "Ask the LLM about Acme Corp's leave policy via /ask. What happens?"
#   Answer: It makes something up. That's the problem RAG solves.
#   Then try /ask/grounded — same question, correct answer.
#   Then try /ingest — see how documents become chunks.
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="RAG Module — Checkpoint 1: Foundations",
    version="0.1.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "checkpoint": 1}
