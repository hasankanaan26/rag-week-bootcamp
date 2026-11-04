# ============================================================
# CHECKPOINT 4 — Failure Modes, Analysis, and Visualization
# ============================================================
# After this checkpoint, students have:
#   - Everything from Checkpoints 1-3
#   - Confidence scoring (high/medium/low/none)
#   - No-result detection ("I don't have that information")
#   - Weak-evidence warnings
#   - Browser UI with confidence badges at /ui
#   - t-SNE/PCA embedding visualization at /visualize
#   - Full structured logging across the pipeline
#   - RAG vs plain comparison with confidence info
#
# Key teaching moments:
#   - "Tell me about quantum physics" -> no_result
#   - "What are the rules?" -> low confidence (too broad)
#   - "How many vacation days?" -> high confidence
#   - Visit /visualize to see how embeddings cluster by document
# ============================================================

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config import (
    LLM_PROVIDER,
    EMBEDDING_PROVIDER,
    VECTOR_STORE,
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_LOW_THRESHOLD,
    NO_RESULT_DISTANCE,
)
from app.llm import get_model_name
from app.rag.doc_types import DOC_TYPES
from app.routers.ask import router as ask_router
from app.routers.ingest import router as ingest_router
from app.routers.search import router as search_router
from app.routers.inspect import router as inspect_router
from app.routers.embed import router as embed_router
from app.routers.query import router as query_router
from app.routers.compare import router as compare_router
from app.routers.ui import router as ui_router
from app.routers.visualize import router as visualize_router

# --- Logging setup ---
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
    description="RAG Module — Checkpoint 4: Failure Modes, Analysis, and Visualization",
    version="0.4.0",
)

# Mount routers
app.include_router(ask_router)
app.include_router(ingest_router)
app.include_router(search_router)
app.include_router(inspect_router)
app.include_router(embed_router)
app.include_router(query_router)
app.include_router(compare_router)
app.include_router(ui_router)
app.include_router(visualize_router)

# CSS and JS for the /ui page
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)


@app.get("/health")
def health_check():
    """Health check — confirms the app is running and shows active settings."""
    return {
        "status": "ok",
        "checkpoint": 4,
        "llm_provider": LLM_PROVIDER,
        "model": get_model_name(),
        "embedding_provider": EMBEDDING_PROVIDER,
        "vector_store": VECTOR_STORE,
        "thresholds": {
            "high": CONFIDENCE_HIGH_THRESHOLD,
            "low": CONFIDENCE_LOW_THRESHOLD,
            "no_result": NO_RESULT_DISTANCE,
        },
        "doc_types": list(DOC_TYPES),
    }
