# ============================================================
# Router: /query — The RAG endpoint
# ============================================================
# This is the core of the RAG application. The full flow:
#
#   User question
#        ↓
#   retrieve(question)       → find relevant chunks
#        ↓
#   build prompt(chunks)     → assemble context into prompt
#        ↓
#   call_llm(prompt)         → get grounded answer
#        ↓
#   Return answer + sources
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
#
# INTENTIONALLY WEAK QUERY:
#   "What about time off?"   → vague, may retrieve mixed results
#   Notice how the answer quality depends on retrieval quality.
# ============================================================

from fastapi import APIRouter, Query
from app.models import QueryRequest, QueryResponse, SourceInfo
from app.llm import call_llm, get_model_name
from app.rag.retriever import retrieve
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT

router = APIRouter(prefix="/query", tags=["RAG Q&A"])


def build_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a text block for the prompt.

    Each chunk is labeled with its source file so the LLM
    can reference where the information came from.
    """
    context_parts = []
    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]
        context_parts.append(f"[Source: {source}]\n{text}")

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
):
    """
    Answer a question using RAG: retrieve relevant context, then generate.

    Try prompt_style=minimal to see how a weaker prompt affects answer quality.
    """
    # Step 1: Retrieve relevant chunks
    chunks = retrieve(query=request.question, top_k=top_k)

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

    # Step 5: Build the response with sources
    sources = [
        SourceInfo(source=c["source"], text=c["text"])
        for c in chunks
    ]

    return QueryResponse(
        question=request.question,
        answer=answer_text,
        model=get_model_name(),
        sources=sources,
        chunks_used=len(chunks),
    )
