"""Entry point for the CrescendoShield pipeline."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from escalation_analyzer import EscalationAnalyzer
from llm_wrapper import SAFE_REFUSAL, LLMWrapper
from memory_sanitizer import MemorySanitizer
from output_verifier import OutputVerifier
from risk_detector import RiskDetector
from user_input import UserInputHandler
from utils import ROOT, setup_logging, write_json


class CrescendoShield:
    """Full user_input -> detector -> escalation -> memory -> LLM -> verifier pipeline."""

    def __init__(self) -> None:
        self.input_handler = UserInputHandler()
        self.risk_detector = RiskDetector()
        self.escalation = EscalationAnalyzer()
        self.memory = MemorySanitizer(self.risk_detector)
        self.llm = LLMWrapper()
        self.output = OutputVerifier()
        self.history: list[dict[str, Any]] = []
        self.risk_history: list[float] = []

    def handle(self, text: str) -> dict[str, Any]:
        started = time.perf_counter()
        turn = self.input_handler.normalize(text, len(self.history) + 1)
        risk = self.risk_detector.score(turn.content, self.history)
        self.risk_history.append(risk.score)
        escalation = self.escalation.analyze(self.risk_history)
        self.history.append({"role": "user", "content": turn.content})

        if risk.blocked or escalation.escalating and risk.score >= 0.45:
            response = SAFE_REFUSAL
            blocked = True
            sanitized = self.memory.sanitize(self.history)
            verified = self.output.verify(response)
        else:
            sanitized = self.memory.sanitize(self.history)
            response = self.llm.generate(sanitized.history)
            verified = self.output.verify(response)
            blocked = not verified.safe or sanitized.removed_count > 0

        final = verified.response
        self.history.append({"role": "assistant", "content": final})
        return {
            "input": turn.content,
            "response": final,
            "blocked": blocked,
            "risk": risk.as_dict(),
            "escalation": escalation.as_dict(),
            "memory": sanitized.as_dict(),
            "output": verified.as_dict(),
            "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CrescendoShield pipeline.")
    parser.add_argument("--prompt", default="Can you explain prompt injection defense at a high level?")
    parser.add_argument("--output", default=str(ROOT / "results" / "single_run.json"))
    args = parser.parse_args()
    setup_logging()
    shield = CrescendoShield()
    result = shield.handle(args.prompt)
    write_json(result, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
