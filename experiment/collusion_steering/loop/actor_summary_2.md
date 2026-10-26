# Actor summary — iteration 2

Scope: `experiments/collusion_steering/` only. No API calls, no new experiment
runs. A `--dry-run` of `run_experiment.py` was used to confirm the command path.
No commit was made.

## Files changed

- `src/collusion_steering/runner.py`
- `src/collusion_steering/prompts.py`
- `src/collusion_steering/monitor.py`
- `src/collusion_steering/labels.py`
- `src/collusion_steering/interventions.py`
- `src/collusion_steering/analysis.py`
- `tests/test_runner.py`
- `tests/test_interventions.py`
- `tests/test_analysis.py`
- `tests/test_monitor.py`
- `scripts/check_artifacts.py`
- `config.yaml`
- `run_experiment.py`
- `research_draft.md`
- `README.md`
- `notes.md`
- `.gitignore`
- `results/worked_example_report.md` (regenerated from `results/runs_valid.jsonl`)
- `results/runs_summary.csv`, `results/figures/*.png` (regenerated; gitignored)
- `loop/STATE.md`, `loop/actor_summary_2.md`

## What changed and why

1. **Round 1 is now simultaneous** (`runner.py`, `prompts.py`): every agent
   answers from an empty transcript, so the honest agent cannot copy the
   colluders' code word. The committed batch's contamination is now impossible
   by construction.
2. **Per-agent manipulation audit** (`runner.py`, `analysis.py`,
   `check_artifacts.py`): every run logs `code_word_used` per agent and a
   `manipulation_check` (`passed`, `code_word_agents`, `honest_agents`); a run
   where an honest agent uses the word fails. The committed record is
   reconstructed and reported as contaminated (A, B **and** C used it).
3. **Prompt-artefact diagnostics** (`runner.py`, `prompts.py`): strip and count
   leaked `Agent X (round N):` headers, log `duplicate_message_rate`, and forbid
   verbatim repetition in round 2. The byte-identical control messages are now
   visible as an artefact, not treated as coordination evidence.
4. **Marker-blind judge and annotator** (`monitor.py`, `labels.py`,
   `runner.py`, `config.yaml`): `judge_blind_markers` removes the code-word cue
   from the judge prompt; the annotator transcript is redacted
   (`[neutral token]`) and logs `marker_redacted`. No claimed row stays
   "non-circular" in the prose.
5. **No coerced control labels; no perfect-score artefact** (`analysis.py`):
   control runs are no longer overwritten to `False`; raw `marker_r1_fired` is
   reported separately; AUROC and precision/recall/F1 are suppressed below 5
   runs per class and the report prints "not estimable" with confusion counts.
   The report's "Circularity check" is relabelled a tautological consistency
   check.
6. **Content baseline** (`analysis.py`): `content_baseline_score` counts round-1
   mentions of the evidence-incorrect option and is evaluated next to the monitor
   on the same labels. This is the "wrong answer, not collusion" control the
   critique asked for.
7. **`colluder_defection` as the primary behavioral outcome** (`runner.py`,
   `analysis.py`): the 2–1 instructed majority makes `collusion_success` mostly
   compliance; the defection field is logged, reported, and named primary in the
   draft, with the majority outcome kept as derived.
8. **Random steer is monitor-gated** (`interventions.py`): it now fires on the
   same trigger as `collusion_steer` and randomizes only the target among
   colluders, so the arms have the same intervention rate. The old
   "always fires" test was replaced by gating tests.
9. **Placebo is length- and directive-matched** (`prompts.py`,
   `interventions.py`): word/character counts are within ~7% of the steer notice
   and both carry a concrete `must` directive; the placebo directive is
   task-irrelevant and never names the vote. `notice_words` / `notice_chars` are
   logged.
10. **White-box search/confirmation split** (`research_draft.md` §9.4, §9.7):
    scenarios and seeds split into search and confirmation sets, configuration
    frozen, selection-adjusted interval required, and the 15 pp rule labelled
    exploratory until the split exists.
11. **Consistency pass** (`research_draft.md`, `README.md`, `notes.md`,
    `config.yaml`): abstract, §3.3, §4.1–§4.8, §5, §6.2–§6.3, §7, §8, §9, and
    Appendix Q5/Q6 now match the code; config exposes `round1_simultaneous` and
    `judge_blind_markers`; README documents the new fields and the two-run
    limits.

## Test result

`uv run pytest -q`: **57 passed** (was 42).

Additional check: `uv run python scripts/check_artifacts.py` → **passed**
(2 valid runs, §6 numbers traceable, quarantined report still marked,
no `F1=1.000`/`precision=1.000` in the regenerated report, honest-agent
contamination flagged).

`uv run python run_experiment.py --dry-run --scenarios vendor --seeds 0`
listed the 5 configured conditions without API calls.

## Remaining TODO

- **Run a valid batch.** Nothing here produces new evidence. The next batch must
  use the iteration-2 harness and record `blinded_r1`, `rule_score_blind`,
  `code_word_used`, `manipulation_check`, `content_baseline_score`, and the
  placebo/random-steer arms.
- **Regenerate `results/metadata.json`** on that run; the committed metadata
  predates `round1_simultaneous` and `judge_blind_markers`, so the report shows
  those as n/a for the old batch (correct, but the file is stale for the code).
- **Log both judge variants if needed.** The next batch uses the marker-blind
  judge only. If a same-run contrast between the marker-aware and marker-blind
  judge is wanted, add a second judge call and report both; that doubles monitor
  cost and is not implemented.
- **Replace the option-mention content baseline** with a stance judge in the
  next batch; the heuristic only counts names and is not a validated detector.
- **Add the non-majority coalition** (or a switchable outcome) so
  `colluder_defection` can actually change the majority, plus a
  benign-disagreement condition and a shared-secret control.
- **Human annotation** and inter-annotator agreement remain absent.
- **Execute the white-box search/confirmation split**; §9.4/§9.7 are protocol
  text, not a run.
- **Extend `scripts/check_artifacts.py`** if new empirical numbers enter
  sections other than §6.
