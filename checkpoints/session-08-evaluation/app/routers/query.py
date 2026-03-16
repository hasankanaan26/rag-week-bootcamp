# ============================================================
# Router: /query — RAG endpoint with query rewriting (Session 7)
# ============================================================
# Updated from Session 6 to add query rewriting and source filtering.
# Query rewriting uses the LLM to rephrase vague questions into
# specific search queries with synonyms and formal terms.
# Source filtering restricts retrieval to a specific document.
#
# TEACHING POINT:
#   Try the same question with rewrite=false then rewrite=true.
#   Watch the logs to see the rewritten query and compare results.
# ============================================================

import logging
import uuid
from fastapi import APIRouter, Query
from app.models import QueryRequest, QueryResponse, SourceInfo
from app.llm import call_llm, get_model_name
from app.rag.retriever import retrieve, score_confidence, is_no_result
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT

logger = logging.getLogger("rag.query")
router = APIRouter(prefix="/query", tags=["RAG Q&A"])

NO_RESULT_ANSWER = (
    "I don't have information about that in the knowledge base. "
    "Try asking about Acme Corp policies like leave, expenses, "
    "coding standards, or remote work."
)


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


@router.post("", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    top_k: int = Query(default=3, description="Number of chunks to retrieve."),
    prompt_style: str = Query(
        default="default",
        description="Prompt style: 'default' (strict grounding) or 'minimal' (loose, may hallucinate).",
    ),
    rewrite: bool = Query(
        default=False,
        description="If true, rewrite the query for better retrieval.",
    ),
    source: str | None = Query(
        default=None,
        description="Filter retrieval to a specific source file (e.g. 'leave-policy.md').",
    ),
    high_threshold: float | None = Query(
        default=None,
        description="Override high-confidence distance threshold.",
    ),
    low_threshold: float | None = Query(
        default=None,
        description="Override low-confidence distance threshold.",
    ),
    no_result_threshold: float | None = Query(
        default=None,
        description="Override no-result distance threshold.",
    ),
):
    """
    Answer a question using RAG with confidence scoring, logging, request tracing,
    optional query rewriting, and source filtering.
    """
    request_id = uuid.uuid4().hex[:8]
    logger.info("req_%s | Query received | question=%r | rewrite=%s | source=%s",
                request_id, request.question, rewrite, source)

    # Step 1: Build metadata filter
    where = {"source": source} if source else None

    # Step 2: Retrieve (with optional rewriting)
    chunks, rewritten_query = retrieve(
        query=request.question, top_k=top_k, rewrite=rewrite, where=where,
    )
    if rewritten_query:
        logger.info("req_%s | Rewritten query: %r", request_id, rewritten_query)

    if chunks:
        distances = [c["distance"] for c in chunks]
        sources = [c["source"] for c in chunks]
        logger.info(
            "req_%s | Retrieved %d chunks | best_distance=%.3f | worst_distance=%.3f | sources=%s",
            request_id, len(chunks), min(distances), max(distances), sources,
        )
    else:
        logger.info("req_%s | Retrieved 0 chunks | store may be empty", request_id)

    # Step 3: No-result check
    if is_no_result(chunks, no_result_threshold=no_result_threshold):
        logger.info("req_%s | Result: NO_RESULT | confidence=none", request_id)
        return QueryResponse(
            question=request.question,
            answer=NO_RESULT_ANSWER,
            model=get_model_name(),
            sources=[],
            chunks_used=0,
            confidence="none",
            no_result=True,
            request_id=request_id,
            rewritten_query=rewritten_query,
        )

    # Step 4: Confidence
    confidence = score_confidence(
        chunks,
        high_threshold=high_threshold,
        low_threshold=low_threshold,
    )
    if confidence == "low":
        logger.warning("req_%s | Result: WEAK_EVIDENCE | confidence=low", request_id)
    else:
        logger.info("req_%s | Result: OK | confidence=%s", request_id, confidence)

    # Step 5: Build context and call LLM
    context = build_context(chunks)
    if prompt_style == "minimal":
        system_prompt = RAG_MINIMAL_PROMPT.format(context=context)
    else:
        system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    answer_text = call_llm(
        user_prompt=request.question,
        system_prompt=system_prompt,
    )

    logger.info("req_%s | LLM responded | prompt_style=%s | answer_length=%d chars",
                request_id, prompt_style, len(answer_text))

    # Step 6: Build response
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
        confidence=confidence,
        no_result=False,
        request_id=request_id,
        rewritten_query=rewritten_query,
    )
