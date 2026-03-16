# ============================================================
# Pydantic models — Session 1
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
