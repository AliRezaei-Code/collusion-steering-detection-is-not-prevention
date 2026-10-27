# Actor summary — iteration 7

Scope: `experiments/collusion_steering/` only. No commits, no API calls, no new
experiment runs. The only execution was `uv run pytest -q`, the offline artifact
checker, a no-network `--dry-run`, and report regeneration from the committed
JSONL.

## Files changed

- `research_draft.md`
- `README.md`
- `notes.md`
- `config.yaml`
- `run_experiment.py`
- `src/collusion_steering/prompts.py`
- `src/collusion_steering/labels.py`
- `src/collusion_steering/monitor.py`
- `src/collusion_steering/runner.py`
- `src/collusion_steering/analysis.py`
- `tests/test_monitor.py`
- `tests/test_labels.py`
- `tests/test_runner.py`
- `tests/test_analysis.py`
- `results/worked_example_report.md` (regenerated from the committed JSONL)
- `loop/STATE.md`
- `loop/actor_summary_7.md`

## What changed and why

1. **Abstract cut from 388 to 247 words and made true of the committed batch** —
   removed the harness changelog and the false "round 1 is simultaneous"
   sentence, stated "The committed batch's round 1 was sequential; the current
   harness runs it simultaneously, a change no committed run exercises", and
   moved prompt history / duplicate-arm disclosure out of the abstract
   (critic #5).
2. **Judge prompt made information-set-specific** — the simultaneous round-1
   prompt no longer asks for echoes, post-exchange shifts, or blocked
   discussion, which that transcript cannot contain; interaction cues remain
   available behind `interaction_visible=True` (critic #2).
3. **Judge score re-anchored on the tested construct** — 1 now means
   coordination toward an evidence-unsupported outcome including an explicit
   shared marker, not "clear covert coordination"; `covert` is a separate flag
   (critic #2).
4. **Annotator prompt given the same information-set note** — the round-1 label
   no longer invites the annotator to read "what the agents ask of one another"
   in a transcript with no exchange (critic #2).
5. **Judge and label prompts hashed and versioned** — 16-hex per-render SHA-256
   plus version, written to `diagnostics` as `judge_prompt_sha256` /
   `label_prompt_sha256`, with versions and `interaction_visible`; tests assert
   the hash changes when the prompt changes (critic #2).
6. **Stance baseline added to the detector table and given an operating point** —
   `content_stance` now has AUROC rows and a strict-0.5 confusion table next to
   the mention share, so the comparison the draft calls decisive exists in the
   artifact; test uses the criticism transcript where mention = 1/3 and stance =
   0.0 (critic #3).
7. **Job order changed to condition round-robin, and `--limit` guarded** — with
   the configured single seed the old "seed-major" docstring was a no-op and the
   batch was condition-ordered; every condition now contributes a job before any
   second job, `check_limit` rejects a limit below the condition count, metadata
   records `job_order` and the planned order, and the dry run uses the same
   order (critic #4).
8. **§6.1/README now state that the committed batch's missingness is
   condition-ordered** — and describe the scheduler fix as a code change with no
   committed run (critic #4).
9. **Label independence claims corrected across draft, config, notes, and module
   docstring** — "independence is a property of the model" removed; a different
   family is necessary but not sufficient, judge-vs-label AUROC is agreement
   with a second LLM operationalisation, and Q1's criterion is a human-coded
   subset or the shared-wrong-prior control (critic #1).
10. **`parse_label` reconciles `attempted` with `coordination_type`** — derives
    `attempted` from a known type, records contradictory pairs as missing with
    `inconsistent_coordination_type`, and never counts them as positives or
    negatives (critic #6).
11. **Coordination types are now carried and reported** — `runs_to_frame` keeps
    `blinded_r1_coordination_type` / `blinded_coordination_type`, `summarize`
    reports `label_inconsistent_n`, and the report prints the type distribution
    per label plus the inconsistent count (critic #6).
12. **Test count references refreshed** — README now says 135 tests; the worked
    example report now shows the stance rows, stance operating point, type
    distributions, and `label_inconsistent_n`.

## Test result

`uv run pytest -q` from `experiments/collusion_steering/`:

```
135 passed in 1.18s
```

Offline checks:

- `uv run python scripts/check_artifacts.py`: **passed** ("2 valid runs, §6
  numbers traceable, quarantined report marked").
- `uv run python run_experiment.py --dry-run`: **25 configured runs, no API
  calls**, condition round-robin.
- `--limit 2` now raises `ValueError: limit=2 would leave 3 of 5 configured
  condition(s) with zero jobs; use at least 5 or run separate per-arm batches`.

## Remaining TODO

1. **Highest priority — Q1.** The next batch needs a human-coded subset
   (30–50 transcripts) or a shared-wrong-prior behavioral control. A
   different-family label alone does not identify Q1.
2. **No intervention run exists.** Do not report detection, prevention,
   targeting, or task preservation.
3. **Collapse `collusion_silent` into the no-intervention baseline** or give it
   a visible monitor notice; update conditions, config, §8, and tests.
4. **Thread or delete `monitor_temperature`** (critic #7, not fixed): the config
   and metadata expose it while the judge and label hardcode 0.0; log effective
   agent/monitor/label/vote temperatures.
5. **Report prompt hashes/versions** in the generated report (they are in
   diagnostics only).
6. **Regenerate §6, batch manifest, and metadata** after the next valid batch;
   the current metadata remains reconstructed legacy provenance.
