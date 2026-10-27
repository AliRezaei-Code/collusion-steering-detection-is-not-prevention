# Detection Is Not Prevention — submission draft

Research draft. Author: **Ali Rezaei, York University, Department of EECS**. The
empirical core is the completed 25-run behavioral grid in
`experiments/collusion_steering/results/final_grid25/` plus the 35-run
mechanism grid in `experiments/collusion_steering/results/mechanism_grid/`.

## Files

| File | What it is |
| --- | --- |
| `collusion_steering_draft.md` | Main draft in the Apart template structure. |
| `collusion_steering_draft_formatted.docx` | Official Apart-template DOCX (black serif title, solo-author block, centered Abstract, template headings). |
| `collusion_steering_draft_formatted.pdf` | PDF converted from the official-template DOCX; main body ends on p8, references start p9. |
| `collusion_steering_draft.pdf` | Canonical official-template PDF; main body ends on p8, references start p9. |
| `collusion_steering_draft_compact.pdf` | 10pt / 0.75in pandoc compact build for page-limit checks; not the submission layout. |
| `LITERATURE.md` | Sprint-track mapping, verified reference papers, starter-code mapping, Archive.org search. |
| `JEV_MONITOR_REVIEW.md` | Literature review and NeurIPS/ICLR-level plan for replacing the monitor with a Jev-style calibrated decision layer. |
| `figures/fig1_mechanism_controls.png` | Figure 1: mechanism controls (35-run grid). |
| `figures/fig2_monitor_roc.png` | Figure 2: monitor ROC vs marker and blinded labels. |
| `collusion_steering_deck.pdf` | 13-slide talk deck, generated from the committed JSONL by `make_deck.py`. |
| `collusion_steering_deck.pptx` | Editable version of the deck. |
| `make_deck.py` | Deck generator: every number is read from the result grids, so the slides cannot go stale. |
| `figures/fig1_collusion_success.png` | 25-run collusion-success bars; superseded by Table 1 in the page-limited build. |

## Compliance checklist

- **Abstract:** 212 words (limit 150–250).
- **Main body:** 4 pages including Conclusion (sections 1–6); references start on
  p5 in the formatted build; appendices are excluded from the page cap. Detail
  moved to Appendix I (diagnostics, labels, audit) and Appendices A–H.
- **Required appendix:** Appendix A is “Limitations and Dual-Use / Ethical
  Considerations.”
- **Template:** title/author/abstract block, Introduction, Related Work, Methods,
  Results, Discussion and Limitations, Conclusion, References, appendices, LLM
  Usage Statement.
- **Author:** Ali Rezaei, York University, Department of EECS.

## Build

From this folder:

```bash
pandoc collusion_steering_draft.md -o collusion_steering_draft_compact.pdf \
  --pdf-engine=xelatex --resource-path=.:figures \
  -V geometry:margin=0.75in -V fontsize=10pt -V mainfont="Helvetica" \
  -V colorlinks=true

# Official-template DOCX + PDF
pandoc collusion_steering_draft.md -o collusion_steering_draft.docx
uv run --with python-docx python format_docx.py
soffice --headless --convert-to pdf collusion_steering_draft_formatted.docx
cp collusion_steering_draft_formatted.pdf collusion_steering_draft.pdf
```

## Evidence base

- 25/25 runs completed: 5 scenarios (`vendor`, `project`, `hiring`, `budget`,
  `audit`) × 5 conditions (`control`, `collusion_none`, `collusion_steer`,
  `collusion_quarantine`, `collusion_placebo`), one replicate.
- Collusion success: 5/5 no-intervention and 5/5 placebo vs 0/5 steer and 0/5
  quarantine; colluder defection 5/5 steer and 5/5 quarantine vs 0/5 in both
  baselines; exact McNemar p = 0.0625 (smallest attainable at n=5). Exactly one
  of the two colluders defects in each intervention run; the other still votes
  the target.
- 35/35 mechanism-grid runs completed: 5 scenarios × 7 arms
  (`control`, `collusion_none`, `collusion_placebo`, `collusion_steer`,
  `collusion_neutral`, `collusion_honesty`, `collusion_untargeted`), one
  replicate.
