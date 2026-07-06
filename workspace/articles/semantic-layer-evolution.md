---
title: "The Semantic Layer Was an Eval Decision"
slug: semantic-layer-evolution
date: 2026-06-11
author: Kanu Madhok
summary: "My text-to-data system got rebuilt twice in six weeks: from free-form SQL generation, to a parallel reconciliation experiment, to a governed semantic layer with a human gate. Each move was forced by the same question — how do I know the answer is right?"
tags: [ai-agents, semantic-layer, evals, text-to-sql, governance, analytics]
status: draft
---

# The Semantic Layer Was an Eval Decision

The architecture of my text-to-data system changed twice in six weeks. Not because either version was broken — both worked. It changed because of a question I couldn't answer cheaply: *how do I know the answer is right?*

This post is the story of those two moves. It starts with an agent that writes free-form SQL, detours through an experiment where every question got answered twice, and lands on a governed semantic layer with a human gate. The punchline is in the title: what looks like an architecture decision was really an eval decision, and I'd argue that's true of most agentic system design.

This is the second post in a series. The [first one](/articles/context-engineering-platform) covered the context platform underneath all of this — the substrate. This one is about the thing users actually touch.

## Version one: context engineering and free-form SQL

The first version was the natural extension of the platform: assemble rich context (schema, join paths, domain rules, similar past queries), hand it to a model, have the model write raw SQL, validate, execute. Everything the model did was traced to persistent logs.

It worked. Stakeholders asked questions in plain English and got answers backed by real, runnable SQL.

Then I got deeper in with the product and data science teams who actually consumed the answers, and the real problem surfaced: **trust**. The same question could produce slightly different SQL and slightly different numbers on different runs. Not wildly different — a filter applied a little differently, a date boundary interpreted another way. Business users notice that immediately, and they notice it in the worst possible way: they stop trusting *all* the answers, including the right ones.

Underneath the trust problem was an eval problem. The eval surface of free-form SQL generation is enormous — every question is a new generation, and there's no cheap regression test for "did the model write the right query this time." I had a golden set of questions it had to score against, SQL correctness judging, and full traces of every action. Good process-level checks. But nothing could cheaply tell me, for a novel production question, whether the *intent* was answered correctly. I could have thrown an LLM judge at it, but a judge grading open-ended generation is the weakest kind of eval — uncalibrated opinion stacked on uncalibrated generation.

That difficulty was the signal. If I can't write a cheap regression test for a system, that's an architecture smell.

## Version two: move the meaning into a semantic layer

So I moved the business logic out of the model and into a semantic layer.

Definitions — what counts as an active user, how engagement is measured, which revenue number is *the* revenue number — live as governed semantic definitions. The model's only job is mapping a natural-language question to the right definition. A compiler then generates the SQL deterministically.

Same question, same answer, every time.

This is the move that collapsed the eval problem. In the free-form world, the eval surface was the entire generation. In the semantic-layer world, the compiler is deterministic — testable like normal software, because it *is* normal software. The only probabilistic step left is question → definition mapping. And here's the part I didn't appreciate until I'd built it: "did the model pick the right definition" *is* the intent question. I didn't skip intent evaluation. I engineered it down to a single, checkable step.

## The detour: answering every question twice

Between those two versions I ran an experiment worth describing, because the way it failed is as instructive as the way it worked.

For a while, both paths ran in parallel on every question. The user only ever saw the semantic layer's answer. Behind the scenes, a reconciliation agent compared it against the free-form path's answer, classified the outcome into a fixed taxonomy (verified, divergent, ambiguous, coverage gap, both-error), and proposed definition fixes or inserts whenever the semantic layer missed something the raw path caught.

The deterministic taxonomy mattered: a strict set of verdict categories keeps the reconciler predictable. If a new category is needed, you extend the spec — you don't let the model invent one mid-run.

And it was genuinely useful. Disagreements between the two paths surfaced real coverage gaps and real modeling bugs. A clean, confident answer from a single path built on a wrong filter is the failure mode I worry about most, and the second path caught exactly that.

But I was paying double compute on every single question, in the request path, for what was fundamentally an *offline* improvement problem. The grading didn't need to happen live. It needed to happen on the logs.

## Version three: sequential, logged, human-gated

