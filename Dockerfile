# ============================================================
# Dockerfile — RAG Module
# ============================================================
# By default runs the base-app scaffold.
# Override the CMD to run a specific checkpoint.
# ============================================================

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--app-dir", "base-app"]
