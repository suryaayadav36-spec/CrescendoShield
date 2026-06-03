"""Memory sanitization for risky conversation context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from risk_detector import RiskDetector


@dataclass
class SanitizationResult:
    history: list[dict[str, Any]]
    removed_count: int
    action: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "history": self.history,
            "removed_count": self.removed_count,
            "action": self.action,
        }


class MemorySanitizer:
    """Removes high-risk user turns before they reach the model."""

    def __init__(self, detector: RiskDetector | None = None, threshold: float = 0.55) -> None:
        self.detector = detector or RiskDetector(threshold=threshold)
        self.threshold = threshold

    def sanitize(self, history: list[dict[str, Any]]) -> SanitizationResult:
        cleaned: list[dict[str, Any]] = []
        removed = 0
        for turn in history:
            if turn.get("role") == "user":
                risk = self.detector.score(turn.get("content", ""), cleaned)
                if risk.score >= self.threshold:
                    removed += 1
                    cleaned.append({"role": "system", "content": "[Sanitized high-risk user context.]"})
                    continue
            cleaned.append(turn)
        return SanitizationResult(cleaned, removed, "sanitize" if removed else "allow")

