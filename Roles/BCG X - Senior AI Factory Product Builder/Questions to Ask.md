
- Success here is explicitly _adoption by consulting teams_. How does the AI Factory measure that in practice, and what's the bar for an asset graduating from a pilot team to firm-wide?

- What makes a solution actually become a reusable accelerator versus staying a one-off — and where do most builds die on that path?

- As a product builder partnering with front-line consultants and offer teams, who owns the roadmap when a consultant's urgent request conflicts with building something that scales?

- The JD frames this as balancing speed of experimentation against robustness, security, and maintainability. Where does the AI Factory currently sit on that spectrum, and is it trying to move?

- When an asset is adopted across practices, regions, and client contexts, who maintains it? Does the original builder keep owning it, or does it hand off to a platform team?

- How does the AI Factory decide _what_ to build — is it bottom-up from consultants spotting repeatable pain, top-down from product leadership, or some mix?

- The role centers on Claude Code and Claude/Markdown-based development. How standardized is the tooling and the architecture across the team versus builder's choice?

- What separates a (Senior) Product Builder who's having outsized impact here in their first year from one who's just shipping?

- You built the Forward Deployment function and scaled it Denver → Europe → global. As the AI Factory scales, what's the hardest thing to keep intact? _(rapport — his lived experience)_

- What's an AI Factory asset or pattern you've shipped that you wish more of the firm used — and what got in the way? _(builder-to-builder)_




















# Questions to Ask — BCG X / Maan · Mon 6/1, 2 PM ET

> **Two kinds of questions matter in this round.** The end-of-interview ones (for Maan) are a final read on how you think — he grades them like your case structure. The *clarifying* ones (during the case) are explicitly on the rubric: structure, clarity, logical reasoning. Both are below.
>
> **Rule:** every question should reveal you think in **adoption, measurement, scoping** — his three axes. A generic question actively costs you.

---

## 🎯 END OF INTERVIEW — for Maan (pick 2–3, lead with ★)

Have 4–5 ready; pick based on what's already been covered. If he spent the technical segment on eval, skip the measurement question — pivot to #4 or #5.

**★ Default three:**

1. **Measurement** — *"How does AI Factory decide a tool is actually working — adoption, hours saved per case, client outcome? And who owns that call?"*
   → The "who owns it" tail probes how decisions get made. Principal-level. Engages his PhD brain.

2. **His translation arc** — *"You went astronomy research → LinkedIn → BCG. What was the hardest part of making technical rigor land in a consulting org?"*
   → Highest-warmth question. Frames you as a peer doing the same research-to-product translation. Opens a real conversation.

3. **Adoption pattern** — *"What's an AI Factory pattern you've shipped that more consultants would use if they knew it existed?"*
   → Signals you think adoption is the rate-limiter, not capability — his exact worldview.

**Swap-ins (use if the conversation ran deep-technical and you want to keep that energy):**

4. **Scoping / subtraction** — *"When you scope a new internal tool, how do you decide what to deliberately leave out of v1?"*
   → Mirrors the "what would you cut" move he rewards in the case. Turns it back on him.

5. **Autonomy line** — *"Where's the current line between 'an agent decides' and 'a human decides' on the tools you ship — and is that line moving?"*
   → Your whole portfolio is HITL postures sized to blast radius. Shows you live in his problem.

**Third-slot only (safe, slightly generic):**

6. **Strong start** — *"Three months in, what does a strong start in this role look like to you?"*
   → Shows you're thinking about delivering, not just landing the offer. Use only as a third.

---

## 🎯 MORE END-OF-INTERVIEW OPTIONS (deeper bench — by angle)

Pull from here if the default three got answered earlier in the conversation, or if you want a question that matches where the discussion went.

**On the build philosophy (great after a deep-technical segment):**

7. **Reuse vs. bespoke** — *"How much of what AI Factory ships is reusable substrate vs. rebuilt per engagement? I've found the substrate is the real asset — curious where BCG X draws that line."*
   → Plants your platform thesis without lecturing. Lets him react to your actual worldview.

8. **Eval as a product surface** — *"Do you treat evaluation as its own deliverable to the client, or as internal plumbing? I've been moving toward making the eval visible."*
   → PhD bait, in a good way. Signals you think eval is first-class, not an afterthought.

