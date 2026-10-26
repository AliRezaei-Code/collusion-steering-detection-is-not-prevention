#!/usr/bin/env python3
"""Autonomous critic-actor loop for the collusion-steering pilot.

Runs a critic session, then an actor session, then tests, then a git commit.
Repeats for a fixed wall-clock duration. Every iteration is logged and committed.

Usage:
    python3 loop/orchestrator.py --once
    python3 loop/orchestrator.py --duration 7200
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # experiments/collusion_steering
WORKTREE = ROOT.parent.parent
LOOP = ROOT / "loop"
CRITIQUES = LOOP / "critiques"
LOGS = LOOP / "logs"

MODEL = "opencode-go/deepseek-v4.1-flash"
AGENT_TIMEOUT = 15 * 60
TEST_TIMEOUT = 5 * 60
SLEEP_BETWEEN = 5
MAX_ITER = 80


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text.rstrip() + "\n")


def run_cmd(
    cmd: list[str],
    cwd: Path,
    log_path: Path,
    timeout: int,
) -> int:
    append(log_path, f"\n$ {' '.join(cmd[:6])}{' ...' if len(cmd) > 6 else ''}")
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


def build_prompt(template: Path, iteration: int) -> str:
    return template.read_text(encoding="utf-8").replace("{{ITER}}", str(iteration))


def next_iteration() -> int:
    """Resume after the highest existing critique, so a restart never overwrites."""
    numbers: list[int] = []
    for path in CRITIQUES.glob("critic_*.md"):
        parts = path.stem.split("_")
        if len(parts) == 2 and parts[1].isdigit():
            numbers.append(int(parts[1]))
    return max(numbers) + 1 if numbers else 1


def git_has_staged_changes() -> bool:
    proc = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(WORKTREE),
        capture_output=True,
    )
    return proc.returncode != 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run one iteration")
    parser.add_argument("--duration", type=int, default=2 * 60 * 60)
    args = parser.parse_args()

    CRITIQUES.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    start = time.time()
    end = start + (60 if args.once else args.duration)
    changelog = LOOP / "CHANGELOG.md"
    if not changelog.exists():
        changelog.write_text("# Critic-actor loop changelog\n\n", encoding="utf-8")
    append(changelog, f"- start: {utc_now()} | duration={args.duration}s | model={MODEL}")

    iteration = next_iteration() - 1
    while time.time() < end and iteration < MAX_ITER:
        iteration += 1
        iter_start = time.time()
        log_path = LOGS / f"iteration_{iteration:03d}.log"
        append(log_path, f"\n===== iteration {iteration} | {utc_now()} =====")

        critic_prompt = build_prompt(LOOP / "prompts" / "critic.md", iteration)
        critic_rc = run_cmd(
            ["opencode", "run", "--model", MODEL, "--auto", critic_prompt],
            cwd=WORKTREE,
            log_path=log_path,
            timeout=AGENT_TIMEOUT,
        )

        actor_prompt = build_prompt(LOOP / "prompts" / "actor.md", iteration)
        actor_rc = run_cmd(
            ["opencode", "run", "--model", MODEL, "--auto", actor_prompt],
            cwd=WORKTREE,
            log_path=log_path,
            timeout=AGENT_TIMEOUT,
        )

        test_rc = run_cmd(
            ["uv", "run", "pytest", "-q"],
            cwd=ROOT,
            log_path=log_path,
            timeout=TEST_TIMEOUT,
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
                    f"critic-actor iteration {iteration}: "
                    f"critic={critic_rc} actor={actor_rc} tests={test_rc}",
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
            f"- {utc_now()} iteration {iteration}: critic={critic_rc} "
            f"actor={actor_rc} tests={test_rc} commit={commit_rc} "
            f"elapsed={elapsed}s",
        )
        (LOOP / "HEARTBEAT").write_text(
            f"{utc_now()} iteration={iteration} tests={test_rc} "
            f"critic={critic_rc} actor={actor_rc}\n",
            encoding="utf-8",
        )
        time.sleep(SLEEP_BETWEEN)

    (LOOP / "DONE.md").write_text(
        f"# Loop finished\n\n"
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
