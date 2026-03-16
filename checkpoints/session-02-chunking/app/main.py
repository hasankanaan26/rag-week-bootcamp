# ============================================================
# CHECKPOINT: Session 2 — Document Ingestion and Chunking
# ============================================================
# After this session, students have:
#   - Everything from Session 1 (plain + grounded endpoints)
#   - A chunking utility that splits documents into overlapping chunks
#   - A /ingest endpoint that loads markdown files and returns chunks
#   - An understanding of WHY chunking matters for RAG
#
# Key question for students:
#   "Why can't we just paste the entire document into the prompt?"
#   Answer: Token limits, cost, and irrelevant noise.
#   Chunking lets us retrieve ONLY the relevant parts.
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="Week 3: RAG Done Properly — Session 2 checkpoint",
    version="0.2.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 2}