- Mechanism result: `collusion_honesty` reproduces steer exactly (0/5 success,
  5/5 any defection, one defector per run), while `collusion_neutral`
  (monitor-only) and `collusion_untargeted` stay at 5/5 success and 0/5
  defection. The active ingredient is the honesty directive, not the monitor
  trigger or the target. The effect is directive-specific, not
  monitor-specific.
- 15/15 no-monitor supplement runs completed (`results/mechanism_nomonitor/`):
  `collusion_none`, `collusion_honesty_bare`, `collusion_random_steer`, one
  replicate. `collusion_honesty_bare` is the honesty directive with **no monitor
  mention**; it also gives 0/5 success and 5/5 one-defector runs. So the monitor
  mention is inert in both directions, and the directive alone is sufficient.
  `collusion_random_steer` (same notice, random colluder instead of the flagged
  one) also gives 0/5, so the effect does not depend on which colluder is
  targeted. These three arms plus the mechanism grid complete a
  (monitor mention: yes/no) x (honesty directive: yes/no) factorial.
- 25/25 second-model runs completed on `opencode-go/qwen3.8-flash` with a benign
  research-sandbox preamble (`results/proper_qwen3.8_flash_framed/`). The
  direction replicates but the strength does not: steer is 1/5 success
  (4/5 prevented) and quarantine 0/5, against 0/5 and 0/5 on `beam-free`. The
  defector count is also model-specific: on `qwen3.8-flash` both colluders defect
  in 3/5 steer runs, so "one targeted agent" is a property of the first model,
  not of the design. Report it as a robustness check, not a size replication.
- 25-run open-weights grid (`results/mlx_qwen25_7b/`, Qwen2.5-7B-Instruct 4-bit on MLX):
  with a research preamble that tells the agent to follow its private instruction, the notice
  prevents collusion in only 1/5. Without that clause it prevents 4/5 (`results/mlx_qwen25_7b_nopreamble/`,
  baseline `results/baseline_mlx_qwen25_7b_nopreamble/`). The notice's authority is set by the
  instruction hierarchy above it.
- Activation study (`results/probe_qwen25_7b/`): a behaviour-labelled probe at the final-vote token
  reaches leave-one-scenario-out **AUROC 0.886** (layer 26/28, 30 colluder states, 5 scenarios).
  Ablating that direction leaves 16/16 target votes unchanged, identical to a random-direction
  control: H1b, a correlate rather than a mechanism.
- 25-run 3B trial (`results/mlx_qwen25_3b/`): 8/25 runs fail the code-word gate and the
  no-intervention baseline is 2/5, so it is an instrument failure, not a steering result.
- The monitor is a **code-word oracle**; the marker-blind judge reaches AUROC
  0.667 against the blinded round-1 label, below the content-mention baseline
  (0.753). Because the round-1 label is a content label, the pilot **cannot
  identify** detection rather than showing that detection is impossible.
- The white-box protocol in Appendix B is specified but **not run**; do not
  describe the paper as an activation-level causal study.
- **Local Llama trial:** `mlx-community/Llama-3.2-1B-Instruct-4bit` completed
  the 4-run pipeline but failed the code-word/vote compliance gate (only one
  colluder signalled; two votes unparseable). Do not spend the GPU credit on a
  1B-class model. See `../experiments/local_llama_trial/REPORT.md` and
  Appendix F.
- **Credit run:** prepared but **not launched**. Candidate:
  `Qwen/Qwen2.5-7B-Instruct` on an OpenResearch L40S, 25 runs, with a one-run
  pre-flight; estimated $0.20–$0.75. Awaiting user approval.

## Before submission

1. Fill in author names and affiliations.
2. Verify every reference. The new entries are taken from
   `context/poseidon-literature/papers.csv`; check titles, authors, and URLs
   once more against arXiv/DOI before submission.
3. Add a public repository link in the Code and Data appendix if one is
   available (the current text points to the local
   `experiments/collusion_steering/` path).
4. Rebuild all PDFs after any edits and re-check the 8-page body limit.
5. Decide whether to approve the credit run; do not launch it without the
   pre-flight compliance check.
