"""
ask.py — one question, several strategies, side by side, with their traces.

    python ask.py "How many reviewers does a change to the billing code need?"
    python ask.py "Who works remotely?" --strategies dense,routed
    python ask.py "Who do I call if I'm locked out?" --strategies dense,hyde --user intern

Shows the top 5 of each strategy: which document, which section, and how it got there.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag.strategies import NEEDS_LLM, STRATEGIES, run  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("question")
    parser.add_argument("--strategies", default="dense,hybrid,hybrid_rerank,parent,routed")
    parser.add_argument("--user", default="eng-manager")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    for name in args.strategies.split(","):
        if name not in STRATEGIES:
            sys.exit(f"unknown strategy {name}; choose from {', '.join(STRATEGIES)}")
        result = run(name, args.question, user=args.user, k=args.k)
        llm = f", {result.llm_calls} LLM call" if result.llm_calls else ""
        print(f"\n== {name}  ({result.ms:.0f} ms{llm}){'  [needs an LLM]' if name in NEEDS_LLM else ''}")
        for line in result.trace:
            print(f"   {line}")
        for i, c in enumerate(result.chunks, 1):
            extra = f"  rerank={c['rerank_score']}" if "rerank_score" in c else (f"  bm25={c['bm25']}" if "bm25" in c else "")
            print(f"   {i}. {c.get('doc_id', ''):<22} {c.get('section', '')[:38]:<38}{extra}")


if __name__ == "__main__":
    main()
