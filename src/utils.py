"""Shared utilities for CrescendoShield."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def seed_everything(seed: int = 42) -> None:
    random.seed(seed)


def read_json(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data: Any, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"

