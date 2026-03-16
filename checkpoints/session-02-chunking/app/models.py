# ============================================================
# Pydantic models — Session 2
# ============================================================
# Added: ChunkInfo and IngestResponse for the /ingest endpoint
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


# --- Session 2 models ---

class ChunkInfo(BaseModel):
    """Metadata about a single chunk — used in API responses."""
    text: str
    source: str
    chunk_index: int


class IngestResponse(BaseModel):
    """Response from the /ingest endpoint — summarizes what was loaded."""
    files_processed: int
    total_chunks: int
    chunks: list[ChunkInfo]
