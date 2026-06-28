# core/matching/engine.py
#
# LUX Core Matching Engine
#
# Matches opportunities (scored assets/sellers) to counterparties (buyers).
# Market-agnostic — operates on Participants and Signals only.
# Real-estate-specific criteria (buy box, property type, etc.) arrive
# as Signals from the adapter, not as hardcoded logic here.

from typing import List
from core.models.entities import Participant, Signal


class MatchingEngine:
    """
    Ranks a list of candidate counterparties against an opportunity
    using their associated Signals.

    Returns a ranked list of matches with scores and explanations.
    """

    def match(
        self,
        opportunity_signals: List[Signal],
        candidates: List[dict]  # [{ "participant": Participant, "signals": List[Signal] }]
    ) -> List[dict]:
        """
        Returns candidates ranked by match score, highest first.

        Each result:
            {
                "participant": Participant,
                "match_score": float,
                "confidence": str,
                "explanation": list[str]
            }
        """
        results = []

        for candidate in candidates:
            participant = candidate["participant"]
            signals = candidate["signals"]

            score, explanation = self._compute_match(opportunity_signals, signals)

            results.append({
                "participant": participant,
                "match_score": round(score, 4),
                "confidence": self._confidence(signals),
                "explanation": explanation
            })

        results.sort(key=lambda r: r["match_score"], reverse=True)
        return results

    def _compute_match(
        self,
        opportunity_signals: List[Signal],
        candidate_signals: List[Signal]
    ) -> tuple:
        """
        Placeholder matching logic.
        V1: weighted signal overlap between opportunity and candidate.
        Replace with richer logic as signal library grows.
        """
        if not candidate_signals:
            return 0.0, ["No candidate signals available."]

        score = sum(s.value * s.weight for s in candidate_signals)
        total_weight = sum(s.weight for s in candidate_signals)
        normalized = score / total_weight if total_weight > 0 else 0.0

        explanation = [f"{s.signal_type}: {s.explanation}" for s in candidate_signals]
        return normalized, explanation

    def _confidence(self, signals: List[Signal]) -> str:
        if len(signals) >= 3:
            return "HIGH"
        elif len(signals) == 2:
            return "MEDIUM"
        return "LOW"
