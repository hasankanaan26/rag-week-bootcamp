# ============================================================
# Strategies — nine ways to fill the top 5 (Checkpoint 6)
# ============================================================
# One contract for all of them:
#
#   run(strategy, question, user, k, as_of) -> Result(chunks, trace, llm_calls, ms)
#
# so compare.py can measure them side by side on the same questions.
# Every strategy searches INSIDE checkpoint 5's access filter: who may
# read it, and which version is in force. Retrieval tricks never get
# to bypass permissions.
#
#   dense          checkpoint 5: embed the question, nearest chunks
#   bm25           keyword scores (exact tokens: IT-4112, Zustand)
#   hybrid         dense + bm25, fused with reciprocal rank fusion
#   rerank         dense top 20, re-ordered by a cross-encoder
#   hybrid_rerank  hybrid top 20, re-ordered by a cross-encoder
#   parent         search sentence-sized children, return their sections
#   hyde           search with an LLM-written hypothetical answer
#   multi_query    three LLM rewrites + the question, fused
#   routed         aggregation questions -> structured lookup, else hybrid_rerank
#
# Which one wins is not a matter of taste. compare.py measures it.
# ============================================================

import time
from dataclasses import dataclass, field

from app.config import CANDIDATES
from app.llm import STATS, cached_call_llm
from app.prompts.query_rewrite import HYDE_PROMPT, MULTI_QUERY_PROMPT
from app.rag import catalog, children, reranker, router
from app.rag.bm25 import BM25, rrf
from app.rag.embedder import embed_text
from app.rag.retriever import access_filter, check_date, resolve_user
from app.rag.store_chroma import get_client, search


@dataclass
class Result:
    strategy: str
    chunks: list[dict]
    trace: list[str] = field(default_factory=list)
    llm_calls: int = 0
    ms: float = 0.0


# ---- helpers ----

def _where(user: str | None, as_of: str | None) -> dict:
    _, groups = resolve_user(user)
    return access_filter(groups, check_date(as_of))


def _allowed(where: dict) -> list[dict]:
    """Every chunk this user may read (for keyword search and lookups)."""
    data = get_client().get_collection(catalog.active_name()).get(where=where, include=["documents", "metadatas"])
    return [{**m, "id": i, "text": t} for i, t, m in zip(data["ids"], data["documents"], data["metadatas"])]


def _by_ids(ids: list[str]) -> list[dict]:
    if not ids:
        return []
    data = get_client().get_collection(catalog.active_name()).get(ids=ids, include=["documents", "metadatas"])
    found = {i: {**m, "id": i, "text": t} for i, t, m in zip(data["ids"], data["documents"], data["metadatas"])}
    return [found[i] for i in ids if i in found]


def _dense(question: str, where: dict, n: int) -> list[dict]:
    return search(embed_text(question), top_k=n, where=where)


def _bm25(question: str, where: dict, n: int) -> list[dict]:
    pool = _allowed(where)
    scores = BM25([c["text"] for c in pool]).scores(question)
    ranked = sorted(zip(pool, scores), key=lambda p: p[1], reverse=True)
    return [{**c, "bm25": round(s, 3)} for c, s in ranked[:n] if s > 0]


def _hybrid(question: str, where: dict, n: int) -> list[dict]:
    dense = [c["id"] for c in _dense(question, where, n)]
    keyword = [c["id"] for c in _bm25(question, where, n)]
    return _by_ids([i for i, _ in rrf([dense, keyword])[:n]])


# ---- the strategies ----

def dense(question, where, k):
    chunks = _dense(question, where, k)
    return chunks, [f"dense top {k}"], 0


def bm25(question, where, k):
    return _bm25(question, where, k), [f"bm25 over the chunks this user may read, top {k}"], 0


def hybrid(question, where, k):
    return _hybrid(question, where, CANDIDATES)[:k], [f"dense top {CANDIDATES} + bm25 top {CANDIDATES} -> RRF -> top {k}"], 0


def rerank(question, where, k):
    chunks, ms = reranker.rerank(question, _dense(question, where, CANDIDATES), k)
    return chunks, [f"dense top {CANDIDATES} -> cross-encoder ({ms:.0f} ms) -> top {k}"], 0


def hybrid_rerank(question, where, k):
    chunks, ms = reranker.rerank(question, _hybrid(question, where, CANDIDATES), k)
    return chunks, [f"hybrid top {CANDIDATES} -> cross-encoder ({ms:.0f} ms) -> top {k}"], 0


def parent(question, where, k):
    col = get_client().get_collection(children.ensure_children())
    res = col.query(query_embeddings=[embed_text(question)], n_results=min(CANDIDATES, col.count()), where=where)
    parents = []
    for meta in res["metadatas"][0]:
        if meta["parent_id"] not in parents:
            parents.append(meta["parent_id"])
    return _by_ids(parents[:k]), [f"children top {CANDIDATES} -> {len(parents)} distinct parents -> top {k}"], 0


def hyde(question, where, k):
    hypothetical = cached_call_llm(HYDE_PROMPT.format(question=question))
    chunks = search(embed_text(hypothetical), top_k=k, where=where)
    return chunks, [f"LLM wrote: {hypothetical[:90]}...", f"dense top {k} on the hypothetical answer"], 1


def multi_query(question, where, k):
    reply = cached_call_llm(MULTI_QUERY_PROMPT.format(question=question))
    queries = [question] + [q.strip(" -•\t") for q in reply.splitlines() if q.strip()][:3]
    rankings = [[c["id"] for c in _dense(q, where, CANDIDATES)] for q in queries]
    return _by_ids([i for i, _ in rrf(rankings)[:k]]), [f"queries: {queries}", f"{len(queries)} x dense top {CANDIDATES} -> RRF -> top {k}"], 1


def routed(question, where, k):
    records = [c for c in _allowed(where) if c.get("doc_type") == "people"]
    shape, wanted = router.classify(question, records)
    if shape == "aggregation":
        hits = router.lookup(records, wanted)
        return hits, [f"route: aggregation on {wanted} -> {len(hits)} matching record(s), all of them"], 0
    chunks, trace, calls = hybrid_rerank(question, where, k)
    return chunks, ["route: pointwise"] + trace, calls


STRATEGIES = {
    "dense": dense, "bm25": bm25, "hybrid": hybrid, "rerank": rerank, "hybrid_rerank": hybrid_rerank,
    "parent": parent, "hyde": hyde, "multi_query": multi_query, "routed": routed,
}
NEEDS_LLM = {"hyde", "multi_query"}


# Purpose:
# Run one strategy for one question, as one user. Time it and count LLM calls.
def run(strategy: str, question: str, user: str | None = None, k: int = 5, as_of: str | None = None) -> Result:
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; choose from {', '.join(STRATEGIES)}")
    where = _where(user, as_of)
    replayed_before = STATS["replayed_ms"]
    start = time.perf_counter()
    chunks, trace, llm_calls = STRATEGIES[strategy](question, where, k)
    # Wall time, plus the original latency of any LLM answer replayed from the cache
    ms = (time.perf_counter() - start) * 1000 + (STATS["replayed_ms"] - replayed_before)
    return Result(strategy, chunks, trace, llm_calls, ms)
