# ============================================================
# Loader — reads different file formats into plain text
# ============================================================
# RAG systems need to handle more than markdown files.
# Real knowledge bases include CSVs, PDFs, JSON, and more.
#
# DESIGN CHOICE:
#   We convert every format to plain text, then chunk it.
#   This keeps the chunker simple — it only deals with text.
#   The loader handles all format-specific parsing.
#
# SUPPORTED FORMATS:
#   .md / .txt  -> read as-is (already text)
#   .csv        -> each row becomes "Column: Value" lines
#   .pdf        -> extract text from all pages via pypdf
#   .json       -> flatten key-value pairs into readable text
# ============================================================

import csv
import json
import io
from pathlib import Path


# Purpose:
# Reads a file of any supported format and returns plain text.
# This is the first step in the RAG ingestion pipeline.
def load_file(path: str) -> str:
    """
    Read a file and return its content as plain text.

    Dispatches to the appropriate parser based on file extension.
    Raises ValueError for unsupported file types.
    """
    filepath = Path(path)
    ext = filepath.suffix.lower()

    if ext in (".md", ".txt"):
        return filepath.read_text(encoding="utf-8")

    elif ext == ".csv":
        return _load_csv(filepath)

    elif ext == ".pdf":
        return _load_pdf(filepath)

    elif ext == ".json":
        return _load_json(filepath)

    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ---- Format-specific loaders ----


def _load_csv(filepath: Path) -> str:
    """
    Convert a CSV into readable text.

    Each row becomes a block of "Column: Value" lines,
    separated by blank lines.
    """
    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))

    rows = []
    for row in reader:
        lines = [f"{col}: {val}" for col, val in row.items()]
        rows.append("\n".join(lines))

    return "\n\n".join(rows)


def _load_pdf(filepath: Path) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return f"[PDF file: {filepath.name} — install pypdf to extract text]"

    reader = PdfReader(str(filepath))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())

    return "\n\n".join(pages)


def _load_json(filepath: Path) -> str:
    """Flatten a JSON file into readable key-value text."""
    text = filepath.read_text(encoding="utf-8")
    data = json.loads(text)

    if isinstance(data, dict):
        return _flatten_dict(data)
    elif isinstance(data, list):
        items = []
        for i, item in enumerate(data):
            if isinstance(item, dict):
                items.append(f"Item {i + 1}:\n{_flatten_dict(item)}")
            else:
                items.append(f"Item {i + 1}: {item}")
        return "\n\n".join(items)
    else:
        return str(data)


def _flatten_dict(d: dict) -> str:
    """Turn a dict into 'Key: Value' lines."""
    lines = []
    for key, value in d.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
