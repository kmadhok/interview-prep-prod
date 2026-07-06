# Interview with Maan — Brief & Format

**Round:** First round, BCG X Senior AI Factory Product Builder
**Date/Time:** Mon 2026-06-01, 2:00 PM ET (1:00 PM CT)
**Duration:** 45 minutes total
**Tool:** Zoom + **Zoom Whiteboarding function** (test before Monday)
**Zoom link:** see `Messages with Recruiter.md` (confirmation email 5/29)
**Honor code:** no external resources, no AI tools during live case, destroy notes after

---

## What the recruiter said (Ganna Volkova, 5/29 6:09 PM CT, verbatim)

> "Thanks for checking in with me. The first round includes two segments: behavioral and technical/AI background, along with a case interview (whiteboarding). Be prepared to discuss your experience, highlight how you approach problem-solving, and demonstrate your understanding of translating ambiguous business problems into solutions. The case will focus on how you structure problems and think through solutions, so clarity and logical reasoning matter more than arriving at a 'perfect' answer."
>
> **Tool:** Zoom Whiteboarding function — check it out ahead of time if you've never used it before.
> **Duration:** 45 minutes.

**Decoding her framing:** three things in 45 minutes, not two — (1) behavioral, (2) technical/AI background, (3) case interview using Zoom Whiteboard. The case is where the whiteboard comes out; behavioral and technical/AI background are conversational. Judged on **structure, clarity, logical reasoning** under ambiguity — NOT on arriving at the right answer.

---

## Maan Hani — background (from public sources)

- **Name:** Maan H. Hani, PhD
- **Current role:** Principal, BCG X (per recruiter email 5/29). ZoomInfo still shows "Project Leader at BCG" — stale; the Principal promotion appears recent.
- **Location:** Calgary, AB (LinkedIn) — historically Boston-affiliated (ZoomInfo).
- **PhD:** Astronomy/Astrophysics, **University of Victoria** (Canada). Vanier Scholar; advisor Prof. Sara Ellison. Research focus: galaxy evolution / star formation; co-authored work in *Monthly Notices of the Royal Astronomical Society* (MNRAS), including work on early massive-galaxy assembly.
- **Prior industry stop:** LinkedIn (pre-BCG).
- **Public signal:** LinkedIn post from ~late 2024 / early 2025 about a "Key to Purpose" recognition — community/purpose dimension. Don't lead with it.

### What this means for the interview

**He's technical-deep.** PhD astrophysicist with publications. Don't dumb down architecture — be precise about the eval loop, retrieval choices, tool-use boundaries. Hand-waving will register; rigor will land.

**He's a career switcher who shipped.** Astronomy → LinkedIn → BCG. He's lived the "research-to-product" arc. Frame your own non-linear path (Loyola → Walmart Data Ventures → AI builder shipping internally) as a peer move, not as something needing apology. He'll over-index on people who can land technical work in non-technical orgs — your "internal champion / shipped to consultants" story is the right shape.

**Recent promotion (Project Leader → Principal).** Now running case teams, not just contributing. The case will likely test how *you'd* run/scope a case team's tooling, not pure execution. Expect questions about prioritization, what to deprioritize, when an AI tool is "done enough" to roll out.

**LinkedIn alum.** Has seen scaled data products and ML platforms at a tier-1 tech co. He'll notice the difference between "I built a demo" and "I shipped something people use." Lead with **adoption + business outcome** on every demo, not architecture.

**Calgary-based / distributed.** Geography unlikely to come up — he's hybrid himself, Chicago base is non-issue.

---

## Segment 1 — Behavioral (~8–10 min, conversational)

Likely opens with TMAY (60–90 sec), then drills into 2–3 stories. He'll probe past surface STAR — wants ownership, judgment under ambiguity, what you'd do differently.

Likely prompts:
- TMAY ("walk me through your background")
- "Tell me about a time you shipped something despite ambiguity / pushback / a moving target"
- "Tell me about a project that didn't go the way you expected" (failure story — have one ready)
- "Why BCG X / why this role?" (peer-move framing: research → LinkedIn → BCG is his arc; Walmart → AI builder is yours)

What he weights: clarity of business problem in dollars/hours, real ownership (not "we"), adoption/business outcome at the close, and one honest "what I'd do differently" beat.

---

## Segment 2 — Technical / AI background (~10–15 min, conversational; possible whiteboard cameo)

Maan probing what you actually built and how rigorously you think about it. Verbal, but he may say "draw me the architecture" mid-discussion — be ready to sketch a 5-box diagram in 60 seconds.

Likely trigger: "Walk me through an AI product you've shipped" or "tell me about your most interesting build."

What he'll push on, ranked by likelihood:

- **Eval strategy.** PhD scientist + LinkedIn alum — he WILL ask "how do you know it works?" Have a concrete answer:
  - NL-to-SQL Copilot: query equivalence checks + execution-result matching + schema grounding + LLM-as-judge on natural-language fidelity
  - Walmart Jira-resolution agent: closure rate, escalation rate, time-to-resolution distribution, human spot-check cadence
- **Hallucination / low-confidence handling.** "What does the system do when it's not sure?" Real mechanism — confidence threshold + abstain, retrieval-grounded constraints, tool-use enforcement, structured outputs with validation.
- **Architecture tradeoffs.** Not "I used LangChain" — but "I chose LangGraph over single-shot because the task needed multi-step tool use with branching, and the agent loop made retries cheap." Have 2–3 real tradeoffs (latency vs. accuracy, cost vs. quality, agent vs. pipeline).
- **Tool-boundary decisions.** "When MCP server vs. custom tool? When agent vs. pipeline?" One-liner heuristics.
- **What didn't work.** He'll ask. Real failure + what you'd do differently. Maan respects this more than a clean win.
- **"What would you build next?"** Product instinct, not just engineering. Pick one, be specific.

