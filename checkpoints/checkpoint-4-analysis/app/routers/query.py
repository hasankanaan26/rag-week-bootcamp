# ============================================================
# Router: /query — RAG endpoint with confidence and logging
# ============================================================
# Updated from Checkpoint 3 to add:
#   - Confidence scoring (high/medium/low/none)
#   - No-result handling ("I don't have that information")
#   - Weak-evidence warnings
#   - Distance scores in source attribution
#   - Threshold override parameters for live experimentation
#   - Doc-type filter: the LLM classifies the question first, retrieval
#     searches only that doc type, and falls back to all documents
#     when the filtered search finds nothing useful
#
# FILTER DEMO (doc_filter param):
#   auto        -> LLM picks the doc type (default)
#   off         -> plain semantic search over everything
#   engineering -> force a type; ask about vacation days to see the fallback
#
# DEMO QUESTIONS:
#   "How many vacation days do I get?"   -> high confidence
#   "What is our Git branching strategy?" -> high confidence
#   "What about time off?"               -> medium (vague query)
#   "Tell me about quantum physics"      -> no result (out of domain)
#   "What are the rules?"                -> low confidence (too broad)
# ============================================================

import logging
import uuid
from fastapi import APIRouter, Query
from app.models import QueryRequest, QueryResponse, SourceInfo, DocFilterInfo
from app.llm import call_llm, get_model_name
from app.rag.doc_types import DOC_TYPES
from app.rag.retriever import retrieve_with_doc_filter, score_confidence, is_no_result
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT

logger = logging.getLogger("rag.query")
router = APIRouter(prefix="/query", tags=["RAG Q&A"])

# Allowed values for doc_filter: auto, off, or one of the doc types
DOC_FILTER_PATTERN = "^(auto|off|" + "|".join(DOC_TYPES) + ")$"

NO_RESULT_ANSWER = (
    "I don't have information about that in the knowledge base. "
    "Try asking about Acme Corp policies like leave, expenses, "
    "coding standards, or remote work."
)


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
# The full RAG endpoint with confidence scoring, no-result detection,
# and structured logging. Logs every step for teaching visibility.
@router.post("", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    top_k: int = Query(default=3, description="Number of chunks to retrieve."),
    prompt_style: str = Query(
        default="default",
        description="Prompt style: 'default' (strict grounding) or 'minimal' (loose, may hallucinate).",
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
    doc_filter: str = Query(
        default="auto",
        pattern=DOC_FILTER_PATTERN,
        description="'auto' (LLM picks a doc type), 'off', or a doc type: " + ", ".join(DOC_TYPES),
    ),
):
    """
    Answer a question using RAG with confidence scoring, logging, and request tracing.
    """
    request_id = uuid.uuid4().hex[:8]
    logger.info("req_%s | Query received | question=%r", request_id, request.question)

    # Step 1: Retrieve (classify -> filtered search -> fallback if needed)
    retrieval = retrieve_with_doc_filter(
        query=request.question,
        top_k=top_k,
        filter_mode=doc_filter,
        no_result_threshold=no_result_threshold,
    )
    chunks = retrieval["chunks"]
    filter_info = DocFilterInfo(
        mode=doc_filter,
        doc_type=retrieval["doc_type"],
        picked_by=retrieval["picked_by"],
        classifier_reply=retrieval["classifier_reply"],
        fallback_used=retrieval["fallback_used"],
        filtered_best_distance=retrieval["filtered_best_distance"],
    )
    logger.info(
        "req_%s | Doc filter | mode=%s | classifier_reply=%r | doc_type=%s | picked_by=%s | fallback=%s",
        request_id, doc_filter, filter_info.classifier_reply, filter_info.doc_type,
        filter_info.picked_by, filter_info.fallback_used,
    )

    if chunks:
        distances = [c["distance"] for c in chunks]
        sources = [c["source"] for c in chunks]
        logger.info(
            "req_%s | Retrieved %d chunks | best_distance=%.3f | worst_distance=%.3f | sources=%s",
            request_id, len(chunks), min(distances), max(distances), sources,
        )
    else:
        logger.info("req_%s | Retrieved 0 chunks | store may be empty", request_id)

    # Step 2: No-result check
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
            doc_filter=filter_info,
        )

    # Step 3: Confidence
    confidence = score_confidence(
        chunks,
        high_threshold=high_threshold,
        low_threshold=low_threshold,
    )
    if confidence == "low":
        logger.warning("req_%s | Result: WEAK_EVIDENCE | confidence=low", request_id)
    else:
        logger.info("req_%s | Result: OK | confidence=%s", request_id, confidence)

    # Step 4: Build context and call LLM
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

    # Step 5: Build response
    sources = [
        SourceInfo(
            source=c["source"],
            text=c["text"],
            distance=c.get("distance", 0),
            doc_type=c.get("doc_type", ""),
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
        doc_filter=filter_info,
    )
