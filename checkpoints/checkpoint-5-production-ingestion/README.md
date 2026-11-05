# Checkpoint 5 — Production Ingestion

## Objective

Turn `POST /ingest` into a sync job that keeps the index true to a source that keeps changing:
the right documents, the right versions, visible only to the right people.

## What's Covered

- **Connectors:** a source system answers three questions: what exists, give me the bytes, what do you know about it
- **Parsing the format zoo:** Markdown, CSV, PDF (and scans), Word, Excel, HTML, email, standard library only
- **The document register:** owner, permissions, status, version, effective dates, kept next to the files, not in them
- **Permissions inside the search:** the filter runs in the vector query, never after it, never in the prompt
- **Versions and "as of" questions:** current by default; superseded documents stay for questions about the past
- **Sync, not ingest:** add, change, relabel, touch, remove, quarantine, decided per document and priced before it runs
- **PII redaction** before anything is embedded
- **Blue/green rebuilds:** build next to the live index, smoke-check, switch, roll back
- **Measuring it:** leaks, stale chunks and ghosts, counted on a hand-written golden set

## The scenario

`data/enterprise/` is a snapshot of Acme's SharePoint on Friday: 20 files in 7 sites, a register
(`register.json`) and five users (`identities.json`). Over the weekend five things happen
(`data/enterprise/events/events.json`):

1. Finance publishes the 2026 Expense Policy. The 2023 policy and its 2024 update become superseded.
2. HR edits the Leave Policy. Carry-over goes from 5 to 10 days; two sections move out. The file gets shorter.
3. Legal withdraws the Q3 planning notes. The file is deleted.
4. HR fixes the salary bands, which had been shared with every employee. Not one word changes.
5. Someone edits the wiki page footer. The article does not change.

`sharepoint.py` plays SharePoint: it copies the seed to `workspace/sharepoint/` and replays the events.

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `sharepoint.py` | Plays the source system: `reset`, `events`, `apply 1`, `apply all`, `status` |
| `sync.py` | The ingestion job: dry run by default, `--apply`, `--rebuild`, `--rollback`, `--naive`, `--wipe` |
| `search.py` | Ask as a user, as of a date, against either index; `--answer` adds the LLM's answer |
| `evaluate.py` | Golden set against checkpoint 4's index and today's, side by side. No LLM calls |
| `warmup.py` | Downloads the local embedding model (about 80 MB). Run it before class |
| `app/ingest/connector.py` | `LocalFolderConnector`: list items with eTags, fetch bytes, fetch the register |
| `app/ingest/parsers.py` | One parser per format; scanned PDFs are quarantined, not indexed empty |
| `app/ingest/register.py` | Loads and checks the register; identities; fail closed |
| `app/ingest/pii.py` | Redacts personal emails, phone numbers and card-like numbers |
| `app/ingest/sync.py` | Builds the plan (reads only) and applies it (embeds first, then writes) |
| `app/ingest/naive.py` | Checkpoint 4's `/ingest`, kept so we can measure what it gets wrong |
| `app/rag/catalog.py` | Which collection is live; activate, roll back |
| `app/rag/store_chroma.py` | Per-document delete, metadata update, index state, filtered search |
| `app/rag/retriever.py` | `access_filter()`: who (ACL flags) and when (status or `as_of`) |
| `app/rag/chunker.py` | Adds `chunk_sections()`: one chunk per section, with a "title > heading" header |
| `app/rag/embedder.py` | Batches, retries with backoff, a free local provider, the model's id |
| `app/evals/golden.json`, `judge.py` | 31 questions; Hit@5, MRR and five safety flags |
| `app/routers/sync.py`, `documents.py` | `POST /sync`, `GET /documents` |
| `app/routers/search.py`, `query.py` | New `user` and `as_of` parameters; sources carry provenance |
| `app/static/*` | "Ask as" and "As of" in the top bar; the Ingest tab became Sync |

