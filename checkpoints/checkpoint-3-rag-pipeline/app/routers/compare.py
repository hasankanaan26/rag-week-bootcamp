# ============================================================
# Router: /compare — RAG vs plain LLM side-by-side
# ============================================================
# Runs the same question through both paths:
#   1. Plain LLM (no retrieval, no grounding)
#   2. RAG pipeline (retrieve -> inject -> generate)
#
# DEMO QUESTIONS:
#   "How many vacation days do I get?"
#       -> Plain: invents a number | RAG: cites leave policy
#   "What is the capital of France?"
#       -> Plain: correct | RAG: may struggle (not in docs)
#   "What about time off?"
#       -> Plain: generic | RAG: finds policy
# ============================================================

import logging
import uuid
from fastapi import APIRouter, Query
from app.models import (
    CompareRequest,
    CompareResponse,
    PlainResult,
    RAGResult,
    SourceInfo,
)
from app.llm import call_llm, get_model_name
from app.rag.retriever import retrieve
from app.prompts.plain_answer import PLAIN_SYSTEM_PROMPT
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT

logger = logging.getLogger("rag.compare")
router = APIRouter(prefix="/compare", tags=["Comparison"])


# Purpose:
# Formats retrieved chunks into a context block for the RAG prompt.
def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a text block for the prompt."""
    context_parts = []
    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]
        context_parts.append(f"[Source: {source}]\n{text}")
    return "\n\n".join(context_parts)


# Purpose:
# Runs the same question through both plain LLM and RAG, returning
# both answers side-by-side so students can compare.
@router.post("", response_model=CompareResponse)
def compare_answers(
    request: CompareRequest,
    top_k: int = Query(default=3, description="Number of chunks to retrieve for RAG."),
):
    """Run the same question through plain LLM and RAG, return both answers."""
    question = request.question
    request_id = uuid.uuid4().hex[:8]
    logger.info("req_%s | Compare request | question=%r", request_id, question)

    # --- Plain LLM path ---
    logger.info("req_%s | Running plain LLM (no retrieval)", request_id)
    plain_answer = call_llm(
        user_prompt=question,
        system_prompt=PLAIN_SYSTEM_PROMPT,
    )
    logger.info("req_%s | Plain LLM responded | answer_length=%d chars", request_id, len(plain_answer))

    plain_result = PlainResult(answer=plain_answer, model=get_model_name())

    # --- RAG path ---
    logger.info("req_%s | Running RAG pipeline", request_id)
    chunks = retrieve(query=question, top_k=top_k)

    if chunks:
        distances = [c["distance"] for c in chunks]
        logger.info(
            "req_%s | RAG retrieved %d chunks | best_distance=%.3f | sources=%s",
            request_id, len(chunks), min(distances),
            [c["source"] for c in chunks],
        )

    context = build_context(chunks)
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    rag_answer = call_llm(user_prompt=question, system_prompt=system_prompt)

    logger.info(
        "req_%s | RAG LLM responded | answer_length=%d chars",
        request_id, len(rag_answer),
    )

    sources = [
        SourceInfo(source=c["source"], text=c["text"], distance=c.get("distance", 0))
        for c in chunks
    ]

    rag_result = RAGResult(
        answer=rag_answer,
        model=get_model_name(),
        sources=sources,
        chunks_used=len(chunks),
    )

    note = (
        "The RAG answer is grounded in company documents. "
        "The plain LLM answer uses general training data. "
        "Compare them — the RAG answer should be more specific and accurate."
    )

    logger.info("req_%s | Compare complete", request_id)

    return CompareResponse(
        question=question,
        rag=rag_result,
        plain=plain_result,
        note=note,
        request_id=request_id,
    )
