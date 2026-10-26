# Detection Is Not Prevention

Code, data, and the paper for *Detection Is Not Prevention: A Behavioral and Activation-Level Study of
Collusion Steering in Multi-Agent LLMs* (Apart Research AI Collusion Sprint 2026, Track 2).

**Claim in one line.** A monitor-triggered notice appears to prevent collusion, but the monitor does nothing: a generic
honesty directive reproduces the effect, a monitor notice alone does not, and a system prompt that fixes the agent's
role mostly defeats it. At the final vote the decision is linearly decodable (0.89 held-out AUROC) and ablating that
direction changes nothing.

## Contents

- `paper/` — the submission PDF (4-page body, appendices), the markdown source, the deck, and `make_deck.py`.
- `experiment/` — the harness (`src/collusion_steering/`), tests, runner scripts, and every committed result grid
  under `results/`.
- `skills/` — the prose rules used for the paper.

## Result grids

| Grid | Runs | What it tests |
| --- | ---: | --- |
| `results/final_grid25` | 25 | pilot: steer and quarantine vs placebo |
| `results/mechanism_grid` | 35 | monitor-only, honesty-only, untargeted |
| `results/mechanism_nomonitor` | 15 | honesty directive with no monitor mention |
| `results/proper_qwen3.8_flash_framed` | 25 | second model, API |
| `results/mlx_qwen25_7b` | 25 | 7B with a competing system instruction |
| `results/mlx_qwen25_7b_nopreamble` | 15 | 7B without it (the clean substrate) |
| `results/probe_qwen25_7b` | 45 states | vote probe and ablation |
| `results/mlx_qwen25_3b` | 25 | 3B trial that fails the instrument gate |

## Reproduce

```bash
cd experiment
uv run pytest -q                      # harness tests
uv run python run_experiment.py --results results/final_grid25/runs.jsonl
```

The activation study needs `mlx-lm` and Apple Silicon (or adapt `src/collusion_steering/mlx_client.py`); see
`scripts/probe_activations.py`, `scripts/analyze_probe.py`, `scripts/ablate_vote.py`.

## Caveats

The behavioural monitor is a code-word oracle, so detection is not identified by design. Grids are one seed each and
descriptive, not powered. The ablation is one layer at one dose over 16 target-voting states.
