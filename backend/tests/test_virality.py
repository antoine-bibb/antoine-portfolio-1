from app.services.virality import ViralityFactors, compute_virality_score


def test_weighted_score():
    factors = ViralityFactors(80, 60, 75, 90, 70)
    assert compute_virality_score(factors) == 75
