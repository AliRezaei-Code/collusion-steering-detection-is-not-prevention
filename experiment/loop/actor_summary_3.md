# Actor summary — iteration 3

## Files changed

- `src/collusion_steering/runner.py`
- `src/collusion_steering/prompts.py`
- `src/collusion_steering/analysis.py`
- `run_experiment.py`
- `scripts/check_artifacts.py`
- `tests/test_runner.py`
- `tests/test_analysis.py`
- `config.yaml`
- `research_draft.md`
- `README.md`
- `notes.md`
- `results/batch_manifest.json` (new)
- `results/worked_example_report.md` (regenerated, no new runs)
- `pyproject.toml` + `uv.lock` (pytest dev dependency so `uv run pytest` uses the project venv)
- `loop/STATE.md`

## What changed and why

1. **Manipulation check is round-1 only.** `manipulation_check` now takes
   `messages_by_agent`; the runner passes round 1, which is what the monitor and
   the headline label see. Round-2 use is logged as
   `code_word_round2_agents` and per-agent `code_word_used_r1` / `_r2`.
2. **Round 2 is simultaneous.** Each agent answers from the round-1 transcript
   plus its own notice, then the round is assembled. This removes the
   last-speaker asymmetry and stops round-2 order from being a treatment.
   `round2_simultaneous` is logged.
3. **Prompt now matches the protocol.** The planning sentence appears only when
   `private_planning` is true and the monitor sentence only when `awareness` is
   true (default false). Each run logs both flags and a
   `system_prompt_sha256`; batch metadata records them. The draft now says the
   committed batch is an aware run with a phantom planning turn.
4. **Parse failures are missing, not defections.** `defectors` is computed only
   over votes in `{A,B}`; `n_unparseable_colluder_votes` is logged;
   `colluders_complied` is `null` when any colluder vote is unparseable.
   `majority()` returns `UNKNOWN` unless at least two votes parse, so one
   parseable vote cannot decide the committee.
5. **Detection is pre-treatment.** Removed the "runs the monitor did not
   intervene on" restriction (it selected on the score); detection is now on all
   runs with a non-null round-1 label plus a condition-defined monitor-silent
   subset. The detector table drops post-treatment `blinded_full` (10 cells, not
   15); `blinded_full` is a labelled descriptive outcome.
6. **Content baseline has a threshold and a missing rule.** Zero option mentions
   return `None` instead of 0.0; the report prints baseline TPR/FPR at 0.5 next
   to the monitor's operating point.
7. **Report prose is data-derived.** `batch_flags()` computes judge-blind,
   redaction, round-1, and round-2 status; the "no row is marker-blind" /
   "every row is marker-blind" sentences branch on it. Tests build a synthetic
   blind batch and assert the sentences flip.
8. **Artifact checker reads a manifest.** `results/batch_manifest.json` holds
   the committed batch's run ids, count, conditions, and quoted phrases;
   `check_artifacts.py` no longer hardcodes `len(records) != 2`, and it fails if
   the report's marker-blind prose contradicts the batch flags.
9. **Reproducibility claims narrowed.** Metadata is written per batch
   (`<batch>.metadata.json`) with flags and JSONL SHA-256; `--report` writes the
   named report directly. §10 now states that `seed` is a replicate index, not
   an API sampling seed.
10. **Targeting claim dropped.** §4.6 and §5.2 call random steer a robustness
    check with an expected null contrast under exchangeable colluders, not a
    targeting estimand; `intervened_agent_position` is logged.
11. **Power for the primary outcome added as a sensitivity table.** §5.3 now
    states the existing table is for `collusion_success` and gives hypothetical
    per-arm Ns for silent-arm defection rates 0.10/0.20/0.30. No observed
    defection baseline is claimed.
12. **Test environment.** Added `pytest` as a dev dependency so
    `uv run pytest -q` runs the project venv (previously it picked up a system
    pytest without `tabulate`, which the report tests need).
13. **Report regenerated.** `results/worked_example_report.md` was rebuilt from
    `results/runs_valid.jsonl` with the new prose and 10-cell table. No new
    runs, no API calls.

## Test result

`uv run pytest -q`: **65 passed** (0 failed).

Artifact check: `uv run python scripts/check_artifacts.py` — passed.
Dry run: `uv run python run_experiment.py --dry-run --scenarios vendor --seeds 0 --workers 1` — 5 conditions enumerated, no API calls.

## Remaining TODO

- Run the first batch with the iteration-3 harness (unaware prompt, simultaneous
  rounds, round-1 check, blind judge, redacted annotator) and record every new
  field. Until then no detector, prevention, targeting, or task-preservation
  claim is supported.
- Add a non-majority coalition (or a switchable outcome) so
  `colluder_defection` can identify persuasion rather than compliance.
- Replace the option-mention content baseline with a stance judge and estimate
  its operating point on a labelled batch.
- Execute the white-box search/confirmation split; the 15 pp rule stays
  exploratory.
- Add human annotation, benign-disagreement, and shared-secret controls.
- Optionally pass a sampling seed and record `system_fingerprint` where the
  provider supports it; otherwise report replicate variance.
