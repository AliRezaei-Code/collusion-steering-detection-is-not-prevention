.PHONY: test run analyze check clean

test:
	uv run pytest -q

run:
	./scripts/run_pilot.sh --scenarios vendor project audit --seeds 0 --workers 2

analyze:
	uv run python run_experiment.py --results results/runs_valid.jsonl

check:
	uv run python scripts/check_artifacts.py

clean:
	rm -f results/runs.jsonl results/run.log results/runs_summary.csv results/report.md
	rm -rf results/figures
