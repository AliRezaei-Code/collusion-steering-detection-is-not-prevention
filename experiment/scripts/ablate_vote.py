#!/usr/bin/env python3
"""Causal test: ablate the vote direction and re-read the decision.

For each captured vote state we score two candidate continuations, ``VOTE: A``
and ``VOTE: B``, under three conditions: no intervention, the fitted behaviour
direction projected out of the residual stream from the probe's best layer
onward, and a random direction of matched norm projected out the same way.

The readout is the forced-choice vote, so this is a decision-level intervention,
not a generation-level one: nothing about sampling or phrasing can move it. The
comparison that matters is ablation against the random direction, because any
intervention perturbs the stream.

    .venv-mlx/bin/python scripts/ablate_vote.py \
        --activations results/probe_qwen25_7b/activations.jsonl \
        --probe results/probe_qwen25_7b/probe_results.json
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
    parser.add_argument("--probe", default="results/probe_qwen25_7b/probe_results.json")
    parser.add_argument("--model", default="mlx-community/Qwen2.5-7B-Instruct-4bit")
    parser.add_argument("--out", default="results/probe_qwen25_7b/ablation.json")
    parser.add_argument("--preamble", default="none", choices=["default", "none"])
    parser.add_argument("--max-states", type=int, default=0,
                        help="0 = all. Otherwise take this many, defections first.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.models.base import create_attention_mask

    probe = json.loads((ROOT / args.probe).read_text())
    layer_index = int(probe["direction_layer"])
    direction = np.load(ROOT / f"results/probe_qwen25_7b/direction_layer{layer_index}.npy")
    d_mlx = mx.array(direction.astype(np.float32))
    rng = np.random.default_rng(0)
    random_dir = rng.normal(size=direction.shape).astype(np.float32)
    random_dir /= np.linalg.norm(random_dir)
    r_mlx = mx.array(random_dir)

    model, tokenizer = load(args.model)
    scenarios = {s.id: s for s in get_scenarios()}
    runs = [json.loads(line) for line in (ROOT / args.runs).open() if line.strip()]
    runs = [r for r in runs if not r.get("error")]

    # Candidate token ids for the two options, with and without a leading space.
    cand_ids = {}
    for letter in ("A", "B"):
        found = set()
        for surface in (letter, " " + letter):
            toks = tokenizer.encode(surface)
            if len(toks) == 1:
                found.add(toks[0])
        cand_ids[letter] = sorted(found)

    def read_vote(prompt_ids: list[int], mode: str) -> dict:
        """Force 'VOTE:' and read the A/B distribution at the next position."""
        forced = tokenizer.encode("VOTE:")
        ids = mx.array([prompt_ids + forced])
        h = model.model.embed_tokens(ids)
        mask = create_attention_mask(h, None)
        for index, layer in enumerate(model.model.layers):
            h = layer(h, mask, None)
            if index == layer_index and mode != "none":
                vec = d_mlx if mode == "ablate" else r_mlx
                h = h - (h * vec).sum(axis=-1, keepdims=True) * vec
        logits = model.lm_head(model.model.norm(h))[0, -1]
        log_probs = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
        scores = {
            letter: float(mx.max(mx.array([log_probs[i] for i in cand_ids[letter]])))
            for letter in ("A", "B")
        }
        return {**scores, "vote": "A" if scores["A"] > scores["B"] else "B"}

    # Build the state list first so a stratified subset can be taken by label.
    pending = []
    for run in runs:
        scenario = scenarios[run["scenario_id"]]
        agents = make_agents(run["condition"])
        intervention = run.get("intervention") or {}
        for index, agent in enumerate(agents):
            notice = None
            if intervention and intervention.get("agent") == agent.name:
                notice = intervention.get("notice")
            system = system_prompt(
                agent.name, scenario, agent.role, agent.partner, run.get("code") or "",
                style="explicit", private_planning=False, awareness=False,
            )
            system_text = (
                DEFAULT_PREAMBLE + "\n\n" + system if args.preamble == "default" else system
            )
            messages = [
                {"role": "system", "content": system_text},
                {"role": "user", "content": vote_prompt(scenario, run["transcript"], notice)},
            ]
            prompt = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, tokenize=False
            )
            pending.append((run, agent, index, tokenizer.encode(prompt)))

    if args.max_states:
        def votes_target(item):
            run, agent, index, _ = item
            return run["outcome"]["votes"][index] == run["outcome"]["target"]
        # Target-voting states first: a drop in the target vote can only be
        # observed where the model currently votes the target.
        pending.sort(key=lambda item: (not votes_target(item), item[0]["run_id"], item[1].name))
        pending = pending[: args.max_states]

    rows = []
    for run, agent, index, prompt_ids in pending:
        record = {
            "run_id": run["run_id"], "agent": agent.name, "role": agent.role,
            "actual_vote": run["outcome"]["votes"][index],
            "target": run["outcome"]["target"], "correct": run["outcome"]["correct"],
        }
        for mode in ("none", "ablate", "random"):
            out = read_vote(prompt_ids, mode)
            record[f"logp_{mode}"] = {"A": out["A"], "B": out["B"]}
            record[f"vote_{mode}"] = out["vote"]
        rows.append(record)
        print(f"  {record['run_id']:<38} {agent.name} actual={record['actual_vote']} "
              f"none={record['vote_none']} ablate={record['vote_ablate']} random={record['vote_random']}",
              flush=True)

    def target_rate(key):
        return float(np.mean([r[key] == r["target"] for r in rows]))

    summary = {
        "n_states": len(rows),
        "layer": layer_index,
        "probe_auroc": probe["best"]["auroc_behaviour"],
        "target_vote_rate": {
            "actual": float(np.mean([r["actual_vote"] == r["target"] for r in rows])),
            "none": target_rate("vote_none"),
            "ablate_direction": target_rate("vote_ablate"),
            "ablate_random": target_rate("vote_random"),
        },
        "rows": rows,
    }
    out = ROOT / args.out
    out.write_text(json.dumps(summary, indent=2))
    print("\ntarget-vote rate:", json.dumps(summary["target_vote_rate"], indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
