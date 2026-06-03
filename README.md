# CrescendoShield

Final-submission-ready research prototype for multi-layer defense against simulated multi-turn jailbreak attacks.

## Highlights

- Multi-layer pipeline for jailbreak, prompt injection, escalation, memory poisoning, and unsafe output detection
- 2,500-record simulated benchmark across five safety categories
- Real evaluation metrics generated from pipeline predictions
- Streamlit dashboard with dynamic metrics, plot, confusion matrix, hover effects, and deployment configuration
- CPU/free-tier friendly default with optional Hugging Face Llama-3.2-3B-Instruct backend

## Folder Structure

```text
CrescendoShield/
├── src/
├── datasets/
├── evaluation/
├── dashboard/
├── requirements.txt
├── environment.yml
├── README.md
└── report.pdf
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python evaluation/benchmark.py --count 500
python src/main.py
python evaluation/evaluate.py
python evaluation/generate_metrics.py
```

Or run the full reproducibility sequence:

```bash
make all
```

## Launch Dashboard

```bash
cd dashboard
streamlit run app.py
```

From the repository root, this also works:

```bash
streamlit run dashboard/app.py
```

Local URL:

```text
http://localhost:8501
```

## Metrics

The evaluation script computes real predictions from the pipeline:

- ASR: attacks allowed / total attacks
- DSR: attacks blocked / total attacks
- FPR: benign blocked / total benign
- Precision, recall, F1, accuracy
- Average latency

Datasets are simulated and safety-scoped. They contain text-only jailbreak, prompt-injection, escalation, and context-poisoning patterns without operational harmful instructions.

## Current Result Snapshot

```text
Records: 2500
Attack Success Rate: 6.3%
Defense Success Rate: 93.7%
False Positive Rate: 0.0%
F1 Score: 0.967
Accuracy: 94.96%
```

## Streamlit Cloud

Push this folder to GitHub and set the Streamlit app entry point to:

```text
dashboard/app.py
```

See `DEPLOY_STREAMLIT.md` for deployment steps.
