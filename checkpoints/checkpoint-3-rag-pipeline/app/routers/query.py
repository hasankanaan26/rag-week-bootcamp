# ============================================================
# Router: /query — The RAG endpoint with logging
# ============================================================
# This is the core of the RAG application. The full flow:
#
#   User question
#        |
#   retrieve(question)       -> find relevant chunks
#        |
#   build prompt(chunks)     -> assemble context into prompt
#        |
#   call_llm(prompt)         -> get grounded answer
#        |
#   Return answer + sources
#
# Includes structured logging so you can see exactly what happens
# inside the pipeline. Tail the terminal while sending queries.
#
# DEMO QUESTIONS TO TRY:
#   "How many vacation days do I get?"
#   "What is our Git branching strategy?"
#   "Can I expense a standing desk?"
#   "What are the core working hours?"
#
# COMPARE with /ask (plain):
#   Same question, different answers. /query uses documents.
#   /ask uses the LLM's general knowledge (and often hallucinates).
# ============================================================

import logging
import uuid
from fastapi import APIRouter, Query
from app.models import QueryRequest, QueryResponse, SourceInfo
from app.llm import call_llm, get_model_name
from app.rag.retriever import retrieve
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT

logger = logging.getLogger("rag.query")
router = APIRouter(prefix="/query", tags=["RAG Q&A"])


# Purpose:
# Formats retrieved chunks into a labeled text block that gets injected
# into the RAG prompt as context for the LLM.
def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a text block for the prompt."""
    context_parts = []
    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]
        distance = chunk.get("distance", 0)
        context_parts.append(
            f"[Source: {source} | Relevance score: {distance:.3f}]\n{text}"
        )
    return "\n\n".join(context_parts)


# Purpose:
# The full RAG endpoint: retrieve chunks, build prompt, call LLM, return answer.
# Logs every step so students can see what happens in the terminal.
@router.post("", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    top_k: int = Query(default=3, description="Number of chunks to retrieve."),
    prompt_style: str = Query(
        default="default",
        description="Prompt style: 'default' (strict grounding) or 'minimal' (loose, may hallucinate).",
    ),
):
    """
    Answer a question using RAG: retrieve relevant context, then generate.

    Tail the terminal logs to see retrieval details in real time.
    """
    request_id = uuid.uuid4().hex[:8]
    logger.info("req_%s | Query received | question=%r", request_id, request.question)

    # Step 1: Retrieve relevant chunks
    chunks = retrieve(query=request.question, top_k=top_k)

    if chunks:
        distances = [c["distance"] for c in chunks]
        sources = [c["source"] for c in chunks]
        logger.info(
            "req_%s | Retrieved %d chunks | best_distance=%.3f | worst_distance=%.3f | sources=%s",
            request_id, len(chunks), min(distances), max(distances), sources,
        )
    else:
        logger.info("req_%s | Retrieved 0 chunks | store may be empty", request_id)

    # Step 2: Build the context block from retrieved chunks
    context = build_context(chunks)

    # Step 3: Select prompt based on style
    if prompt_style == "minimal":
        system_prompt = RAG_MINIMAL_PROMPT.format(context=context)
    else:
        system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    # Step 4: Call the LLM with the grounded prompt
    answer_text = call_llm(
        user_prompt=request.question,
        system_prompt=system_prompt,
    )

    logger.info(
        "req_%s | LLM responded | prompt_style=%s | answer_length=%d chars",
        request_id, prompt_style, len(answer_text),
    )

    # Step 5: Build the response with sources
    sources = [
        SourceInfo(
            source=c["source"],
            text=c["text"],
            distance=c.get("distance", 0),
        )
        for c in chunks
    ]

    return QueryResponse(
        question=request.question,
        answer=answer_text,
        model=get_model_name(),
        sources=sources,
        chunks_used=len(chunks),
        request_id=request_id,
    )
