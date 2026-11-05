# Instructor Notes — Checkpoint 5: Production Ingestion (Session 8)

Deck: `slides/session-08-production-ingestion.pptx` (34 shown + 3 reference). The speaker notes carry
what to say per slide and the exact commands; this page is the run sheet.

## Before class

- [ ] On the presenting laptop: `python checkpoints/checkpoint-5-production-ingestion/warmup.py`
      (downloads the local embedding model, ~80 MB, ~3 min on slow Wi-Fi). Tell students to run it
      the night before.
- [ ] Start from Friday: `sync.py --wipe`, `sharepoint.py reset`. Do NOT apply the events yet.
- [ ] Open `data/enterprise/` in the editor (register.json, one site folder), and a terminal in
      `checkpoints/checkpoint-5-production-ingestion`.
- [ ] Optional: `python run_checkpoint.py checkpoint-5-production-ingestion` in a second terminal
      for `/ui` (Ask as / As of in the top bar) and `/docs`.

## Timing (~2 hours)

| Block | Slides | Time | Live |
|---|---|---|---|
| Opening: last session, the scenario | 1-6 | 15 min | `sharepoint.py reset`, `sync.py --naive` |
| Predict, then measure checkpoint 4's index | 7-8 | 10 min | `sharepoint.py apply all`, `sync.py --naive`, `evaluate.py --only naive` |
| Connect | 9-12 | 15 min | open `connector.py` |
| Parse | 13-16 | 15 min | `sync.py` (dry run) shows the scan quarantined |
| Break | 17 | 10 min | |
| Govern: register, permissions | 18-21 | 20 min | live-code `access_filter()`, `search.py --user intern / hr-partner` |
| Versions, PII | 22-23 | 10 min | `search.py "meal per diem" --as-of 2023-06-01` |
| Sync | 24-28 | 15 min | `sync.py`, `sync.py --apply` |
| Measure | 29-32 | 10 min | `evaluate.py` |

Dry run with the full sequence takes about 1 minute of compute in total; most of the time is talk.

## Numbers you will see (local embeddings, reproducible)

- Friday sync: add 18, quarantine 1 (the scan), skip 1 (the draft); 88 chunks; ~4.5 s.
- Checkpoint 4's `/ingest` on Friday: 50 chunks; 5 files silently skipped; the scan embedded as "".
- Monday plan: add 1, change 1, relabel 3, touch 1, remove 1, unchanged 12; 11 chunks to embed.
- Monday evaluation, checkpoint 4's index vs today's: Hit@5 0.81 vs 0.96; MRR 0.63 vs 0.90;
  leak 7 vs 0, stale 14 vs 0, ghost 11 vs 0, PII 4 vs 0 (out of 31 questions).

## If something breaks

- **Model download too slow:** `EMBEDDING_PROVIDER=gemini` works (needs the key; costs fractions
  of a cent). The sync will ask for a rebuild if a local index already exists: `sync.py --rebuild --apply`.
- **"No source"**: run `sharepoint.py reset`.
- **Numbers differ from the slides:** check `sharepoint.py status` shows all 5 events, and that both
  `sync.py --apply` and `sync.py --naive` ran AFTER `apply all`.
- **Start over:** `sync.py --wipe` then `sharepoint.py reset`.

## Common questions

- "Why not LangChain's loaders?" They return documents; they don't give you deletions, permissions,
  a register or a cost estimate. Use them for parsing if you like; the sync logic is yours either way.
- "Where do groups come from in production?" The identity provider token (Entra ID, Okta). Never a
  request field. `identities.json` stands in for it.
- "Why keep superseded documents at all?" Questions about the past (an expense from 2023). Withdrawn
  documents are deleted; superseded ones are filtered.
- "Isn't the FAQ wrong now?" Yes, and the sync report says so (it quotes two changed documents).
  The index can't fix a stale copy; its owner can. That's exercise 3.
