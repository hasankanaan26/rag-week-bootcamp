# Instructor Notes — Checkpoint 2: Vector Store

## Timing (~2 hours)

| Activity | Time | Notes |
|----------|------|-------|
| Recap Checkpoint 1 | 5 min | "We chunked documents. Now we make them searchable." |
| Build embedder | 15 min | Explain vectors, type the functions |
| Build store | 20 min | ChromaDB add + search |
| Update /ingest | 10 min | Add embed + store steps |
| Build /search | 15 min | Type live, first search demo |
| Semantic search demo | 15 min | vacation days vs annual leave |
| /embed exploration | 10 min | Pairwise distances |
| Lab exercise | 15 min | Students explore different queries |
| Wrap-up | 10 min | Preview: "Next we wire retrieval into generation" |

## Key Talking Points

1. **The "magic moment"** is when "vacation days" and "annual leave" return the same chunks. Pause here. Let it sink in. "They share zero words, but the embeddings know they mean the same thing."

2. **Distance = relevance.** Low distance = similar meaning = relevant. Walk through a few distance scores and what they mean.

3. **ChromaDB is just one option.** Mention Pinecone, Weaviate, pgvector, FAISS as alternatives. The RAG pattern stays the same.

4. **Inspect the store.** Use `/store/inspect` to show students exactly what's stored — text, metadata, embedding dimensions.

## Common Questions

- "What are the numbers in the embedding?" — Each dimension captures a different aspect of meaning. We don't know exactly what each one means, but similar texts produce similar numbers.
- "Why is the distance between X and Y so high/low?" — Depends on the embedding model's training data and how it interprets meaning.
- "Can we use a different embedding model?" — Yes, just change the config. Different models produce different distance ranges.
