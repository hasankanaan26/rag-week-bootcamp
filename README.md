# RAG Module — Hands-On Teaching Repository

A 4-session, checkpoint-based teaching repository for building a Retrieval-Augmented Generation (RAG) system from scratch. Students build incrementally from a plain LLM scaffold to a full RAG pipeline with failure handling and visualization.

## What Students Learn

- How RAG works: chunking, embedding, retrieval, generation
- Building a vector store with ChromaDB
- Wiring retrieval into generation (the full RAG loop)
- Handling RAG failure modes (no-result, weak evidence)
- Comparing RAG vs plain LLM answers
- Visualizing embeddings with t-SNE and PCA

## Repository Structure

```
base-app/                           <- Clean starting scaffold for live coding
checkpoints/
    checkpoint-1-foundations/        <- Chunking, ingestion, grounding demo
    checkpoint-2-vector-store/       <- Embeddings, ChromaDB, semantic search
    checkpoint-3-rag-pipeline/       <- Full RAG endpoint, compare, logging
    checkpoint-4-analysis/           <- Confidence, failure modes, visualization
data/knowledge/                     <- Sample Acme Corp knowledge base (10 docs)
docs/                               <- Architecture, common mistakes, demo questions
instructor-notes/                   <- Per-checkpoint teaching guides
tests/                              <- Unit tests (run without API keys)
```

## 4-Checkpoint Progression

| Checkpoint | Focus | Key Endpoints |
|------------|-------|---------------|
| 1 — Foundations | Chunking, ingestion, grounding demo | `/ask`, `/ask/grounded`, `/ingest` |
| 2 — Vector Store | Embeddings, ChromaDB, semantic search | `/search`, `/embed`, `/store/inspect` |
| 3 — RAG Pipeline | Full RAG loop, comparison, logging | `/query`, `/compare` |
| 4 — Analysis | Confidence, failure modes, visualization | `/ui`, `/visualize` |

Each checkpoint builds on the previous one. See [CHECKPOINTS.md](CHECKPOINTS.md) for detailed descriptions.

## Quick Start

### Prerequisites

- Python 3.12+
- A Gemini API key ([get one here](https://aistudio.google.com/apikey)) or Azure OpenAI credentials

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd rag-week-bootcamp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API key
```

Want free, offline embeddings? See [docs/local-embeddings.md](docs/local-embeddings.md)
for running the embedding model locally with Ollama (or Hugging Face as an exercise).

### Running the Base App (for live coding)

```bash
cd base-app
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI.

### Running a Checkpoint

```bash
# From the repo root:
python run_checkpoint.py checkpoint-1-foundations
python run_checkpoint.py checkpoint-2-vector-store
python run_checkpoint.py checkpoint-3-rag-pipeline
python run_checkpoint.py checkpoint-4-analysis
```

Each checkpoint starts on http://localhost:8000 with Swagger at `/docs`.

### Running Tests

```bash
pytest tests/ -v
```

Tests run without API keys or a running server.

## Tech Stack

- **Python 3.12** + **FastAPI** — web framework
- **ChromaDB** — local vector store (from Checkpoint 2)
- **Gemini / Azure OpenAI** — LLM and embeddings
- **Ollama** (optional) — local embeddings, see `docs/local-embeddings.md`
- **scikit-learn + matplotlib** — embedding visualization (Checkpoint 4)
- **Pydantic** — data validation

## Sample Domain

All sample data is from a fictional "Acme Corp" internal knowledge base:
- Leave policy, expense policy, coding standards
- Remote work policy, onboarding checklist
- Team directory, tech stack, meeting notes, FAQ

## For Instructors

- See `instructor-notes/` for per-checkpoint teaching guides
- See `docs/live-coding-plan.md` for session-by-session coding order
- See `docs/demo-questions.md` for a consolidated question bank
- See `docs/common-student-mistakes.md` for common pitfalls

## Code Style

- Plain functions, no classes, no async
- Small files, small functions, descriptive names
- `# Purpose:` comments above key functions
- Visible prompt templates (not hidden in packages)
- No LangChain/LlamaIndex — everything is explicit
