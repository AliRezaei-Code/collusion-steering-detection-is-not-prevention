#!/usr/bin/env python3
"""Behaviour-labelled probe on vote-time activations, with a scenario holdout.

The label is the agent's behaviour at the decision point — did it vote the target
(1) or the evidence-backed option (0) — never its condition. A direction trained
on "colluder vs honest role" would be an instruction-following direction; this
script refuses that shortcut by construction.

Reports leave-one-scenario-out AUROC per layer and, as a diagnostic, the AUROC of
a direction trained on the *condition* label. If the two are nearly identical,
the behaviour direction is probably reading the private instruction.

    .venv/bin/python scripts/analyze_probe.py --activations results/probe_qwen25_7b/activations.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--activations", default="results/probe_qwen25_7b/activations.jsonl")
    parser.add_argument("--out", default=None)
    parser.add_argument(
        "--subset",
        default="colluders",
        choices=["colluders", "all"],
        help="Restrict to colluder states: with all agents the label is almost "
        "perfectly predicted by the role, which is the condition shortcut this "
        "probe is supposed to avoid.",
    )
    return parser.parse_args()


def load(path: Path):
    rows = [json.loads(line) for line in path.open() if line.strip()]
    layers = sorted({int(k) for row in rows for k in row["activations"]})
    return rows, layers


def held_out_auroc(X, y, groups, seed=0):
    """Leave-one-scenario-out AUROC, pooling held-out scores."""
    scores = np.full(len(y), np.nan)
    for group in np.unique(groups):
        test = groups == group
        train = ~test
        if len(np.unique(y[train])) < 2 or test.sum() == 0:
            continue
        model = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, C=0.05, class_weight="balanced"),
        )
        model.fit(X[train], y[train])
        scores[test] = model.decision_function(X[test])
    mask = ~np.isnan(scores)
    if len(np.unique(y[mask])) < 2:
        return float("nan"), int(mask.sum())
    return float(roc_auc_score(y[mask], scores[mask])), int(mask.sum())


def main() -> int:
    args = parse_args()
    path = ROOT / args.activations
    rows, layers = load(path)
    if args.subset == "colluders":
        rows = [r for r in rows if r["role"] == "colluder"]
    y = np.array([r["label"] for r in rows])
    groups = np.array([r["scenario"] for r in rows])
    # Diagnostic label: the condition, not the behaviour.
    y_condition = np.array([1 if r["role"] == "colluder" else 0 for r in rows])
    print(f"{len(rows)} vote states · {len(layers)} layers · "
          f"{len(np.unique(groups))} scenarios · target-vote rate {y.mean():.2f}")

    results = []
    best = None
    for layer in layers:
        X = np.array([r["activations"][str(layer)] for r in rows], dtype=np.float32)
        auc, n = held_out_auroc(X, y, groups)
        auc_cond, _ = held_out_auroc(X, y_condition, groups)
        results.append({"layer": layer, "auroc_behaviour": auc, "auroc_condition": auc_cond, "n": n})
        print(f"  layer {layer:>2}: behaviour AUROC {auc:.3f}  condition AUROC {auc_cond:.3f}")
        if best is None or (auc == auc and auc > best["auroc_behaviour"]):
            best = {"layer": layer, "auroc_behaviour": auc, "auroc_condition": auc_cond, "n": n}

    # Direction at the best layer, trained on all behaviour labels (for ablation).
    layer = best["layer"]
    X = np.array([r["activations"][str(layer)] for r in rows], dtype=np.float32)
    scaler = StandardScaler().fit(X)
    clf = LogisticRegression(max_iter=2000, C=0.05, class_weight="balanced").fit(
        scaler.transform(X), y
    )
    direction = clf.coef_[0] / np.linalg.norm(clf.coef_[0])

    out_dir = ROOT / (args.out or "results/probe_qwen25_7b")
    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / f"direction_layer{layer}.npy", direction.astype(np.float32))
    (out_dir / "probe_results.json").write_text(
        json.dumps(
            {
                "n_states": len(rows),
                "target_vote_rate": float(y.mean()),
                "layers": results,
                "best": best,
                "direction_layer": layer,
            },
            indent=2,
        )
    )
    print(f"\nbest layer {layer}: behaviour AUROC {best['auroc_behaviour']:.3f} "
          f"(condition AUROC {best['auroc_condition']:.3f})")
    print(f"wrote {out_dir / 'probe_results.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
