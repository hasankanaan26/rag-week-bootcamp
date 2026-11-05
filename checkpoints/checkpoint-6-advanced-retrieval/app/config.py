# ============================================================
# Configuration — Checkpoint 5
# ============================================================
# Added: everything an ingestion JOB needs that a demo endpoint
# did not: where the source system is, who may read what, how
# big an embedding batch is, how often to retry, what a run costs.
#
# TEACHING POINT:
#   Checkpoint 4 ingested a folder when you called POST /ingest.
#   Checkpoint 5 syncs a source system on a schedule. The settings
#   below are the knobs a production team actually turns.
# ============================================================

import os
from pathlib import Path

from dotenv import load_dotenv

# Paths are resolved from the repository root, so the scripts in this
# checkpoint work no matter which folder you run them from.
REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKPOINT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(REPO_ROOT / ".env")


def _path(value: str) -> Path:
    """Resolve a path from .env: absolute stays absolute, relative is from the repo root."""
    p = Path(value)
    return p if p.is_absolute() else REPO_ROOT / p


# --- LLM provider: "gemini" or "azure" ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# --- Gemini settings (used when LLM_PROVIDER=gemini) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# --- Azure OpenAI settings (used when LLM_PROVIDER=azure) ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")

# --- Embedding provider: "local", "gemini", "azure" or "ollama" ---
# CHANGED in Checkpoint 5: the default is now "local", a small model
# (all-MiniLM-L6-v2) that ships with ChromaDB and runs on your laptop.
# Free, offline after the first download, and the same numbers on every
# machine, which is what you want when you MEASURE. Set
# EMBEDDING_PROVIDER=gemini to use the cloud model instead; the sync job
# will then tell you the index needs a full rebuild.
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")

# --- Ollama settings (used when EMBEDDING_PROVIDER=ollama) ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# --- The source system ---
# data/enterprise is the seed: a snapshot of Acme's SharePoint on Friday.
# sharepoint.py copies it to workspace/sharepoint, and replays the weekend's
# changes there. The sync job only ever reads workspace/sharepoint.
SEED_DIR = _path(os.getenv("SEED_DIR", "data/enterprise"))
SOURCE_DIR = _path(os.getenv("SOURCE_DIR", "workspace/sharepoint"))
REGISTER_FILENAME = "_register.json"
IDENTITIES_FILE = _path(os.getenv("IDENTITIES_FILE", "data/enterprise/identities.json"))

# The user the API acts as when you don't say. Least privilege by default.
DEFAULT_USER = os.getenv("DEFAULT_USER", "intern")

# --- Sync job settings ---
# Bump PIPELINE_VERSION whenever parsing or chunking logic changes: it is
# part of every document's content hash, so the next sync re-embeds all.
PIPELINE_VERSION = "cp6.1"
SECTION_MAX_CHARS = int(os.getenv("SECTION_MAX_CHARS", "900"))
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "64"))
EMBED_MAX_ATTEMPTS = int(os.getenv("EMBED_MAX_ATTEMPTS", "5"))
EMBED_RETRY_BASE_SECONDS = float(os.getenv("EMBED_RETRY_BASE_SECONDS", "1.0"))

# Rough list prices in USD per 1M input tokens, for the cost estimate the
# sync job prints BEFORE it spends anything. Check current pricing.
EMBEDDING_PRICE_PER_1M_TOKENS = {
    "local": 0.0,
    "ollama": 0.0,
    "fake": 0.0,
    "gemini": float(os.getenv("GEMINI_EMBEDDING_PRICE", "0.15")),
    "azure": float(os.getenv("AZURE_EMBEDDING_PRICE", "0.02")),
}

# Personal data we redact before embedding. Addresses at these domains
# are business contacts and stay readable.
CORPORATE_EMAIL_DOMAINS = ["acmecorp.com", "acme.example"]

# --- Vector store settings ---
# Checkpoint 5 uses ChromaDB only. (The pgvector backend from Checkpoint 4
# would need the same metadata filters written as SQL WHERE clauses.)
CHROMA_PATH = _path(os.getenv("CHROMA_PATH", "chroma_data"))
CATALOG_FILE = CHROMA_PATH / "cp6_catalog.json"
NAIVE_COLLECTION = "cp6_naive"
RUNS_DIR = _path(os.getenv("CP6_RUNS_DIR", str(CHECKPOINT_DIR / "runs")))

# --- Checkpoint 6: retrieval strategies ---
# How many candidates the first stage hands to fusion or the reranker.
CANDIDATES = int(os.getenv("CANDIDATES", "20"))
# The cross-encoder used to re-rank candidates (ONNX, CPU).
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
# Parent-document retrieval: children are sentences up to this length.
CHILD_MAX_CHARS = int(os.getenv("CHILD_MAX_CHARS", "220"))
# HyDE, multi-query and the judge cache their LLM calls here.
LLM_CACHE_FILE = RUNS_DIR / "llm_cache.json"

# --- Kept from Checkpoint 4 ---
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "500"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))
VECTOR_STORE = "chroma"

# --- Confidence thresholds (Checkpoint 4) ---
# Squared L2 distance between normalized vectors: 0 = identical, 2 = unrelated.
CONFIDENCE_HIGH_THRESHOLD = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", "0.8"))
CONFIDENCE_LOW_THRESHOLD = float(os.getenv("CONFIDENCE_LOW_THRESHOLD", "1.4"))
NO_RESULT_DISTANCE = float(os.getenv("NO_RESULT_DISTANCE", "1.6"))
