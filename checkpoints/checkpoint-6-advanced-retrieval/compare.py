"""
compare.py — every retrieval strategy, the same 24 questions, one scoreboard.

    python compare.py                          # the strategies that need no LLM
    python compare.py --llm                    # + hyde and multi_query (cached LLM calls)
    python compare.py --strategies dense,hybrid_rerank --details
    python compare.py --save-baseline          # freeze today's numbers in runs/baseline.json
    python compare.py --against-baseline       # what moved since the baseline, question by question

The golden set (app/evals/golden_retrieval.json) describes MONDAY: run
`python sharepoint.py apply all` and `python sync.py --apply` first.
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import RUNS_DIR  # noqa: E402
from app.evals.metrics import score, summarize  # noqa: E402
from app.llm import STATS  # noqa: E402
from app.rag.strategies import NEEDS_LLM, STRATEGIES, run  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "app" / "evals" / "golden_retrieval.json"
BASELINE = RUNS_DIR / "baseline.json"
TAGS = ["casual", "identifier", "buried", "pointwise", "multi-doc", "list"]


def evaluate(strategy: str, questions: list[dict], k: int) -> list[dict]:
    rows = []
    for q in questions:
        result = run(strategy, q["question"], user=q["user"], k=k, as_of=q.get("as_of"))
        row = score(q, result.chunks, k)
        row.update(id=q["id"], tags=q["tags"], ms=result.ms, llm_calls=result.llm_calls,
                   got=[c.get("doc_id") for c in result.chunks[:k]], trace=result.trace)
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategies", default="")
    parser.add_argument("--llm", action="store_true", help="include hyde and multi_query")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--save-baseline", action="store_true")
    parser.add_argument("--against-baseline", action="store_true")
    args = parser.parse_args()

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    questions, k = golden["questions"], golden["top_k"]
    names = [s for s in args.strategies.split(",") if s] or [
        s for s in STRATEGIES if args.llm or s not in NEEDS_LLM]

    # Warm up: load the embedder, the cross-encoder and the children index
    # once, so the timings below measure queries, not model loading.
    for name in names:
        run(name, "warm up", user=questions[0]["user"], k=k)

    results = {}
    for name in names:
        rows = evaluate(name, questions, k)
        summary = summarize(rows)
        summary["ms_median"] = round(statistics.median(r["ms"] for r in rows), 1)
        summary["by_tag"] = {t: round(sum(r["hit"] for r in rows if t in r["tags"]) /
                                      max(1, sum(1 for r in rows if t in r["tags"])), 2) for t in TAGS}
        results[name] = {"summary": summary, "rows": rows}

    print(f"\n{len(questions)} questions, top {k}, Monday's index\n")
    print(f"{'strategy':<15}{'Hit@5':>7}{'MRR':>7}{'Recall':>8}{'ms/q':>8}{'LLM/q':>7}   " +
          "".join(f"{t[:9]:>10}" for t in TAGS))
    for name, res in results.items():
        s = res["summary"]
        print(f"{name:<15}{s['hit@5']:>7.2f}{s['mrr']:>7.2f}{s['recall']:>8.2f}{s['ms_median']:>8.0f}{s['llm_calls']:>7.1f}   " +
              "".join(f"{s['by_tag'][t]:>10.2f}" for t in TAGS))
    tag_counts = {t: sum(1 for q in questions if t in q["tags"]) for t in TAGS}
    print(f"{'':<52}   " + "".join(f"{'n=' + str(tag_counts[t]):>10}" for t in TAGS))
    print("(Hit@5 per question type on the right. ms/q: median per question.)")
    if STATS["calls"] or STATS["cache_hits"]:
        print(f"LLM: {STATS['calls']} real call(s), {STATS['cache_hits']} answered from runs/llm_cache.json")

    if args.details:
        for name, res in results.items():
            misses = [r for r in res["rows"] if not r["hit"] or r["recall"] < 1]
            print(f"\n{name}: {len(misses)} question(s) not fully answered")
            for r in misses:
                print(f"  {r['id']} hit={r['hit']} recall={r['recall']:.2f} got={r['got']}")

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = RUNS_DIR / f"compare-{stamp}.json"
    out.write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\nSaved: {out}")

    if args.save_baseline:
        BASELINE.write_text(json.dumps({"saved": stamp, "results": results}, indent=1), encoding="utf-8")
        print(f"Baseline frozen: {BASELINE}")

    if args.against_baseline:
        if not BASELINE.exists():
            sys.exit("No baseline yet. Run: python compare.py --save-baseline")
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        print(f"\nAgainst the baseline of {base['saved']}:")
        for name, res in results.items():
            if name not in base["results"]:
                continue
            old, new = base["results"][name], res
            d = {m: new["summary"][m] - old["summary"][m] for m in ("hit@5", "mrr", "recall")}
            print(f"  {name:<15} Hit@5 {d['hit@5']:+.2f}  MRR {d['mrr']:+.2f}  Recall {d['recall']:+.2f}")
            before = {r["id"]: r for r in old["rows"]}
            for r in new["rows"]:
                b = before.get(r["id"])
                if b and b["hit"] != r["hit"]:
                    print(f"      {r['id']}: {'miss -> HIT ' if r['hit'] else 'HIT -> miss'}  explain this one")


if __name__ == "__main__":
    main()
