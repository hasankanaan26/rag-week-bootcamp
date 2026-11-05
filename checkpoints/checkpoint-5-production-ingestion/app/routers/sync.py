# ============================================================
# Router: /sync — run the ingestion job from Swagger or the UI
# ============================================================
# Replaces Checkpoint 4's POST /ingest. Same job as `python sync.py`.
#
#   POST /sync                -> dry run: the plan and its cost, nothing written
#   POST /sync?apply=true     -> do it, write a report to runs/
#   POST /sync?rebuild=true&apply=true
#                             -> build a fresh index next to the live
#                                one, switch over if the smoke check passes
#
# In production this endpoint would not exist: the job runs on a
# schedule (cron, a queue worker, or a webhook from the source).
# It is here so you can watch it in class.
# ============================================================

from fastapi import APIRouter, HTTPException, Query

from app.ingest.sync import ModelMismatch, run_sync
from app.models import SyncDocAction, SyncResponse

router = APIRouter(prefix="/sync", tags=["Sync (ingestion job)"])


@router.post("", response_model=SyncResponse)
def sync(
    apply: bool = Query(default=False, description="False = dry run (plan only). True = write to the index."),
    rebuild: bool = Query(default=False, description="Build a new index next to the live one (blue/green)."),
):
    """Compare the source with the index; plan or apply the changes."""
    try:
        report = run_sync(apply=apply, rebuild=rebuild)
    except ModelMismatch as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return SyncResponse(
        applied=report["applied"],
        collection=report["collection"],
        embedding_model=report["embedding_model"],
        counts=report["counts"],
        chunks_to_embed=report["chunks_to_embed"],
        estimated_tokens=report["estimated_tokens"],
        estimated_cost_usd=report["estimated_cost_usd"],
        warnings=report["warnings"],
        documents=[SyncDocAction(**{k: d[k] for k in ("doc_id", "path", "action", "reason", "chunks")})
                   for d in report["documents"]],
        report_file=report.get("report_file"),
    )
