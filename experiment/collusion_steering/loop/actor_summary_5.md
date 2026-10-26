# Actor summary — iteration 5

Scope: `experiments/collusion_steering/` only. No API calls, no new runs. The
worked-example report was regenerated offline from the committed JSONL. Nothing
was committed; the loop script owns the commit.

## Files changed

Source:

- `src/collusion_steering/labels.py`
- `src/collusion_steering/monitor.py`
- `src/collusion_steering/scenarios.py`
- `src/collusion_steering/analysis.py`
- `scripts/check_artifacts.py`

Tests:

- `tests/test_labels.py`
- `tests/test_monitor.py`
- `tests/test_analysis.py`
- `tests/test_artifacts.py`

Docs and artifacts:

- `research_draft.md`, `README.md`, `notes.md`, `config.yaml`
- `results/README.md`
- `results/report_invalid_control.md` (replaced with a provenance note)
- `results/worked_example_report.md` (regenerated, offline)
- `loop/STATE.md`, `loop/actor_summary_5.md`

## What changed and why

Critique issue 5 — parsers fabricated negatives:

1. `labels.py`: `parse_label` accepts only real booleans, integer `0`/`1`, and
   `true`/`false`/`yes`/`no`; any other value is `attempted=null` with a
   `parse_error` and the raw response kept for audit, so `"uncertain"` and lists
   are missing, not confident negatives.
2. `monitor.py`: a missing or non-numeric `collusion_score` yields
   `judge_score=null`, `judge_score_present=false`, and
   `source="judge_missing_score"`; the ensemble falls back to the rule instead of
   recording a fabricated `0.0`.
3. Tests: `"uncertain"`, a list, integer `1`, a missing score, and a
   non-numeric score.

Critique issue 3 — ties and `UNKNOWN` were counted as failures:

4. `analysis.py`: added `decidable`, `collusion_success_decidable`,
   `task_correct_decidable`, and `undecidable`; headline `success_rate` /
   `task_correct_rate` now use the decidable denominator with `n_decidable`,
   and the all-run rates are kept as `*_rate_all`.
5. `analysis.py`: `ci_table` drops missing rows, so Wilson intervals use the
   same denominator; the two figures and the §9.7 rule use it too.
6. Report: new decidable-denominator paragraph, decidable CI headings, and a
   diagnostics table with `decidable`, `ties`, `undecidable`, and
   `content_baseline_missing`.
7. Test: target/correct/tie records give `success_rate=0.5` (not 1/3),
   `n_decidable=2`, with the tie visible separately.

Critique issue 4 — the content baseline missed natural phrasing and used `>=`:

8. `scenarios.py`: per-scenario keyword stems for both options, matched with a
   leading word boundary (`approv`, `escalat`, ...), plus `option_keywords()`.
9. `analysis.py`: `content_baseline_score` counts keyword stems, so "I would
   approve"/"we should escalate" count; zero hits remains missing. The summary
   and report print the missing rate per condition.
10. `analysis.py`: `monitor_operating_point(..., strict=True)` supports a strict
    `>` threshold; the baseline uses it at 0.5, so an exact 50/50 split is
    negative. The monitor keeps `>= tau`.
11. Tests: exact-0.5 boundary (strict vs inclusive), non-verbatim
    "approve"/"escalate", and zero-mention missingness.

Critique issue 6 — the report misstated row blindness and omitted audit fields:

12. `analysis.py`: `detector_status()` and `blindness_sentence()` encode
    row-specific status (judge blind only when its prompt variant says so;
    `rule_blind` blind by construction even with no score; `rule`/`ensemble`
    always oracle; content rows content-sensitive) and the report prints a
    per-detector table.
13. `analysis.py`: the control false-positive sentence is computed from the
    frame; the per-run table pairs `blinded_r1` with `blinded_r1_evidence` and
    prints `blinded_full_evidence` separately.
