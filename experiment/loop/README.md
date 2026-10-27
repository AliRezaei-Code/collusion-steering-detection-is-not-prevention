# Critic–actor loop

This folder runs an autonomous critic → actor loop over the collusion-steering
pilot. It is intentionally separate from the paper artifacts so the loop's
history is auditable.

## Files

| File | Purpose |
| --- | --- |
| `STATE.md` | Shared state: branch, hard rules, open issues, next priority. |
| `prompts/critic.md` | Critic instructions (template with `{{ITER}}`). |
| `prompts/actor.md` | Actor instructions (template with `{{ITER}}`). |
| `critiques/critic_<N>.md` | One critique per iteration, written by the critic. |
| `actor_summary_<N>.md` | One actor summary per iteration. |
| `logs/iteration_<N>.log` | Raw output of the critic, actor, and tests. |
| `CHANGELOG.md` | One line per iteration with exit codes and test status. |
| `HEARTBEAT` | Latest iteration and timestamp. |
| `DONE.md` | Written when the loop finishes. |
| `orchestrator.py` | The loop driver. |

## Run

```bash
cd experiments/collusion_steering
python3 loop/orchestrator.py
```

The orchestrator runs for **2 hours** (`DURATION_SECONDS = 7200`), or until
`MAX_ITER`, whichever comes first. It commits after every iteration and writes a
heartbeat.

## Rules

- Work only in `experiments/collusion_steering/`.
- No fabricated results, no paid API calls, no new experiment runs.
- Tests must pass or the failure must be recorded.
- Every iteration is committed; the actor does not commit.
