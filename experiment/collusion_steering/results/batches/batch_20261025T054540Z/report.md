# Batch report — batch_20261025T054540Z

**Status: no completed runs.** This file is a failure report, not a results
report. The harness did not produce one because the batch contains zero usable
records.

## Attempts

| # | Condition | Scenario | Seed | Model | Completed | Wall time | Failure |
|---|---|---|---|---|---|---|---|
| 1 | `collusion_steer` | vendor | 0 | `poolside/laguna-s-2.1:free` | 0/1 | 34.73 s | HTTP 429 free-model daily quota |
| 2 | `collusion_steer` | vendor | 0 | `recursive/flint-v1.0:free` | 0/1 | 34.83 s | HTTP 429 free-model daily quota |

Both attempts failed on the **first** agent call, after the client exhausted its
six retries. No transcript, monitor score, label, or vote exists for either
attempt, so there are no outcome numbers to report.

Raw error (both attempts):

```
OpenRouterError: OpenRouter call failed after 6 attempts: HTTP 429:
{"error":{"message":"Rate limit exceeded: free-models-per-day-high-balance. ",
"code":429,"metadata":{"headers":{"X-RateLimit-Limit":"1000",
"X-RateLimit-Remaining":"0","X-RateLimit-Reset":"1792972800000"}}}}
```

## Blocker

The OpenRouter key is at its **account-wide free-model daily request cap**:

- `free_model_daily_requests.used = 1017`
- `free_model_daily_requests.limit = 1000`
- `free_model_daily_requests.remaining = 0`
- reset: `2026-10-26T00:00:00Z`
- paid fallback unavailable: key limit `$0.00`, usage `$0.00`

Direct probes of all four candidate free models (`poolside/laguna-s-2.1:free`,
`recursive/flint-v1.0:free`, `dots-studio/dots-3-note-preview:free`,
`nvidia/nemotron-3.5-lightning:free`) returned the same 429 with
`X-RateLimit-Remaining: 0` (see `quota_probe.json`). The limit is account-wide,
not per model, so switching models cannot clear it.

`collusion_quarantine`, `collusion_placebo`, and `collusion_silent` were **not
attempted**: they would repeat the identical failure at the same quota. The
batch is not evidence about any treatment arm.

## Harness issue observed

Report regeneration on an all-error JSONL crashes:

```
uv run python run_experiment.py --results <batch>/runs.jsonl --report report.md
KeyError: 'condition'  (src/collusion_steering/analysis.py:450, summarize)
```

An all-error batch should print "0 completed runs" and write a report with the
attrition table instead of raising. Full traceback in `report_generation.log`.

## Files

- `runs.jsonl` — one error record (`vendor__collusion_steer__s0`)
- `runs.metadata.json` — runner dump for attempt 1
- `metadata.json` — verbatim copy of `runs.metadata.json`
- `run.log` — attempt 1 console output
- `quota_probe.json` — key usage and four direct model probes
- `report_generation.log` — traceback from the report step
- `batch_status.json` — machine-readable summary of this batch
- `probe_fallback_recursive/` — attempt 2, its own `runs.jsonl`,
  `runs.metadata.json`, `run.log`, and `config.yaml`

## What cannot be claimed

No collusion success rate, task-correct rate, monitor score, or blinded label
exists for this batch. The intervention arms remain unrun, and the comparison to
the two-record baseline (`results/runs_valid.jsonl`) is still not possible.
