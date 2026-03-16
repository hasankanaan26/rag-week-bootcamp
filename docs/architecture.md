# Architecture — Week 3: RAG Done Properly

## The RAG Pattern

RAG (Retrieval-Augmented Generation) is a three-step process:

```
User Question
     │
     ▼
┌─────────────┐
│  1. EMBED   │  Turn the question into a vector (list of numbers)
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ 2. RETRIEVE │  Search the vector store for similar chunks
└─────┬───────┘
      │
      ▼
┌─────────────┐
│ 3. GENERATE │  Send the question + retrieved context to the LLM
└─────────────┘
      │
      ▼
  Grounded Answer
  (with sources)
```

That's it. Everything else is refinement.

## How Our App Is Organized

```
app/
├── main.py              ← FastAPI app, mounts all routers
├── config.py            ← Settings from .env file
├── models.py            ← Pydantic models (request/response shapes)
├── llm.py               ← Sends prompts to the LLM
│
├── routers/
│   ├── ask.py           ← POST /ask (plain LLM, no retrieval)
│   ├── ingest.py        ← POST /ingest (load + chunk + embed + store)
│   ├── search.py        ← GET /search (test vector search in isolation)
│   ├── query.py         ← POST /query (the RAG endpoint)
│   ├── compare.py       ← POST /compare (RAG vs plain, side-by-side)
│   └── ui.py            ← GET /ui (browser-based query interface)
│
├── prompts/
│   ├── plain_answer.py  ← System prompt for plain answers
│   ├── grounded_answer.py ← System prompt with context injection
│   └── rag_answer.py    ← System prompt for RAG answers
│
├── static/
│   └── query.html       ← Browser UI (vanilla HTML/JS)
│
└── rag/
    ├── chunker.py       ← Splits documents into chunks
    ├── embedder.py      ← Generates vector embeddings
    ├── store.py          ← Reads/writes ChromaDB
    └── retriever.py     ← Searches for relevant chunks
```

## What Flows Where

### Ingestion flow (one-time, loads documents into the store)

```
Markdown files → chunker.py → embedder.py → store.py → ChromaDB
```

### Query flow (every user question)

```
User question → embedder.py → retriever.py → prompt template → llm.py → Answer
                                  │
                                  └── ChromaDB (search)
```

## Key Design Decisions

**Why plain functions instead of classes?**
Every module exports simple functions. No inheritance, no abstract base classes. You can read each file top-to-bottom and understand what it does.

**Why separate prompt files?**
Prompts are the most important part of any LLM application. Keeping them in dedicated files makes them easy to find, read, and modify. You should always be able to see the exact text the LLM receives.

**Why ChromaDB?**
It's the simplest vector store to set up. It runs in-process (no separate server needed for development) and has a clean Python API. For production, you might choose Pinecone, Weaviate, or pgvector — but the RAG pattern stays the same.

**Why not LangChain / LlamaIndex?**
These frameworks hide the retrieval and prompting logic behind abstractions. For learning, you need to see every step. Once you understand the raw pattern, you can choose to use a framework later — or not.

## Data Flow Summary

| Step | Module | Input | Output |
|------|--------|-------|--------|
| Chunk | `rag/chunker.py` | Document text | List of text chunks |
| Embed | `rag/embedder.py` | Text (chunk or query) | Vector (list of floats) |
| Store | `rag/store.py` | Chunks + vectors | Persisted in ChromaDB |
| Retrieve | `rag/retriever.py` | Query vector | Top-K relevant chunks |
| Generate | `llm.py` | Prompt with context | LLM response text |
