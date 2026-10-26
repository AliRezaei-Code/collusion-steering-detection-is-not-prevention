import random

import pytest

from collusion_steering.conditions import (
    CANONICAL_CONDITIONS,
    CONDITION_POLICY,
    policy_for,
    validate_conditions,
)
from collusion_steering.interventions import apply_intervention


@pytest.mark.parametrize(
    "bad",
    [
        ["collusion_steer "],
        ["collusion_steering"],
        ["collusion_random"],
        ["control "],
        ["CONTROL"],
    ],
)
def test_unknown_or_mistyped_condition_raises(bad):
    """Regression: a typo ran a collusion-only baseline with zero interventions."""
    with pytest.raises(ValueError, match="unknown condition"):
        validate_conditions(bad)


def test_unknown_condition_raises_in_intervention_layer():
    with pytest.raises(ValueError, match="unknown condition"):
        apply_intervention(
            "collusion_steer ",
            {"collusion_score": 1.0, "flagged_agents": ["A"]},
            {"A": 1.0, "B": 1.0, "C": 0.0},
            0.6,
            random.Random(0),
        )


def test_duplicate_condition_raises():
    with pytest.raises(ValueError, match="duplicate condition"):
        validate_conditions(["control", "control"])


def test_empty_condition_list_raises():
    with pytest.raises(ValueError, match="no conditions"):
        validate_conditions([])


def test_every_canonical_condition_has_a_policy():
    assert set(CANONICAL_CONDITIONS) == set(CONDITION_POLICY)
    for condition in CANONICAL_CONDITIONS:
        assert policy_for(condition) == CONDITION_POLICY[condition]


def test_only_baselines_have_no_intervention_policy():
    no_policy = {c for c, p in CONDITION_POLICY.items() if p is None}
    assert no_policy == {"control", "collusion_none", "collusion_silent"}
    for condition in CANONICAL_CONDITIONS:
        if condition not in no_policy:
            assert CONDITION_POLICY[condition] is not None


def test_validate_conditions_returns_the_input_order():
    given = ["control", "collusion_none", "collusion_steer"]
    assert validate_conditions(given) == given


def _monitor(score=0.9, flagged=None):
    return {
        "collusion_score": score,
        "judge_score": score,
        "rule_score": score,
        "flagged_agents": flagged or [],
    }


def test_steer_can_target_the_honest_agent_when_the_judge_flags_it():
    """The steer arm is not role-conditioned: C can be the target."""
    result = apply_intervention(
        "collusion_steer",
        _monitor(flagged=["C"]),
        {"A": 0.0, "B": 0.0, "C": 1.0},
        0.6,
        random.Random(0),
        roles={"A": "colluder", "B": "colluder", "C": "honest"},
    )
    assert result is not None
    assert result["agent"] == "C"
    assert result["agent_role"] == "honest"


def test_random_steer_is_explicitly_colluder_only():
    """Random steer must not silently sample the honest agent as a fallback."""
    roles = {"A": "colluder", "B": "colluder", "C": "honest"}
    targets = set()
    for seed in range(20):
        result = apply_intervention(
            "collusion_random_steer",
            _monitor(flagged=["C"]),
            {"A": 0.0, "B": 0.0, "C": 1.0},
            0.6,
            random.Random(seed),
            roles=roles,
        )
        assert result is not None
        assert result["target_selection"] == "colluder_only"
        assert result["agent"] in {"A", "B"}
        targets.add(result["agent"])
    assert targets == {"A", "B"}


def test_random_steer_returns_none_when_no_colluder_is_eligible():
    result = apply_intervention(
        "collusion_random_steer",
        _monitor(flagged=["A"]),
        {"A": 1.0},
        0.6,
        random.Random(0),
        roles={"A": "honest"},
    )
    assert result is None


@pytest.mark.parametrize(
    "condition", ["control", "collusion_none", "collusion_silent"]
)
def test_baseline_conditions_never_intervene(condition):
    assert (
        apply_intervention(
            condition,
            _monitor(flagged=["A"]),
            {"A": 1.0, "B": 1.0, "C": 0.0},
            0.6,
            random.Random(0),
        )
        is None
    )
