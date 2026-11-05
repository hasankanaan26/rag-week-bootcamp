# Slides: Sessions 8 and 9

Two decks for the second half of the RAG module, in the SE Factory style of
`Applied AI Engineering Workshop - RAG.pptx` (the deck used with checkpoints 1 to 4).

| Deck | Code | Shown | Reference |
|------|------|-------|-----------|
| `session-08-production-ingestion.pptx` | `checkpoints/checkpoint-5-production-ingestion` | 34 slides (5 parts + break) | 3 slides |
| `session-09-retrieval-you-can-defend.pptx` | `checkpoints/checkpoint-6-advanced-retrieval` | 31 slides (4 parts + break) | 5 slides |

Every number on a slide comes from a run of the checkpoint it belongs to (local embeddings, so the
retrieval numbers reproduce on any laptop; latencies vary by machine). Speaker notes follow the
About / Say format and carry the demo commands, expected output, and anything that points ahead to a
later session (visible slide text only describes the code of that session).

## Where the material came from

The four Week 7 decks of the previous bootcamp, split across two sessions and rewritten around this
repository's code (hand-rolled, no LangChain):

| Previous deck | Now |
|---|---|
| W7 S3 Enterprise connectors and ingestion | Session 8, parts 1 to 3 (connect, parse, govern) |
| W7 S4 RAG evaluation, retrieval metrics and golden set | Session 8, part 5 (measure) |
| *new* | Session 8, part 4 (sync: plan, price, apply, blue/green) and versions in part 3 |
| W7 S1 Advanced RAG architectures | Session 9, parts 1 to 3 (hybrid, parent-document, HyDE, multi-query, routing, agentic) |
| W7 S2 GraphRAG and re-ranking | Session 9, parts 1 and 3 (re-ranking, candidates, GraphRAG), reference (ColBERT, managed re-rankers) |
| W7 S4 generation metrics, LLM-as-judge, regression | Session 9, part 4 (prove it) |
| history-rag (top-k vs aggregation) | Session 9, part 3 (some answers are bigger than k) |

## Rebuilding

The decks are generated from `src/` (PptxGenJS). Edit the slide spec, rebuild, check the preview:

```bash
cd slides/src
npm install          # once
npm run build        # writes out/s08.pptx, out/s09.pptx and out/*-preview.html
npm run shots        # one PNG per slide + a text-overflow report (needs a headless Chromium)
```

`kit.js` renders one spec to both the `.pptx` and an HTML preview; `sef.js` holds the SE Factory
look (colors, title and divider slides, cards, tables, code blocks); `s08.js` and `s09.js` are the
decks. `shoot.js` points at a Playwright headless Chromium; change `executablePath` for your machine.
Copy `out/s08.pptx` and `out/s09.pptx` over the decks in this folder when you are happy.

After changing a checkpoint, re-run its numbers (`evaluate.py`, `compare.py`, `judge.py`) and
update the slides that quote them.
