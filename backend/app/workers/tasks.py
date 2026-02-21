from pathlib import Path

from app.schemas.clip import ClipCandidate
from app.services.audio_analysis import detect_loudness_peaks, normalize
from app.services.scoring import score_segments
from app.services.transcription import split_into_timestamped_segments
from app.workers.celery_app import celery_app


@celery_app.task(name="process_clip_job")
def process_clip_job(job_id: str, source_video_path: str) -> dict:
    # Placeholder pipeline with deterministic sample data.
    _ = Path(source_video_path)
    transcript_raw = [
        {"start": 0.0, "end": 15.0, "text": "Why most startups fail before product market fit."},
        {"start": 15.0, "end": 32.0, "text": "I lost $50k because I ignored customer pain points."},
        {"start": 32.0, "end": 53.0, "text": "Then we changed one thing and revenue doubled."},
        {"start": 53.0, "end": 76.0, "text": "You can apply this framework in 7 days."},
        {"start": 76.0, "end": 95.0, "text": "Most people skip this and wonder why growth stalls."},
    ]
    segments = split_into_timestamped_segments(transcript_raw)
    sentiment_scores = [65, 84, 78, 69, 72]
    loudness = normalize(detect_loudness_peaks([0.12, 0.44, 0.31, 0.29, 0.34]))
    top = score_segments(segments, sentiment_scores, loudness)

    return {
        "job_id": job_id,
        "status": "complete",
        "top_segments": [ClipCandidate.model_validate(c).model_dump() for c in top],
        "output_urls": [],
    }
