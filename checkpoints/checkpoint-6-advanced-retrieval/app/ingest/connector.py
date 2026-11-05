# ============================================================
# Connector — talks to the source system
# ============================================================
# Every enterprise source (SharePoint, Confluence, Google Drive,
# Slack, S3) answers the same three questions:
#
#   1. What items exist right now?      -> list_items()
#   2. Give me the bytes of this item.  -> fetch()
#   3. What do you know ABOUT it?       -> fetch_register()
#      (owner, who may read it, status, dates)
#
# Here the source is a folder, workspace/sharepoint, that stands in
# for a SharePoint document library. Swap this class for one that
# calls Microsoft Graph and nothing else in the pipeline changes.
#
# THE REAL THING (Microsoft Graph), for reference:
#   GET /drives/{drive-id}/root/delta
#     -> every item changed since your last deltaLink, with an eTag,
#        plus "deleted" markers for items that are gone
#   GET /drives/{drive-id}/items/{item-id}/content      -> the bytes
#   GET /drives/{drive-id}/items/{item-id}/permissions  -> who may read it
#   Auth: a service principal (app registration), not a person's token.
#
# TEACHING POINT:
#   The eTag is the cheap change signal: it changes whenever the bytes
#   change. We compute it as a SHA-256 of the file. A real source hands
#   it to you, so you can skip downloading files that did not change.
# ============================================================

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.config import REGISTER_FILENAME


@dataclass
class SourceItem:
    """One file in the source system."""
    path: str        # relative path with forward slashes, e.g. "hr/leave-policy.md"
    size: int        # bytes
    modified: float  # last-modified time (seconds since epoch)
    etag: str        # changes whenever the bytes change


class LocalFolderConnector:
    """A document library on disk, standing in for SharePoint."""

    def __init__(self, root: Path):
        self.root = Path(root)

    # Purpose:
    # Walk the library and describe every file. Nothing is parsed here.
    def list_items(self) -> list[SourceItem]:
        if not self.root.exists():
            raise FileNotFoundError(
                f"No source at {self.root}. Run: python sharepoint.py reset"
            )
        items = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.name == REGISTER_FILENAME or path.name.startswith("."):
                continue
            data = path.read_bytes()
            items.append(SourceItem(
                path=path.relative_to(self.root).as_posix(),
                size=len(data),
                modified=path.stat().st_mtime,
                etag=hashlib.sha256(data).hexdigest()[:16],
            ))
        return items

    def fetch(self, path: str) -> bytes:
        """Download one item."""
        return (self.root / path).read_bytes()

    def fetch_register(self) -> dict:
        """The library's metadata: one entry per document (see register.py)."""
        register_path = self.root / REGISTER_FILENAME
        if not register_path.exists():
            raise FileNotFoundError(f"No {REGISTER_FILENAME} in {self.root}")
        return json.loads(register_path.read_text(encoding="utf-8"))

    def source_url(self, path: str) -> str:
        """The link a user would click in a citation."""
        site, _, rest = path.partition("/")
        return f"https://acme.sharepoint.com/sites/{site}/Shared%20Documents/{rest}"
