import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.clip import ClipJobStatus, ClipUploadResponse
from app.workers.tasks import process_clip_job

router = APIRouter(prefix="/api/v1/clips", tags=["clips"])


@router.post("/upload", response_model=ClipUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    user_id: int | None = Form(default=None),
    guest_fingerprint: str | None = Form(default=None),
    ip_address: str = Form(...),
) -> ClipUploadResponse:
    """Accept upload and queue async processing (non-blocking)."""
    _ = (user_id, guest_fingerprint, ip_address)
    job_id = str(uuid.uuid4())
    upload_dir = Path("tmp_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"{job_id}_{file.filename}"
    stored_path.write_bytes(await file.read())

    process_clip_job.delay(job_id=job_id, source_video_path=str(stored_path))
    return ClipUploadResponse(job_id=job_id, polling_endpoint=f"/api/v1/clips/jobs/{job_id}")


@router.get("/jobs/{job_id}", response_model=ClipJobStatus)
async def poll_job(job_id: str) -> ClipJobStatus:
    task = process_clip_job.AsyncResult(job_id)
    if task.state in {"PENDING", "RECEIVED", "STARTED"}:
        return ClipJobStatus(job_id=job_id, status="processing")
    if task.state == "FAILURE":
        return ClipJobStatus(job_id=job_id, status="failed", error=str(task.result))
    result = task.result or {}
    return ClipJobStatus(
        job_id=job_id,
        status=result.get("status", "complete"),
        top_segments=result.get("top_segments", []),
        output_urls=result.get("output_urls", []),
    )