So the current architecture is sequential. Only the semantic layer runs in the request path, with heavy logging and full traceability: which definition was selected, what SQL the compiler produced, what the number was. When something's off, the trace shows exactly which step broke.

I review the misses offline. The logs distinguish the two failure modes cleanly: a *no-match* means a coverage gap — that's a candidate for a new definition. A *wrong-match* means an existing definition or its description needs fixing. Different failure, different fix, and the trace tells me which one I'm looking at.

Any new or changed definition goes through a human gate: me first, then the business team that owns that definition. That gate is the governance. The business owns the meaning of its own metrics — the system proposes, humans ratify.

The gate turned out to be more than governance. **Every correction that passes through it is a labeled example of a failure mode.** Definition changed? That's a labeled wrong-match. Definition inserted? A labeled coverage gap. The eval dataset grows from real usage instead of from me inventing test cases. The gate is the flywheel.

Two smaller design choices that pull weight:

- **Abstain over guess.** When no definition matches, the system says so rather than improvising. And every answer shows which definition was used — so if a user meant something different by "active user," they can see the definition and catch it. Showing your work is part of the trust design.
- **Rigor scales with blast radius.** Right now I'm first in the gate on purpose, calibrating what a good definition looks like. The scaling path is that the owning business team approves and I drop to sampling. While the definition set is young, a human gate is the right amount of friction.

## What I'd build next

The honest gap: my evals today are process-level. I verify that a definition was selected, that the compiler produced correct SQL from it, and that the number is right. What I haven't built is answer-level eval — does the answer satisfy what the user *meant*, end to end. The gate for that today is me reviewing logs.

But the semantic layer shrank that problem to a buildable size, and the harness I'd build is focused:

1. **A golden intent set** — real logged questions paired with their expected definitions and expected answers. Because the back half of the pipeline is deterministic, this doubles as a cheap regression suite to rerun on every definition change.
2. **The gate as the labeling engine** — every human correction flows straight into the regression set.
3. **Three metrics:** definition-selection accuracy, coverage rate (no match → abstain, never guess), and regression pass rate on definition changes.
4. **LLM-as-judge as triage only, never as truth.** A judge flags suspect answers for human review, calibrated against the human verdicts coming out of the gate. Ground truth stays with the business owner of the definition.

## The takeaway

Three lessons, in the order I paid for them:

**Determinism builds trust.** Business users will forgive a system that says "I don't have a definition for that." They will not forgive a system that gives two different numbers for the same question. If your users are deciding whether to trust the numbers, deterministic compilation beats clever generation.

**Don't pay request-path costs for offline value.** The parallel reconciliation experiment was good engineering aimed at the wrong place in the pipeline. Grading belongs on the logs, not in the hot path. Same improvement loop, a fraction of the cost.

**Eval difficulty is an architecture signal.** When I couldn't write a cheap regression test for free-form SQL generation, the answer wasn't a more elaborate eval harness — it was a different architecture that left less to evaluate. The semantic layer is the testable version of the same capability. That's why I say it was an eval decision as much as an architecture decision: the systems that survive in production are the ones you can cheaply prove are still working.

---

*Previously in this series: [Context Engineering for Multi-Agent Analytics](/articles/context-engineering-platform) — the substrate all of this runs on.*

---

## Confidentiality pre-publication checklist

Before this article goes anywhere public, verify each line:

- [ ] No internal product names (Wibey, cp-hybrid, cp-analytics, customer-voice-semantic-layer, jira-ticket-worker, etc.)
- [ ] No internal team names, manager names, or coworker names
- [ ] No fully-qualified table references or warehouse column/table names
- [ ] No vendor/tool names tied to internal infrastructure choices (Cube.js deliberately omitted — "governed semantic definitions + compiler" is the public shape)
- [ ] No row-level scale numbers that aren't already public (panelist counts, task-row counts generalized away entirely)
- [ ] No internal repo paths, Slack channels, or config references
- [ ] No screenshots of internal UIs
- [ ] Manager test: would my manager shrug or flinch?

Current sanitization status: written sanitized from the start. All numbers are qualitative ("six weeks", failure-mode taxonomy); the 0.5% reconciliation tolerance and verdict-category names were generalized. No internal names appear.
