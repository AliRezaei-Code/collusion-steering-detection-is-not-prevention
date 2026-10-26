# Actor summary — iteration 1

## Files changed

**Artifacts / provenance**
- `results/runs_valid.jsonl` (new) — committed copy of the only valid batch (2 records: `vendor__control__s0`, `vendor__collusion_none__s0`).
- `.gitignore` — added `!results/runs_valid.jsonl` so the valid batch is committed while local `runs.jsonl` stays ignored.
- `results/worked_example_report.md` — regenerated mechanically from `runs_valid.jsonl` via `write_report()`; now reports 2 runs, attrition, component AUROCs, and per-run labels.
- `results/report_invalid_control.md` — prefixed with a loud `INVALID CONTROL BATCH — DO NOT CITE` banner explaining the broken control and that no row is citable.
- `results/README.md` — documents valid vs. quarantined files, the missing-label convention, and the checker.
- `scripts/check_artifacts.py` (new) — verifies every number quoted in §6 against `runs_valid.jsonl`, forbids the stale 6,672/11,084/240 s claims, and checks the quarantine banner.

**Draft / docs**
- `research_draft.md` — rewrote §6 around the two runs that actually exist; removed the non-existent `collusion_steer` narrative and its untraceable cost numbers; status/abstract/contributions/§3.3 now say "two completed runs, no valid intervention run".
- `research_draft.md` — §4.4 states plainly that the rule component is a code-word oracle; §4.5 replaces "independent/unbiased" with "second noisy annotator", adds `blinded_r1`, and makes API failures missing rather than negative; §6.2 reports the control false positive at 0.9 confidence.
- `research_draft.md` — §4.8 states `task_correct = 1 - collusion_success` on non-tie runs and replaces the vacuous cost estimand with tie rate + reasoning quality; §5.2/§9.5/§9.7 and Appendix Q9 updated to match.
- `research_draft.md` — §5.3 adds a two-proportion power table (36/167/385 per arm at 80% for 30/15/10 pp; 54/250/577 with design effect 1.5); §8 labels the 63-run grid as feasibility, not powered; §9.7 corrects 40/arm at 15 pp to ~28% power.
- `README.md`, `notes.md`, `Makefile` — synchronized with the two-run status, new fields, `runs_valid.jsonl`, and `make check`.
- `run_experiment.py` — passes raw records to the report (so failures appear in attrition) and uses seed-major dry-run order.

**Code**
- `monitor.py` — added `rule_score_blind()` (generic cues, no code-word table) and logs `rule_score_blind` on every monitor path.
- `labels.py` — `attempted=None` on unparseable/missing/failed label; docstring now says "second noisy annotator".
- `runner.py` — logs `blinded_r1_attempted` (round-1 label), intervention role/trigger/judge/rule scores; `build_jobs()` is seed-major so a stalled batch is not a condition-ordered prefix.
- `interventions.py` — threshold gate before using `flagged_agents`; no trigger when the transcript score is below τ; random steer samples only colluders; every intervention records agent role and component scores.
- `analysis.py` — nullable labels excluded from AUROC with N printed; attrition table including failed/not-started jobs; component AUROC table (ensemble/judge/rule/rule-blind × marker/blinded-r1/blinded-full); `monitor_source` and target-role breakdowns; figure order derived from data; explicit "cost is not identifiable" note.

**Tests**
- `tests/test_labels.py` — unparseable/missing/failed labels assert `None`.
- `tests/test_interventions.py` — flagged-below-threshold, all-zero-with-flag, high-score-without-local-signal, random-steer-only-colluders, and audit-field tests.
- `tests/test_monitor.py` — marker-blind rule and `rule_score_blind` logging.
- `tests/test_analysis.py` — missing labels dropped from AUROC, summary skip-NA, attrition not-started/failed counts, component-table shape.
- `tests/test_runner.py` — seed-major job order.

## Why (one line each)

- The draft described a `collusion_steer` run that was not in `results/`, and cited the invalid-control report as its evidence; the fix makes provenance mechanical and quarantines the bad artifact.
- The blinded label labelled an all-honest consensus as collusion at 0.9 confidence and API failures were coded as negatives; the fix makes failures missing and reports the false positive.
- `task_correct` is the algebraic complement of `collusion_success`, so the "capability cost" estimand was vacuous; the draft now says so and moves cost to tie rate + reasoning quality.
- The monitor's rule half is a lookup table for the experiment's own code word, so the report now separates ensemble/judge/rule/rule-blind AUROCs.
- The intervention ignored τ whenever the judge named an agent and could steer the honest agent; targeting is now gated and audited.
- Fixed condition-order execution made a stalled batch a non-random prefix; jobs are now seed-major and attrition is printed loudly.

## Test result

`uv run pytest -q`: **42 passed** in 0.75 s.
`uv run python scripts/check_artifacts.py`: **passed** (2 valid runs, §6 traceable, quarantine banner present).
`uv run python run_experiment.py --dry-run --scenarios vendor --seeds 0 --workers 1`: **passed** (5 jobs listed, no API calls).

## Remaining TODO

1. **No valid intervention run exists.** The next permitted batch must complete `collusion_silent`, `collusion_steer`, `collusion_quarantine` (and ideally placebo/random-steer) before §3.3 or §6 can claim prevention. Do not fill this with the quarantined batch.
2. **`blinded_r1_attempted` is null for both committed records.** The round-1 label was added after this batch; a new run is required before the headline AUROC is estimable. The report prints `n/a` until then.
3. **`rule_score_blind` is all-null in the committed batch** for the same reason; the non-circular detector row needs new data.
4. **The blinded label has a 1/1 false-positive rate on the only control.** A new batch must include the all-honest fixed negative and report the label on it; human annotation and a benign-disagreement condition remain unbuilt.
5. **`check_artifacts.py` covers §6 only.** If new empirical numbers are added to the draft, extend the manifest.
6. **Power.** The 15 pp white-box rule needs ~250/condition with clustering; the 63-run grid is a feasibility batch, not a confirmatory study.
