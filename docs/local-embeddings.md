# Local Embeddings — Run the Embedding Model on Your Own Machine

From Checkpoint 2 onward, every chunk and every question is turned into a
vector by an embedding model. By default that model is a cloud API (Gemini
or Azure OpenAI). This guide shows how to swap in a model that runs
locally instead.

**Why bother?**

- **Free**: no API cost, however many times you re-ingest
- **Private**: your documents never leave your laptop
- **Offline**: works without internet once the model is downloaded
- **Instructive**: you can compare how different models "see" the same text

You can mix and match: keep Gemini or Azure for *answers* (`LLM_PROVIDER`)
and use a local model for *embeddings* (`EMBEDDING_PROVIDER`).

---

## Option A — Ollama (built in)

Already supported in `app/rag/embedder.py` for Checkpoints 2–4.

### 1. Install Ollama and pull a model

Download Ollama from https://ollama.com, then:

```bash
ollama pull nomic-embed-text     # ~270 MB, 768-dimensional vectors
```

Check it's running:

```bash
curl http://localhost:11434/api/version
```

### 2. Switch the embedding provider in `.env`

```env
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

`LLM_PROVIDER` stays as it is. Answers still come from Gemini or Azure.

### 3. Re-ingest from scratch

Vectors from different models live in different "spaces" and can't be
compared. After switching, always rebuild the store:

```
POST /ingest?fresh=true
```

Skip this and you'll get dimension errors (e.g. Azure is 1536 dims,
nomic-embed-text is 768) or nonsense search results.

### 4. Retune the confidence thresholds (Checkpoint 4)

The thresholds in `config.py` were tuned for the cloud models. Local
models spread their distances differently. In our test with
`nomic-embed-text`:

| Question | Best match distance |
|---|---|
| "What is the expense reimbursement policy?" | 0.69 |
| "How many vacation days do I get?" | 0.77 |
| "What are the rules?" (too broad) | 0.88 |
| "Tell me about quantum physics" (off-topic) | 1.14 |

With the default `NO_RESULT_DISTANCE=1.6`, the off-topic question would
**not** be rejected. A reasonable starting point for nomic-embed-text:

```env
CONFIDENCE_HIGH_THRESHOLD=0.8
CONFIDENCE_LOW_THRESHOLD=0.85
NO_RESULT_DISTANCE=1.05
```

Try your own questions on `/search` and adjust. This is a good exercise
in itself: thresholds are tied to the model, not universal.

### Troubleshooting

| Error | Fix |
|---|---|
| `Can't reach Ollama at http://localhost:11434` | Start the Ollama app, or run `ollama serve` |
| `Model 'nomic-embed-text' isn't downloaded yet` | `ollama pull nomic-embed-text` |
| `CUDA error: device kernel image is invalid` | Your GPU isn't supported by Ollama's build. Run it on CPU instead (see below) |
| Works locally but not in Docker | Inside a container, `localhost` is the container. Use `OLLAMA_BASE_URL=http://host.docker.internal:11434` |

Running Ollama on CPU only (Windows PowerShell; quit the Ollama tray app first):

```powershell
$env:CUDA_VISIBLE_DEVICES = "-1"; $env:OLLAMA_LLM_LIBRARY = "cpu"; ollama serve
```

Embedding models are small, so CPU is plenty fast for this course.

---

## Option B — Hugging Face (optional exercise)

Ollama runs the model in a separate app. With the
[`sentence-transformers`](https://www.sbert.net) library you can load a
Hugging Face model **directly inside Python** with no extra server. This
isn't built in; adding it is your exercise.

> **Heads up:** `sentence-transformers` installs PyTorch, which is a large
> download (hundreds of MB, more in Docker). That's why it isn't in
> `requirements.txt`.

### Setup

```bash
pip install sentence-transformers
```

Good small models to try (any model from https://huggingface.co/models
tagged *sentence-transformers* works):

| Model | Dims | Notes |
|---|---|---|
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Tiny and fast, a classic baseline |
| `BAAI/bge-small-en-v1.5` | 384 | Usually better retrieval quality |

The model downloads on first use (cached in `~/.cache/huggingface`), then
works offline.

### Your task

1. In `app/config.py`, add:

   ```python
   # --- Hugging Face settings (used when EMBEDDING_PROVIDER=huggingface) ---
   HF_EMBEDDING_MODEL = os.getenv(
       "HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
   )
   ```

2. In `app/rag/embedder.py`:
   - import `HF_EMBEDDING_MODEL`
   - add a `"huggingface"` branch to `embed_texts()`
   - write `_embed_huggingface(texts)`

   ```python
   def _embed_huggingface(texts: list[str]) -> list[list[float]]:
       """Generate embeddings using a local Hugging Face model."""
       # TODO (Lab exercise):
       #   1. Load a SentenceTransformer(HF_EMBEDDING_MODEL)
       #   2. Call model.encode(texts, normalize_embeddings=True)
       #   3. Return the result as a plain list of lists (.tolist())
       raise NotImplementedError
   ```

3. Set `EMBEDDING_PROVIDER=huggingface`, run `POST /ingest?fresh=true`,
   and try the `/embed` and `/search` endpoints.

**Hints**

- Loading a model takes a few seconds. If you load it inside
  `_embed_huggingface`, every search pays that cost. How can you load it
  only once? (Look up `functools.lru_cache`.)
- Why `normalize_embeddings=True`? The cloud APIs and Ollama return
  unit-length vectors, so distances stay between 0 and 4. Without
  normalizing, the distances, and therefore the thresholds, mean
  something different.
- Import `sentence_transformers` *inside* the function, like the Gemini
  and Azure code does, so the app still starts for people who didn't
  install it.

<details>
<summary>Reference solution (try it yourself first!)</summary>

```python
from functools import lru_cache


# Purpose:
# Loads the Hugging Face model once and keeps it in memory.
@lru_cache(maxsize=1)
def _load_hf_model():
    """Load the sentence-transformers model (downloaded on first use)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(HF_EMBEDDING_MODEL)


def _embed_huggingface(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using a local Hugging Face model."""
    model = _load_hf_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()
```

</details>

---

## Things to explore

Once you have two or more providers working:

- Run `/embed` with `["vacation days", "annual leave", "Python programming"]`
  under each provider. Which model separates related vs unrelated best?
- Open `/visualize` (Checkpoint 4) for each provider. Do the document
  clusters look different?
- Ask the same tricky question with each. Does the top chunk change?
