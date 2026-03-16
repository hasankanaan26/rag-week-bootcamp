# ============================================================
# Loader — reads different file formats into plain text
# ============================================================
import csv
import json
import io
from pathlib import Path


def load_file(path: str) -> str:
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


def _load_csv(filepath: Path) -> str:
    text = filepath.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        lines = [f"{col}: {val}" for col, val in row.items()]
        rows.append("\n".join(lines))
    return "\n\n".join(rows)


def _load_pdf(filepath: Path) -> str:
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
    lines = []
    for key, value in d.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        lines.append(f"{key}: {value}")
    return "\n".join(lines)
