# ============================================================
# Configuration — Checkpoint 2
# ============================================================
# Added: Embedding model settings, ChromaDB path
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
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")
