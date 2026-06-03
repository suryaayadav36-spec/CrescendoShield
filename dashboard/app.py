"""Streamlit dashboard for CrescendoShield."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "results" / "metrics.json"
CSS_PATH = Path(__file__).resolve().parent / "static" / "css" / "style.css"
JS_PATH = Path(__file__).resolve().parent / "static" / "js" / "animations.js"


def load_metrics() -> dict:
    if not METRICS_PATH.exists():
        return {}
    with open(METRICS_PATH, encoding="utf-8") as f:
        return json.load(f)["metrics"]


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


st.set_page_config(page_title="CrescendoShield", layout="wide")
st.markdown(f"<style>{CSS_PATH.read_text()}</style>", unsafe_allow_html=True)

metrics = load_metrics()
st.markdown(
    """
    <section class="hero">
      <div>
        <h1>CrescendoShield</h1>
        <p>Research dashboard for multi-layer defense against simulated multi-turn jailbreak attacks.</p>
      </div>
      <span class="status">Evaluation-ready</span>
    </section>
    """,
    unsafe_allow_html=True,
)

if not metrics:
    st.warning("Metrics not found. Run `python evaluation/evaluate.py` and `python evaluation/generate_metrics.py` first.")
    st.stop()

cols = st.columns(4)
cards = [
    ("Attack Success Rate", pct(metrics["attack_success_rate"]), "Lower is better"),
    ("Defense Success Rate", pct(metrics["defense_success_rate"]), "Higher is better"),
    ("False Positive Rate", pct(metrics["false_positive_rate"]), "Benign blocked"),
    ("Avg Latency", f"{metrics['avg_latency_ms']:.2f} ms", "Per record"),
]
for col, (label, value, note) in zip(cols, cards):
    col.markdown(
        f"""
        <div class="card metric-card">
          <span>{label}</span>
          <strong>{value}</strong>
          <small>{note}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="card">
      <h2>Pipeline</h2>
      <div class="pipeline">
        <b>User Input</b><b>Risk Detector</b><b>Escalation Analyzer</b>
        <b>Memory Sanitizer</b><b>LLM Wrapper</b><b>Output Verifier</b><b>Final Response</b>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.1, 0.9])
with left:
    st.markdown('<div class="card"><h2>Metric Plot</h2>', unsafe_allow_html=True)
    plot_path = ROOT / "results" / "metrics.png"
    if plot_path.exists():
        st.image(str(plot_path), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        f"""
        <div class="card">
          <h2>Confusion Matrix</h2>
          <table>
            <tr><th></th><th>Predicted Block</th><th>Predicted Allow</th></tr>
            <tr><th>Attack</th><td>{metrics['true_positive']}</td><td>{metrics['false_negative']}</td></tr>
            <tr><th>Benign</th><td>{metrics['false_positive']}</td><td>{metrics['true_negative']}</td></tr>
          </table>
          <p class="muted">Records evaluated: {metrics['records']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="card">
      <h2>Run Commands</h2>
      <pre>python evaluation/benchmark.py --count 500
python src/main.py
python evaluation/evaluate.py
python evaluation/generate_metrics.py
streamlit run dashboard/app.py</pre>
    </div>
    """,
    unsafe_allow_html=True,
)

components.html(f"<script>{JS_PATH.read_text()}</script>", height=0)

