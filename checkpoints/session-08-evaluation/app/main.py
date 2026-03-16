# ============================================================
# CHECKPOINT: Session 8 — Evaluation & Safety
# ============================================================
# After this session, students have:
#   - Everything from Sessions 1-7
#   - POST /safety/check — LLM-as-judge prompt injection detection
#   - Evaluation pipeline: test_questions.json + run_eval.py
#   - Test coverage for factual, vague, out-of-domain, and injection queries
#
# Key teaching moment:
#   Run the eval pipeline and see which questions pass or fail.
#   Then try prompt injection attacks through /safety/check.
#   Students learn that evaluation and safety are not optional extras.
# ============================================================

import logging
from fastapi import FastAPI
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.query import router as query_router
from app.routers.compare import router as compare_router
from app.routers.embed import router as embed_router
from app.routers.safety import router as safety_router
from app.routers.ui import router as ui_router

# --- Logging setup ---
# Structured, readable format that connects to Week 2 tracing concepts.
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
    description="Week 3: RAG Done Properly — Session 8 checkpoint",
    version="0.8.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(query_router)
app.include_router(compare_router)
app.include_router(embed_router)
app.include_router(safety_router)
app.include_router(ui_router)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "week": 3, "session": 6}