Removed: `app/rag/loader.py` (now `parsers.py`), `app/routers/ingest.py` (now `sync`), and the
pgvector backend (this checkpoint's filters are written for Chroma).

Diff it against Checkpoint 4:

```bash
git diff --no-index checkpoints/checkpoint-4-analysis checkpoints/checkpoint-5-production-ingestion
```

## How to Run

```bash
python checkpoints/checkpoint-5-production-ingestion/warmup.py      # once, at home: downloads the model
```

The class demo, in order (each script works from any folder):

```bash
python checkpoints/checkpoint-5-production-ingestion/sharepoint.py reset    # Friday
python checkpoints/checkpoint-5-production-ingestion/sync.py                # dry run: the plan and its cost
python checkpoints/checkpoint-5-production-ingestion/sync.py --apply        # build the live index
python checkpoints/checkpoint-5-production-ingestion/sync.py --naive        # checkpoint 4's /ingest, for comparison
python checkpoints/checkpoint-5-production-ingestion/sharepoint.py apply all # the weekend happens
python checkpoints/checkpoint-5-production-ingestion/sync.py                # what changed? one action per document
python checkpoints/checkpoint-5-production-ingestion/sync.py --apply        # today's index catches up
python checkpoints/checkpoint-5-production-ingestion/sync.py --naive        # checkpoint 4's catches up its own way
python checkpoints/checkpoint-5-production-ingestion/evaluate.py            # measure both
```

Then the API and the browser workbench:

```bash
python run_checkpoint.py checkpoint-5-production-ingestion
# http://localhost:8000/ui     (Ask as / As of in the top bar)
# http://localhost:8000/docs   (POST /sync, GET /documents, GET /search?user=...&as_of=...)
```

Embeddings are local by default (`EMBEDDING_PROVIDER=local`): free, offline after the warm-up, and the
same numbers on every laptop. `/query` and `search.py --answer` still call your LLM.

## What you should see

The weekend's sync, as a dry run: 11 chunks to embed out of 89, nothing else touched.

```
 ! quarantine ENG-INCIDENT-REPORT      1 page(s), 0 characters of text: a scan. Queued for OCR, not indexed.
 = touch      ENG-WIKI-VECTOR-DB       bytes changed but the extracted text is identical: no re-embedding
 * relabel    FIN-EXP-2023             status: 'current' -> 'superseded'; effective_to: 99991231 -> 20261101; ...
 * relabel    FIN-EXP-2024-UPDATE      status: 'current' -> 'superseded'; ...
 + add        FIN-EXP-2026             new: 7 chunk(s) from the markdown parser
 ~ change     HR-LEAVE                 text changed: 6 old chunk(s) out, 4 new in
 * relabel    HR-SALARY-BANDS-2026     allowed_groups: 'employees' -> 'hr,managers'
 - remove     LEAD-Q3-NOTES            no longer in the register (deleted at the source)
```

The evaluation on Monday's SharePoint (31 questions, top 5, local embeddings):

| | Checkpoint 4's `/ingest` | Today's sync |
|---|---:|---:|
| Hit@5 (27 answerable) | 0.81 | 0.96 |
| MRR | 0.63 | 0.90 |
| Questions with a chunk the user may not read | 7 | 0 |
| Questions with a superseded or draft chunk | 14 | 0 |
| Questions with a deleted or outdated chunk | 11 | 0 |
| Questions with personal data in a chunk | 4 | 0 |

The one question today's sync misses (Q08, billing changes need two reviewers) is a retrieval
problem, not an ingestion one: the rule sits mid-paragraph in a PDF page. Checkpoint 6 picks it up.

## Demo questions

| Try | As | Expect |
|---|---|---|
| `search.py "salary range for a senior developer"` | `--user intern` | nothing about salaries |
| same | `--user hr-partner` | the 2026 bands |
| `search.py "team dinner limit per person"` | | $90, 2026 edition |
| same | `--as-of 2023-06-01` | $50, 2023 edition (superseded) |
| same | `--index naive` | $50 first: checkpoint 4's index serves the old rule |
| `search.py "phone of the person whose laptop battery died"` | `--user sales-rep` | `[PHONE REDACTED]` |

## Tests

Offline, with a fake embedder and temp folders (your index and `.env` are not touched):

```bash
pytest checkpoints/checkpoint-5-production-ingestion/tests -q
```

## Exercises

1. Add a sixth event: Finance withdraws the 2024 update outright. What should the sync do? Which golden
   questions change?
2. HR's leave policy was edited in place, so "how many days could I carry over in 2025?" has no answer
   any more. Change the register so both versions survive. (Hint: publications supersede, edits replace.)
3. The sync report says the FAQ quotes two documents that changed. Find the two stale numbers in it.
4. Add a `sales` document readable only by `sales`, and a golden question for each side of the fence.
