# ============================================================
# Test setup — offline, isolated, no API keys
# ============================================================
# Run from the repository root:
#   pytest checkpoints/checkpoint-6-advanced-retrieval/tests -q
#
# Before any app module is imported, point every path at a temp
# folder and switch the embedder to "fake" (hash-based vectors).
# Nothing here touches your real index, your .env keys or the network.
# ============================================================

import os
import sys
import tempfile
from pathlib import Path

import pytest

CHECKPOINT = Path(__file__).resolve().parents[1]
TMP = Path(tempfile.mkdtemp(prefix="cp6-tests-"))

os.environ["SOURCE_DIR"] = str(TMP / "sharepoint")
os.environ["CHROMA_PATH"] = str(TMP / "chroma")
os.environ["CP6_RUNS_DIR"] = str(TMP / "runs")
os.environ["EMBEDDING_PROVIDER"] = "fake"
os.environ["EMBED_RETRY_BASE_SECONDS"] = "0"
os.environ["RERANKER"] = "fake"  # Checkpoint 6: word-overlap scores instead of the ONNX model
os.environ["ANONYMIZED_TELEMETRY"] = "False"
sys.path.insert(0, str(CHECKPOINT))


@pytest.fixture
def friday():
    """A fresh SharePoint (Friday) and no index at all."""
    import sharepoint
    from app.config import CATALOG_FILE
    from app.rag.store_chroma import drop_collection, get_client

    for col in get_client().list_collections():
        drop_collection(col if isinstance(col, str) else col.name)
    CATALOG_FILE.unlink(missing_ok=True)
    sharepoint.reset()
    return sharepoint


@pytest.fixture
def events():
    """Load the weekend's events by id."""
    import sharepoint
    return {e["id"]: e for e in sharepoint.load_events()}
