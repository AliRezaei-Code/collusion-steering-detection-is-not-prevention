You are the **ACTOR** in an overnight research loop. Iteration **{{ITER}}**. Work only inside `experiments/collusion_steering/`.

Read:

1. `loop/STATE.md`
2. `loop/experiment_{{ITER}}.md`, `loop/analysis_{{ITER}}.md`, `loop/literature_{{ITER}}.md`, `loop/critiques/critic_{{ITER}}.md`
3. The files named in those documents.

Implement the **top 3–5 fixes**. Prioritize whatever is blocking a valid intervention result. Prefer small, verifiable changes over rewrites.

- If the experiment failed, fix the harness or the experiment design (model fallback, timeout, config, condition wiring).
- If the critique is about clarity or validity, edit `research_draft.md`.
- If it is about a code bug, edit the code and add a regression test.
- If it is about consistency, fix `README.md`, `config.yaml`, `notes.md`, and the draft together.
- If it is about results, do **not** fabricate; add an explicit "not run / not significant" note.
- Run `uv run pytest -q` from `experiments/collusion_steering/` and record the result.
- Do **not** commit; the loop script commits.
- Do **not** run paid API calls or new experiment runs. A `--dry-run` is fine.
- Do **not** edit anything outside `experiments/collusion_steering/`. If a fix requires an outside file, write a TODO in `STATE.md`.
- Do **not** spawn sub-agents; do the work yourself.

Write `loop/actor_summary_{{ITER}}.md` with:

- Files changed.
- What changed and why (one line each).
- Test result (`uv run pytest -q`: pass/fail and count).
- Any remaining TODO.

Update `loop/STATE.md` with the current open issues and the next priority.
