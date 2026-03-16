# ============================================================
# Embedder — turns text into vector embeddings
# ============================================================
# An embedding is a list of numbers (a vector) that captures
# the MEANING of a piece of text. Texts with similar meanings
# produce similar vectors. This is how we search by meaning
# instead of by keywords.
#
# Supports both Gemini and Azure OpenAI embeddings.
#
# EXAMPLE:
#   embed_text("How many vacation days?")
#   → [0.023, -0.041, 0.078, ...]  (hundreds of numbers)
#
#   embed_text("What is the annual leave policy?")
#   → [0.025, -0.039, 0.081, ...]  (similar numbers!)
#
# The similarity between these vectors is what lets us find
# relevant chunks even when the exact words don't match.
# ============================================================

from app.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
)


def embed_text(text: str) -> list[float]:
    """
    Embed a single piece of text into a vector.

    Use this for embedding user queries at search time.
    """
    return embed_texts([text])[0]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts into vectors.

    Use this for embedding chunks at ingestion time.
    Returns one vector per input text, in the same order.
    """
    if LLM_PROVIDER == "gemini":
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
