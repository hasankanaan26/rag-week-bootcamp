# ============================================================
# CHECKPOINT: Session 4 — RAG Pipeline Wiring
# ============================================================
# After this session, students have:
#   - Everything from Sessions 1-3
#   - A retriever that embeds a query and searches the store
#   - A RAG prompt template with context injection
#   - POST /query — the full RAG endpoint:
#       question → retrieve → build prompt → call LLM → answer
#   - Answers include source attribution
#
# The complete RAG loop is now working:
#   Retrieve → Inject → Generate
#
# Key comparison:
#   POST /ask {"question": "How many vacation days?"}     → hallucination
#   POST /query {"question": "How many vacation days?"}   → correct, with sources
# ============================================================

from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.query import router as query_router
from app.routers.embed import router as embed_router

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="Week 3: RAG Done Properly — Session 4 checkpoint",
    version="0.4.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(query_router)
app.include_router(embed_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 4}
