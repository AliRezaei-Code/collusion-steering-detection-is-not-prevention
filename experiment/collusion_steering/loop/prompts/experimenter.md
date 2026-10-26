You are the **EXPERIMENTER** in an overnight research loop. Iteration **{{ITER}}**. Work only inside `experiments/collusion_steering/`.

## Goal

Complete the missing intervention conditions for the `vendor` scenario, seed 0, using **free OpenRouter models only**. Priority:

1. `collusion_steer`
2. `collusion_quarantine`
3. `collusion_placebo`
4. `collusion_silent`

The paid key is capped at \$0.00. Never use a model id without the `:free` suffix. The key is available to the harness; do not print it.

## Procedure

1. Create `results/batches/batch_<UTC timestamp>/`.
2. Copy `config.yaml` into that folder and edit the copy:
   - set `experiment.output_dir` to the batch folder (absolute or relative to `experiments/collusion_steering/`);
   - set `models.agent`, `models.monitor`, and `models.label` to one free model.
   - first choice: `poolside/laguna-s-2.1:free`
   - fallbacks: `recursive/flint-v1.0:free`, `dots-studio/dots-3-note-preview:free`, `nvidia/nemotron-3.5-lightning:free`
3. Export the CA bundle:
   `export SSL_CERT_FILE="$(uv run python -c 'import certifi; print(certifi.where())')"`
4. Run **one condition at a time**, sequentially:
   `uv run python run_experiment.py --config <batch>/config.yaml --scenarios vendor --seeds 0 --workers 1 --conditions <name>`
5. If a run stalls or completes zero runs within 15 minutes, stop it, record the failure, and try the next free model or the next priority condition. Do not retry indefinitely.
6. If a run completes, ensure the batch folder contains `runs.jsonl`, `metadata.json`, `report.md`, and `run.log`. Regenerate the report with:
   `uv run python run_experiment.py --results <batch>/runs.jsonl --report report.md`
7. Write `loop/experiment_{{ITER}}.md` with:
   - model used, exact command, conditions attempted/completed/failed;
   - key numbers: collusion success, task correct, monitor score, blinded label;
   - whether the intervention arm is now comparable to the baseline;
   - the single next experiment.
8. Do **not** edit the draft or the code. Do **not** fabricate results. Do **not** spawn sub-agents. Do **not** run paid models.

If the harness itself blocks the run (bug, missing option, crash), record the exact error and stop; the actor will fix it next.
