# ============================================================
# Retrieval metrics — no LLM, computed against the golden set
# ============================================================
#   Hit@5    1 if an expected document (or record) is in the top 5
#   MRR      1 / rank of the first expected one in the top 5, else 0
#            (rank 1 -> 1.0, rank 2 -> 0.5, rank 5 -> 0.2)
#   Recall   of everything that BELONGS in the answer, how much reached
#            the LLM? Matters for multi-document questions (both
#            documents needed) and list questions (every record needed).
#            Counted over everything the strategy returns.
#
# A strategy that returns more chunks will look better on Recall and
# cost more tokens. Report both.
# ============================================================


def score(q: dict, chunks: list[dict], k: int = 5) -> dict:
    by_chunk = bool(q.get("expect_chunks"))
    targets = set(q["expect_chunks"] if by_chunk else q["expect_docs"])
    keys = [c.get("id") if by_chunk else c.get("doc_id") for c in chunks]
    top = keys[:k]
    rank = next((i + 1 for i, key in enumerate(top) if key in targets), None)
    found = targets & set(keys)
    recall = 1.0 if (q.get("any_of") and found) else len(found) / len(targets)
    return {"hit": rank is not None, "rank": rank, "rr": 1 / rank if rank else 0.0, "recall": recall,
            "returned": len(chunks)}


def summarize(rows: list[dict]) -> dict:
    n = len(rows) or 1
    return {
        "hit@5": round(sum(r["hit"] for r in rows) / n, 3),
        "mrr": round(sum(r["rr"] for r in rows) / n, 3),
        "recall": round(sum(r["recall"] for r in rows) / n, 3),
        "ms": round(sum(r["ms"] for r in rows) / n, 1),
        "llm_calls": round(sum(r["llm_calls"] for r in rows) / n, 2),
        "chunks": round(sum(r["returned"] for r in rows) / n, 1),
    }
