# ============================================================
# CHECKPOINT: Session 1 — RAG Foundations and FastAPI Integration
# ============================================================
# After this session, students have:
#   - A running FastAPI app with /health and /ask endpoints
#   - A plain LLM call that answers questions (no retrieval)
#   - A /ask/grounded demo showing what "grounded" answers look like
#   - An understanding of WHY plain LLM answers aren't enough
#
# Key question for students:
#   "Ask the LLM about Acme Corp's leave policy. What happens?"
#   Answer: It makes something up. That's the problem RAG solves.
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="Week 3: RAG Done Properly — Session 1 checkpoint",
    version="0.1.0",
)

# Mount the ask router
app.include_router(ask_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 1}
