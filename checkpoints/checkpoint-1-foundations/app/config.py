# ============================================================
# Configuration — Checkpoint 1
# ============================================================
# LLM settings + data/chunking settings for document ingestion.
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM provider: "gemini" or "azure" ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# --- Gemini settings (used when LLM_PROVIDER=gemini) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- Azure OpenAI settings (used when LLM_PROVIDER=azure) ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")

# --- Data settings ---
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "data/knowledge")

# --- Chunking settings ---
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "500"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "50"))

# --- Supported file types for ingestion ---
SUPPORTED_EXTENSIONS = [".md", ".txt", ".csv", ".pdf", ".json"]
