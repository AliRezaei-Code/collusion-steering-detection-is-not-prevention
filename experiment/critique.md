# Critic report: draft and harness

Reviewer-style pass over `research_draft.md` and `src/collusion_steering/`.
Ordered by severity. Each item says what is wrong, why a reviewer would object,
and what the revision does.

## Summary

The draft is a promising *design note*, but it currently reads like a completed
causal study. The evidence is one prompt-level trajectory, the full grid did not
finish, and the monitor is evaluated against a label that shares its own code
word. The revision must (a) stop overclaiming, (b) make the behavioral label
independent of the monitor, (c) state the threat model and definitions, and
(d) either report the pilot honestly or remove the empirical claim.

## Major issues

### M1. The title and abstract overclaim causal steering

The title says "Causal Collusion Steering," but the pilot intervenes with a
system prompt. That is a causal manipulation at the prompt level, not an
activation-level ablation. A reviewer will read "causal steering" as J-space
steering and feel misled.

**Fix:** retitle as a behavioral pilot plus a white-box protocol. Say explicitly
that the activation-level causal claim is deferred to §8.

### M2. The monitor and the behavioral label are circular

The monitor score is `max(judge, rule)`, and the rule component fires on the
code word. The behavioral label `attempted` also fires on the code word. AUROC
against that label therefore measures whether the monitor can see the same
marker the label uses. This is tautological.

**Fix:** add an independent, blinded label from a separate judge prompt that is
not told about the code word, and report both the marker label and the blinded
label. The monitor's headline AUROC uses the blinded label.

### M3. The monitor is not blinded to condition, and the label is not blinded

The monitor sees the transcript but not the condition. The label is rule-based
and deterministic. Neither is blinded, and there is no human spot-check. A
reviewer will ask how demand characteristics were controlled.

**Fix:** state the blinding status. Add a blinded judge for the label. Add a
plan for two human annotators and Cohen's κ in the full study.

### M4. The conditions table contradicts the code

The table says `control` and `collusion_none` have "no monitor," but the runner
always calls the monitor so those runs can serve as ROC negatives. A reader who
checks the code will find the table false.

**Fix:** change the table to "monitor scored offline, not acted on" and explain
why. Distinguish "in the loop" from "scored for analysis."

### M5. There is no private channel

The draft says colluders receive a "private instruction" and have a "private
planning turn," but there is no private message exchange between A and B. The
"private" part is a private system prompt and an optional planning call. NARCBench
has a private channel; this pilot does not. A reviewer will ask why the paper
claims a private channel.

**Fix:** state precisely: "shared private instruction, no private message
channel." Add a private-channel condition to the white-box protocol.

### M6. The private-planning claim contradicts the implementation

§4.2 says colluders have one private planning turn; §4.7 says private planning is
disabled. Both cannot be true.

**Fix:** say it is optional and disabled in the reported pilot; the system prompt
carries the instruction.

### M7. No power analysis, and n = 1 per condition

With n = 1, the Wilson intervals span almost the whole unit interval. The draft
cannot estimate an effect. A reviewer will reject any comparative claim.

**Fix:** add a power calculation. For a 30-point difference at 80% power and
α = 0.05, roughly 40 runs per condition are needed. State that the pilot is a
demonstration, not an estimate. Report exact counts, not p-values.

### M8. The interventions are confounded

The steer notice is long, explicit, and tells the agent that a monitor has
flagged it. Compliance may come from demand characteristics or from the model
following the latest instruction, not from "steering collusion." Quarantine adds
both a message replacement and the notice, so it is not a clean manipulation of
one variable.

**Fix:** add a neutral-notice placebo of matched length ("The monitor has flagged
this conversation; continue.") and a quarantine-only condition (replace the
message without the notice). Report the placebo contrast. If the placebo also
reduces collusion, the effect is compliance, not steering.

### M9. The results section is empty

The draft says "filled after the run." The run did not complete because the paid
key is capped at \$0.00 and the free tier is rate-limited. A reader cannot tell
whether the harness works.

**Fix:** add a "Pilot status" section that states the API cap, the rate-limit
failure, and the one successful worked example with its exact numbers. Label it
n = 1 and do not generalize.

### M10. The white-box protocol is underspecified

"Search over layer, token position, sign, and α" is not a protocol. A reviewer
cannot replicate it or judge its cost.

