"""Generate dashboard-ready CSV, plots, and a compact PDF report."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "results" / ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def plot_metrics(metrics: dict, output_dir: Path) -> None:
    rows = [
        ("ASR", metrics["attack_success_rate"]),
        ("DSR", metrics["defense_success_rate"]),
        ("FPR", metrics["false_positive_rate"]),
        ("F1", metrics["f1"]),
        ("Accuracy", metrics["accuracy"]),
    ]
    df = pd.DataFrame(rows, columns=["metric", "value"])
    df.to_csv(output_dir / "metrics.csv", index=False)
    plt.figure(figsize=(8, 4.8))
    plt.bar(df["metric"], df["value"], color=["#a63e3e", "#2f7452", "#a6651a", "#285f9f", "#5f6680"])
    plt.ylim(0, 1)
    plt.ylabel("Score")
    plt.title("CrescendoShield Evaluation Metrics")
    plt.tight_layout()
    plt.savefig(output_dir / "metrics.png", dpi=180)
    plt.close()


def write_pdf(metrics: dict, output_path: Path) -> None:
    """Write a minimal valid PDF without external converters."""
    lines = [
        "CrescendoShield Final Report",
        "Multi-layer defense against simulated multi-turn jailbreak attacks.",
        f"Records evaluated: {metrics['records']}",
        f"Attack Success Rate: {metrics['attack_success_rate']:.3f}",
        f"Defense Success Rate: {metrics['defense_success_rate']:.3f}",
        f"False Positive Rate: {metrics['false_positive_rate']:.3f}",
        f"F1 Score: {metrics['f1']:.3f}",
        "Pipeline: user_input -> risk_detector -> escalation_analyzer -> memory_sanitizer -> llm_wrapper -> output_verifier.",
    ]
    text_ops = ["BT /F1 14 Tf 72 760 Td"]
    for idx, line in enumerate(lines):
        safe = line.replace("(", "\\(").replace(")", "\\)")
        if idx:
            text_ops.append("0 -24 Td")
        text_ops.append(f"({safe}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    output_path.write_bytes(pdf)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate final metrics artifacts.")
    parser.add_argument("--input", default=str(ROOT / "results" / "metrics.json"))
    parser.add_argument("--output", default=str(ROOT / "results"))
    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(args.input, encoding="utf-8") as f:
        metrics = json.load(f)["metrics"]
    plot_metrics(metrics, output_dir)
    write_pdf(metrics, ROOT / "report.pdf")
    print(f"Saved metrics.csv, metrics.png, and {ROOT / 'report.pdf'}")


if __name__ == "__main__":
    main()
