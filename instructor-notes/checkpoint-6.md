# Instructor Notes — Checkpoint 6: Advanced Retrieval (Session 9)

Deck: `slides/session-09-retrieval-you-can-defend.pptx` (31 shown + 5 reference). The speaker notes
carry what to say per slide and the exact commands; this page is the run sheet.

## Before class

- [ ] `cd checkpoints/checkpoint-6-advanced-retrieval`
- [ ] Monday's SharePoint and this checkpoint's own index:
      `python sharepoint.py reset && python sharepoint.py apply all && python sync.py --apply`
- [ ] `python warmup.py` — embedding model, cross-encoder (~90 MB), children index. Students too,
      the night before.
- [ ] `python compare.py --llm` once, so HyDE and multi-query answers are cached
      (`runs/llm_cache.json`; ~50 LLM calls the first time, free after).
- [ ] `python judge.py --strategy dense` and `--strategy routed` once (~70 calls each, then cached).
- [ ] `python compare.py --strategies rerank,hybrid_rerank --save-baseline` for the regression drill.

## Timing (~2 hours)

| Block | Slides | Time | Live |
|---|---|---|---|
| Where we left off, why top-k breaks | 1-3 | 10 min | `ask.py` on R11 and on the San Francisco question |
| Golden set, baseline, decision framework | 4-6 | 10 min | `compare.py --strategies dense --details` |
| Search better: BM25, hybrid, re-ranking | 7-12 | 25 min | `ask.py "Which database do we use for primary data?" --strategies dense,rerank` |
| Live scoreboard | 13 | 10 min | `compare.py --strategies dense,bm25,hybrid,rerank --details` |
| Break | 14 | 10 min | |
| Parent-document, HyDE, scoreboard | 15-18 | 15 min | `compare.py --llm` (cached) |
| Route, agentic, GraphRAG | 19-23 | 15 min | `ask.py "Who works remotely?" --strategies dense,routed` |
| Prove it | 24-29 | 20 min | `judge.py --strategy dense --ids R11 --show`, regression drill |

## Numbers you will see

Retrieval (24 questions, top 5, local embeddings; latency varies by machine, ranking should not):
dense 0.92 / 0.84 MRR; bm25 0.96 / 0.87; hybrid 0.96 / 0.90; rerank and hybrid_rerank 0.96 / 0.94
(~0.5 s); parent 0.96 / 0.89; hyde 0.96 / 0.88 (~1.8 s, 1 LLM call); multi_query 0.92 / 0.87;
routed 1.00 / 0.98, Recall 1.00.

Answers (gpt-4.1-mini answering and judging): faithfulness 0.99 for dense and routed; correctness
17/24 (dense) vs 23/24 (routed). LLM numbers can move by a question or two between providers.

## The regression drill

```powershell
python compare.py --strategies rerank,hybrid_rerank --against-baseline   # nothing moved
$env:CANDIDATES=5; python compare.py --strategies rerank,hybrid_rerank --against-baseline
Remove-Item Env:CANDIDATES
```

Expected: `rerank Hit@5 -0.04 ... R11: HIT -> miss`; `hybrid_rerank +0.00`. Ask the room to explain
it before you do: the billing rule was never in dense's top 5, so the re-ranker never saw it.

## If something breaks

- **Reranker download fails in class:** skip the live re-rank runs; the numbers are on slides 11, 12
  and 18. `ask.py --strategies dense,bm25,hybrid,parent,routed` needs no download.
- **No LLM key / quota:** everything except `--llm`, `judge.py` and `/query` is LLM-free. The cache
  answers HyDE, multi-query and the judge if you ran them before class.
- **Different numbers:** this checkpoint has its own index (`cp6_kb_*`): run `sync.py --apply` from
  this folder after `apply all`.

## Common questions

- "Why didn't HyDE help more?" Small, clearly written corpus; the embedding already bridges most
  wording gaps. On jargon-heavy corpora it earns more. The point is to measure on your own questions.
- "Isn't the router cheating?" It's the lesson: a set question isn't a similarity question. In
  production the lookup is SQL over a table.
- "Should we always re-rank?" When the right chunk lands in the top 20 but not the top 5 and you
  can afford ~0.5 s. Not for autocomplete or voice.
- "Can we trust the judge?" Not without spot-checks: slide 27 has three of its mistakes from our run.
