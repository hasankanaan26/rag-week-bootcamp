"""
judge.py — was the ANSWER any good? An LLM grades the answers.

    python judge.py --strategy hybrid_rerank            # 24 answers, 2 verdicts each
    python judge.py --strategy dense --ids R11,R16 --show

For each golden question: retrieve with the strategy, answer with the RAG
prompt, then ask the LLM two questions:
  faithfulness   share of the answer's claims supported by the retrieved context
  correctness    does the answer agree with the hand-written reference answer?

Every LLM call is cached in runs/llm_cache.json: re-running costs nothing.
Read the "eyes open" note at the end of the output before trusting a number.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.llm import STATS, cached_call_llm, get_model_name  # noqa: E402
from app.prompts.judge import CORRECTNESS_PROMPT, FAITHFULNESS_PROMPT  # noqa: E402
from app.prompts.rag_answer import RAG_SYSTEM_PROMPT  # noqa: E402
from app.rag.strategies import run  # noqa: E402
from app.routers.query import build_context  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "app" / "evals" / "golden_retrieval.json"


def parse_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.S)
    try:
        return json.loads(match.group(0)) if match else {}
    except json.JSONDecodeError:
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", default="hybrid_rerank")
    parser.add_argument("--ids", default="")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    questions = json.loads(GOLDEN.read_text(encoding="utf-8"))["questions"]
    if args.ids:
        wanted = set(args.ids.split(","))
        questions = [q for q in questions if q["id"] in wanted]

    rows = []
    for q in questions:
        result = run(args.strategy, q["question"], user=q["user"], k=5)
        context = build_context(result.chunks)
        answer = cached_call_llm(q["question"], RAG_SYSTEM_PROMPT.format(context=context))
        faith = parse_json(cached_call_llm(FAITHFULNESS_PROMPT.format(context=context, answer=answer)))
        correct = parse_json(cached_call_llm(CORRECTNESS_PROMPT.format(question=q["question"], reference=q["answer"], answer=answer)))
        claims = faith.get("claims", [])
        supported = sum(1 for c in claims if c.get("supported"))
        row = {"id": q["id"], "faithfulness": supported / len(claims) if claims else 1.0,
               "correct": bool(correct.get("correct")), "reason": correct.get("reason", ""), "answer": answer}
        rows.append(row)
        if args.show:
            print(f"\n{q['id']} {q['question']}\n  answer: {answer}\n  reference: {q['answer']}")
            print(f"  faithfulness {row['faithfulness']:.2f} ({supported}/{len(claims)} claims) | correct: {row['correct']} ({row['reason']})")

    n = len(rows) or 1
    print(f"\nStrategy {args.strategy}, {len(rows)} questions, generator and judge: {get_model_name()}")
    print(f"  faithfulness (mean share of supported claims): {sum(r['faithfulness'] for r in rows) / n:.2f}")
    print(f"  correctness (answers agreeing with the reference): {sum(r['correct'] for r in rows)}/{len(rows)}")
    wrong = [r["id"] for r in rows if not r["correct"]]
    if wrong:
        print(f"  not correct: {', '.join(wrong)}  (read them: python judge.py --strategy {args.strategy} --ids {','.join(wrong)} --show)")
    print(f"  LLM: {STATS['calls']} real call(s), {STATS['cache_hits']} from the cache")
    print("\nEyes open: the same model wrote and graded these answers (self-grading is generous),"
          "\nscores vary between runs, and every verdict cost a call. Spot-check 10 by hand.")


if __name__ == "__main__":
    main()
