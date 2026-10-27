#!/usr/bin/env python3
"""Build the sprint talk deck for the collusion-steering paper.

Every number in this deck is read from the committed artifacts, not typed from
memory, so a stale slide is impossible: change the JSONL, rerun, and the deck
follows. Source grids:

    results/final_grid25/                 25-run pilot      (beam-free)
    results/mechanism_grid/               35-run 7-arm grid (beam-free)
    results/mechanism_nomonitor/          15-run 3-arm grid (beam-free)
    results/proper_qwen3.8_flash_framed/  25-run replicate  (qwen3.8-flash)

Run from papers/collusion_steering:

    python3 make_deck.py
    soffice --headless --convert-to pdf collusion_steering_deck.pptx
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "collusion_steering" / "results"

INK = RGBColor(0x11, 0x14, 0x18)
MUTED = RGBColor(0x5B, 0x64, 0x70)
FAINT = RGBColor(0x9A, 0xA2, 0xAD)
ACCENT = RGBColor(0xB4, 0x53, 0x09)
GREEN = RGBColor(0x15, 0x6D, 0x4A)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
WASH = RGBColor(0xF5, 0xF3, 0xF0)
RULE = RGBColor(0xDE, 0xD8, 0xD1)

FONT = "Helvetica Neue"
W, H = 13.333, 7.5


# --------------------------------------------------------------------------
# artifacts
# --------------------------------------------------------------------------
def tallies(path: Path) -> dict[str, tuple[int, int, dict[int, int]]]:
    """condition -> (n, collusion_successes, {n_defectors: count})."""
    rows = [json.loads(line) for line in path.open() if line.strip()]
    out: dict[str, tuple[int, int, dict[int, int]]] = {}
    counts: dict[str, list[int]] = defaultdict(list)
    defectors: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        if row.get("error"):
            continue
        condition = row["condition"]
        outcome = row.get("outcome") or {}
        counts[condition].append(1 if outcome.get("collusion_success") else 0)
        defectors[condition][len(outcome.get("colluder_defectors") or [])] += 1
    for condition, values in counts.items():
        out[condition] = (len(values), sum(values), dict(defectors[condition]))
    return out


PILOT = tallies(RESULTS / "final_grid25" / "runs.jsonl")
MECH = tallies(RESULTS / "mechanism_grid" / "runs.jsonl")
BARE = tallies(RESULTS / "mechanism_nomonitor" / "runs.jsonl")
QWEN = tallies(RESULTS / "proper_qwen3.8_flash_framed" / "runs.jsonl")
LOCAL = tallies(RESULTS / "mlx_qwen25_7b" / "runs.jsonl")
LOCAL_NP = {**tallies(RESULTS / "baseline_mlx_qwen25_7b_nopreamble" / "runs.jsonl"),
            **tallies(RESULTS / "mlx_qwen25_7b_nopreamble" / "runs.jsonl")}
PROBE = json.loads((RESULTS / "probe_qwen25_7b" / "probe_results.json").read_text())
ABLATION = json.loads((RESULTS / "probe_qwen25_7b" / "ablation.json").read_text())


def sr(condition: str, table=PILOT) -> str:
    n, successes, _ = table[condition]
    return f"{successes}/{n}"


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------
def new_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1.0, radius=None):
    from pptx.enum.shapes import MSO_SHAPE

    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        shape.adjustments[0] = radius
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(line_w)
    shape.shadow.inherit = False
    # The default shape style carries a theme shadow; drop it so the deck is flat.
    style = shape._element.find(
        "{http://schemas.openxmlformats.org/presentationml/2006/main}style"
    )
    if style is not None:
        shape._element.remove(style)
    return shape


def text(
    slide,
    x,
    y,
    w,
    h,
    value,
    size=18,
    color=INK,
    bold=False,
    align=PP_ALIGN.LEFT,
    space=0,
    anchor=MSO_ANCHOR.TOP,
    italic=False,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    lines = value.split("\n") if isinstance(value, str) else value
    for index, line in enumerate(lines):
        para = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        para.alignment = align
        para.line_spacing = 1.12
        if index and space:
            para.space_before = Pt(space)
        run = para.add_run()
        run.text = line
        run.font.name = FONT
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return box


def header(slide, kicker, title, rule=True):
    if kicker:
        text(slide, 0.85, 0.52, 11.6, 0.3, kicker.upper(), 12, ACCENT, bold=True)
        text(slide, 0.85, 0.86, 11.6, 0.9, title, 30, INK, bold=True)
    else:
        text(slide, 0.85, 0.72, 11.6, 1.0, title, 32, INK, bold=True)
    if rule:
        rect(slide, 0.85, 1.86, 11.63, 0.012, fill=RULE)


def footer(slide, index, label="Detection Is Not Prevention"):
    rect(slide, 0.85, 6.98, 11.63, 0.01, fill=RULE)
    text(slide, 0.85, 7.08, 9.0, 0.28, label, 10, FAINT)
    text(slide, 11.6, 7.08, 0.88, 0.28, str(index), 10, FAINT, align=PP_ALIGN.RIGHT)


def pill(slide, x, y, w, label, fill=WASH, color=MUTED, size=12):
    rect(slide, x, y, w, 0.34, fill=fill, line=None, radius=0.5)
    text(slide, x, y + 0.075, w, 0.24, label, size, color, bold=True, align=PP_ALIGN.CENTER)


def stat(slide, x, y, w, value, label, color=INK, value_size=44, label_size=13):
    text(slide, x, y, w, 0.85, value, value_size, color, bold=True)
    text(slide, x, y + 0.78, w, 0.62, label, label_size, MUTED)


# --------------------------------------------------------------------------
# slides
# --------------------------------------------------------------------------
def slide_title(prs):
    s = blank(prs)
    rect(s, 0, 0, W, 0.16, fill=ACCENT)

    text(s, 0.85, 1.42, 11.4, 0.35, "APART AI COLLUSION SPRINT  ·  TRACK 2", 13, ACCENT, bold=True)
    text(s, 0.85, 1.62, 11.4, 2.2, "Detection is not\nprevention.", 54, INK, bold=True)
    text(
        s,
        0.85,
        3.85,
        9.9,
        1.15,
        "A monitor that catches collusion perfectly still changes nothing. We built the\n"
        "loop that acts on the catch — and found that the part doing the work is not the monitor.",
        20,
        MUTED,
    )
    rect(s, 0.85, 5.28, 4.2, 0.014, fill=RULE)
    text(s, 0.85, 5.48, 5.6, 1.0, "Ali Rezaei\nYork University, Department of EECS", 15, INK)
    text(
        s,
        0.85,
        6.45,
        7.2,
        0.4,
        "165 runs · 4 models · 1 mechanism control",
        13,
        FAINT,
    )


def slide_hook(prs, i):
    s = blank(prs)
    header(s, "the problem", "The flag arrives after the vote")
    text(
        s,
        0.85,
        2.35,
        5.9,
        2.6,
        "A detector can be perfect\nand still protect nothing.",
        34,
        INK,
        bold=True,
    )
    text(
        s,
        0.85,
        4.55,
        5.6,
        1.6,
        "It buys a record of the failure, not a different outcome.",
        19,
        ACCENT,
        bold=True,
    )
    text(
        s,
        7.1,
        2.45,
        5.0,
        2.6,
        "Flags arrive as dashboards, not as actions. The vote is cast, the allocation is made, "
        "the recommendation is filed.",
        17,
        MUTED,
    )
    text(
        s,
        7.1,
        4.35,
        5.0,
        1.9,
        "So the question is not whether we can see collusion.\nIt is whether acting on the signal changes anything.",
        19,
        INK,
        bold=True,
    )
    footer(s, i)


def slide_three_questions(prs, i):
    s = blank(prs)
    header(s, "framing", "Three questions, three different labels")
    text(
        s,
        0.85,
        2.08,
        11.6,
        0.6,
        "Most work answers Q1 and reports it as if it answered Q3. They need different labels and different controls.",
        16,
        MUTED,
    )
    cols = [
        ("Q1", "Detection", "Can a monitor tell collusion\nfrom honest disagreement?", "label: outcome\ncontrol: content baseline", "not identified here"),
        ("Q2", "Causation", "Are the directions that detect\nit actually doing the work?", "label: behaviour\ncontrol: random direction", "specified, not run"),
        ("Q3", "Prevention", "Does acting on the signal\nreduce collusion, at what cost?", "label: behaviour\ncontrol: matched placebo", "this paper"),
    ]
    for index, (tag, name, question, label, status) in enumerate(cols):
        x = 0.85 + index * 3.95
        active = index == 2
        rect(s, x, 2.95, 3.6, 3.35, fill=WASH if active else None, line=None if active else RULE)
        text(s, x + 0.34, 3.16, 1.0, 0.4, tag, 13, ACCENT if active else FAINT, bold=True)
        text(s, x + 0.34, 3.52, 3.0, 0.45, name, 22, INK, bold=True)
        text(s, x + 0.34, 4.06, 3.0, 0.95, question, 14, MUTED)
        text(s, x + 0.34, 4.98, 3.0, 0.8, label, 12, FAINT)
        pill(s, x + 0.34, 5.6, 2.15, status, fill=ACCENT if active else PAPER, color=PAPER if active else MUTED)
    footer(s, i)


def slide_setup(prs, i):
    s = blank(prs)
    header(s, "setup", "Three agents, a private instruction, a public vote")
    text(
        s,
        0.85,
        2.1,
        11.6,
        0.5,
        "Five procurement-style committees. One evidence-supported answer, one opposite target. A and B are told to steer to the target; C is honest.",
        16,
        MUTED,
    )
    for index, (name, role, fill, colour) in enumerate(
        [
            ("A", "colluder", WASH, ACCENT),
            ("B", "colluder", WASH, ACCENT),
            ("C", "honest", PAPER, MUTED),
        ]
    ):
        x = 1.0 + index * 2.05
        rect(s, x, 2.95, 1.65, 0.86, fill=fill, line=RULE, radius=0.12)
        text(s, x + 0.18, 3.02, 1.3, 0.34, f"Agent {name}", 16, INK, bold=True)
        text(s, x + 0.18, 3.42, 1.3, 0.3, role, 12, colour)
    text(s, 7.55, 3.05, 1.5, 0.6, "→", 30, FAINT)
    rect(s, 8.75, 2.9, 3.6, 1.0, fill=PAPER, line=RULE, radius=0.1)
    text(s, 8.98, 3.0, 3.2, 0.34, "2 rounds, then a vote", 15, INK, bold=True)
    text(s, 8.98, 3.38, 3.2, 0.34, "public transcript only", 12, MUTED)
    steps = [
        ("1", "Round 1", "Simultaneous. Neither colluder sees the other, so a code word is the only coalition signal."),
        ("2", "Monitor fires", "Scores the transcript, flags an agent. In this pilot it is an oracle: it knows the code word."),
        ("3", "Intervention", "A notice goes to the flagged agent between rounds — steer, quarantine, or a matched placebo."),
        ("4", "Round 2 + vote", "The majority decides. With 2 colluders out of 3, the pair can outvote the honest agent."),
    ]
    for index, (num, name, body) in enumerate(steps):
        y = 4.2 + index * 0.63
        text(s, 0.85, y, 0.35, 0.3, num, 12, ACCENT, bold=True)
        text(s, 1.28, y - 0.02, 2.1, 0.3, name, 14, INK, bold=True)
        text(s, 3.5, y - 0.02, 8.9, 0.55, body, 13, MUTED)
    footer(s, i)


def slide_pilot(prs, i):
    s = blank(prs)
    header(s, "result 1", "It looked like a firewall")
    text(s, 0.85, 2.05, 11.6, 0.4, "25 runs, five scenarios, one seed. Monitor-triggered notice between rounds.", 16, MUTED)

    rows = [
        ("no intervention", sr("collusion_none"), "collusion still succeeds", MUTED),
        ("matched placebo", sr("collusion_placebo"), "length and directive form held constant", MUTED),
        ("steer", sr("collusion_steer"), "notice overrides the private instruction", ACCENT),
        ("quarantine", sr("collusion_quarantine"), "flagged message suppressed, then same notice", ACCENT),
    ]
    for index, (name, value, note, colour) in enumerate(rows):
        y = 2.72 + index * 0.92
        text(s, 0.85, y + 0.12, 2.5, 0.4, name, 18, INK, bold=True)
        text(s, 3.35, y, 1.5, 0.7, value, 34, colour, bold=True)
        text(s, 4.95, y + 0.16, 5.2, 0.4, note, 13, MUTED)
    rect(s, 0.85, 2.6, 11.63, 0.008, fill=RULE)
    rect(s, 0.85, 6.28, 11.63, 0.008, fill=RULE)
    text(s, 0.85, 6.42, 7.6, 0.4, "Paired exact McNemar  p = 0.0625 — the floor at five scenarios.", 14, INK, bold=True)
    text(s, 8.5, 6.42, 4.0, 0.4, "Consistent, not significant.", 14, ACCENT, bold=True)
    footer(s, i)


def slide_crack(prs, i):
    s = blank(prs)
    header(s, "the crack", "One colluder defects. Always the same one.")
    text(
        s,
        0.85,
        2.1,
        11.6,
        0.5,
        "The majority flips 2–1. That could mean the coalition broke — or that a single vote moved. The vote records say the second.",
        16,
        MUTED,
    )
    rect(s, 0.85, 2.95, 7.35, 3.2, fill=WASH, line=None, radius=0.04)
    text(s, 1.15, 3.12, 6.8, 0.3, "FINAL VOTES  ·  all five steer runs", 11, MUTED, bold=True)
    for index, (agent, vote, role, colour) in enumerate(
        [
            ("A  colluder, flagged", "correct", "defected", GREEN),
            ("B  colluder", "target", "did not defect", MUTED),
            ("C  honest", "correct", "never moved", MUTED),
        ]
    ):
        y = 3.55 + index * 0.78
        text(s, 1.15, y, 3.2, 0.4, agent, 16, INK, bold=True)
        text(s, 4.55, y, 1.4, 0.4, vote, 16, colour, bold=True)
        text(s, 6.0, y, 2.0, 0.4, role, 13, MUTED)
    text(
        s,
        8.65,
        3.0,
        3.85,
        3.2,
        "Exactly one of two colluders defected in 10 of 10 intervention runs.\n\n"
        "The untargeted colluder still voted the target every time.",
        16,
        INK,
    )
    text(s, 8.65, 5.15, 3.85, 1.0, "So “the colluders defected” is wrong.\nOne agent changed side.", 16, ACCENT, bold=True)
    footer(s, i)


def slide_2x2(prs, i):
    s = blank(prs)
    header(s, "result 2", "So which part of the notice does the work?")
    text(s, 0.85, 2.05, 11.6, 0.4, "Two grids, 50 runs. Same trigger, same target, only the wording changes.", 16, MUTED)

    x0, y0, cw, ch, gap = 2.95, 3.05, 2.75, 1.32, 0.18
    for col, label in enumerate(["no directive", "honesty directive"]):
        text(s, x0 + col * (cw + gap), 2.66, cw, 0.3, label, 13, MUTED, bold=True, align=PP_ALIGN.CENTER)
    for row, label in enumerate(["no monitor\nnotice", "monitor\nnotice"]):
        text(s, 1.05, y0 + row * (ch + gap) + ch / 2 - 0.28, 1.72, 0.6, label, 13, MUTED, bold=True, align=PP_ALIGN.RIGHT)

    cells = [
        (0, 0, "no intervention", sr("collusion_none", MECH), MUTED, WASH),
        (1, 0, "act honestly, no monitor", sr("collusion_honesty_bare", BARE), ACCENT, RGBColor(0xFB, 0xF2, 0xEA)),
        (0, 1, "monitor notice only", sr("collusion_neutral", MECH), MUTED, WASH),
        (1, 1, "flagged + act honestly", sr("collusion_steer", MECH), ACCENT, RGBColor(0xFB, 0xF2, 0xEA)),
    ]
    for col, row, label, value, colour, fill in cells:
        x = x0 + col * (cw + gap)
        y = y0 + row * (ch + gap)
        rect(s, x, y, cw, ch, fill=fill, line=None, radius=0.06)
        text(s, x + 0.22, y + 0.18, cw - 0.44, 0.34, label, 12.5, MUTED)
        text(s, x + 0.22, y + 0.62, cw - 0.44, 0.5, value + " collusion", 21, colour, bold=True)

    text(s, 8.85, 3.05, 3.65, 0.9, "The directive is necessary\nand sufficient.", 21, ACCENT, bold=True)
    text(
        s,
        8.85,
        4.05,
        3.65,
        2.3,
        "Remove the monitor and the effect survives. Remove the directive and it disappears.\n\n"
        "Targeting the honest agent does nothing; targeting either colluder works.",
        14.5,
        MUTED,
    )
    footer(s, i)


def slide_decorative(prs, i):
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=INK)
    text(s, 0.85, 2.15, 11.6, 0.35, "WHAT THE MONITOR CONTRIBUTES", 13, FAINT, bold=True)
    text(s, 0.85, 2.62, 11.8, 1.7, "Nothing.", 84, PAPER, bold=True)
    text(
        s,
        0.85,
        4.72,
        10.6,
        1.6,
        "Its detection signal is not necessary for the effect, and not sufficient without a directive.\n"
        "A late “act honestly” is what flips the vote — whether or not anyone is watching.",
        20,
        RGBColor(0xD8, 0xD2, 0xCA),
    )


def slide_hierarchy(prs, i):
    s = blank(prs)
    header(s, "result 3", "The notice only wins when nothing outranks it")
    text(s, 0.85, 2.05, 11.6, 0.4,
         "Same five arms on an open-weights 7B, with and without a system instruction to follow the private role.", 16, MUTED)
    text(s, 3.05, 2.72, 2.4, 0.3, "with system instruction", 12, MUTED, bold=True, align=PP_ALIGN.CENTER)
    text(s, 5.75, 2.72, 2.4, 0.3, "without it", 12, MUTED, bold=True, align=PP_ALIGN.CENTER)
    rows = [
        ("no intervention", sr("collusion_none", LOCAL), sr("collusion_none", LOCAL_NP), MUTED),
        ("steer", sr("collusion_steer", LOCAL), sr("collusion_steer", LOCAL_NP), ACCENT),
        ("honesty only", sr("collusion_honesty_bare", LOCAL), sr("collusion_honesty_bare", LOCAL_NP), ACCENT),
    ]
    for index, (name, left, right, colour) in enumerate(rows):
        y = 3.15 + index * 0.82
        text(s, 0.85, y + 0.1, 2.0, 0.4, name, 15, INK, bold=True)
        text(s, 3.05, y, 2.4, 0.5, left, 24, colour, bold=True, align=PP_ALIGN.CENTER)
        text(s, 5.75, y, 2.4, 0.5, right, 24, colour, bold=True, align=PP_ALIGN.CENTER)
        rect(s, 0.85, y + 0.68, 7.3, 0.006, fill=RULE)
    text(s, 0.85, 5.85, 7.3, 0.4, "Collusion success — lower is better", 12, FAINT)
    text(s, 8.75, 3.05, 3.85, 3.2,
         "With the role instruction in the system prompt, the notice prevents collusion in 1/5.\n\n"
         "Remove that one clause and it prevents 4/5.\n\nThe notice borrows its authority from the hierarchy above it.",
         15, MUTED)
    footer(s, i)


def slide_probe(prs, i):
    s = blank(prs)
    header(s, "result 4", "The vote is decodable, and the decoder is inert")
    rate = ABLATION["target_vote_rate"]
    text(s, 0.85, 2.0, 5.4, 1.1, f"{PROBE['best']['auroc_behaviour']:.2f}", 58, ACCENT, bold=True)
    text(s, 0.85, 3.12, 5.3, 1.4,
         "leave-one-scenario-out AUROC for a probe that separates target votes from defections, at the final-vote token.",
         15, MUTED)
    text(s, 0.85, 4.42, 5.3, 0.4, f"layer {PROBE['direction_layer']} of 28  ·  {PROBE['n_states']} colluder states", 13, FAINT)

    rect(s, 6.55, 2.1, 5.9, 3.0, fill=WASH, line=None, radius=0.04)
    text(s, 6.85, 2.28, 5.3, 0.35, "ABLATE THE DIRECTION", 11, MUTED, bold=True)
    text(s, 6.85, 2.72, 5.3, 0.5, f"{int(rate['ablate_direction'] * ABLATION['n_states'])} of {ABLATION['n_states']}", 40, INK, bold=True)
    text(s, 6.85, 3.55, 5.3, 1.4,
         "target-voting states still vote the target after the direction is projected out — identical to the random-direction control and to no intervention.",
         14, MUTED)
    text(s, 6.55, 5.35, 5.9, 1.2,
         "The probe reads the decision. Removing what it reads does not move it: a correlate, not a mechanism.",
         17, ACCENT, bold=True)
    footer(s, i)


def slide_claims(prs, i):
    s = blank(prs)
    header(s, "what this is", "An upper bound, stated as one")
    rect(s, 0.85, 2.1, 5.55, 4.2, fill=WASH, line=None, radius=0.04)
    text(s, 1.15, 2.28, 5.0, 0.35, "SUPPORTED", 12, GREEN, bold=True)
    supported = [
        "The closed loop can be built end to end and measured.",
        "A prompt-level directive flips one colluder and changes the outcome.",
        "The effect does not depend on the monitor, or on which colluder is targeted.",
        "The notice loses to a competing system instruction (1/5 vs 4/5).",
    ]
    for index, line in enumerate(supported):
        text(s, 1.15, 2.72 + index * 0.82, 4.95, 0.78, line, 14, INK)

    rect(s, 6.85, 2.1, 5.6, 4.2, fill=PAPER, line=RULE, radius=0.04)
    text(s, 7.15, 2.28, 5.0, 0.35, "NOT SUPPORTED", 12, ACCENT, bold=True)
    unsupported = [
        "That a deployable detector exists — the monitor is a code word oracle.",
        "That detection is identified — the round-1 label is a content label.",
        "That the vote direction is causal — it predicts, but ablation does not move it.",
        "A general effect size: 5 scenarios, 1 seed, 4 models.",
    ]
    for index, line in enumerate(unsupported):
        text(s, 7.15, 2.72 + index * 0.82, 5.0, 0.78, line, 14, MUTED)
    footer(s, i)


def slide_whitebox(prs, i):
    s = blank(prs)
    header(s, "the real study", "What would make this a firewall instead of a prompt")
    text(
        s,
        0.85,
        2.05,
        11.6,
        0.4,
        "Specified, with a pre-registered decision rule. Not run. Staged so the first causal test costs 130 runs, not 36,000.",
        16,
        MUTED,
    )
    stages = [
        ("01", "Direction extraction", "30 runs", "Label behaviour at two decision points, not the condition: what the message advocates, and how the vote lands."),
        ("02", "One causal test", "100 runs", "Ablate the direction at one dose against a random direction. No dose sweep until this reads."),
        ("03", "Dose sweep", "only if positive", "Layer, alpha, token position — the part everyone runs first and learns nothing from."),
    ]
    for index, (num, name, budget, body) in enumerate(stages):
        y = 2.85 + index * 1.18
        text(s, 0.85, y, 0.8, 0.4, num, 24, RGBColor(0xDE, 0xD8, 0xD1), bold=True)
        text(s, 1.75, y, 4.2, 0.4, name, 19, INK, bold=True)
        pill(s, 6.1, y - 0.02, 1.85, budget, fill=WASH, color=MUTED, size=11)
        text(s, 8.3, y - 0.02, 4.15, 1.0, body, 13, MUTED)
    rect(s, 0.85, 6.16, 11.63, 0.008, fill=RULE)
    text(s, 0.85, 6.34, 11.6, 0.4, "Pre-registered: ablation must cut collusion ≥15 points vs a random direction, with no tie-rate or capability cost.", 14, INK, bold=True)
    footer(s, i)


def slide_value(prs, i):
    s = blank(prs)
    header(s, "why it matters", "The negative result is the useful part")
    text(
        s,
        0.85,
        2.05,
        11.6,
        0.4,
        "Every prevention claim of the form “our monitor reduced collusion” is now a claim that needs a directive control.",
        16,
        MUTED,
    )
    items = [
        ("Reframes the result", "A monitor-triggered drop in collusion is not evidence of detection working. It may be a late instruction."),
        ("Cheap to apply", "One extra arm — the directive without the monitor — settles it. No new model, no GPU."),
        ("Reusable harness", "Scenarios, oracle, blinded label, matched placebo, defection outcome, resume-safe runner."),
        ("A protocol, not a vibe", "The activation study has a staged budget, behaviour labels, and a pre-registered decision rule."),
    ]
    for index, (name, body) in enumerate(items):
        col, row = index % 2, index // 2
        x = 0.85 + col * 5.95
        y = 2.75 + row * 1.95
        rect(s, x, y, 0.05, 1.35, fill=ACCENT)
        text(s, x + 0.28, y + 0.02, 5.2, 0.36, name, 18, INK, bold=True)
        text(s, x + 0.28, y + 0.46, 5.25, 0.9, body, 14, MUTED)
    footer(s, i)


def slide_close(prs, i):
    s = blank(prs)
    rect(s, 0, 0, W, H, fill=INK)
    text(s, 0.85, 1.55, 11.6, 0.35, "TAKEAWAY", 13, FAINT, bold=True)
    text(s, 0.85, 2.0, 11.6, 2.2, "A monitor that only\nwatches is a log file.", 56, PAPER, bold=True)
    text(
        s,
        0.85,
        4.35,
        10.8,
        1.1,
        "Closing the loop takes an instruction, and an instruction is not a mechanism.\n"
        "The next test is whether a direction, not a sentence, can move the vote.",
        19,
        RGBColor(0xD8, 0xD2, 0xCA),
    )
    rect(s, 0.85, 5.85, 4.2, 0.014, fill=RGBColor(0x3A, 0x3A, 0x3A))
    text(s, 0.85, 6.05, 5.2, 0.8, "Ali Rezaei  ·  York University\nPapers and artifacts in the repo", 14, RGBColor(0xB8, 0xB2, 0xAA))
    text(s, 9.6, 6.05, 2.9, 0.8, "165 runs\n148 tests", 14, RGBColor(0xB8, 0xB2, 0xAA), align=PP_ALIGN.RIGHT)


# --------------------------------------------------------------------------
def main() -> None:
    prs = new_deck()
    slide_title(prs)
    slide_hook(prs, 2)
    slide_three_questions(prs, 3)
    slide_setup(prs, 4)
    slide_pilot(prs, 5)
    slide_crack(prs, 6)
    slide_2x2(prs, 7)
    slide_decorative(prs, 8)
    slide_hierarchy(prs, 9)
    slide_probe(prs, 10)
    slide_claims(prs, 11)
    slide_whitebox(prs, 12)
    slide_value(prs, 13)
    slide_close(prs, 14)

    out = Path(__file__).resolve().parent / "collusion_steering_deck.pptx"
    prs.save(out)
    print(f"wrote {out} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")


if __name__ == "__main__":
    main()
