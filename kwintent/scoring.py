"""Deterministic scoring on top of Claude's estimates.

The inputs are guesses, so the output is a ranking aid, not a forecast.
"""
from .models import VOLUME_BANDS

_DIFF = {"low": 0.15, "medium": 0.4, "high": 0.7, "very_high": 0.9}
_CONF = {"low": 0.8, "medium": 0.9, "high": 1.0}
_AI = {"low": 1.0, "medium": 0.85, "high": 0.65}
_DEMAND = {"rare": 0.1, "occasional": 0.4, "common": 0.7, "very_common": 1.0}


def _clamp5(n: int) -> int:
    return max(1, min(5, int(n)))


def volume_midpoint(band: str) -> int:
    """Geometric midpoint of a band, for display/sorting only."""
    return {"<10": 5, "10-100": 30, "100-1k": 300, "1k-10k": 3000,
            "10k-100k": 30000, "100k+": 200000}[band]


def seo_score(volume_band: str, confidence: str, difficulty: str,
              ai_risk: str, business_value: int, business_fit: int) -> float:
    vol = VOLUME_BANDS.index(volume_band) / (len(VOLUME_BANDS) - 1)
    s = (_clamp5(business_value) / 5) * (_clamp5(business_fit) / 5)
    s *= 0.3 + 0.7 * vol
    s *= 1 - 0.8 * _DIFF[difficulty]
    s *= _AI[ai_risk] * _CONF[confidence]
    return round(100 * s, 1)


def geo_score(demand: str, citation_difficulty: str,
              business_value: int, business_fit: int) -> float:
    s = (_clamp5(business_value) / 5) * (_clamp5(business_fit) / 5)
    s *= 0.3 + 0.7 * _DEMAND[demand]
    s *= 1 - 0.8 * _DIFF[citation_difficulty]
    # GEO demand has no public data at all, so discount it as low-confidence.
    return round(100 * s * 0.8, 1)
