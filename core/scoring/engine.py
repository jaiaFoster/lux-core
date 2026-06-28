# core/scoring/engine.py
#
# LUX Core Scoring Engine
#
# Computes opportunity scores and confidence ratings from Signals.
# Deterministic and weighted — no black box. Every score is explainable.
# Signal weights are configured externally, not hardcoded.

from typing import List
from core.models.entities import Signal


class ScoringEngine:
    """
    Computes a composite score for a subject (participant or asset)
    from a list of Signals.

    Score is a weighted average of signal values, normalized to 0.0 - 1.0.
    Confidence is derived from signal count and average signal confidence.
    """

    def score(self, signals: List[Signal]) -> dict:
        """
        Returns:
            {
                "score": float,          # 0.0 - 1.0
                "confidence": str,       # LOW / MEDIUM / HIGH
                "explanation": list[str] # human-readable signal breakdown
            }
        """
        if not signals:
            return {"score": 0.0, "confidence": "LOW", "explanation": ["No signals detected."]}

        weighted_sum = sum(s.value * s.weight for s in signals)
        total_weight = sum(s.weight for s in signals)
        score = weighted_sum / total_weight if total_weight > 0 else 0.0

        confidence = self._confidence(signals)
        explanation = [f"{s.signal_type}: {s.explanation} (value={s.value:.2f}, weight={s.weight})" for s in signals]

        return {
            "score": round(score, 4),
            "confidence": confidence,
            "explanation": explanation
        }

    def _confidence(self, signals: List[Signal]) -> str:
        if len(signals) >= 3:
            return "HIGH"
        elif len(signals) == 2:
            return "MEDIUM"
        return "LOW"
