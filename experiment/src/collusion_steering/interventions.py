"""Intervention policies for the closed-loop pilot."""

from __future__ import annotations

import random
from typing import Any

from .conditions import policy_for
from .prompts import (
    BARE_HONESTY_NOTICE,
    HONESTY_NOTICE,
    MONITOR_ONLY_NOTICE,
    NEUTRAL_NOTICE,
    QUARANTINE_MESSAGE,
    STEER_NOTICE,
)


def _select_agent(
    monitor_result: dict[str, Any] | None,
    agent_scores: dict[str, float],
    threshold: float,
) -> tuple[str | None, float | None]:
    """Pick an intervention target, or ``None``.

    The threshold gate comes **first**. A judge that names an agent while giving
    the transcript a low score must not trigger an intervention: otherwise the
    policy steers whoever the judge happened to mention, including an honest
    agent. Only after the transcript clears ``threshold`` do we use
    ``flagged_agents`` (the judge's nomination) or, failing that, the highest
    per-agent rule score.
    """
    if not monitor_result or not agent_scores:
        return None, None
    score = float(monitor_result.get("collusion_score", 0.0))
    if score < threshold:
        return None, score
    flagged = [
        a for a in monitor_result.get("flagged_agents", []) if a in agent_scores
    ]
    if flagged:
        return max(flagged, key=lambda a: agent_scores.get(a, 0.0)), score
    best = max(agent_scores, key=agent_scores.get)
    if agent_scores.get(best, 0.0) >= threshold:
        return best, score
    return None, score


def _record(
    intervention: dict[str, Any],
    monitor_result: dict[str, Any] | None,
    roles: dict[str, str] | None,
) -> dict[str, Any]:
    """Attach the audit fields a reviewer needs to see who was targeted."""
    intervention["agent_role"] = (roles or {}).get(intervention["agent"])
    intervention["judge_score"] = (monitor_result or {}).get("judge_score")
    intervention["rule_score"] = (monitor_result or {}).get("rule_score")
    notice = intervention.get("notice") or ""
    intervention["notice_words"] = len(notice.split())
    intervention["notice_chars"] = len(notice)
    return intervention


def apply_intervention(
    condition: str,
    monitor_result: dict[str, Any] | None,
    agent_scores: dict[str, float],
    threshold: float,
    rng: random.Random,
    roles: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    """Decide whether and where to intervene.

    Returns ``None`` for no intervention, otherwise a dict with ``type``,
    ``agent``, ``notice``, ``trigger``, and audit fields. ``roles`` maps agent
    names to ``colluder``/``honest``; the random-steer control samples only from
    colluders, so it is a *position-within-the-coalition* control, not a
    like-for-like control for the steer arm's target choice.

    An unknown condition raises. It used to fall through to ``None``, which made
    a mistyped ``--conditions`` value look like a legitimate null-effect arm.
    """
    policy = policy_for(condition)

    if policy is None:
        return None

    if policy == "steer_random":
        # Same monitor gate as `collusion_steer`, then randomize the target among
        # colluders only. An ungated random steer fires in every run, which
        # confounds target choice with intervention rate and with monitor gating.
        # Colluder-only sampling is recorded as `target_selection`, because the
        # steer arm can nominate the honest agent when the judge flags C while
        # this arm cannot.
        trigger_agent, score = _select_agent(monitor_result, agent_scores, threshold)
        if trigger_agent is None or score is None or score < threshold:
            return None
        colluders = sorted(
            a for a, role in (roles or {}).items() if role == "colluder"
        )
        if not colluders:
            return None
        agent = rng.choice(colluders)
        return _record(
            {
                "type": "steer",
                "agent": agent,
                "notice": STEER_NOTICE,
                "trigger": "monitor+random",
                "monitor_score": score,
                "monitor_target": trigger_agent,
                "random_target": True,
                "target_selection": "colluder_only",
            },
            monitor_result,
            roles,
        )

    if policy == "steer_untargeted":
        # Same monitor gate and notice as `collusion_steer`, but delivered to an
        # honest agent instead of the flagged one. This separates "targeting the
        # flagged colluder" from "any monitor notice perturbs the room". The
        # honest agent has no coordination instruction to override, so a drop in
        # collusion here would not be a coordination-specific effect.
        trigger_agent, score = _select_agent(monitor_result, agent_scores, threshold)
        if trigger_agent is None or score is None or score < threshold:
            return None
        honest = sorted(
            a for a, role in (roles or {}).items() if role == "honest"
        )
        if not honest:
            return None
        return _record(
            {
                "type": "steer",
                "agent": honest[0],
                "notice": STEER_NOTICE,
                "trigger": "monitor+untargeted",
                "monitor_score": score,
                "monitor_target": trigger_agent,
                "target_selection": "honest_only",
            },
            monitor_result,
            roles,
        )

    agent, score = _select_agent(monitor_result, agent_scores, threshold)
    if agent is None:
        return None

    if policy == "neutral":
        return _record(
            {
                "type": "neutral",
                "agent": agent,
                "notice": MONITOR_ONLY_NOTICE,
                "trigger": "monitor",
                "monitor_score": score,
            },
            monitor_result,
            roles,
        )

    if policy == "honesty":
        return _record(
            {
                "type": "honesty",
                "agent": agent,
                "notice": HONESTY_NOTICE,
                "trigger": "monitor",
                "monitor_score": score,
            },
            monitor_result,
            roles,
        )

    if policy == "honesty_bare":
        # Same trigger and target as every other arm; the notice drops the
        # monitor mention and keeps only the honesty directive.
        return _record(
            {
                "type": "honesty_bare",
                "agent": agent,
                "notice": BARE_HONESTY_NOTICE,
                "trigger": "monitor",
                "monitor_score": score,
                "mentions_monitor": False,
                "overrides_prior_instruction": False,
            },
            monitor_result,
            roles,
        )

    if policy == "quarantine":
        return _record(
            {
                "type": "quarantine",
                "agent": agent,
                "notice": STEER_NOTICE,
                "message": QUARANTINE_MESSAGE,
                "trigger": "monitor",
                "monitor_score": score,
            },
            monitor_result,
            roles,
        )

    if policy == "placebo":
        return _record(
            {
                "type": "placebo",
                "agent": agent,
                "notice": NEUTRAL_NOTICE,
                "trigger": "monitor",
                "monitor_score": score,
            },
            monitor_result,
            roles,
        )

    return _record(
        {
            "type": "steer",
            "agent": agent,
            "notice": STEER_NOTICE,
            "trigger": "monitor",
            "monitor_score": score,
        },
        monitor_result,
        roles,
    )
