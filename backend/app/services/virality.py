from dataclasses import dataclass


@dataclass
class ViralityFactors:
    emotional_charge: float
    controversy_or_tension: float
    story_completeness: float
    strong_opening_hook: float
    relatability: float


def compute_virality_score(factors: ViralityFactors) -> int:
    """Weighted 0-100 virality score.

    Weights:
      - Emotional charge: 30%
      - Controversy/tension: 20%
      - Story completeness: 20%
      - Opening hook: 15%
      - Relatability: 15%
    """
    weighted = (
        factors.emotional_charge * 0.30
        + factors.controversy_or_tension * 0.20
        + factors.story_completeness * 0.20
        + factors.strong_opening_hook * 0.15
        + factors.relatability * 0.15
    )
    return int(max(0, min(100, round(weighted))))
