"""Tests for the artifact checker's data-derived expectations."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_artifacts", ROOT / "scripts" / "check_artifacts.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_count_phrase_is_derived_from_the_record_count():
    """Regression: the checker compared the manifest phrase to itself.

    It now derives the phrase from ``len(records)``, so a three-record batch
    cannot pass with a stale "two completed runs" phrase.
    """
    checker = _load_checker()
    assert checker.count_phrase(2) == "two completed runs"
    assert checker.count_phrase(3) == "three completed runs"
    assert checker.count_phrase(12) == "12 completed runs"


def test_quarantined_report_contains_provenance_only():
    """Regression: the quarantined report printed AUROC and precision/recall/F1.

    A banner that forbids citation does not help if the body is a results table.
    """
    report = (ROOT / "results" / "report_invalid_control.md").read_text(
        encoding="utf-8"
    )
    assert "No estimator is reported" in report
    assert "INVALID CONTROL BATCH" in report[:400]
    for banned in ("AUROC", "precision=", "recall=", "F1=", "effect-size", "TP="):
        assert banned not in report, banned
    # The record ids are kept so the quarantine is auditable.
    assert "vendor__collusion_steer__s0" in report
