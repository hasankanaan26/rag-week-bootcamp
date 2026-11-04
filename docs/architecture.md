# Architecture

## The RAG Pattern

```
User Question
     |
     v
[1. RETRIEVE]     Embed the question, search the vector store
     |
     v
[2. INJECT]       Format retrieved chunks into the prompt
     |
     v
[3. GENERATE]     Call the LLM with grounded prompt
     |
     v
Grounded Answer + Sources
```

## Ingestion Pipeline

```
Files (md, csv, pdf, json)
     |
     v
[Load]            Convert to plain text (loader.py)
     |
     v
[Chunk]           Split into overlapping segments (chunker.py)
     |
     v
[Embed]           Convert each chunk to a vector (embedder.py)
     |
     v
[Store]           Persist in ChromaDB with metadata (store.py)
```

## Module Responsibilities

| Module | Job |
|--------|-----|
| `app/rag/loader.py` | Read any file format into plain text |
| `app/rag/chunker.py` | Split text into chunks (fixed-size or sections) |
| `app/rag/embedder.py` | Convert text to embedding vectors |
| `app/rag/store.py` | Store and search chunks in ChromaDB |
| `app/rag/retriever.py` | Orchestrate embed + search for a query |
| `app/rag/visualize.py` | Reduce embeddings to 2D for visualization |
| `app/prompts/*.py` | Prompt templates (visible, not hidden) |
| `app/routers/*.py` | FastAPI endpoints |
| `app/llm.py` | Thin wrapper around LLM API calls |
| `app/config.py` | All settings from environment variables |
| `app/models.py` | Pydantic request/response models |

## Design Decisions

**Plain functions, not classes.** Everything is a function. No service classes, no dependency injection. Students can follow the flow by reading function calls top to bottom.

**Separate prompt files.** Each prompt is in its own file in `app/prompts/`. You can open them side-by-side to compare strict vs minimal grounding.

**ChromaDB (local vector store).** No cloud services needed. Persists to disk. Easy to inspect and reset. The RAG pattern works the same with any vector store.

**Dual provider support.** Both Gemini and Azure OpenAI work. Students use whichever they have access to. Provider-specific code is isolated in `llm.py` and `embedder.py`.

**No LangChain/LlamaIndex.** The entire RAG pipeline is ~100 lines of explicit Python. Students see every step. Nothing is hidden behind framework abstractions.
