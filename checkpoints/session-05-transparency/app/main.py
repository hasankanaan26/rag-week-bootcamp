# ============================================================
# CHECKPOINT: Session 5 — Source Panel and Transparent UX
# ============================================================
# After this session, students have:
#   - Everything from Sessions 1-4
#   - Confidence scoring (high/medium/low/none)
#   - No-result handling: "I don't have that information"
#   - Weak-evidence warnings for borderline queries
#   - A browser-based UI at /ui showing:
#       answer, confidence badge, source snippets, distances
#   - Distance scores on each source in the API response
#
# Key teaching moment:
#   "A good RAG system knows when it doesn't know."
#   Try: "Tell me about quantum physics" → no_result: true
#   Try: "What about time off?"          → confidence: medium
#   Try: "How many vacation days?"       → confidence: high
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.query import router as query_router
from app.routers.embed import router as embed_router
from app.routers.ui import router as ui_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="Week 3: RAG Done Properly — Session 5 checkpoint",
    version="0.5.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(query_router)
app.include_router(embed_router)
app.include_router(ui_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 5}
