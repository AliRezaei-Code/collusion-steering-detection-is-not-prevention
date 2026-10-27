# Literature and sprint-context report

**Purpose:** map the steering paper to the sprint’s tracks, reference papers, and
starter code; record the Archive.org/repository search; and list what was added
to the paper. Sources: the sprint page pasted by the user, the local
`context/poseidon-literature/papers.csv` index, the Poseidon starter-repo README,
and Archive.org’s advanced-search API (queried 2026-10-25).

## 1. Which stream/track this is

The paper sits in **Track 2: Detection and Audit of Collusion** and **Track 3:
Collusion Carriers and Countermeasures**.

| Sprint question | How this paper speaks to it |
| --- | --- |
| **2.3** What should count as convincing evidence of collusion? | The paper separates *plan transmission* from *vote execution*. A false negative can be an attempted coalition, a failed execution, or a refusal; the judge’s “yes” on 8/10 full-defection Core runs shows that plan transmission is not the same as success. |
| **3.4** What does a coalition do when it learns it is being watched? | The steer/quarantine/placebo pilot is a monitor-triggered intervention. The current grid is deliberately **unaware**; the white-box protocol adds an awareness condition and a shared-secret control. |
| **1.5** Which single restriction removes the most collusion at the least cost? | Steer and quarantine are two single restrictions, with a placebo and a colluder-defection outcome. The cost side is not yet independently measured (`task_correct = 1 - collusion_success` in the binary design). |
| **2.2** Does combining what agents say with what they do beat either alone? | The `colluder_defection` outcome and the post-treatment blinded label expose the say-do gap; the white-box protocol adds action-only and private-channel controls. |
| **3.1** Can actions/tools/side channels carry collusion? | Not run. The protocol specifies action-only, tool-use, and private-channel conditions; the current pilot has no private channel. |
| **3.2** Can a trusted agent expose/disrupt a coalition? | Not run. It is the natural next countermeasure after steer/quarantine. |

## 2. Reference papers (verified in the local index)

These are the sprint-page papers with the closest bearing on this work. Titles
and URLs are from `context/poseidon-literature/papers.csv`.

| Paper | Why it matters here |
| --- | --- |
| **Nakamura et al. 2026 — Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems** (`arXiv:2602.15198`) | Private-channel positive control, coalition advantage, and “collusion on paper” (plan in text, non-collusive action). Directly motivates the plan-vs-execution distinction. |
| **Agrawal et al. 2025 — Evaluating LLM Agent Collusion in Double Auctions** (`arXiv:2507.01413`) | Seller chat, oversight, message caps, and pressure as separable levers; the closest behavioral analogue to steer/quarantine/placebo. |
| **Fish et al. 2024 — Algorithmic Collusion by Large Language Models** (`arXiv:2404.00806`) | Prompt cues can shift pricing toward collusive outcomes; model behavior is sensitive to the harness, so model identity must be reported. |
| **Keppo et al. 2026 — On the Fragility of AI Agent Collusion** (`arXiv:2603.20281`) | Collusion is fragile under replacement/model mixing; supports the “model is part of the treatment” caveat and the replication need. |
| **Aharon et al. 2026 — Tacit Coordination of Large Language Models** (`arXiv:2601.22184`) | LLMs can coordinate on Schelling points without communication; a benign-coordination control is necessary before calling all agreement collusion. |
| **Rippin et al. 2026 — Tool Use Enables Undetectable Steganography in Multi-Agent LLM Systems** (`arXiv:2606.28425`) | Covert carriers can move to tool calls; the white-box protocol’s action-only condition targets this. |
| **Bonjour et al. 2022 — Information-Theoretic Approach to Detect Collusion in Multi-Agent Games** (PMLR v180) | Pairwise net influence is a compact information-theoretic detector; a useful non-activation baseline for future work. |
| **Bracale Syrnikov et al. 2026 — Institutional AI: Governing LLM Collusion in Multi-Agent Cournot Markets** (`arXiv:2601.11369`) | Strong non-activation mitigation baseline; prompt-only instructions produce small, unreliable shifts. |
| **Kale et al. 2025 — Reliable Weak-to-Strong Monitoring of LLM Agents** (`arXiv:2508.19461`) | Monitor awareness can reduce detection accuracy; motivates the awareness condition. |
| **Jiralerspong et al. 2026 — Noticing the Watcher** (`arXiv:2603.16928`) | Agents can infer CoT monitoring from blocking feedback; the coalition may adapt rather than stop. |
| **Najt et al. 2026 — SLEIGHT-Bench** (`arXiv:2605.16626`) | Monitor blind spots are exploitable; a successful intervention on a perfect monitor is not evidence of robustness. |
| **Berger et al. 2025 — Coordination Code: Rethinking Antitrust Liability in the Age of AI Pricing** (ABA) | Antitrust “plus factors”: parallel conduct alone is not agreement. Supports treating plan transmission as attempted, not successful, collusion. |
| **Shi et al. 2026 — When Agents Lie** (`arXiv:2607.05132`) | Private plans predict public deviations; motivates the private-plan/public-action distinction and the action-trace controls. |
| **Radev et al. 2026 — The Best-Laid SCHEMEs** (`arXiv:2605.29178`) | Coordinated sabotage and monitoring; a structured multi-agent monitor baseline. |
| **Nguyen et al. 2026 — TraceGuard** (`arXiv:2604.03968`) | Structured multi-dimensional action-trace monitoring; a stronger baseline than a single judge. |
| **Arike et al. 2026 — How does information access affect LLM monitors’ ability to detect sabotage?** (`arXiv:2601.21112`) | More monitor information can hurt; supports the simple code-word/judge design and the “less is more” caveat. |
| **Zeng & Rudzicz 2026 — Voluntary Collusion with Secret Tools** (`arXiv:2605.27593`) | Secret-alliance offers and voluntary collusion; relevant to the trusted-agent/honeypot track (3.2). |
| **Tao et al. 2026 — GroupGuard** (`arXiv:2603.13940`) | Collusive-attack modeling and defense; a future countermeasure baseline. |
| **Greenblatt et al. 2023 — AI Control** (`arXiv:2312.06942`) | Monitoring under intentional subversion; the threat model behind “the colluders know a monitor may exist.” |
| **Q. Liu et al. 2026 — Breaking the Secret** (`arXiv:2604.23511`) | Economic interventions for embodied multi-agent collusion; a non-prompt restriction baseline. |
| **Collina et al. 2025 — Breaking Algorithmic Collusion in Human-AI Ecosystems** (`arXiv:2511.21935`) | A no-regret participant can destabilize a collusive equilibrium; a different single-restriction design. |
| **Xu et al. 2026a — Collusion with Competitive Marginals** (`arXiv:2607.26385`) | Price-level audits can be blind by construction; supports the warning that a detector’s negative set needs an audit. |
| **Dhanda 2026 — A Price Cap Can Act as a Focal Point** (DOI `10.21203/rs.3.rs-10183486/v1`) | A single market restriction can shift collusion; a comparator for 1.5. |

