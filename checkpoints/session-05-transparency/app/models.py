# ============================================================
# Pydantic models — Session 5
# ============================================================
# Added: confidence field, QueryResponse updated,
#        no-result and weak-evidence support
# ============================================================

from pydantic import BaseModel


# --- Session 1 models (unchanged) ---

class Question(BaseModel):
    """A user question sent to the assistant."""
    question: str


class Answer(BaseModel):
    """A plain LLM answer — may or may not be grounded in context."""
    answer: str
    model: str
    grounded: bool = False


# --- Session 2 models (unchanged) ---

class ChunkInfo(BaseModel):
    """Metadata about a single chunk — used in API responses."""
    text: str
    source: str
    chunk_index: int


class IngestResponse(BaseModel):
    """Response from the /ingest endpoint — summarizes what was loaded."""
    files_processed: int
    total_chunks: int
    chunks_stored: int
    chunks: list[ChunkInfo]


# --- Session 3 models (unchanged) ---

class SearchResult(BaseModel):
    """A single search result from the vector store."""
    text: str
    source: str
    chunk_index: int
    distance: float


class SearchResponse(BaseModel):
    """Response from the /search endpoint."""
    query: str
    results: list[SearchResult]
    total_results: int


class EmbedRequest(BaseModel):
    """Request to embed texts for exploration."""
    texts: list[str]


class EmbedResponse(BaseModel):
    """Response with pairwise distances between embedded texts."""
    distances: dict[str, float]
    dimensions: int


# --- Session 4 models ---

class SourceInfo(BaseModel):
    """A source chunk that contributed to a RAG answer."""
    source: str
    text: str
    distance: float = 0.0


class QueryRequest(BaseModel):
    """A question to be answered using RAG."""
    question: str


# --- Session 5 models ---

class QueryResponse(BaseModel):
    """
    A RAG-grounded answer with source attribution and confidence.

    Confidence levels:
      - "high"  → strong match, answer is well-supported
      - "medium" → reasonable match, answer is likely correct
      - "low"  → weak evidence, answer may be unreliable
      - "none" → no relevant documents found
    """
    question: str
    answer: str
    model: str
    sources: list[SourceInfo]
    chunks_used: int
    confidence: str = "high"
    no_result: bool = False
