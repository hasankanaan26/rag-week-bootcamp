# ============================================================
# Pydantic models — Base scaffold
# ============================================================

from pydantic import BaseModel


class Question(BaseModel):
    """A user question sent to the assistant."""
    question: str