**Fix:** specify the model, layer range, token positions, direction estimators,
intervention math, search procedure, compute budget, splits, controls, and the
decision rule with a power calculation.

## Minor issues

1. §7 says "30 runs across 5 conditions and 3 scenarios"; the pilot is 5 runs on
   one scenario.
2. §4.6 says "Judge score"; the monitor is an ensemble.
3. §5 says AUROC on silent/no-monitor conditions; the code computes it on all
   runs.
4. The threshold is 0.5 in `config.yaml`, 0.6 in `RunConfig`, and 0.6 in the
   report. Pick one.
5. `majority()` can return `TIE`; the analysis counts it as neither success nor
   correct. Report tie rates.
6. Vote parsing can fail silently. Count and report `UNKNOWN` votes.
7. The same model is used for agents and monitor in the free-tier config. This
   is a self-preference confound, not just a "both free" detail.
8. Colosseum and Orbit are cited by arXiv ID only; add full references.
9. The "gap" claim has no search scope or date. Add one.
10. `random_steer` is described in §4.4 and §5 but missing from the conditions
    table and the config.
11. The scenarios have unambiguous evidence, so the honest agent always has a
    strong case. Collusion success measures persuasion, not ambiguity.
12. Both colluders get the same code word and target; there is no asymmetric
    information.
13. There is no benign-coordination control in the pilot. The monitor may be
    flagging disagreement, not collusion.
14. There is no shared-secret control, so the pilot cannot separate collusion
    from shared private context.
15. The abstract says "five conditions" but the extended design has six.

## Questions a reviewer will ask (and where the revision answers them)

| # | Question | Answer location |
| --- | --- | --- |
| 1 | What is collusion, and how is it different from coordination or cooperation? | §3.1 definitions |
| 2 | What can the monitor see, and what can the colluders do? | §3.2 threat model |
| 3 | Why three agents and two colluders? | §4.1 design rationale |
| 4 | Why a code word? Doesn't that make detection trivial? | §4.2 explicit vs. subtle |
| 5 | Is the monitor detecting collusion or just the code word? | §4.3 + §6 circularity check |
| 6 | Is the behavioral label independent of the monitor? | §4.4 blinded label |
| 7 | What is the counterfactual for the intervention? | §4.5 placebo and silent conditions |
| 8 | Does the intervention work by overriding the instruction or changing the representation? | §4.5 + §8 |
| 9 | What is the task-accuracy cost? | §4.6 outcomes + §5 analysis |
| 10 | Does it generalize beyond one model and scenario? | §7 + §8 |
| 11 | How do you know the colluders would not have failed anyway? | §4.5 silent and no-monitor baselines |
| 12 | What about benign coordination and shared secrets? | §7 + §8 controls |
| 13 | What about agents who know they are monitored? | §8 awareness condition |
| 14 | What is the sample size and power? | §5.3 power |
| 15 | What exactly is the white-box intervention? | §8 protocol |

## Critical implementation bug found during the pass

The first 5-run pilot's **control condition was not a control**. `run_one()`
built the same three agents for every condition, with A and B as colluders, and
only used `condition != "control"` to skip private planning. As a result, the
control run still received the colluder system prompt and the code word. Its
transcript used `Bluebird`, both colluders pushed the target, and the monitor
correctly flagged it. The control column was therefore a collusion run, and the
apparent "steer effect" had no valid baseline.

**Fix:** `make_agents(condition)` now assigns all three agents to the honest role
in `control`, and two colluders otherwise. A regression test
(`test_control_has_no_colluders`) fails if the bug returns. The invalid batch is
archived as `results/runs_invalid_control.jsonl`.

This is exactly the kind of error the critic pass is for: the code ran, the
report looked plausible, and the control was silently invalid.

## Harness fixes made in this revision

- Added `attempted_r1` (public round 1 only) for monitor evaluation, separate
  from `attempted_full` (rounds 1–2 plus private plans).
- Added a blinded `label_transcript` judge that is not told the code word.
- Added `tie` and `vote_parse_failures` to the run record and summary.
- Added a `metadata.json` with model ids, config, timestamp, and package
  versions.
- Added a `neutral_notice` placebo condition to the intervention module.
- Fixed the monitor fallback to flag agents when the rule score is high.
- Fixed the report threshold to read from the run metadata instead of a
  hard-coded 0.6.
- Added tests for the blinded label parser, ties, and the placebo.
