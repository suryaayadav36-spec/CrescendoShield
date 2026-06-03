"""Evaluate CrescendoShield on all benchmark datasets."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import CrescendoShield
from utils import write_json


ROOT = Path(__file__).resolve().parents[1]


def load_records(dataset_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(dataset_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        records.extend(payload["records"])
    return records


def predict_record(record: dict[str, Any]) -> tuple[int, float]:
    shield = CrescendoShield()
    blocked = False
    latencies: list[float] = []
    for turn in record["turns"]:
        result = shield.handle(turn["content"])
        blocked = blocked or bool(result["blocked"])
        latencies.append(float(result["latency_ms"]))
    return int(blocked), sum(latencies) / max(1, len(latencies))


def compute_metrics(y_true: list[int], y_pred: list[int], latencies: list[float]) -> dict[str, float]:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    attacks = max(1, sum(y_true))
    benign = max(1, len(y_true) - sum(y_true))
    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    f1 = 2 * precision * recall / max(1e-9, precision + recall)
    return {
        "attack_success_rate": fn / attacks,
        "defense_success_rate": tp / attacks,
        "false_positive_rate": fp / benign,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": (tp + tn) / max(1, len(y_true)),
        "avg_latency_ms": sum(latencies) / max(1, len(latencies)),
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CrescendoShield final benchmark.")
    parser.add_argument("--datasets", default=str(ROOT / "datasets"))
    parser.add_argument("--output", default=str(ROOT / "results" / "metrics.json"))
    args = parser.parse_args()
    records = load_records(Path(args.datasets))
    y_true: list[int] = []
    y_pred: list[int] = []
    latencies: list[float] = []
    started = time.perf_counter()
    for record in records:
        pred, latency = predict_record(record)
        y_true.append(int(record["label"]))
        y_pred.append(pred)
        latencies.append(latency)
    metrics = compute_metrics(y_true, y_pred, latencies)
    metrics["records"] = len(records)
    metrics["wall_time_seconds"] = round(time.perf_counter() - started, 3)
    write_json({"metrics": metrics, "y_true": y_true, "y_pred": y_pred}, args.output)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

