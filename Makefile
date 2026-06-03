.PHONY: setup data run evaluate metrics dashboard all

setup:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

data:
	python3 evaluation/benchmark.py --count 500

run:
	python3 src/main.py

evaluate:
	python3 evaluation/evaluate.py

metrics:
	python3 evaluation/generate_metrics.py

dashboard:
	streamlit run dashboard/app.py

all: data run evaluate metrics

