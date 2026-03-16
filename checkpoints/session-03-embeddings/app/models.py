# ============================================================
# Pydantic models — Session 3
# ============================================================
# Added: SearchResult and SearchResponse for the /search endpoint
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


# --- Session 3 models ---

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


class StoredChunkInfo(BaseModel):
    """Detailed info about a stored chunk — for the /store/inspect endpoint."""
    id: str
    text: str
    source: str
    chunk_index: int
    embedding_preview: list[float] | None = None
    embedding_dimensions: int | None = None


class StoreInspectResponse(BaseModel):
    """Response from the /store/inspect endpoint."""
    total_stored: int
    sources: list[str]
    chunks: list[StoredChunkInfo]


class EmbedRequest(BaseModel):
    """Request to embed texts for exploration."""
    texts: list[str]


class EmbedResponse(BaseModel):
    """Response with pairwise distances between embedded texts."""
    distances: dict[str, float]
    dimensions: int


# --- Session 3 models ---

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
