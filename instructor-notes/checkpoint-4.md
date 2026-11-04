# Instructor Notes — Checkpoint 4: Analysis

## Timing (~2 hours)

| Activity | Time | Notes |
|----------|------|-------|
| Recap Checkpoint 3 | 5 min | "RAG works. Now: when does it fail?" |
| Build confidence scoring | 15 min | Threshold logic, type live |
| Build no-result detection | 10 min | "Know when you don't know" |
| Update /query | 15 min | Add confidence + no-result |
| Demo: confidence levels | 10 min | High, medium, low, none queries |
| Show the UI | 10 min | Browser-based demo with badges |
| Failure mode gallery | 15 min | Subjective, temporal, cross-domain |
| Show visualization | 15 min | t-SNE and PCA plots |
| Discussion | 10 min | When to use RAG, when not to |
| Wrap-up | 10 min | Summary of the full module |

## Key Talking Points

1. **"A good RAG system knows when it doesn't know."** This is the core message. Confidence scoring and no-result detection prevent the system from giving bad answers confidently.

2. **Threshold tuning is empirical.** There's no magic number. Students should try different thresholds and see how they affect behavior. The override parameters make this easy.

3. **Failure modes are features, not bugs.** Subjective questions, temporal queries, and cross-domain questions are inherent limitations of retrieval-based systems. Understanding them helps you design better systems.

4. **Visualization builds intuition.** The t-SNE plot shows WHY semantic search works — similar chunks cluster together. This is more powerful than explaining embeddings abstractly.

## Demo Script for Visualization

1. Make sure documents are ingested: `POST /ingest`
2. Open `/visualize` in a browser tab
3. Point out clusters: "See how the leave policy chunks are grouped together? And coding standards over here?"
4. Open `/visualize?method=pca` — "PCA shows similar clustering but preserves global structure better"
5. "These clusters are why a question about vacation days finds leave policy chunks — they're close in embedding space"

## Common Questions

- "What's the right confidence threshold?" — It depends on your use case. For safety-critical apps, use strict thresholds. For general Q&A, looser is fine.
- "What's the difference between t-SNE and PCA?" — PCA preserves global structure (distances between clusters), t-SNE preserves local structure (which points are neighbors). Both are useful.
- "How do I fix the failure modes?" — Some can't be fixed with RAG alone. Subjective questions need different system design. Temporal queries need versioned documents.
