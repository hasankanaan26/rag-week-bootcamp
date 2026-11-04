# ============================================================
# CHECKPOINT 3 — Retrieval to Generation Wiring
# ============================================================
# After this checkpoint, students have:
#   - Everything from Checkpoints 1-2
#   - A retriever that embeds a query and searches the store
#   - A RAG prompt template with context injection
#   - POST /query — the full RAG endpoint
#   - POST /compare — RAG vs plain LLM side-by-side
#   - Structured logging across the pipeline
#
# The complete RAG loop is now working:
#   Retrieve -> Inject -> Generate
#
# Key comparison:
#   POST /ask {"question": "How many vacation days?"}     -> hallucination
#   POST /query {"question": "How many vacation days?"}   -> correct, with sources
# ============================================================

import logging
from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.inspect import router as inspect_router
from app.routers.embed import router as embed_router
from app.routers.query import router as query_router
from app.routers.compare import router as compare_router

# --- Logging setup ---
# Structured, readable format for teaching.
# In production you'd use JSON logging. For teaching, human-readable is better.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-18s | %(levelname)-5s | %(message)s",
    datefmt="%H:%M:%S",
)

# Silence noisy third-party loggers
logging.getLogger("chromadb.telemetry").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai.models").setLevel(logging.WARNING)

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="RAG Module — Checkpoint 3: Retrieval to Generation",
    version="0.3.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(inspect_router)
app.include_router(embed_router)
app.include_router(query_router)
app.include_router(compare_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "checkpoint": 3}
