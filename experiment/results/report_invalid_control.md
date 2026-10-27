> # ⛔ INVALID CONTROL BATCH — DO NOT CITE
>
> **No estimator is reported in this file.** It is a provenance note, not a
> results report. The estimator tables, intervals, confusion counts, and figures
> that an earlier version of this file contained have been removed because the
> batch is invalid and the banner forbade citing them.
>
> This batch's `control` condition was misconfigured: the control agents kept
> their colluder roles. The "control" row is therefore a bug, not a baseline.
> The batch is kept only so the failure is auditable and so the regression test
> has a named input.
>
> - Data: `results/runs_invalid_control.jsonl`
> - Records (all five are quarantined): `vendor__control__s0`,
>   `vendor__collusion_none__s0`, `vendor__collusion_silent__s0`,
>   `vendor__collusion_steer__s0`, `vendor__collusion_quarantine__s0`
> - No row — including the `collusion_steer` row — is promoted to valid
>   evidence, and no row appears in draft §6.
> - Regression test: `tests/test_runner.py::test_control_has_no_colluders`
> - Valid batch: `results/runs_valid.jsonl`; its report is
>   `results/worked_example_report.md`
>
> The non-control rows were produced under the same broken batch configuration
> and are not promoted either.
