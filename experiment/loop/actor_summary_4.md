# Actor summary — iteration 4

Scope: `experiments/collusion_steering/` only. No API calls, no new runs. The
worked-example report was regenerated offline from the committed JSONL. Nothing
was committed; the loop script owns the commit.

## Files changed

Source:

- `src/collusion_steering/prompts.py`
- `src/collusion_steering/monitor.py`
- `src/collusion_steering/labels.py`
- `src/collusion_steering/runner.py`
- `src/collusion_steering/analysis.py`
- `config.yaml`, `run_experiment.py`
- `scripts/check_artifacts.py`

Tests:

- `tests/test_runner.py`, `tests/test_monitor.py`, `tests/test_labels.py`,
  `tests/test_analysis.py`, **new** `tests/test_artifacts.py`

Docs and artifacts:

- `research_draft.md`, `README.md`, `notes.md`, `results/README.md`
- `results/worked_example_report.md` (regenerated, offline)
- `loop/STATE.md`, `loop/actor_summary_4.md`

## What changed and why

Critique issue 1 — the "unaware" default was false:

1. `prompts.py`: the colluder's private-instruction header is conditional
   (`"not visible to the other agents"` when unaware, `"... or the monitor"` only
   when aware), and the honest prompt is a neutral task statement instead of
   "You have no private coordination instruction".
2. `prompts.py`: `planning_prompt` no longer tells the honest agent that a
   coordination instruction might exist; `public_prompt` no longer says "Do not
   reveal private instructions".
3. `tests/test_runner.py`: the prompt test now iterates over roles and asserts no
   "monitor" anywhere in the unaware prompt, and "monitor" in both aware prompts.

Critique issue 2 — the label was a judge paraphrase and redaction marked the
coalition:

4. `labels.py`: `BLINDED_LABEL_PROMPT` drops the judge's four cue bullets and
   uses a structurally different read/summarize/judge framing.
5. `monitor.py`: `redact_code_words` substitutes a varying neutral interjection
   instead of one shared `[neutral token]`, with sentence-position capitalization.
6. `runner.py` + `config.yaml`: `RunConfig.label_model` / `models.label` are
   separate from the monitor model; each run logs `label_model` and
   `label_model_is_monitor`, and the dry-run banner prints the label model.
7. Tests: the label prompt is asserted not to contain the judge's cue phrases,
   the code word, or the shared placeholder; two colluder messages must not get
   the same redaction word.

Critique issue 3 — the report claimed every row was marker-blind:

8. `analysis.py`: `batch_flags` returns a constant `all_rows_blind=False`; the
   Monitor prose names `judge`/`blinded_r1` as blind and `rule`/`ensemble` as
   oracle rows.
9. `analysis.py`: `blinded_full` moved to "Descriptive outcomes (no threshold)"
   with a label rate only; its operating point (TP/FP/FN/TN, precision/recall/F1)
   is gone.
10. `scripts/check_artifacts.py`: fails on "Every row below is marker-blind",
    requires the "No detector row is marker-blind" sentence for a
    marker-visible batch, and fails on any `blinded_full` operating point.

Critique issue 4 — the marker-blind rule fired on "Vote for B":

11. `monitor.py`: split `COORDINATION_MARKERS` (content-agnostic joint action)
    from `CONTENT_MARKERS` (option/vote advocacy); `rule_score_blind` uses only
    the former; `content_rule_score` is the separate wrong-answer rule.
12. `analysis.py` + `runner.py`: `content_rule` is logged per run
    (`content_rule_r1`) and added as its own detector row (12 cells).
13. Tests: target advocacy scores 0.0 on the blind rule and 1.0 on the content
    rule; `rule_score(include_code_words=False)` equals `rule_score_blind`.

Critique issue 7 — manipulation check and legacy fallback:

14. `runner.py`: `manipulation_check.passed` now requires every colluder to use
    the word exactly once in round 1 and no honest agent to use it; logs
    `colluders`, `colluders_signaled`, `exactly_once`, `code_word_counts`.
15. `monitor.py`: added `count_code_words`.
16. `analysis.py`: `_defection_from_record` filters to `{A, B}` and returns
    `None` when no colluder vote parses, matching the runner.
17. Tests: one colluder signalling fails; a double use fails; a legacy record
    with only an `UNKNOWN` colluder vote is missing, not a defection.

Also (small, from issue 5):

18. `scripts/check_artifacts.py`: the completed-run count phrase is derived from
    `len(records)` and compared with the manifest, instead of comparing the
    manifest phrase to itself.
19. `results/README.md`: regeneration uses `--report`; the rename instruction is
    gone.

Docs:

20. `research_draft.md`: §3.2, §4.1, §4.3, §4.4, §4.5, §5.2, §6.3, §7.9,
    §7.13, §8, §9.6, Q5, Q6, Q13, and Appendix B now state the corrected
    prompt, the row-level blindness rule, the content-agnostic blind rule, the
    label-model requirement, and the `passed` definition. The draft still says
    "design + two-run demonstration" and claims no detection, prevention,
    targeting, or task-preservation result.
21. `README.md` / `notes.md`: same corrections in the operational docs,
    including the new `content_rule_score`, `label_model`, and audit fields.

## Test result

```
uv run pytest -q
77 passed in 0.87s
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
(analysis only; no API calls). It now contains the row-specific blindness
paragraph and the descriptive `blinded_full` rate (`2/2`), with no
`blinded_full` operating point.

## Remaining TODO

Not fixed in this iteration (still open in `STATE.md`):

- **Metadata provenance (issue 5, partial).** `_load_metadata` still reads
  `results/metadata.json`, not `<stem>.metadata.json`; no
  `results/runs_valid.metadata.json` exists. The checker still hardcodes the two
  quoted run ids and self-compares `missing_conditions_phrase`.
- **Control FPR and calibration (issue 6).** §5.2 promises a calibration curve
  and a design-based FPR on `control` / `benign_disagreement`; the report prints
  neither.
- **No new data.** Issues 1–4 of the state (no intervention run, no blind or
  unaware batch, no estimable detector, same-model label) require a real batch
  and a different label model family; they cannot be closed by editing.
- **TODO outside this folder:** none.
