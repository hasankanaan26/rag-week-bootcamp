# Week 3: RAG Done Properly

Build a knowledge-grounded Q&A assistant using FastAPI and Retrieval-Augmented Generation.

## What You'll Build

A FastAPI application that answers questions about a company's internal knowledge base (Acme Corp policies, standards, and guides). By the end of the week, you'll have a system that:

- Loads company documents and splits them into searchable chunks
- Embeds chunks into a vector store (ChromaDB) for semantic search
- Retrieves relevant context for any user question
- Generates accurate, grounded answers using an LLM
- Shows its sources and knows when it doesn't have an answer
- Compares RAG answers against plain LLM answers side-by-side

## Prerequisites

You must have completed **Weeks 1 and 2**, where you learned:

- FastAPI basics (routes, models, request/response)
- LLM API calls (hosted and local)
- Structured JSON outputs
- Prompt architecture and chaining
- Chat endpoints and tracing
- Docker/containerization
- Retries and error handling
- Prompt-to-pipeline thinking

## Setup

### 1. Clone and configure

```bash
git clone <repo-url>
cd rag-week-bootcamp
cp .env.example .env
# Edit .env with your API key
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the app

```bash
uvicorn app.main:app --reload
```

Then open http://localhost:8000/docs to see the Swagger UI.

### Alternative: Docker

```bash
docker compose up --build
```

## Repository Structure

```
rag-week-bootcamp/
├── app/                        # Main application code
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment-based settings
│   ├── models.py               # Pydantic request/response models
│   ├── llm.py                  # LLM caller (thin wrapper)
│   ├── routers/                # API route handlers
│   ├── prompts/                # Prompt templates (visible, readable)
│   └── rag/                    # RAG components (chunker, embedder, etc.)
├── data/knowledge/             # Sample company documents (Acme Corp)
├── checkpoints/                # Complete code snapshots per session
├── docs/                       # Session reference documentation
├── instructor-notes/           # Teaching guides per session
└── tests/                      # Test files
```

## Session Roadmap

| Session | Topic | What You'll Build |
|---------|-------|-------------------|
| 1 | RAG Foundations | Plain chat + manually grounded answer demo |
| 2 | Document Ingestion | Chunking utility + /ingest endpoint |
| 3 | Embeddings & Search | Vector embeddings + ChromaDB + /search endpoint |
| 4 | RAG Pipeline | Retriever + RAG prompt + /query endpoint |
| 5 | Transparent UX | Confidence scoring, no-result handling, browser UI |
| 6 | Failure Modes | Structured logging, /compare endpoint, tricky queries |
| 7 | Smarter Retrieval | Query rewriting, metadata filtering, better search |
| 8 | Evaluation & Safety | Eval pipeline, safety checks, prompt injection defense |

See [SESSIONS.md](SESSIONS.md) for the detailed session guide.

## Falling Behind?

Each session has a complete checkpoint in the `checkpoints/` folder. If you get lost:

```bash
# Copy the checkpoint code into your app/ folder
cp -r checkpoints/session-02-chunking/app/* app/
```

Then restart the server and you're caught up.

## Sample Questions to Try

These questions work well for testing throughout the week:

**Should work with RAG (answer is in the knowledge base):**
- "How many vacation days do I get?"
- "What is the Git branching convention?"
- "Can I expense a monitor for my home office?"
- "What are the core working hours for remote employees?"
- "How do I get access to GitHub as a new employee?"

**Should NOT work with RAG (answer is not in the knowledge base):**
- "What is the company stock price?"
- "Who is the CEO of Acme Corp?"
- "What programming language was invented in 1995?"

## Tech Stack

- **FastAPI** — Web framework (same as Weeks 1-2)
- **Google Gemini** — LLM calls and embeddings (via `google-genai`)
- **ChromaDB** — Vector store for semantic search
- **Pydantic** — Data validation and response models
- **Docker** — Containerization (same as Weeks 1-2)
