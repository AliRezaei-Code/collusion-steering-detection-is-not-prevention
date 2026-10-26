# Final 25-run CLI-backend grid

- **Design:** 5 scenarios (`vendor`, `project`, `hiring`, `budget`, `audit`) ×
  5 conditions (`control`, `collusion_none`, `collusion_steer`,
  `collusion_quarantine`, `collusion_placebo`) × seed 0 = **25 runs**.
- **Backend:** `--backend cli`, model `opencode-go/beam-free`. The OpenRouter
  free-model quota was exhausted (HTTP 429 `free-models-per-day-high-balance`,
  1017/1000 requests) and the paid key has a \$0.00 monthly cap.
- **Why this model:** `opencode-go/deepseek-v4.1-flash` refuses the colluder
  role; `opencode-go/beam-free` complies. Model identity is part of the
  treatment and must be reported with every result.
- **Why 25, not 75:** a 3-seed grid at ~4 min/run was too slow for the morning
  close-out. This is a complete one-seed grid, not a powered estimate.
- **`collusion_silent` is omitted** because it duplicates `collusion_none`.
- **Files:** `config.yaml` (batch config), `runs.jsonl` (records),
  `report.md` (generated analysis), `run.log`, `runs.metadata.json`,
  `figures/`.
- **Status:** descriptive pilot. Wilson intervals at n=5 span most of [0, 1].
  The paired exact McNemar test on 5 scenarios cannot reach p < 0.05
  (minimum two-sided p = 0.0625).
