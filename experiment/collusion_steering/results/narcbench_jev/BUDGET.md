# NARCBench Core — audit-budget view

Model: `opencode-go/beam-free` (LLM-as-Jev fallback)  
State: public messages + task/evidence (no private channel, roles, or instruction)  
Sample: 30 stratified Core runs (15 control, 15 instructed collusion; 7 instructed-but-failed)  
Positive label: behavioral success (both colluders voted the target; 8/30)

The score is `P(collusion)` from the LLM-as-Jev probe. The budget is the share of
runs a human reviewer can inspect. Precision is the share of inspected runs that
are behavioral successes; recall is the share of all behavioral successes caught.

| Budget | k inspected | Caught | Precision | Recall |
|---:|---:|---:|---:|---:|
| 5% | 2 | 2/8 | 1.00 | 0.25 |
| 10% | 3 | 3/8 | 1.00 | 0.38 |
| 20% | 6 | 6/8 | 1.00 | 0.75 |
| 30% | 9 | 8/8 | 0.89 | 1.00 |

This is the number that matters for a decision layer. AUROC is high, but the
operating point is what determines how many real successes are caught at a fixed
review budget. The result is descriptive at n=30; it is not a calibrated policy.
