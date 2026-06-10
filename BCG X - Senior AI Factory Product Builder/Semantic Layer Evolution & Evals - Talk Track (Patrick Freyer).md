# Semantic Layer Evolution & Evals — Talk Track (Patrick Freyer)

**For:** Round 2, Tue 6/16. Covers the resume bullet *"Productized two AI skills (cp-analytics, Simple CP Interaction) org-wide as official internal Wibey skills"* — which has moved substantially since the resume was submitted 4/28.

> **The frame:** the resume being "out of date" is not a liability — it's your best material. Six weeks of ship → watch → restructure is exactly the build-break-rebuild profile Patrick hires for. Tell it as a product story, not a correction.

---

## 1. The evolution story (~90 sec, hard cut)

Five beats: context engineering → trust problem → semantic layer → parallel reconciliation experiment → sequential + human gate.

> "That bullet has actually moved a lot since I submitted this resume — which is kind of the story. It started as a context-engineering approach: the skill assembled context and had the model write raw SQL, with everything it did traced to persistent logs. It worked, but once I was deeper in with the product and data science teams, the real problem surfaced: trust. The same question could produce slightly different SQL and slightly different numbers, and business users notice that immediately.
>
> So I moved the business logic into a semantic layer. Definitions live as governed semantic definitions, the model's only job is mapping the question to the right definition, and a compiler generates the SQL deterministically. Same question, same answer, every time.
>
> I first ran both paths in parallel — user only ever saw the semantic layer's answer, and a reconciliation agent graded it against the context-engineered path and proposed definition fixes or inserts when the semantic layer missed. Useful, but I was paying double compute on every question for what was really an offline improvement problem.
>
> So now it's sequential: only the semantic layer runs, with heavy logging and traceability. I review the misses, and any new or changed definition goes through a human gate — me first, then the business team that owns that definition. That gate is the governance: the business owns the meaning of its own metrics."

**Why this lands with Patrick:**

- Ship → watch usage → restructure twice in six weeks = his "build, break, rebuild" hiring filter, lived.
- Parallel → sequential is a real product judgment: 2x compute in the request path for offline value → move the grading offline, onto logs.
- The human gate is a governance answer — connects directly to his "which MCP servers and what governance" thesis without quoting his post.
- Determinism-for-trust is product instinct, not eval theory.

---

## 2. The reframe (internalize before drilling answers)

You've been thinking "I only verify the steps, not whether the intent of the question was answered." Flip it:

**The semantic layer collapsed the eval problem.** In the context-engineering world, the eval surface was the entire free-form SQL generation. In the semantic-layer world, the compiler is deterministic — testable like normal software. The *only* probabilistic step left is **question → semantic definition mapping**. And "did the model map the question to the right definition" *is* the intent question. You didn't skip intent eval; you engineered it down to one step.

Two corollaries:

1. **The human gate is your labeling engine.** Every correction you or a business owner makes — definition changed, definition inserted — is a labeled example of a failure mode. The gate isn't just governance; it's the eval-dataset flywheel.
2. **Eval difficulty was an architecture signal.** The context-engineering path was hard to evaluate end-to-end *because* free-form generation has no cheap regression test. That difficulty is part of why the semantic layer is the right design.

---

## 3. "How do you evaluate it?" — the answer (did / gap / would)

**Did (claim precisely — this is all real):**

> "Today my evals are process-level, and that's deliberate. On the semantic layer side: I verify the model selected a definition, that the compiler produced correct SQL from it, and that the number is right — every step logged and traceable, so when something's off I can see exactly which step broke. Misses become definition changes or inserts, and those go through the human gate. On the context-engineering side I had a golden set of questions and answers it had to score against, plus SQL correctness judging and full traces of every model action."

**Gap (volunteer it — drawing the line yourself reads senior):**

> "What I haven't built yet is answer-level eval — does the answer actually satisfy what the user meant, end to end. My checks verify the machinery, not the intent fulfillment. I'll be straight that the gate for that today is me reviewing the logs."

**Would (always land this — the design, with metrics):**

> "But here's the thing the semantic layer bought me: the eval problem shrank. The compiler is deterministic, so the only probabilistic step left is question-to-definition mapping — and that mapping *is* the intent question. So the harness I'd build is focused:
>
> 1. **Golden intent set** — real logged questions paired with the expected definition(s) and expected answer. Because the back half is deterministic, this doubles as a cheap regression suite I rerun on every definition change.
> 2. **The human gate as the labeling flywheel** — every correction through the gate is a labeled failure case that goes straight into the regression set. The eval dataset grows from real usage, not from me inventing test cases.
> 3. **Metrics:** definition-selection accuracy, coverage rate (no matching definition → abstain, never guess), and regression pass rate on definition changes.
> 4. **LLM-as-judge only as triage, never as truth** — a judge flags suspect answers for human review, and I'd calibrate it against the human verdicts coming out of the gate before trusting its flags. Ground truth stays with the business owner of the definition."

**The closer:**

> "Honestly, the semantic layer was an eval decision as much as an architecture decision. When I couldn't write a cheap regression test for the context-engineering path, that was a smell. The semantic layer is the testable version of the same capability."

---

## 4. If he pushes on the context-engineering era specifically

> "There I had traceability — every model action written persistently to markdown or JSON — SQL correctness judging, and a golden question set it scored against. The honest gap was the same one, sharper: nothing judged whether a *novel* production question was actually answered as intended, and with free-form SQL generation there's no cheap way to regression-test that. I could have thrown an LLM judge at it, but a judge grading open-ended generation is the weakest kind of eval — uncalibrated opinion on top of uncalibrated generation. The better move was structural, and that's the move I made."

---

## 5. Anticipated follow-ups

**"Doesn't the human gate bottleneck you?"**
> "Right now I'm first in the gate on purpose — I'm calibrating what a good definition looks like. The scaling path is that the business team owning the definition approves, and I drop to sampling. Rigor scales with blast radius: while the definition set is young, a human gate is the right amount of friction."

**"How do you tell a missing definition from a mis-selected one?"**
> "The logs distinguish them. No-match means a coverage gap — that's an insert candidate. Wrong-match means the definition or its description needs fixing. Different failure, different fix, and the trace tells me which I'm looking at."

**"What about ambiguous questions?"**
> "Abstain or clarify over guess. And the answer shows which definition was used — so if the user meant something different by 'active panelist,' they can see the definition and catch it. Showing your work is part of the trust design."

**"Why not keep the parallel reconciliation agent?"**
> "It was double compute in the request path for value that's really offline. The grading doesn't need to happen live — it needs to happen on the logs. Same improvement loop, removed from the hot path."

**"Is the resume wrong then?"**
> "It was accurate on April 28th. The skills are still productized and in use — what's evolved is the architecture underneath them, twice. Happy to walk through both moves."

---

## 6. One-line anchors

- "The semantic layer was an eval decision as much as an architecture decision."
- "Only one probabilistic step left — question to definition — so that's where the eval lives."
- "Every correction through the gate is a labeled example. The gate is the flywheel."
- "If I can't write a cheap regression test for a system, that's an architecture smell."
- "Determinism builds trust; the human gate is the governance."
- "Judge as triage, business owner as truth."

---

*Companion to `Honest Framing - Research-Driven Builds & Eval Gaps.md` (the did/gap/would mechanics) and `Round 2 Prep Plan - Patrick Freyer.md` (overall strategy). Note: `Work Artifacts/customer-voice-semantic-layer.md` describes the earlier parallel/reconciliation design — superseded by the sequential approach described here.*
