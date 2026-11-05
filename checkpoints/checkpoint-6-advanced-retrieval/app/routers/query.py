# ============================================================
# Router: /query — RAG endpoint, as a user, as of a date
# ============================================================
# Checkpoint 4: confidence, no-result detection, doc-type routing.
# Checkpoint 5: user (permissions), as_of (versions), provenance on
#   every context block.
# Added in Checkpoint 6:
#   - strategy: which retrieval fills the context (default "routed",
#     the winner on the golden set; see compare.py). "dense" keeps
#     Checkpoint 5's path, doc-type routing included.
#   - the no-result guard still uses the dense best distance, so the
#     safety check does not change when the strategy does.
#
# DEMO QUESTIONS (Monday, after a sync):
#   "How many reviewers does a change to the billing code need?"
#       strategy=dense -> "at least one" (grounded, and wrong)   routed -> two
#   "Who works in our San Francisco office?"
#       strategy=dense -> five of six people   routed -> all six
# ============================================================

import logging
import uuid

from fastapi import APIRouter, HTTPException, Query

from app.llm import call_llm, get_model_name
from app.models import DocFilterInfo, QueryRequest, QueryResponse, SourceInfo
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT
from app.prompts.rag_answer_minimal import RAG_MINIMAL_PROMPT
from app.rag.doc_types import DOC_TYPES
from app.rag.retriever import is_no_result, resolve_user, retrieve, retrieve_with_doc_filter, score_confidence
from app.rag.strategies import STRATEGIES, run
from app.routers.search import to_result

logger = logging.getLogger("rag.query")
router = APIRouter(prefix="/query", tags=["RAG Q&A"])

DOC_FILTER_PATTERN = "^(auto|off|" + "|".join(DOC_TYPES) + ")$"

NO_RESULT_ANSWER = (
    "I don't have information about that in the documents you can access. "
    "Try asking about Acme Corp policies like leave, expenses, "
    "coding standards, or remote work."
)


# Purpose:
# Label every chunk with where it came from before the LLM sees it.
def build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        r = to_result(c)
        parts.append(
            f"[{r.title} | v{r.version} | effective {r.effective_from} | {r.status} | "
            f"section: {r.section}]\n{c['text']}"
        )
    return "\n\n".join(parts)


def to_source(c: dict) -> SourceInfo:
    r = to_result(c)
    return SourceInfo(**r.model_dump(exclude={"chunk_index"}), doc_type=c.get("doc_type", ""))


@router.post("", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    user: str | None = Query(default=None, description="Who is asking: intern, eng-manager, hr-partner, finance-lead, sales-rep."),
    as_of: str | None = Query(default=None, description="YYYY-MM-DD: answer from the documents in force that day."),
    strategy: str = Query(default="routed", description="Retrieval strategy: " + ", ".join(STRATEGIES)),
    top_k: int = Query(default=5, description="Number of chunks to retrieve."),
    prompt_style: str = Query(default="default", description="'default' (strict) or 'minimal' (loose)."),
    high_threshold: float | None = Query(default=None, description="Override high-confidence distance threshold."),
    low_threshold: float | None = Query(default=None, description="Override low-confidence distance threshold."),
    no_result_threshold: float | None = Query(default=None, description="Override no-result distance threshold."),
    doc_filter: str = Query(default="off", pattern=DOC_FILTER_PATTERN,
                            description="Only used with strategy=dense: 'auto', 'off', or a doc type."),
):
    """Answer a question with RAG, as one user, with the chosen retrieval strategy."""
    request_id = uuid.uuid4().hex[:8]
    filter_info = DocFilterInfo(mode=doc_filter)
    try:
        user, groups = resolve_user(user)
        # The safety check: the best dense distance decides "no result", whatever the strategy.
        guard = retrieve(request.question, user=user, top_k=1, as_of=as_of)
        if strategy == "dense":
            retrieval = retrieve_with_doc_filter(
                query=request.question, user=user, top_k=top_k, filter_mode=doc_filter,
                no_result_threshold=no_result_threshold, as_of=as_of,
            )
            chunks = retrieval["chunks"]
            filter_info = DocFilterInfo(
                mode=doc_filter, doc_type=retrieval["doc_type"], picked_by=retrieval["picked_by"],
                classifier_reply=retrieval["classifier_reply"], fallback_used=retrieval["fallback_used"],
                filtered_best_distance=retrieval["filtered_best_distance"],
            )
        else:
            chunks = run(strategy, request.question, user=user, k=top_k, as_of=as_of).chunks
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    logger.info("req_%s | user=%s strategy=%s | %d chunks | docs=%s", request_id, user, strategy,
                len(chunks), [c.get("doc_id") for c in chunks])

    if not chunks or is_no_result(guard, no_result_threshold=no_result_threshold):
        return QueryResponse(
            question=request.question, answer=NO_RESULT_ANSWER, model=get_model_name(),
            user=user, as_of=as_of, sources=[], chunks_used=0, confidence="none",
            no_result=True, request_id=request_id, doc_filter=filter_info,
        )

    confidence = score_confidence(guard, high_threshold=high_threshold, low_threshold=low_threshold)
    template = RAG_MINIMAL_PROMPT if prompt_style == "minimal" else RAG_SYSTEM_PROMPT
    answer_text = call_llm(user_prompt=request.question, system_prompt=template.format(context=build_context(chunks)))

    return QueryResponse(
        question=request.question, answer=answer_text, model=get_model_name(), user=user, as_of=as_of,
        sources=[to_source(c) for c in chunks], chunks_used=len(chunks), confidence=confidence,
        no_result=False, request_id=request_id, doc_filter=filter_info,
    )
