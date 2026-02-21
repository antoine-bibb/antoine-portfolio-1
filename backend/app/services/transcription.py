from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


def split_into_timestamped_segments(raw_segments: list[dict]) -> list[TranscriptSegment]:
    return [
        TranscriptSegment(start=s["start"], end=s["end"], text=s["text"].strip())
        for s in raw_segments
        if s.get("text")
    ]


def detect_topic_shifts(segments: list[TranscriptSegment]) -> list[int]:
    keywords = {"however", "but", "anyway", "now", "so", "next"}
    indices = []
    for i, s in enumerate(segments):
        if any(k in s.text.lower() for k in keywords):
            indices.append(i)
    return indices


def pronoun_hook_bonus(text: str) -> float:
    trigger_words = ["i", "you", "they", "why", "how"]
    lower = text.lower()
    hits = sum(1 for word in trigger_words if f" {word} " in f" {lower} ")
    return min(10.0, hits * 2.0)
