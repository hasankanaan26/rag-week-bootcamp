# ============================================================
# CHECKPOINT 6 — Retrieval You Can Defend
# ============================================================
# Added in Checkpoint 6:
#   - Nine retrieval strategies behind one contract (app/rag/strategies.py):
#     dense, bm25, hybrid (RRF), rerank (cross-encoder), hybrid_rerank,
#     parent (match small, return big), hyde, multi_query, routed
#   - A router: list questions go to a structured lookup, not top-k
#   - compare.py: one scoreboard, Hit@5 / MRR / Recall / latency / LLM calls,
#     and a regression check against a frozen baseline
#   - judge.py: LLM-as-judge faithfulness and correctness, cached
#   - GET /retrieve?strategy=...  and  POST /query?strategy=...
#
# From Checkpoint 5, students have:
#   - Everything from Checkpoints 1-4
#   - A sync JOB instead of POST /ingest: add / change / relabel /
#     touch / remove / quarantine, decided per document, priced
#     before it runs (sync.py, POST /sync)
#   - Format-aware parsers: md, csv, pdf (and scans), docx, xlsx,
#     html (boilerplate stripped), eml
#   - A document register: owner, permissions, status, versions,
#     effective dates (data/enterprise/register.json)
#   - Permission and freshness filters INSIDE the vector search
#   - "As of" retrieval for questions about the past
#   - PII redaction before embedding
#   - Blue/green rebuilds with a smoke check and rollback
#   - An evaluation that measures leaks, stale chunks and ghosts
#     (evaluate.py)
#
# Key teaching moments:
#   - Checkpoint 4's /ingest vs today's sync on the same SharePoint
#   - "salary bands" as an intern vs as an HR partner
#   - "meal per diem" today vs as_of=2024-03-15
#   - a footer edit: bytes changed, nothing re-embedded
# ============================================================

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import (
    CONFIDENCE_HIGH_THRESHOLD,
    CONFIDENCE_LOW_THRESHOLD,
    DEFAULT_USER,
    LLM_PROVIDER,
    NO_RESULT_DISTANCE,
    SOURCE_DIR,
)
from app.llm import get_model_name
from app.rag import catalog
from app.rag.doc_types import DOC_TYPES
from app.rag.embedder import embedding_model_id
from app.routers.ask import router as ask_router
from app.routers.compare import router as compare_router
from app.routers.documents import router as documents_router
from app.routers.embed import router as embed_router
from app.routers.inspect import router as inspect_router
from app.routers.query import router as query_router
from app.routers.retrieve import router as retrieve_router
from app.routers.search import router as search_router
from app.routers.sync import router as sync_router
from app.routers.ui import router as ui_router
from app.routers.visualize import router as visualize_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-18s | %(levelname)-5s | %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("chromadb.telemetry").setLevel(logging.WARNING)
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai.models").setLevel(logging.WARNING)

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="RAG Module — Checkpoint 6: Retrieval You Can Defend",
    version="0.6.0",
)

app.include_router(ask_router)
app.include_router(sync_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(inspect_router)
app.include_router(embed_router)
app.include_router(query_router)
app.include_router(retrieve_router)
app.include_router(compare_router)
app.include_router(ui_router)
app.include_router(visualize_router)

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/health")
def health_check():
    """Health check — confirms the app is running and shows active settings."""
    info = catalog.active_info()
    return {
        "status": "ok",
        "checkpoint": 6,
        "llm_provider": LLM_PROVIDER,
        "model": get_model_name(),
        "embedding_model": embedding_model_id(),
        "live_index": catalog.active_name(),
        "live_index_built_with": info.get("embedding_model"),
        "source": str(SOURCE_DIR),
        "default_user": DEFAULT_USER,
        "thresholds": {
            "high": CONFIDENCE_HIGH_THRESHOLD,
            "low": CONFIDENCE_LOW_THRESHOLD,
            "no_result": NO_RESULT_DISTANCE,
        },
        "doc_types": list(DOC_TYPES),
    }
