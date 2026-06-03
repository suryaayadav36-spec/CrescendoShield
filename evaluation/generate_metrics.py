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
from matplotlib.backends.backend_pdf import PdfPages
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


def add_text_page(pdf: PdfPages, title: str, body: list[str]) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    fig.text(0.08, 0.93, title, fontsize=20, fontweight="bold", color="#18202a")
    y = 0.87
    for line in body:
        if line.startswith("## "):
            y -= 0.025
            fig.text(0.08, y, line[3:], fontsize=13, fontweight="bold", color="#285f9f")
            y -= 0.035
        else:
            fig.text(0.08, y, line, fontsize=10.5, color="#273244", wrap=True)
            y -= 0.032
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def write_pdf(metrics: dict, output_path: Path) -> None:
    """Write a multi-page research report PDF."""
    with PdfPages(output_path) as pdf:
        add_text_page(
            pdf,
            "CrescendoShield: Multi-Layer Defense Against Multi-Turn Jailbreaks",
            [
                "Abstract",
                "CrescendoShield is a reproducible AI safety prototype for detecting simulated Crescendo-style jailbreak attacks.",
                "It integrates user input handling, risk detection, escalation analysis, memory sanitization, an LLM wrapper, and output verification.",
                "",
                "## Objective",
                "Build a CPU-friendly research prototype that can detect, prevent, and report multi-turn jailbreak risk.",
                "The project is designed for internship evaluation, classroom review, and GitHub reproducibility.",
                "",
                "## Pipeline",
                "user_input -> risk_detector -> escalation_analyzer -> memory_sanitizer -> llm_wrapper -> output_verifier -> final_response",
            ],
        )
        add_text_page(
            pdf,
            "Dataset and Methodology",
            [
                "The benchmark contains 2,500 simulated text-only records across five categories.",
                "Each category has 500 examples generated deterministically by evaluation/benchmark.py.",
                "",
                "## Categories",
                "Benign: ordinary safe requests for false-positive testing.",
                "Jailbreak: roleplay and instruction-bypass attempts.",
                "Prompt injection: synthetic system/developer override patterns.",
                "Escalation: multi-turn requests that move from harmless to risky.",
                "Context poisoning: false authority, fake approval, and memory manipulation.",
                "",
                "## Safety Scope",
                "The dataset avoids operational malware, phishing, chemical synthesis, and real harm instructions.",
            ],
        )
        fig = plt.figure(figsize=(8.27, 11.69))
        ax = fig.add_subplot(111)
        labels = ["ASR", "DSR", "FPR", "F1", "Accuracy"]
        values = [
            metrics["attack_success_rate"],
            metrics["defense_success_rate"],
            metrics["false_positive_rate"],
            metrics["f1"],
            metrics["accuracy"],
        ]
        ax.bar(labels, values, color=["#a63e3e", "#2f7452", "#a6651a", "#285f9f", "#5f6680"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Score")
        ax.set_title("Evaluation Results", fontweight="bold")
        for i, value in enumerate(values):
            ax.text(i, value + 0.02, f"{value:.3f}", ha="center")
        fig.text(0.08, 0.12, f"Records evaluated: {metrics['records']}", fontsize=11)
        fig.text(
            0.08,
            0.09,
            f"TP={metrics['true_positive']} TN={metrics['true_negative']} FP={metrics['false_positive']} FN={metrics['false_negative']}",
            fontsize=11,
        )
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
        add_text_page(
            pdf,
            "Limitations and Future Work",
            [
                "## Limitations",
                "The benchmark is simulated and pattern-centered, so it cannot replace human red-team evaluation.",
                "The default LLM wrapper uses an offline-safe deterministic backend for reproducibility.",
                "Real Llama-3.2-3B-Instruct evaluation requires model access, compute, and safety review.",
                "",
                "## Future Work",
                "Add semantic embedding classifiers, multilingual examples, human-reviewed labels, and open-source guard model baselines.",
                "Extend the dashboard with risk trajectory charts and model comparison experiments.",
                "",
                "## Conclusion",
                "CrescendoShield provides a complete, reproducible, deployment-ready AI safety submission with code, data, metrics, dashboard, and report.",
            ],
        )


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