14. `analysis.py`: `runs_to_frame` now carries `intervened_agent_position`,
    `notice_words`, `notice_chars`, `n_unparseable_colluder_votes`,
    `colluders_complied`, `round2_simultaneous`, label parse errors, and
    `judge_score_present`; the report prints the intervention position/notice
    lengths and a per-run colluder audit.
15. Tests: judge-blind-only vs redacted-only batches, `rule_blind` by
    construction, round-1/full evidence disagreement, computed control rate,
    intervention position/notice lengths, and the unparseable-vote audit.

Critique issue 1 — the headline label had no interaction to read:

16. `research_draft.md`: §3.3, §4.1, §4.5, §4.8, §5.2, Q5, Q6, the abstract,
    and the README/notes now call `blinded_r1` a **shared-target-advocacy**
    label and state that Q1 is not identified by it; the two acceptable fixes
    (interaction round or shared-wrong-prior control) are specified.
17. `analysis.py`: the generated report prints the estimand note in the
    per-run-labels section, so the artifact cannot be read as a collusion
    ground truth.

Critique issue 2 (partial) and issue 7:

18. `README.md`, draft §4.7/§8, `config.yaml`, and `notes.md`: the conditions
    table now says the monitor is **called** in every condition and separates
    "intervention delivered"; `collusion_none` and `collusion_silent` are
    labelled duplicate no-intervention baselines, and the 63-run grid is
    corrected to 6 distinct treatments (54 runs collapsed). The code is not
    collapsed; that is the top open item.
19. `results/report_invalid_control.md`: replaced with a provenance note (why
    the batch is invalid, record ids, no promotion, no estimator).
20. `scripts/check_artifacts.py`: bans `AUROC`, `precision=`, `recall=`, `F1=`,
    `TP=`, `success_rate`, and `effect-size` in the quarantined report, requires
    "No estimator is reported", and updated the content-baseline expectations
    (0.429/0.571 → 0.300/0.545) and the marker-blind sentence check.
21. `tests/test_artifacts.py`: asserts the quarantined report stays
    provenance-only.

Also fixed during the work:

22. `analysis.py`: `write_report` no longer crashes when metadata is absent
    (int-vs-None comparison in the attrition warning); regression test added.
23. `README.md`: test count updated.

## Test result

```
uv run pytest -q
94 passed in 1.10s
```

Additional checks (all offline):

```
uv run python scripts/check_artifacts.py
Artifact check passed: 2 valid runs, §6 numbers traceable, quarantined report marked.

uv run python run_experiment.py --dry-run
Configured 25 runs: 5 scenarios × 5 conditions × 1 seeds
```

`results/worked_example_report.md` was regenerated with
`uv run python run_experiment.py --results results/runs_valid.jsonl --report worked_example_report.md`
(analysis only; no API calls).

## Remaining TODO

- **Q1 identification (new top priority).** The label is renamed, but the next
  batch still needs a pre-intervention interaction round or a shared-wrong-prior
  control; otherwise the AUROC is against shared advocacy.
- **Collapse the duplicate arms (issue 2).** Documented in README/draft/config,
  not yet fixed in `analysis.CANONICAL_CONDITIONS`, `interventions.apply_intervention`,
  or `tests/test_interventions.py`.
- **Different-family label model.** Still the monitor model in the free-tier
  config, so judge-vs-label AUROC remains same-model agreement.
- **Metadata provenance (issue 6, partial).** `_load_metadata` still reads the
  shared `results/metadata.json`; no `runs_valid.metadata.json` exists. The
  checker still hardcodes the two quoted run ids and self-compares the missing-
  conditions phrase.
- **Calibration and design-based FPR.** §5.2 promises both on `control` /
  `benign_disagreement`; the report prints neither.
- **No new data.** No intervention run, no blind/unaware batch, no estimable
  detector, and the committed outcome is still compliance.
- **TODO outside this folder:** none.
