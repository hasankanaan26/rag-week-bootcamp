"""
run_eval.py — Evaluate the RAG pipeline against test questions.

Usage:
    python eval/run_eval.py

Requires the server to be running on http://localhost:8000.
Run this AFTER ingesting documents.

The script:
  1. Loads test questions from eval/test_questions.json
  2. Sends each question to /query and /safety/check
  3. Checks: correct source retrieved? expected keywords in answer? injection caught?
  4. Prints a summary with pass/fail for each test

TEACHING POINT:
  This is a basic eval pipeline. Production systems use frameworks like
  RAGAS, DeepEval, or custom metrics. But the pattern is the same:
  define expected outcomes → run the system → check results.
"""

import json
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000"


def run_query(question: str, rewrite: bool = False) -> dict:
    """Send a question to the /query endpoint."""
    resp = requests.post(
        f"{BASE_URL}/query",
        json={"question": question},
        params={"rewrite": str(rewrite).lower()},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def run_safety_check(question: str) -> dict:
    """Send a question to the /safety/check endpoint."""
    resp = requests.post(
        f"{BASE_URL}/safety/check",
        json={"question": question},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def check_source(result: dict, expected_source: str | None) -> tuple[bool, str]:
    """Check if the expected source was retrieved."""
    if expected_source is None:
        # Out-of-domain: expect no_result=True
        if result.get("no_result", False):
            return True, "Correctly identified as out-of-domain"
        return False, f"Expected no_result but got answer with confidence={result.get('confidence')}"

    sources = [s["source"] for s in result.get("sources", [])]
    if expected_source in sources:
        return True, f"Found {expected_source} in sources"
    return False, f"Expected {expected_source} but got {sources}"


def check_keywords(result: dict, expected_keywords: list[str]) -> tuple[bool, str]:
    """Check if expected keywords appear in the answer."""
    if not expected_keywords:
        return True, "No keywords to check"

    answer = result.get("answer", "").lower()
    found = [kw for kw in expected_keywords if kw.lower() in answer]
    missing = [kw for kw in expected_keywords if kw.lower() not in answer]

    if missing:
        return False, f"Missing keywords: {missing} (found: {found})"
    return True, f"All keywords found: {found}"


def main():
    # Load test questions
    eval_dir = Path(__file__).parent
    questions_path = eval_dir / "test_questions.json"

    if not questions_path.exists():
        print(f"ERROR: {questions_path} not found")
        sys.exit(1)

    with open(questions_path) as f:
        test_cases = json.load(f)

    print(f"Running evaluation with {len(test_cases)} test cases...\n")
    print("=" * 70)

    results = {"pass": 0, "fail": 0, "error": 0}
    details = []

    for i, tc in enumerate(test_cases, 1):
        question = tc["question"]
        category = tc.get("category", "unknown")
        print(f"\n[{i}/{len(test_cases)}] ({category}) {question}")

        try:
            if category == "injection":
                # Test safety endpoint
                safety_result = run_safety_check(question)
                is_safe = safety_result.get("is_safe", True)

                if not is_safe:
                    status = "PASS"
                    results["pass"] += 1
                    detail = f"  Safety: correctly flagged as UNSAFE — {safety_result.get('reason', '')}"
                else:
                    status = "FAIL"
                    results["fail"] += 1
                    detail = f"  Safety: MISSED injection — classified as SAFE ({safety_result.get('reason', '')})"

                print(f"  → {status}")
                print(detail)
                details.append({"question": question, "category": category, "status": status, "detail": detail})

            else:
                # Test RAG query
                result = run_query(question)

                source_ok, source_msg = check_source(result, tc.get("expected_source"))
                keyword_ok, keyword_msg = check_keywords(result, tc.get("expected_keywords", []))

                if source_ok and keyword_ok:
                    status = "PASS"
                    results["pass"] += 1
                else:
                    status = "FAIL"
                    results["fail"] += 1

                print(f"  → {status} | confidence={result.get('confidence')} | no_result={result.get('no_result')}")
                print(f"  Source: {source_msg}")
                print(f"  Keywords: {keyword_msg}")
                details.append({
                    "question": question, "category": category, "status": status,
                    "source": source_msg, "keywords": keyword_msg,
                })

        except Exception as e:
            results["error"] += 1
            print(f"  → ERROR: {e}")
            details.append({"question": question, "category": category, "status": "ERROR", "error": str(e)})

    # Summary
    total = results["pass"] + results["fail"] + results["error"]
    print("\n" + "=" * 70)
    print(f"RESULTS: {results['pass']}/{total} passed, {results['fail']} failed, {results['error']} errors")
    print("=" * 70)

    if results["fail"] > 0 or results["error"] > 0:
        print("\nFailed/Error cases:")
        for d in details:
            if d["status"] != "PASS":
                print(f"  - [{d['category']}] {d['question']}: {d['status']}")


if __name__ == "__main__":
    main()
