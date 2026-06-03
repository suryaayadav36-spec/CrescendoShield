"""Conversation-level escalation analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class EscalationDecision:
    cumulative_risk: float
    trend: float
    escalating: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "cumulative_risk": round(self.cumulative_risk, 4),
            "trend": round(self.trend, 4),
            "escalating": self.escalating,
        }


class EscalationAnalyzer:
    """Tracks risk growth across user turns."""

    def __init__(self, window: int = 5, threshold: float = 0.50) -> None:
        self.window = window
        self.threshold = threshold

    def analyze(self, risk_history: list[float]) -> EscalationDecision:
        if not risk_history:
            return EscalationDecision(0.0, 0.0, False)
        recent = risk_history[-self.window :]
        cumulative = sum(recent) / len(recent)
        trend = recent[-1] - recent[0] if len(recent) > 1 else 0.0
        escalating = cumulative >= self.threshold or trend >= 0.25
        return EscalationDecision(cumulative, trend, escalating)

