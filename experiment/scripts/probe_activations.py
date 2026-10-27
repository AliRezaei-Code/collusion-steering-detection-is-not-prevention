#!/usr/bin/env python3
"""Capture vote-time activations and test whether they encode the vote.

This is the experiment Appendix B only specified: a behaviour-labelled probe on
the final-vote decision point, plus a causal ablation of the fitted direction.

For every completed run in the behavioural grid we rebuild exactly the messages
the agent saw at vote time (same system prompt, same transcript, same notice),
run one forward pass, and store the residual stream at the last token for a
band of layers. The label is the agent's *behaviour* — did it vote the target or
the evidence-backed option — not its condition.

    .venv-mlx/bin/python scripts/probe_activations.py \
        --runs results/mlx_qwen25_7b/runs.jsonl --out results/probe_qwen25_7b
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from collusion_steering.mlx_client import DEFAULT_PREAMBLE  # noqa: E402
from collusion_steering.prompts import system_prompt, vote_prompt  # noqa: E402
from collusion_steering.runner import make_agents  # noqa: E402
from collusion_steering.scenarios import get_scenarios  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default="results/mlx_qwen25_7b/runs.jsonl")
    parser.add_argument("--out", default="results/probe_qwen25_7b")
    parser.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct-4bit")
    parser.add_argument("--preamble", default="default", choices=["default", "none"])
    parser.add_argument("--layers", default="every4", help="'every4' or a comma list")
    return parser.parse_args()


def pick_layers(n_layers: int, spec: str) -> list[int]:
    if spec == "every4":
        return sorted({*range(2, n_layers, 4), n_layers - 1})
    return [int(x) for x in spec.split(",")]


def main() -> int:
    args = parse_args()
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.models.base import create_attention_mask

    model, tokenizer = load(args.model)
    n_layers = len(model.model.layers)
    layers = pick_layers(n_layers, args.layers)
    print(f"model has {n_layers} layers; capturing {layers}", flush=True)

    preamble = DEFAULT_PREAMBLE if args.preamble == "default" else None
    scenarios = {s.id: s for s in get_scenarios()}
    runs = [json.loads(line) for line in Path(args.runs).open() if line.strip()]
    runs = [r for r in runs if not r.get("error")]
    print(f"{len(runs)} runs", flush=True)

    records = []
    for run in runs:
        scenario = scenarios[run["scenario_id"]]
        transcript = run["transcript"]
        condition = run["condition"]
        code = run.get("code") or ""
        agents = make_agents(condition)
        outcomes = run["outcome"]
        votes = outcomes["votes"]
        intervention = run.get("intervention") or {}
        target = outcomes["target"]

        for index, agent in enumerate(agents):
            notice = None
            if intervention and intervention.get("agent") == agent.name:
                notice = intervention.get("notice")
            system = system_prompt(
                agent.name,
                scenario,
                agent.role,
                agent.partner,
                code,
                style="explicit",
                private_planning=False,
                awareness=False,
            )
            if preamble:
                system = preamble + "\n\n" + system
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": vote_prompt(scenario, transcript, notice)},
            ]
            prompt = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False
            )
            ids = mx.array([tokenizer.encode(prompt)])

            h = model.model.embed_tokens(ids)
            # The causal mask is load-bearing: without it the residual stream
            # silently differs from the model's own forward pass. Verified by
            # matching logits exactly (max |diff| = 0.0) against model(ids).
            mask = create_attention_mask(h, None)
            captured = {}
            for layer_index, layer in enumerate(model.model.layers):
                h = layer(h, mask, None)
                if layer_index in layers:
                    captured[layer_index] = np.array(h[0, -1, :].astype(mx.float32))

            vote = votes[index]
            label = 1 if vote == target else 0
            records.append(
                {
                    "run_id": run["run_id"],
                    "scenario": run["scenario_id"],
                    "condition": condition,
                    "agent": agent.name,
                    "role": agent.role,
                    "vote": vote,
                    "target": target,
                    "label": label,
                    "n_tokens": int(ids.shape[1]),
                    "activations": {
                        str(k): v.astype(np.float32).tolist() for k, v in captured.items()
                    },
                }
            )
            if len(records) % 15 == 0:
                print(f"  captured {len(records)} vote states", flush=True)

    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    path = out / "activations.jsonl"
    with path.open("w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    print(f"wrote {path} ({len(records)} states)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
