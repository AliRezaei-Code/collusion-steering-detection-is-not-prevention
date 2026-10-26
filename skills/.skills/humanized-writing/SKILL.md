---
name: humanized-writing
description: Use when writing or revising prose in this repository (papers, reports, READMEs, decks) so it reads like a person wrote it, without weakening claims or changing numbers. Also use when reviewing text that a humanizer tool has already rewritten.
---

# Humanized academic prose

Detectors and humanizers chase a moving target, so do not optimise for a detector.
Optimise for the thing detectors approximate: prose whose sentences were chosen one
at a time by someone with something to say.

## The non-negotiables

A style pass may change **how** a claim is stated. It may never change **what** is
claimed. Before you start, mark every number, hedge, and comparison in the passage.
After you finish, diff them. If a rewritten sentence is stronger than the original,
the edit is wrong, even if it reads better.

Concretely: never soften "5/5" to "most", never turn "cannot identify" into "does not
find", never promote "correlate" to "cause", and never delete a limitation to make a
paragraph flow. A paper that reads beautifully and overclaims is worse than one that
reads stiffly and is true.

## Tells, and what to do instead

**Uniform sentence length.** Three 25-word sentences in a row is the loudest machine
tell. Break one into two. Let one be six words. Variation carries more voice than any
word choice.

**The triadic list.** "Detection, causation, and prevention" is fine once. Three
parallel items per paragraph, paragraph after paragraph, is a template. Use two items,
or four, or a clause.

**Em-dash apposition.** `X — which does Y — is Z`. One per page is punctuation. One
per paragraph is a tic. Most can be a comma, a colon, a full stop, or a parenthetical.

**Nominalisation.** "The identification of the mechanism" → "identifying the
mechanism". "The utilisation of" → "using". Verbs do the work.

**Hedge stacking.** "It is worth noting that this may potentially suggest" is three
hedges on one claim. Decide how sure you are and say that once.

**The empty opener.** "It is important to note that", "In this section, we", "As
previously mentioned". Delete the first four words and check whether the sentence
improved. It usually did.

**Symmetrical paragraph shapes.** Every paragraph starting with a topic sentence,
three supporting sentences, and a wrap-up is a tell. Start one paragraph mid-thought.
End one on a detail rather than a summary.

**"This is consistent with".** Fine once. As a recurring connective it means the
argument is not actually being made.

## What good looks like

Before:

> The intervention is therefore changing the colluders' votes, not only the honest
> agent's. The placebo shows that being noticed and receiving a directive is not
> sufficient: it has the same monitor trigger and a concrete directive, but it does
> not name the target or the vote, and collusion still succeeds in 5/5.

After:

> So the intervention changes one colluder's vote, not the honest agent's. The
> placebo makes the point sharper: it carries the same trigger and a directive just
> as concrete, but it never names the target, and collusion still succeeds in 5/5.

The numbers are identical. The second version has a short sentence, an asymmetric
rhythm, and no colon-led triad.

Before:

> The active ingredient is the **honesty directive**, not the monitor trigger or the
> target; the effect is directive-specific, not monitor-specific.

After:

> The active ingredient is the **honesty directive**. Not the trigger, not the
> target. The effect belongs to the directive.

Same claim, three sentences of different lengths, no semicolon scaffold.

## Procedure

1. Read the passage aloud in your head. Every place you would breathe wrong is a
   candidate.
2. Mark the claims and numbers before touching a word.
3. Rewrite paragraph by paragraph, not sentence by sentence — the paragraph is the
   unit of rhythm.
4. Cut 10% by default. Humanizers lengthen; good writers cut.
5. Diff the numbers. Diff the hedges. Diff the comparisons.
6. Read the result once more for a single question: does any sentence exist because
   the previous one needed company?

## On humanizer tools (QuillBot and friends)

They reliably flatten. They also reword claims, drop qualifiers, and occasionally
invent a connective that reverses causation. If a tool's output is used, treat it as
a draft of the prose and the original as the source of truth: port the rhythm, then
restore every number and hedge by hand, then re-read for meaning. Never paste tool
output over a technical paragraph without that comparison.

Their useful habit is paragraph-scale rewriting. Their harmful habit is synonym
substitution for its own sake — "significant" for "large", "leverage" for "use".
Prefer the plain word.

## Scope

This applies to papers, reports, READMEs, and slide copy in this repository. It does
not apply to code comments, commit messages, or API docs, where consistency and
greppability beat voice.
