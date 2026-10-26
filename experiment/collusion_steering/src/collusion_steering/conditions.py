"""Canonical condition names and the intervention policy each one selects.

This module exists so a typo cannot silently produce a collusion-only run with
no intervention. A mistyped condition used to reach ``run_one``, create two
colluders, and then fall through ``apply_intervention``'s unknown-condition
branch, which returns ``None``: the record looked like a steer arm with a null
effect. Validation now happens before any job is built and again in ``run_one``.
"""

from __future__ import annotations

from collections.abc import Iterable

# The configured labels. ``collusion_silent`` currently executes the same code
# path as ``collusion_none`` (see the draft §4.7); it is kept as a separate
# label only because the committed grid and config still name it. Collapsing it
# is tracked in ``loop/STATE.md``.
#
# The three ``collusion_{neutral,honesty,untargeted}`` arms are the mechanism
# controls for the prevention result. They separate "any monitor notice" and
# "a generic honesty directive" from the coordination-specific override, and
# they test whether targeting the flagged colluder matters.
CANONICAL_CONDITIONS: tuple[str, ...] = (
    "control",
    "collusion_none",
    "collusion_silent",
    "collusion_steer",
    "collusion_quarantine",
    "collusion_placebo",
    "collusion_random_steer",
    "collusion_neutral",
    "collusion_honesty",
    "collusion_honesty_bare",
    "collusion_untargeted",
)

# ``None`` means the condition delivers no intervention. Every other value names
# the policy ``apply_intervention`` must implement, so a condition cannot be
# advertised as a treatment and then run as a baseline.
CONDITION_POLICY: dict[str, str | None] = {
    "control": None,
    "collusion_none": None,
    "collusion_silent": None,
    "collusion_steer": "steer",
    "collusion_quarantine": "quarantine",
    "collusion_placebo": "placebo",
    "collusion_random_steer": "steer_random",
    "collusion_neutral": "neutral",
    "collusion_honesty": "honesty",
    "collusion_honesty_bare": "honesty_bare",
    "collusion_untargeted": "steer_untargeted",
}


def validate_conditions(conditions: Iterable[str]) -> list[str]:
    """Return ``conditions`` as a list, or raise on an unknown/duplicate name.

    Trailing whitespace is treated as an error rather than stripped: a name that
    differs from the canonical spelling is exactly the silent failure this guard
    is for, and stripping it would hide a broken ``--conditions`` invocation.
    """
    names = list(conditions)
    if not names:
        raise ValueError("no conditions configured")
    unknown = [name for name in names if name not in CONDITION_POLICY]
    if unknown:
        raise ValueError(
            f"unknown condition(s) {unknown}; canonical names are "
            f"{list(CANONICAL_CONDITIONS)}"
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate condition(s) {duplicates}")
    return names


def policy_for(condition: str) -> str | None:
    """Intervention policy for a validated condition, or raise."""
    try:
        return CONDITION_POLICY[condition]
    except KeyError:
        raise ValueError(
            f"unknown condition {condition!r}; canonical names are "
            f"{list(CANONICAL_CONDITIONS)}"
        ) from None
