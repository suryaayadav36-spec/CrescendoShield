# Deploy CrescendoShield With Streamlit

## Local Deployment

From the `CrescendoShield/` folder:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python evaluation/benchmark.py --count 500
python evaluation/evaluate.py
python evaluation/generate_metrics.py
streamlit run dashboard/app.py
```

Open:

```text
http://localhost:8501
```

## Streamlit Community Cloud

1. Push this `CrescendoShield` folder to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the app entry file to:

```text
dashboard/app.py
```

5. Deploy.

The dashboard reads generated files from:

```text
results/metrics.json
results/metrics.png
report.pdf
```

If you regenerate metrics locally, commit the updated `results/` files before redeploying.

