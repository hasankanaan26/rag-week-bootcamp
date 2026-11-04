# ============================================================
# Base App — Minimal FastAPI scaffold for live coding
# ============================================================
# This is your starting point. Run it with:
#   cd base-app && uvicorn app.main:app --reload
#
# What's here:
#   - A running FastAPI app with /health
#   - LLM calling utility (pre-built in llm.py)
#   - Empty routers/ and rag/ directories for you to fill
#
# What you'll build during the sessions:
#   - Document loading and chunking
#   - Embedding and vector storage
#   - Retrieval-augmented generation
#   - Failure handling and visualization
# ============================================================

from fastapi import FastAPI

app = FastAPI(
    title="Acme Corp Knowledge Assistant",
    description="RAG Module — Base scaffold for live coding",
    version="0.0.1",
)


@app.get("/health")
def health_check():
    """Simple health check — confirms the app is running."""
    return {"status": "ok", "checkpoint": "base"}
