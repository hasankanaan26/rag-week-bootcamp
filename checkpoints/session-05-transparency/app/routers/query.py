# ============================================================
# Router: /query — RAG endpoint with transparency (Session 5)
# ============================================================
# Updated from Session 4 to add:
#   - Confidence scoring (high/medium/low/none)
#   - No-result handling ("I don't have that information")
#   - Weak-evidence warnings in the answer
#   - Distance scores in source attribution
#
# DEMO QUESTIONS:
#   "How many vacation days do I get?"   → high confidence
#   "What is our Git branching strategy?" → high confidence
#   "What about time off?"               → medium (vague query)
#   "Tell me about quantum physics"      → no result (out of domain)
#   "What are the rules?"                → low confidence (too broad)
# ============================================================

from fastapi import APIRouter, Query
from app.models import QueryRequest, QueryResponse, SourceInfo
from app.llm import call_llm, get_model_name
from app.rag.retriever import retrieve, score_confidence, is_no_result
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT

router = APIRouter(prefix="/query", tags=["RAG Q&A"])

# Answer returned when retrieval finds nothing relevant
NO_RESULT_ANSWER = (
    "I don't have information about that in the knowledge base. "
    "Try asking about Acme Corp policies like leave, expenses, "
    "coding standards, or remote work."
)


def build_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a text block for the prompt.

    Each chunk is labeled with its source file and distance score,
    so the LLM knows which information is most relevant.
    """
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
    top_k: int = Query(
        default=3,
        description="Number of chunks to retrieve.",
    ),
    prompt_style: str = Query(
        default="default",
        description="Prompt style: 'default' (strict grounding) or 'minimal' (loose, may hallucinate).",
    ),
    high_threshold: float | None = Query(
        default=None,
        description="Override high-confidence distance threshold (default from config).",
    ),
    low_threshold: float | None = Query(
        default=None,
        description="Override low-confidence distance threshold (default from config).",
    ),
    no_result_threshold: float | None = Query(
        default=None,
        description="Override no-result distance threshold (default from config).",
    ),
):
    """
    Answer a question using RAG with confidence scoring.

    Supports prompt A/B testing via prompt_style and interactive
    threshold tuning via the threshold override parameters.
    """
    # Step 1: Retrieve relevant chunks
    chunks = retrieve(query=request.question, top_k=top_k)

    # Step 2: Check for no-result (nothing relevant found)
    if is_no_result(chunks, no_result_threshold=no_result_threshold):
        return QueryResponse(
            question=request.question,
            answer=NO_RESULT_ANSWER,
            model=get_model_name(),
            sources=[],
            chunks_used=0,
            confidence="none",
            no_result=True,
        )

    # Step 3: Score confidence based on retrieval distances
    confidence = score_confidence(
        chunks,
        high_threshold=high_threshold,
        low_threshold=low_threshold,
    )

    # Step 4: Build the context block from retrieved chunks
    context = build_context(chunks)

    # Step 5: Select prompt based on style
    if prompt_style == "minimal":
        system_prompt = RAG_MINIMAL_PROMPT.format(context=context)
    else:
        system_prompt = RAG_SYSTEM_PROMPT.format(context=context)

    # Step 6: Call the LLM with the grounded prompt
    answer_text = call_llm(
        user_prompt=request.question,
        system_prompt=system_prompt,
    )

    # Step 7: Build the response with sources and confidence
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
    )
