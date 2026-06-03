"""User query handling for interactive and batch modes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserTurn:
    content: str
    turn_id: int


class UserInputHandler:
    """Normalizes user text before it enters the safety pipeline."""

    def normalize(self, text: str, turn_id: int = 1) -> UserTurn:
        clean = " ".join(text.strip().split())
        if not clean:
            clean = "Hello"
        return UserTurn(content=clean, turn_id=turn_id)

