import json
from typing import Any

from app.schemas.clip import ClipCandidate
from app.services.transcription import TranscriptSegment, pronoun_hook_bonus
from app.services.virality import ViralityFactors, compute_virality_score


SYSTEM_PROMPT = """
You are a viral short-form clip strategist.
For each transcript segment, return factor scores 0-100:
- emotional_charge
- controversy_or_tension
- story_completeness
- strong_opening_hook
- relatability
Also return reasoning and suggested_caption.
Respond as strict JSON.
""".strip()


def _heuristic_factors(text: str, sentiment_score: float, loudness_score: float) -> ViralityFactors:
    hook = min(100.0, 40 + pronoun_hook_bonus(text) * 4)
    emotional = min(100.0, max(0.0, sentiment_score * 0.7 + loudness_score * 0.3))
    controversy = 70.0 if any(x in text.lower() for x in ["hate", "never", "wrong", "problem"]) else 35.0
    story = 65.0 if any(x in text.lower() for x in ["because", "then", "finally", "result"]) else 45.0
    relatable = 60.0 if any(x in text.lower() for x in ["you", "we", "everyone", "people"]) else 40.0
    return ViralityFactors(emotional, controversy, story, hook, relatable)


def score_segments(
    segments: list[TranscriptSegment],
    sentiment_scores: list[float],
    loudness_scores: list[float],
    gpt_client: Any | None = None,
) -> list[ClipCandidate]:
    candidates: list[ClipCandidate] = []

    for i, segment in enumerate(segments):
        factors = _heuristic_factors(segment.text, sentiment_scores[i], loudness_scores[i])

        # In production replace this with a GPT structured output call and blend with heuristics.
        _ = json.dumps({"prompt": SYSTEM_PROMPT, "text": segment.text})

        score = compute_virality_score(factors)
        candidates.append(
            ClipCandidate(
                start_time=segment.start,
                end_time=segment.end,
                virality_score=score,
                reasoning=(
                    "High score due to emotional spike, hook language, and audio-energy alignment."
                ),
                suggested_caption=f"{segment.text[:90].strip()}...",
                suggested_title="Viral Moment: " + segment.text[:40].strip(),
            )
        )

    return sorted(candidates, key=lambda c: c.virality_score, reverse=True)[:5]
