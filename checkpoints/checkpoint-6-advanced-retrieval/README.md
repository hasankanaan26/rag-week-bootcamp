# Checkpoint 6 — Retrieval You Can Defend

## Objective

Make retrieval better on purpose: diagnose why a question fails, pick the lever that fixes that
kind of failure, and prove it on a frozen golden set, including what it costs and what it makes worse.

## What's Covered

- **Diagnose before you fix:** retrieval failure or generation failure? Which kind of question?
- **Hybrid search:** BM25 keywords + dense vectors, fused with reciprocal rank fusion (RRF)
- **Re-ranking:** a cross-encoder re-orders the top 20; it can only promote what was retrieved
- **Change what you store:** parent-document retrieval (match a sentence, return its section)
- **Change what you search with:** HyDE and multi-query (one LLM call per question each)
- **Route by question shape:** "who works in San Francisco?" is a list, not a top-k search
- **Measure everything:** Hit@5, MRR, Recall, latency, LLM calls; regression against a baseline
- **Judge the answers:** LLM-as-judge faithfulness and correctness, and why not to trust it blindly

Checkpoint 5's ingestion is unchanged: every strategy searches inside the same permission and
version filter.

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/rag/strategies.py` | Nine strategies behind one contract: `run(strategy, question, user, k)` |
| `app/rag/bm25.py` | BM25 by hand (keeps identifiers like `IT-4112` whole), plus `rrf()` |
| `app/rag/reranker.py` | Cross-encoder `ms-marco-MiniLM-L-6-v2` on onnxruntime: no PyTorch |
| `app/rag/children.py` | The derived children index for parent-document retrieval, rebuilt when the index changes |
| `app/rag/router.py` | Pointwise or aggregation? Aggregation goes to a lookup over the records |
| `app/llm.py` | `cached_call_llm()`: HyDE, multi-query and the judge never pay twice |
| `app/prompts/query_rewrite.py`, `judge.py` | HyDE, multi-query, faithfulness and correctness prompts |
| `app/evals/golden_retrieval.json` | 24 questions in 6 kinds, with hand-written reference answers |
| `app/evals/metrics.py` | Hit@5, MRR, Recall (documents, or records for list questions) |
| `compare.py` | The scoreboard; `--save-baseline`, `--against-baseline` |
| `ask.py` | One question through several strategies, with traces |
| `judge.py` | Generation metrics with an LLM judge (cached) |
| `app/routers/retrieve.py` | `GET /retrieve?strategy=...` |
| `app/routers/query.py` | `POST /query?strategy=...` (default `routed`) |

```bash
git diff --no-index checkpoints/checkpoint-5-production-ingestion checkpoints/checkpoint-6-advanced-retrieval
```

## How to Run

```bash
cd checkpoints/checkpoint-6-advanced-retrieval
python sharepoint.py reset && python sharepoint.py apply all   # Monday's SharePoint
python sync.py --apply                                         # this checkpoint's own index
python warmup.py                                               # models + children index (at home!)

python compare.py                      # the scoreboard (no LLM)
python compare.py --llm                # + HyDE and multi-query (24 LLM calls each, cached)
python ask.py "How many reviewers does a change to the billing code need?"
python judge.py --strategy dense       # answer quality (72 LLM calls the first time, then cached)
```

API: `python run_checkpoint.py checkpoint-6-advanced-retrieval`, then `/docs` (`GET /retrieve`) or
`/ui` (Ask tab, "Retrieval strategy").

## What you should see

24 questions, top 5, Monday's index, local embeddings, a laptop CPU:

| Strategy | Hit@5 | MRR | Recall | ms / question | LLM calls |
|---|---:|---:|---:|---:|---:|
| dense (Checkpoint 5) | 0.92 | 0.84 | 0.89 | ~45 | 0 |
| bm25 | 0.96 | 0.87 | 0.95 | ~17 | 0 |
| hybrid | 0.96 | 0.90 | 0.95 | ~75 | 0 |
| rerank | 0.96 | 0.94 | 0.95 | ~520 | 0 |
| hybrid_rerank | 0.96 | 0.94 | 0.95 | ~500 | 0 |
| parent | 0.96 | 0.89 | 0.93 | ~60 | 0 |
| hyde | 0.96 | 0.88 | 0.91 | ~1,800 | 1 |
| multi_query | 0.92 | 0.87 | 0.90 | ~1,700 | 1 |
| **routed** | **1.00** | **0.98** | **1.00** | ~480 | 0 |

Latency varies by machine; the ranking of strategies should not.

What moved, and why:

- **R11, "How many reviewers does a change to the billing code need?"** Dense misses it: the rule is
  one sentence in a PDF page about deployments and on-call. BM25 finds "billing" and "reviewers";
  the reranker pulls it from dense rank 6-20 to rank 1; parent-document matches the sentence and
  returns the page.
- **R16, "Which database do we use for primary data?"** Dense rank 4, reranked rank 1.
- **BM25 alone** loses rank on casually phrased questions (R04, R05, R17); hybrid wins them back.
- **List questions (R21-R23)** have 3 to 6 right records. Top-5 can't hold six; only the router,
  which looks up every matching record, gets Recall 1.00.

Answer quality, judged by `gpt-4.1-mini` (same model generating and judging, read the caveats):

| | dense | routed |
|---|---:|---:|
| Faithfulness (claims supported by the context) | 0.99 | 0.99 |
| Correctness (agrees with the reference answer) | 17/24 | 23/24 |

Faithfulness can't see a retrieval failure: with dense retrieval, R11's answer ("at least one
reviewer", from the coding standards) is 100% faithful to its context, and wrong.

## The regression drill

```bash
python compare.py --strategies rerank,hybrid_rerank --save-baseline
CANDIDATES=5 python compare.py --strategies rerank,hybrid_rerank --against-baseline
```

```
rerank          Hit@5 -0.04  MRR -0.04  Recall -0.06
    R11: HIT -> miss  explain this one
hybrid_rerank   Hit@5 +0.00  MRR +0.00  Recall +0.00
```

A reranker can only promote what was retrieved. With 5 candidates, the billing rule never reaches it;
hybrid's BM25 side still brings it in. (On Windows PowerShell: `$env:CANDIDATES=5; python compare.py ...`)

## Tests

```bash
pytest checkpoints/checkpoint-6-advanced-retrieval/tests -q
```

Offline: fake embedder, word-overlap reranker, no LLM calls.

## Exercises

1. Add three golden questions that you think dense will miss. Were you right? Which strategy fixes each?
2. Run `judge.py --show` on five answers and grade them yourself. How often do you agree with the judge?
3. Make the router send "Which teams grew from Q2 to Q3?" (the Excel headcount sheet) to a lookup.
4. Change `CHILD_MAX_CHARS` to 120 and 400. What happens to `parent` on R11 and R12? Explain the move.
