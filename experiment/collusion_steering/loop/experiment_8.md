# Experimenter — iteration 8

**Date:** 2026-10-25T05:45–05:48Z
**Batch:** `results/batches/batch_20261025T054540Z/`
**Outcome:** **0 completed runs.** External quota blocker. No free model could
be called.

## Model and command

Primary attempt:

- Agent / monitor / label: `poolside/laguna-s-2.1:free` (all three; first choice)
- Config copy: `results/batches/batch_20261025T054540Z/config.yaml`
  (`experiment.output_dir` = `results/batches/batch_20261025T054540Z`)
- Command (run from `experiments/collusion_steering/`, with
  `SSL_CERT_FILE` set from `certifi`):

```
uv run python run_experiment.py \
  --config results/batches/batch_20261025T054540Z/config.yaml \
  --scenarios vendor --seeds 0 --workers 1 --conditions collusion_steer
```

Fallback attempt 1 (`probe_fallback_recursive/`, same command shape):

- Agent / monitor / label: `recursive/flint-v1.0:free`

## Conditions

| Priority | Condition | Status |
|---|---|---|
| 1 | `collusion_steer` | attempted twice (two models) → **failed, 0/1 each** |
| 2 | `collusion_quarantine` | **not attempted** (same account-wide block) |
| 3 | `collusion_placebo` | **not attempted** (same account-wide block) |
| 4 | `collusion_silent` | **not attempted** (same account-wide block) |

The two attempts used different models but failed on the **first** agent call,
after six retries, with the same account-wide error. Direct probes of all four
candidate models (`poolside/laguna-s-2.1:free`, `recursive/flint-v1.0:free`,
`dots-studio/dots-3-note-preview:free`, `nvidia/nemotron-3.5-lightning:free`)
returned identical 429s with `X-RateLimit-Remaining: 0`
(`results/batches/batch_20261025T054540Z/quota_probe.json`). Because the cap is
per account, not per model, further attempts on the remaining arms could only
reproduce the failure, so they were skipped.

## Blocker (exact, external)

```
OpenRouterError: OpenRouter call failed after 6 attempts: HTTP 429:
{"error":{"message":"Rate limit exceeded: free-models-per-day-high-balance. ",
"code":429,"metadata":{"headers":{"X-RateLimit-Limit":"1000",
"X-RateLimit-Remaining":"0","X-RateLimit-Reset":"1792972800000"}}}}
```

- `free_model_daily_requests`: **used 1017 / limit 1000 / remaining 0**
- reset: **2026-10-26T00:00:00Z** (≈18.2 h after the attempt)
- paid fallback impossible: key limit `$0.00`, usage `$0.00`

This is not a harness bug in the runner: `run_one` caught the error and wrote a
record, but the batch has zero usable rows.

Secondary harness crash, observed while regenerating the report:

```
uv run python run_experiment.py --results <batch>/runs.jsonl --report report.md
KeyError: 'condition'  (src/collusion_steering/analysis.py:450, summarize)
```

An all-error JSONL should report "0 completed runs" and write a report with the
attrition table instead of raising. Traceback saved in
`results/batches/batch_20261025T054540Z/report_generation.log`. This is the
only harness defect found; it does not cause the zero-run outcome.

## Key numbers

**Not measured.** No run reached the transcript stage, so there is no collusion
success, task-correct, monitor score, or blinded label for any arm. The error
records carry empty `usage` and no `outcome`. Do not report these as zeros:
they are missing.

## Is the intervention arm comparable to the baseline?

**No.** The baseline is still the two committed records
(`vendor__control__s0`, `vendor__collusion_none__s0` in
`results/runs_valid.jsonl`). `collusion_steer`, `collusion_quarantine`,
`collusion_placebo`, and `collusion_silent` still have **zero** completed runs,
and this batch adds no evidence either way.

## Single next experiment

**One fresh batch after the daily quota resets (2026-10-26T00:00Z): run all four
priority arms for `vendor`, seed 0, in a single invocation so the batch has one
`runs.jsonl`:**

```
uv run python run_experiment.py \
  --config results/batches/batch_<new_stamp>/config.yaml \
  --scenarios vendor --seeds 0 --workers 1 \
  --conditions collusion_steer collusion_quarantine collusion_placebo collusion_silent
```

Four runs at roughly 12 requests each is ~48 requests, far below the 1000/day
cap, and `--workers 1` executes them sequentially while the condition
round-robin guarantees every arm gets a job before any arm gets a second. Using
one invocation avoids the runner's per-invocation `runs_<stamp>.jsonl` split,
which would otherwise fragment the batch across four files and leave
`runs.jsonl` holding only the first arm. Verify `runs.jsonl` has 4 records, then
regenerate `report.md` from it. If the quota is still exhausted at reset (or the
cap is hit again), stop and report it rather than spending the remaining window
on retries.

## Files

- Batch folder: `results/batches/batch_20261025T054540Z/` with `config.yaml`,
  `runs.jsonl` (1 error record), `runs.metadata.json`, `metadata.json`,
  `run.log`, `quota_probe.json`, `report_generation.log`, `batch_status.json`,
  `report.md`, and `probe_fallback_recursive/`.
- No code, config, draft, or notes file outside the batch folder was modified.