9. **Failure tolerance** — *"What's BCG X's posture on a tool that works 90% of the time — ship with guardrails, or hold until it's higher? Where's the bar for client-facing?"*
   → Surfaces how they reason about confident-wrong risk, your exact concern.

**On the role / day-to-day (use if you want concrete texture):**

10. **Builder vs. advisor split** — *"How much of this role is hands-on building vs. advising case teams on what to build? I do my best work end-to-end and want to calibrate."*
    → Honest calibration; signals you know your strength is shipping, not slideware.

11. **Speed vs. rigor** — *"Consulting runs on tight timelines; science rigor wants more cycles. How do you hold both in a 4–6 week engagement?"*
    → Names the real tension of the job. He's lived exactly this (research → consulting).

12. **What breaks at scale** — *"As AI Factory grows, what's the thing that's hardest to keep good — eval quality, adoption, the talent bar?"*
    → Forward-looking, Principal-altitude. Invites a candid answer.

**On BCG X positioning (use sparingly — slightly higher-level):**

13. **Edge** — *"What does BCG X do that a client couldn't get from a pure AI shop or their own team? Where's the durable edge?"*
    → Shows commercial instinct. Risk: can read as interview-y — only if rapport is warm.

14. **Pattern library** — *"Is there a shared library of patterns across the team, or does each builder reinvent? How does knowledge move?"*
    → Adoption-of-internal-knowledge angle — same instinct as your substrate story.

---

## 🧩 DURING THE CASE — clarifying questions (these are GRADED)

Per the recruiter: judged on structure + logical reasoning, not the "right" answer. Ask **2–3 vital** scoping questions before you frame — the test is *"does the answer change my design?"* If it doesn't, don't ask it.

**Universal openers (work on almost any prompt):**

- *"Who's the user — a consultant, a partner, the client directly? That changes the trust bar."*
- *"What does success look like to you here — time saved, adoption, or output quality? I want to design toward the right one."*
- *"Is this a one-off for an engagement, or a reusable tool across case teams?"* (scopes build-vs-platform)
- *"What's the current process, and where does it actually break — the input gathering or the synthesis?"*

**Two more universal openers (constraint + scope):**

- *"What's the constraint that matters most here — timeline, budget, data access, or accuracy? I'd design differently for each."*
- *"Am I scoping the whole solution, or the first version we'd put in front of someone in ~4 weeks?"* (forces MVP framing — a move he rewards)

**By case archetype (see `Case Study Question Bank.md` for full prompts):**

- **Internal-tool product case** → "What inputs do they already have in a structured form vs. scattered?" · "What's the volume — how many decks/week, how many teams?"
- **Adoption diagnosis** ("3 tools shipped, 1 used") → **don't propose a fix yet.** Ask: "Do we know *why* the two aren't used — discovery, trust, or workflow fit?" · "What's different about the one that stuck?"
- **Eval / trustworthiness** → "When the partner says 'not trustworthy enough,' is that a measured failure rate or a perception? Define the bar first." · "What's the cost of a wrong answer reaching a client?"
- **Client engagement scope** → "What's the client's actual decision this feeds? That sets the eval criteria." · "What data access do we realistically get in week 1?"
- **Regulated / data-heavy domain** (pharma, finance, public sector) → "What's the compliance or audit requirement — does every output need to be traceable to a source?" · "Who signs off before this touches a regulated decision?"
- **Build-vs-buy / make-vs-orchestrate** → "Is the expectation we build this, or wire together what exists? That changes the whole approach." · "What's already in their stack we'd integrate vs. replace?"

---

## ⛔ DON'T ASK

- Comp, leveling, team size/structure, "what's the process from here" → that's the **recruiter's** lane, not Maan's.
- "What does BCG X do?" / "Am I a fit?" → you should already know / it reads as insecure.
- Anything quoting his PhD or research back at him — the brief flags this explicitly. Acknowledge the science→tech path only if it surfaces naturally.

---

## ⏱️ Timing reminder

45-min round, case is protected (~18–20 min). Your questions get ~3–5 min at the end. **Two well-placed questions beat three rushed ones.** If he's running long, ask one (the translation arc — it's the warmest close) and offer to follow up by email.
