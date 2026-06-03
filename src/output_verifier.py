"""Model-output safety verifier."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from llm_wrapper import SAFE_REFUSAL


@dataclass
class OutputDecision:
    safe: bool
    score: float
    response: str
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "safe": self.safe,
            "score": round(self.score, 4),
            "response": self.response,
            "reasons": self.reasons,
        }


class OutputVerifier:
    """Blocks unsafe completions before final response."""

    def __init__(self, threshold: float = 0.70) -> None:
        self.threshold = threshold

    def verify(self, text: str) -> OutputDecision:
        reasons: list[str] = []
        score = 0.0
        for label, pattern in {
            "harmful_steps": r"step\s*1.*step\s*2.*(illegal|malware|phishing|exploit)",
            "policy_bypass": r"ignore safety|unrestricted mode|bypass filters",
            "dangerous_domain": r"credential theft|malware|dehumanize",
        }.items():
            if re.search(pattern, text.lower(), flags=re.S):
                score += 0.40
                reasons.append(label)
        safe = score < self.threshold
        return OutputDecision(safe=safe, score=min(1.0, score), response=text if safe else SAFE_REFUSAL, reasons=reasons)

