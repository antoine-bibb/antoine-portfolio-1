# AI Video Clipper Backend (FastAPI + Celery)

## Folder placement (separation of concerns)

- `app/main.py` — FastAPI app entry point.
- `app/api/routes.py` — upload + polling endpoints (`job_id` workflow, non-blocking).
- `app/workers/` — Celery app + async background pipeline task.
- `app/services/` — pure domain services:
  - `ffmpeg_pipeline.py` for media processing.
  - `transcription.py` for transcript segmentation and topic-shift signals.
  - `audio_analysis.py` for loudness peaks and normalization.
  - `scoring.py` for GPT + heuristics + top-5 ranking.
  - `virality.py` for weighted scoring algorithm.
  - `quotas.py` for guest/free/paid usage enforcement.
- `app/models/entities.py` — SQLAlchemy entities.
- `app/schemas/clip.py` — request/response DTOs.
- `sql/schema.sql` — PostgreSQL DDL.

## Step-by-step backend pipeline

1. **Upload request** to `POST /api/v1/clips/upload`.
   - API stores the video to temporary storage/S3.
   - API immediately enqueues a Celery job and returns:
   ```json
   {"job_id":"...","polling_endpoint":"/api/v1/clips/jobs/{job_id}"}
   ```
2. **Background worker** (`process_clip_job`) performs:
   - Audio extraction with FFmpeg.
   - Whisper transcription.
   - Transcript segmentation with timestamps.
   - Enrichment (topic-shifts, pronoun hooks, sentiment + loudness).
   - GPT scoring + weighted virality score.
   - Top-5 segment ranking.
   - Optional clip rendering (9:16 + burned captions) and storage upload.
3. **Polling request** to `GET /api/v1/clips/jobs/{job_id}` returns processing state and final clips.

## Virality scoring algorithm (0-100)

```python
score = (
  emotional_charge * 0.30
  + controversy_or_tension * 0.20
  + story_completeness * 0.20
  + strong_opening_hook * 0.15
  + relatability * 0.15
)
```

The service clamps to `[0, 100]` and returns integer score.

## Required AI output shape

```json
{
  "start_time": "",
  "end_time": "",
  "virality_score": "",
  "reasoning": "",
  "suggested_caption": ""
}
```

## Usage controls

- **Guest**: max 2 clips (tracked by `ip_address + fingerprint` in `guest_sessions`).
- **Free**: max 5 total clips.
- **Paid**: max 50 clips/month (`monthly_clip_count`, reset at `monthly_reset_date`).

## FFmpeg output targets

Render vertical 1080x1920 clips with burned subtitles and hook overlay, then export as H.264 + AAC with faststart for TikTok/Shorts/Reels compatibility.

## Scale target: 10,000 concurrent uploads

- Frontend uploads to pre-signed S3 URL to offload API bandwidth.
- API only validates + enqueues jobs (constant-time request path).
- Redis/Celery horizontal workers with queue partitioning (`transcribe`, `score`, `render`).
- Postgres for metadata; object storage for media.
- Autoscale workers based on queue depth and per-stage latency SLOs.