**Not added:** Tomašev et al. 2026 was named on the sprint page but is not in the
local index; it is not cited to avoid an unverified reference.

## 3. Starter-code mapping

The Poseidon starter repo (`github.com/poseidon-research/collusion_hackathon`)
maps folders to sprint projects. The relevant folders for this paper:

| Folder | Why it is relevant | Status |
| --- | --- | --- |
| `colosseum/` | Private-channel positive control, coalition advantage, “collusion on paper”; the closest environment for a plan-vs-action replication. | Not run (needs Terrarium/CoLLAB preflight; medium setup). |
| `llm-trust-breaking/` | Private plans, public commitments, final actions; directly supports the say-do gap and the action-trace control. | Not run; cited as the design ancestor for the action-only condition. |
| `llm-agent-collusion/` | Seller chat, oversight, message caps, pressure; the closest single-restriction harness for 1.5/3.4. | Not run; cited as the intervention-cost comparator. |
| `trace-guard/` | Structured multi-dimensional monitor; a stronger monitor baseline than a single LLM judge. | Not run (needs Docker); cited as future baseline. |
| `focal-points/` | Benign Schelling-point control; separates coordination from collusion. | Not run; cited as the benign-coordination control. |
| `steganographic-collusion/` | Covert-channel detectors and ColludeBench environments; the hard case for transcript monitors. | Not run; cited as the covert-carrier target. |

The repo has **no license file** (per the local review), so it should remain a
private submodule/reference and code should not be copied into a public tree
without checking permission.

## 4. Archive.org search

Queries run against `archive.org/advancedsearch.php` on 2026-10-25:
`algorithmic collusion`, `tacit collusion algorithms`, `antitrust plus factors`,
`multi-agent collusion`, `steganographic collusion`, `price fixing algorithms`,
`coalition formation multi-agent`, `AI safety multi-agent`.

**Finding:** Archive.org has **no direct 2025–2026 LLM-collusion paper** in these
results. The relevant hits are older economics/legal/information-hiding material:

- *The Fundamental Unimportance of Algorithmic Collusion* (Harvard JOLT digest,
  perma.cc archive, 2022) — a skeptical legal/economics view.
- *Artificial intelligence, algorithmic pricing, and collusion* (CEPR VoxEU,
  perma.cc archive, 2022) — economic background on algorithmic pricing.
- *Algorithmic Choice and Collusion* (OSF registration, 2024) — an
  algorithmic-pricing study.
- *Information Hiding: Third International Workshop (IH’99)* (Springer, 2000) —
  background on steganography, not LLM-specific.

**Decision:** do not add these to the paper. They are background for the
economics/legal framing, not evidence about the 2026 LLM experiments; the paper
already cites the stronger, sprint-specific sources (Berger et al. 2025 for plus
factors; Fish et al. 2024 and Keppo et al. 2026 for market behavior). The search
is recorded here so the gap is auditable rather than silently omitted.

## 5. What was added to the paper

- A short **sprint-context** paragraph in Related Work naming Colosseum,
  Agrawal et al., Kale et al./Jiralerspong et al./Najt et al., Berger et al.,
  Fish et al./Keppo et al., and Aharon et al./Rippin et al.
- **Appendix E. Sprint track fit and starter-code mapping** with the table above.
- The verified references added to the reference list.
- **Appendix F. Local Llama compliance trial** with the 4-run result and the
  gate failure.
- An updated **LLM Usage Statement** listing DeepSeek V4.1 Flash 1017, the
  OpenCode models, the Nvidia judges, Qwen3-32B, and the local Llama trial.

## 6. Issues surfaced

1. **The local 1B Llama is not a valid replication vehicle.** It follows the
   target vote but not the code-word/vote protocol; the trial gate fails. Do not
   spend the credit on a 1B-class model.
2. **The credit run needs a pre-flight.** One `collusion_none` run must pass the
   manipulation check before the remaining 24 runs; otherwise stop.
3. **The reference list is now larger and needs a final citation pass.** The
   new entries are verified from the local index, but the PDF/venue fields should
   be checked once more before submission.
4. **Archive.org adds no direct LLM-collusion evidence.** The paper’s claims
   should rest on the sprint/arXiv sources, not on the older Archive.org hits.
5. **The official DOCX template uses a text-box author block** that
   `python-docx` does not expose cleanly; the formatted build recreates the
   layout from the template images rather than editing those text boxes in place.
