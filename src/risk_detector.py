"""Multi-turn and pattern-based jailbreak risk detector."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


PATTERNS = {
    "jailbreak": [
        r"ignore (previous|prior|all) instructions",
        r"developer mode|jailbreak mode|unrestricted ai",
        r"disregard .*?(safety|policy|guidelines)",
    ],
    "prompt_injection": [
        r"<\s*system\s*>|system_prompt|ignore_safety_protocols",
        r"override .*?(system|developer|safety)",
        r"hidden instruction|new instruction hierarchy",
    ],
    "roleplay": [
        r"pretend .*?(no rules|no safety|unrestricted)",
        r"roleplay .*?(bypass|without ethical|ignore)",
        r"act as .*?(malicious|unfiltered|uncensored)",
    ],
    "context_poisoning": [
        r"your creators authorized|direct order|i am an admin",
        r"ethics board approved|testing team|check your system prompt",
        r"activate .*?(jailbreak|developer)",
    ],
    "harmful_request": [
        r"bypass .*?(security|filters|safety)",
        r"bypass steps|remove caveats",
        r"without rebuttals|without caveats|without warnings",
        r"convincing without|more convincing",
        r"illegal|malware|phishing|credential theft",
        r"step-by-step .*?(harmful|criminal|exploit|operational)",
    ],
}


@dataclass
class RiskDecision:
    score: float
    label: str
    blocked: bool
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "label": self.label,
            "blocked": self.blocked,
            "reasons": self.reasons,
        }


class RiskDetector:
    """Scores current user turn using transparent patterns and escalation context."""

    def __init__(self, threshold: float = 0.60) -> None:
        self.threshold = threshold

    def score(self, text: str, history: list[dict[str, Any]] | None = None) -> RiskDecision:
        history = history or []
        lower = text.lower()
        category_scores: dict[str, float] = {}
        reasons: list[str] = []
        for category, patterns in PATTERNS.items():
            hits = sum(1 for pattern in patterns if re.search(pattern, lower, flags=re.I | re.S))
            category_scores[category] = min(1.0, hits * 0.72)
            if hits:
                reasons.append(f"{category}:{hits}")

        score = max(category_scores.values(), default=0.0)
        recent_text = " ".join(t.get("content", "") for t in history[-4:] if t.get("role") == "user").lower()
        if score > 0 and any(term in recent_text for term in ["just", "without", "pretend", "authorized"]):
            score = min(1.0, score + 0.12)
            reasons.append("multi_turn_escalation")
        if "hypothetical" in lower and any(term in lower for term in ["bypass", "illegal", "unsafe"]):
            score = min(1.0, score + 0.18)
            reasons.append("hypothetical_framing")

        label = max(category_scores, key=category_scores.get) if score > 0 else "benign"
        return RiskDecision(score=score, label=label, blocked=score >= self.threshold, reasons=reasons)
