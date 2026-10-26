# Actor summary — iteration 6

Scope: `experiments/collusion_steering/` only. No API calls, no new runs, no
commits. Offline regeneration and a `--dry-run` only.

## Files changed

Code
- `src/collusion_steering/conditions.py` (new) — one canonical condition set and
  policy map.
- `src/collusion_steering/analysis.py` — legacy-safe judge status, per-label N,
  batch-metadata preference, endorsement-stance baseline, report prose.
- `src/collusion_steering/labels.py` — collusion-specific label prompt and
  three-way `coordination_type`.
- `src/collusion_steering/monitor.py` — removed the hardcoded `["A","B"]`
  flagged-agent fallback; added `flag_source`.
- `src/collusion_steering/interventions.py` — validated condition dispatch;
  explicit `colluder_only` random steer; raises on unknown conditions.
- `src/collusion_steering/runner.py` — validates conditions before any call;
  records `blinded_r1_coordination_type`.
- `run_experiment.py` — validates `--conditions` before dry-run or jobs.
- `scripts/check_artifacts.py` — manifest-driven `quoted_run_ids`; derives the
  missing-conditions phrase instead of comparing it to itself.

Tests
- `tests/test_conditions.py` (new) — typos/duplicates raise; steer can target C;
  random steer is colluder-only; baselines never intervene.
- `tests/test_analysis.py` — stance score, missing-not-zero stance, legacy judge
  status, split label counts, metadata preference, control-sentence wording.
- `tests/test_labels.py` — prompt asks the collusion construct; Appendix B quote
  matches the code; `coordination_type` parsing.
- `tests/test_monitor.py` — no fabricated A/B coalition on rule fallback or a
  judge response without names.
- `tests/test_runner.py` — `build_jobs` and `run_one` reject mistyped conditions
  before any API call.

Docs / artifacts
- `research_draft.md` — Abstract, §3.3, §4.2, §4.4–§4.8, §5.2–§5.3, §6.1, §6.3,
  §8, §9.7, §10, Appendix B, Q5.
- `README.md`, `notes.md`, `config.yaml` — same changes in the operational docs.
- `results/batch_manifest.json` — `configured_conditions`, `quoted_run_ids`.
- `results/runs_valid.metadata.json` (new) — reconstructed legacy flags.
- `results/worked_example_report.md` — regenerated offline.
- `loop/STATE.md`, `loop/actor_summary_6.md`.

## What changed and why (one line each)

1. Prompt asks whether agents coordinated toward an outcome **not justified by
   the evidence**, with `independent`/`benign`/`collusive`; the old coordination
   question is satisfied by honest consensus, so its control positive was not a
   collusion false positive (critic #1).
2. Appendix B now quotes the code sentence and a test enforces it, so the
   documented prompt cannot drift from `BLINDED_LABEL_PROMPT` (critic #1).
3. Report says the committed control positive came from the earlier prompt and
   is **not** an FPR for the current label; no rate is transferred (critic #1).
4. `content_baseline_score` is documented and labelled as a **mention-share**
   heuristic; criticism of the target counts as a mention (critic #2).
5. New `content_stance_score` counts only explicit endorsements per sentence and
   treats criticism/negation as opposition; missing when nobody endorses
   (critic #2).
6. Report prints the stance row, the criticized-or-ambiguous share, and requires
   the monitor to beat the stance row; no value is invented for the collusion run
   (it is missing) (critic #2).
7. Removed `flagged_agents=["A","B"]` from all `score_transcript` paths; the
   judge's nomination is no longer synthesized from the known coalition (critic
   #3).
8. `flag_source` records whether the judge named an agent; the only fallback is
   the role-agnostic per-agent rule score (critic #3).
9. Random steer is explicitly `target_selection="colluder_only"` and the draft
   drops the false "null by construction" claim because steer can target C
   (critic #3).
10. Draft/README now specify a target-role analysis and the judge-nomination vs
    selected-target audit (critic #3).
11. `conditions.py` centralizes names and policies; `run_experiment.py`,
    `build_jobs`, `run_one`, and `apply_intervention` raise on unknown,
    duplicate, or whitespace-differing names (critic #5).
12. Tests cover a trailing-space typo and an unknown name reaching the
    intervention layer, the same failure class as the invalid control batch
    (critic #5).
13. `judge_status` returns `unknown/legacy` when `judge_prompt_variant` is
    absent, matching the design-flags line instead of contradicting it (critic
    #6).
14. Summary reports `blinded_r1_n` and `blinded_full_n` separately, so a null
    round-1 label no longer shows the full label's N (critic #6).
15. `write_report`/`analyze` prefer `<stem>.metadata.json`; the shared file is a
    fallback only, and `results/runs_valid.metadata.json` is committed (critic
    #6).
16. The checker derives the missing-conditions phrase from
    `configured_conditions` and reads `quoted_run_ids` from the manifest instead
    of hardcoding two ids or comparing a phrase to itself (critic #6).
17. §5.3 replaces the 0.5 baseline with the two-proportion formula and a
    baseline range (0.7–1.0), labels 0.5 as an illustrative worst case, and
    updates §8/§9.7 so the grid is no longer sized from a contradiction
    (critic #4).
18. Docs record that fewer than 5 per class still suppresses AUROC, and no
    result is promoted from the two-run batch.

## Test result

`uv run pytest -q` from `experiments/collusion_steering/`: **125 passed** (was
94). `uv run python scripts/check_artifacts.py`: **passed** (2 valid runs, §6
numbers traceable, quarantined report marked). `uv run python
run_experiment.py --dry-run`: **25 configured runs, no API calls**. Ruff on the
touched modules: clean.

## Remaining TODO

- **No intervention run exists.** `collusion_steer`, `collusion_quarantine`,
  `collusion_placebo`, and `collusion_random_steer` still have zero completed
  runs; the "design + two-run demonstration" framing stays.
- **Q1 is still not identified.** The new prompt has never been run and has no
  measured control FPR. The next batch needs a pre-intervention interaction
  round or a shared-wrong-prior control.
- **`collusion_silent` is still a duplicate** of `collusion_none` in code; the
  grid is still seven labels / six distinct treatments. Not collapsed in this
  iteration.
- **Label is same-model** (free tier); judge-vs-label agreement is not
  validation.
- **Stance score is a word-list heuristic**, not the promised stance judge, and
  the committed collusion run has no explicit endorsement (score missing).
- **Not run in this iteration:** calibration curve and design-based control FPR
  promised in §5.2; human annotation; shared-secret, benign-disagreement, and
  shared-wrong-prior controls; search/confirmation split and selection-adjusted
  interval for §9.4/§9.7.
