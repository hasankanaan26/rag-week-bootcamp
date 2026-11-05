# ============================================================
# Router: /retrieve — try any retrieval strategy (Checkpoint 6)
# ============================================================
# Same filters as /search (who is asking, as of when), plus:
#   strategy  dense | bm25 | hybrid | rerank | hybrid_rerank |
#             parent | hyde | multi_query | routed
# Returns the chunks AND the trace: what the strategy did, how long it
# took, how many LLM calls it made. No answer is generated.
#
# DEMO:
#   q="How many reviewers does a change to the billing code need?"
#       strategy=dense -> misses   strategy=hybrid_rerank -> handbook first
#   q="Who works remotely?"
#       strategy=dense -> remote-work policy   strategy=routed -> 3 people
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models import SearchResult
from app.rag.retriever import resolve_user
from app.rag.strategies import STRATEGIES, run
from app.routers.search import to_result

router = APIRouter(prefix="/retrieve", tags=["Retrieval strategies"])


class RetrieveResponse(BaseModel):
    query: str
    strategy: str
    user: str
    trace: list[str]
    ms: float
    llm_calls: int
    results: list[SearchResult]


@router.get("", response_model=RetrieveResponse)
def retrieve_with(
    q: str = Query(description="The question."),
    strategy: str = Query(default="routed", description="One of: " + ", ".join(STRATEGIES)),
    user: str | None = Query(default=None, description="Who is asking (default: intern)."),
    k: int = Query(default=5, ge=1, le=20),
    as_of: str | None = Query(default=None, description="YYYY-MM-DD"),
):
    try:
        user, _ = resolve_user(user)
        result = run(strategy, q, user=user, k=k, as_of=as_of)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return RetrieveResponse(query=q, strategy=strategy, user=user, trace=result.trace, ms=round(result.ms, 1),
                            llm_calls=result.llm_calls, results=[to_result(c) for c in result.chunks])