Whiteboard cameo: if asked to draw architecture, use a 5-box pipeline — user / router / retrieval / tool-execution / eval — with arrows. No paragraphs.

---

## Segment 3 — Case interview / Zoom Whiteboarding (~20–25 min)

The new muscle. Grading rubric (per Ganna): structure, clarity, logical reasoning. Not "did you arrive at the right answer."

**Mechanics:** Maan gives a prompt verbally, probably shares the Zoom Whiteboard or hands over control. You think out loud while drawing. Back-and-forth — he'll add constraints, push on weak spots, ask "what would you cut?" Wrap with how you'd measure success.

### Prompt archetypes — one of these is very likely

Cases tend to track the interviewer's recent work. Given Maan's profile:

1. **Internal-tool product case** — *"BCG case teams spend ~6 hrs/wk building client-status decks from disparate inputs. Design an AI product to halve that."* Tests product scoping + AI architecture + adoption. Plays to your strengths — you've literally shipped this shape at Walmart.
2. **Adoption diagnosis case** — *"We shipped three AI tools; consultants only use one. Why, and what would you build to fix it?"* Principal-level scoping. **Don't jump to a feature** — scope the *why* first. Maan will weight this heavily because it's the work he actually does.
3. **Eval / quality strategy case** — *"A partner says the model's outputs aren't trustworthy enough to put in front of clients. What's your evaluation strategy?"* PhD bait. Frame: define "trustworthy" in measurable terms first, then tiered golden-set + LLM-judge + human-review, then a regression gate before any client touchpoint.
4. **Client-facing engagement scope** — *"Pharma client wants GenAI for trial-document summarization. How do you scope the first 4 weeks?"* Forward-deployed thinking — discovery → scoped MVP → eval criteria → adoption plan.
5. **AI in regulated / data-heavy domain** — pharma, financial services, public sector. BCG X's bread and butter; ties to his science-rigor instinct.

### Universal 5-step structure — say it out loud at the start

Buys 30 sec to think and signals you're structured. Memorize this.

1. **Clarify** — restate, ask 2–3 scoping questions
2. **Frame** — sketch a tree or 2×2 out loud
3. **Prioritize** — pick the highest-leverage branch, say *why*
4. **Solution** — what you'd build, who uses it, data/integrations, failure modes
5. **Measure** — how you'd know it worked ($ / hours / adoption %). **Maan will notice if you skip this.**

### Zoom Whiteboard layout (rehearse Sunday)

- **Top-left:** problem restated in one line. Title block.
- **Down the left edge:** vertical list of the 5 steps as an anchor.
- **Center:** tree or 2×2, 3 levels deep max, 2–3 word labels only.
- **Right side:** chosen branch's solution sketch — boxes for users / data / model / eval / rollout, arrows.
- **Bottom:** "Measure" — 2–3 metrics with target directions. Never leave empty.

### UI mechanics

Pen for sketching, text tool only for short labels (typing on whiteboard is slow), shapes for boxes. Test Sunday with a 10-min sandbox — draw a 2×2, a tree, an arrow flow, a 5-box pipeline. That's the whole vocabulary you need.

**Don't go silent while drawing.** Narrate every line. He's judging the reasoning trace, not the artwork.

---

## Two moves Maan will specifically reward

1. **Call out what you'd deprioritize and why.** "I'd cut integration X from v1 because the value-to-effort ratio is worse than the deck-generation branch." Most candidates only add features — Principal-level scoping subtracts. Highest-signal move you can make.
2. **Close on adoption mechanism, not just a metric.** "We'd measure success at adoption % of case teams using it weekly in month 2, with a 30% gate before scaling — and we'd run a 2-team pilot first with embedded support." LinkedIn-product instinct.

**Bonus talk-track move:** acknowledge the research-to-product parallel obliquely once — e.g., "what drew me to AI eng was the same loop a science build runs: hypothesis → experiment → eval → iterate." Don't oversell it.

---

## Questions for Maan at the end (pick 2–3)

1. *"How does AI Factory measure 'this tool is working' — adoption, time saved per case, something else?"* — measurement frame, his PhD brain engages
2. *"You moved from astronomy research → LinkedIn → BCG. What was the hardest part of translating technical rigor into a consulting environment?"* — peer move, opens a real conversation
3. *"What's an AI Factory pattern you've shipped recently that you think more consultants would use if they knew about it?"* — Principal-level scoping, signals you think about adoption

---

## Time budget (45 min)

Flex by 2–3 min, but if any segment overruns hard, the case is the one he'll protect:

- Intro / TMAY: ~3 min
- Behavioral drill-down: ~7 min
- Technical/AI background: ~12 min
- Case (whiteboard): ~18–20 min
- Your questions + wrap: ~3–5 min

Behavioral + technical talk-tracks land in **3–4 min each**, not 5–6. The 60-second TMAY needs to be a real 60 seconds, not 90.

---

## Things NOT to do

- Don't quote his PhD or research back at him as if you Googled him. Acknowledge the science-to-tech path *if* it comes up naturally; don't volunteer it.
- Don't lean on "Walmart Data Ventures" as a credential — lean on *what you shipped there*.
- Don't bring up the "Key to Purpose" post — too personal for a first interview.
- Don't dumb down architecture in the AI-background segment — he'll respect rigor.
- Don't skip "Measure" in the case. He WILL notice.
- Don't go silent while drawing on the whiteboard.
