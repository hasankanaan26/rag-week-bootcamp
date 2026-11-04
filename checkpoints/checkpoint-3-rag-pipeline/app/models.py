# ============================================================
# Pydantic models — Checkpoint 3
# ============================================================
# Added: SourceInfo, QueryRequest, QueryResponse,
#        CompareRequest, CompareResponse, PlainResult, RAGResult
# ============================================================

from pydantic import BaseModel


class Question(BaseModel):
    """A user question sent to the assistant."""
    question: str


class Answer(BaseModel):
    """A plain LLM answer — may or may not be grounded in context."""
    answer: str
    model: str
    grounded: bool = False


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
    """Detailed info about a stored chunk."""
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


class SourceInfo(BaseModel):
    """A source chunk that contributed to a RAG answer."""
    source: str
    text: str
    distance: float = 0.0


class QueryRequest(BaseModel):
    """A question to be answered using RAG."""
    question: str


class QueryResponse(BaseModel):
    """A RAG-grounded answer with source attribution."""
    question: str
    answer: str
    model: str
    sources: list[SourceInfo]
    chunks_used: int
    request_id: str = ""


class CompareRequest(BaseModel):
    """A question to compare RAG vs plain LLM answers."""
    question: str


class PlainResult(BaseModel):
    """The plain (non-RAG) LLM answer."""
    answer: str
    model: str


class RAGResult(BaseModel):
    """The RAG-grounded answer."""
    answer: str
    model: str
    sources: list[SourceInfo]
    chunks_used: int


class CompareResponse(BaseModel):
    """Side-by-side comparison of RAG vs plain LLM for the same question."""
    question: str
    rag: RAGResult
    plain: PlainResult
    note: str
    request_id: str = ""
