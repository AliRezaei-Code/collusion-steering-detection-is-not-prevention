#!/usr/bin/env python3
"""Overnight experimenter -> analyst -> critic -> actor loop.

Each iteration:
  1. EXPERIMENTER runs a small free-model batch (or records why it could not).
  2. ANALYST compares the batch to the baseline, diagnoses failures, searches
     the literature for fixes.
  3. CRITIC reviews the experiment, analysis, and draft.
  4. ACTOR implements the top fixes and runs the test suite.
Then the orchestrator commits only `experiments/collusion_steering/`.

Usage:
    python3 loop/overnight_orchestrator.py --once
    python3 loop/overnight_orchestrator.py --duration 28800
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKTREE = ROOT.parent.parent
LOOP = ROOT / "loop"
LOGS = LOOP / "logs"

MODEL = "opencode-go/deepseek-v4.1-flash"
DEFAULT_DURATION = 8 * 60 * 60
MAX_ITER = 24

ROLES = [
    ("experimenter", 25 * 60),
    ("analyst", 15 * 60),
    ("critic", 12 * 60),
    ("actor", 20 * 60),
]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text.rstrip() + "\n")


def next_iteration() -> int:
    numbers: list[int] = []
    for pattern in ("experiment_*.md", "analysis_*.md", "critiques/critic_*.md"):
        for path in LOOP.glob(pattern):
            parts = path.stem.split("_")
            if parts[-1].isdigit():
                numbers.append(int(parts[-1]))
    return max(numbers) + 1 if numbers else 1


def run_cmd(cmd: list[str], cwd: Path, log_path: Path, timeout: int) -> int:
    append(log_path, f"\n$ {' '.join(cmd[:5])}{' ...' if len(cmd) > 5 else ''}")
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd),
                stdout=handle,
                stderr=subprocess.STDOUT,
                timeout=timeout,
            )
        append(log_path, f"[exit {proc.returncode}]")
        return proc.returncode
    except subprocess.TimeoutExpired:
        append(log_path, f"[timeout after {timeout}s]")
        return 124
    except Exception as exc:  # noqa: BLE001 - keep the loop alive
        append(log_path, f"[error {type(exc).__name__}: {exc}]")
        return 1


def kill_stray_experiments() -> None:
    """Kill only this pilot's experiment children after an experimenter timeout."""
    subprocess.run(
        ["pkill", "-f", "experiments/collusion_steering/run_experiment.py"],
        capture_output=True,
    )


def build_prompt(template: Path, iteration: int) -> str:
    return template.read_text(encoding="utf-8").replace("{{ITER}}", str(iteration))


def git_has_staged_changes() -> bool:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(WORKTREE),
        capture_output=True,
    )
    return proc.returncode != 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION)
    args = parser.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)
    start = time.time()
    end = start + (60 * 45 if args.once else args.duration)
    changelog = LOOP / "OVERNIGHT_CHANGELOG.md"
    if not changelog.exists():
        changelog.write_text("# Overnight loop changelog\n\n", encoding="utf-8")
    append(
        changelog,
        f"- start: {utc_now()} | duration={args.duration}s | model={MODEL}",
    )

    iteration = next_iteration() - 1
    while time.time() < end and iteration < MAX_ITER:
        iteration += 1
        iter_start = time.time()
        log_path = LOGS / f"overnight_{iteration:03d}.log"
        append(log_path, f"\n===== overnight iteration {iteration} | {utc_now()} =====")
        codes: dict[str, int] = {}

        for role, timeout in ROLES:
            prompt = build_prompt(LOOP / "prompts" / f"{role}.md", iteration)
            code = run_cmd(
                ["opencode", "run", "--model", MODEL, "--auto", prompt],
                cwd=WORKTREE,
                log_path=log_path,
                timeout=timeout,
            )
            codes[role] = code
            if role == "experimenter" and code == 124:
                kill_stray_experiments()

        test_rc = run_cmd(
            ["uv", "run", "pytest", "-q"],
            cwd=ROOT,
            log_path=log_path,
            timeout=5 * 60,
        )

        run_cmd(
            ["git", "add", "experiments/collusion_steering"],
            cwd=WORKTREE,
            log_path=log_path,
            timeout=120,
        )

        commit_rc = 0
        if git_has_staged_changes():
            commit_rc = run_cmd(
                [
                    "git",
                    "commit",
                    "-m",
                    "overnight iteration {i}: exp={e} analyst={a} critic={c} "
                    "actor={ac} tests={t}".format(
                        i=iteration,
                        e=codes.get("experimenter"),
                        a=codes.get("analyst"),
                        c=codes.get("critic"),
                        ac=codes.get("actor"),
                        t=test_rc,
                    ),
                ],
                cwd=WORKTREE,
                log_path=log_path,
                timeout=120,
            )
        else:
            append(log_path, "[no staged changes]")

        elapsed = round(time.time() - iter_start, 1)
        append(
            changelog,
            f"- {utc_now()} iteration {iteration}: "
            f"exp={codes.get('experimenter')} analyst={codes.get('analyst')} "
            f"critic={codes.get('critic')} actor={codes.get('actor')} "
            f"tests={test_rc} commit={commit_rc} elapsed={elapsed}s",
        )
        (LOOP / "OVERNIGHT_HEARTBEAT").write_text(
            f"{utc_now()} iteration={iteration} tests={test_rc} "
            f"exp={codes.get('experimenter')} analyst={codes.get('analyst')} "
            f"critic={codes.get('critic')} actor={codes.get('actor')}\n",
            encoding="utf-8",
        )
        time.sleep(5)

    (LOOP / "OVERNIGHT_DONE.md").write_text(
        f"# Overnight loop finished\n\n"
        f"- finished: {utc_now()}\n"
        f"- iterations: {iteration}\n"
        f"- wall clock: {round(time.time() - start, 1)}s\n"
        f"- model: {MODEL}\n",
        encoding="utf-8",
    )
    append(changelog, f"- done: {utc_now()} | iterations={iteration}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
