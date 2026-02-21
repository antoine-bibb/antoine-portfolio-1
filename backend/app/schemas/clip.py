from typing import Literal

from pydantic import BaseModel, Field


class ClipRequestContext(BaseModel):
    user_id: int | None = None
    guest_fingerprint: str | None = None
    ip_address: str


class ClipUploadResponse(BaseModel):
    job_id: str
    polling_endpoint: str


class ClipCandidate(BaseModel):
    start_time: float
    end_time: float
    virality_score: int = Field(ge=0, le=100)
    reasoning: str
    suggested_caption: str
    suggested_title: str


class ClipJobStatus(BaseModel):
    job_id: str
    status: Literal["pending", "processing", "complete", "failed"]
    top_segments: list[ClipCandidate] = []
    output_urls: list[str] = []
    error: str | None = None
