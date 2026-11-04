# ============================================================
# Configuration — Checkpoint 4
# ============================================================
# Added: Confidence thresholds for transparent UX.
#
# TEACHING POINT:
#   These thresholds control when the system says "I don't know"
#   vs "I'm not sure" vs "here's your answer."
#   Students should experiment with these values live.
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM provider: "gemini" or "azure" ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# --- Gemini settings (used when LLM_PROVIDER=gemini) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")

# --- Azure OpenAI settings (used when LLM_PROVIDER=azure) ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")

# --- Embedding provider: "gemini", "azure", or "ollama" ---
# Defaults to LLM_PROVIDER. Set it to mix and match,
# e.g. Azure for answers + a local model for embeddings.
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", LLM_PROVIDER)

# --- Ollama settings (used when EMBEDDING_PROVIDER=ollama) ---
# Install Ollama (https://ollama.com), then: ollama pull nomic-embed-text
# Running the app in Docker? Use http://host.docker.internal:11434
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

# --- Data settings ---
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "data/knowledge")

# --- Chunking settings ---
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "500"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))

# --- Supported file types for ingestion ---
SUPPORTED_EXTENSIONS = [".md", ".txt", ".csv", ".pdf", ".json"]

# --- Vector store settings ---
# "chroma" (default, local files) or "postgres" (pgvector, see docker-compose.yml)
VECTOR_STORE = os.getenv("VECTOR_STORE", "chroma")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://rag:rag@localhost:5434/rag_bootcamp"
)

# --- Confidence thresholds ---
# ChromaDB uses L2 (squared Euclidean) distance by default.
# Lower distance = closer vectors = more relevant.
# These thresholds classify retrieval confidence:
#   distance <= HIGH  -> high confidence (strong match)
#   distance <= LOW   -> medium confidence (reasonable match)
#   distance > LOW    -> low confidence (weak evidence)
# If ALL results exceed NO_RESULT, treat as no result found.
CONFIDENCE_HIGH_THRESHOLD = float(os.getenv("CONFIDENCE_HIGH_THRESHOLD", "0.8"))
CONFIDENCE_LOW_THRESHOLD = float(os.getenv("CONFIDENCE_LOW_THRESHOLD", "1.4"))
NO_RESULT_DISTANCE = float(os.getenv("NO_RESULT_DISTANCE", "1.6"))
