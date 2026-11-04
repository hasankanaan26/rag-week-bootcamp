# ============================================================
# Embedder — turns text into vector embeddings
# ============================================================
# An embedding is a list of numbers (a vector) that captures
# the MEANING of a piece of text. Texts with similar meanings
# produce similar vectors. This is how we search by meaning
# instead of by keywords.
#
# Supports three providers:
#   gemini / azure  -> cloud APIs (need an API key)
#   ollama          -> local model running on your machine
# Pick one with EMBEDDING_PROVIDER in .env (defaults to LLM_PROVIDER).
#
# IMPORTANT: Vectors from different models can't be compared.
# After switching EMBEDDING_PROVIDER or the model, re-ingest with
# POST /ingest?fresh=true. Distances also shift between models,
# so the confidence thresholds may need retuning.
#
# EXAMPLE:
#   embed_text("How many vacation days?")
#   -> [0.023, -0.041, 0.078, ...]  (hundreds of numbers)
#
#   embed_text("What is the annual leave policy?")
#   -> [0.025, -0.039, 0.081, ...]  (similar numbers!)
#
# The similarity between these vectors is what lets us find
# relevant chunks even when the exact words don't match.
# ============================================================

import httpx

from app.config import (
    EMBEDDING_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    OLLAMA_BASE_URL,
    OLLAMA_EMBEDDING_MODEL,
)


# Purpose:
# Embeds a single text string into a vector. Used for queries at search time.
def embed_text(text: str) -> list[float]:
    """Embed a single piece of text into a vector."""
    return embed_texts([text])[0]


# Purpose:
# Embeds a batch of texts into vectors. Used for chunks at ingestion time.
def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts into vectors. Returns one vector per input text."""
    if EMBEDDING_PROVIDER == "ollama":
        return _embed_ollama(texts)
    if EMBEDDING_PROVIDER == "gemini":
        return _embed_gemini(texts)
    return _embed_azure(texts)


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Google Gemini."""
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=texts,
    )

    return [embedding.values for embedding in result.embeddings]


def _embed_azure(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Azure OpenAI."""
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )

    response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        input=texts,
    )

    return [item.embedding for item in response.data]


# Purpose:
# Embeds texts with a model running on your own machine via Ollama.
# No API key, no cost, and the text never leaves your laptop.
def _embed_ollama(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using a local model served by Ollama."""
    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": OLLAMA_EMBEDDING_MODEL, "input": texts},
            timeout=120.0,
        )
    except httpx.ConnectError:
        raise RuntimeError(
            f"Can't reach Ollama at {OLLAMA_BASE_URL}. "
            "Is it installed and running? (https://ollama.com)"
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"Model '{OLLAMA_EMBEDDING_MODEL}' isn't downloaded yet. "
            f"Run: ollama pull {OLLAMA_EMBEDDING_MODEL}"
        )
    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    return response.json()["embeddings"]
