# AI Build Walkthrough — Cue Card (BCG X / Maan, 6-1)

**Source of truth for content:** root `AI Build Walkthrough - Master.md`. This file is the *selection + Maan-specific tweaks* — same pattern as `Interview Answers.md` selecting from `Master Story Bank.md`.

**Read the Master file first.** It has the 4-beat scaffold, the single sentence to lock in, the drill pattern, the anti-patterns, and the full pre-written walkthroughs for every project. Don't duplicate that here.

---

## Lead with these 2 walkthroughs for Maan

1. **A3 — Jira Resolution Agent** (primary). Strongest builder credibility, biggest measured impact, owns the HITL gap honestly. Maan rewards the "automating my role bought me time to build the rest" close.
2. **A1 — Self-Service Analytics Agent** (secondary). Use if he asks for a second walkthrough or wants to see sub-agent orchestration rigor specifically. The context-isolated validation beat (4 sub-agents not sharing context) and the deterministic-rules-under-LLM beat both land well with a PhD scientist.

**Have A7 (live NL-to-SQL demo) ready as a tertiary** — if he asks "do you have anything I can actually try," you have a live URL. Don't volunteer it unless prompted.

**Skip for this interview:**
- I1 (Innovare) — too early-career, would weaken positioning.
- F1 (FTI capstone) — keep in pocket only if he asks about consulting-shaped client work specifically.
- U1 (UChicago donation experiment) — strong project, wrong audience; Maan wants to see shipped products with adoption, not research artifacts.

---

## Maan-specific tweaks to bake in

Maan = PhD astrophysics (U. Victoria, MNRAS publications) → LinkedIn → BCG, recently promoted to Principal. Technical-deep, will respect rigor, cares about adoption + measurement. See `Interview with Maan.md` for the full brief.

**Phrases that land especially well with him** (drop in naturally, do not force):

- "Context engineering, not prompt engineering." — reads as a builder phrase, signals you actually think about it
- "Today, I'm the gate. The next version moves the gate to [mechanism]." — Maan thinks in gates
- "The failure mode I worry about most is confident-wrong." — names the eval failure mode he actually cares about
- "Stakeholders never knew an agent was answering them." — LinkedIn-product instinct, Maan's home turf
- "Automating my role bought me the time to build the rest." — the portfolio-effect close, Principal-level framing

**Beat 4 priority order for Maan** (adoption is the rate-limiter for him, not architecture):

1. Adoption fact first (Sr. Director approval, only AI skill in active use)
2. Through-line second ("automating my role bought me time to build the rest")
3. List 2–3 follow-on builds max, never all five

**Beat 3 must-haves for Maan** (he WILL push on eval — preempt it):

- Name the **gate** explicitly ("today I'm the gate, next version moves to golden-set regression")
- Name the **abstain mechanism** even if it doesn't exist yet ("if process diverges from golden, the agent kicks back a 'need clarification' artifact instead of guessing")
- Name the **failure mode you worry about** ("confident-wrong — clean SQL on a stale flag")

If you skip any of these, he'll dig until you produce one — better to lead with them than be cornered into them.

---

## Anti-patterns specific to the Maan interview

These are the ones you (Kanu) actually did in the drill we ran:

- **Closed beat 1 on a philosophy beat** ("I design my agents around observability"). Move that into beat 3 if anywhere. Beat 1 closes on the dollar/hour outcome.
- **Said "I fundamentally believe"** about eval. Maan will pounce instantly. Replace with a gate, or own the gap explicitly.
- **Listed projects sideways in beat 4** without the through-line. The through-line — *"automating my role bought me the time to build these"* — is the move that makes the list land instead of feel scattered.
- **Went 4:30+.** The Maan interview is 45 minutes total with a protected ~20-min case segment. Eating into that with a rambling build walkthrough costs the case time, which Maan grades hardest.

---

## Pre-flight ritual for this interview specifically

Before Monday 1pm CT, run the drill from the root Master file **5 times** — 3 on A3, 2 on A1. Out loud, phone timer, hard cut at 4 min. Self-score the 5-question rubric per rep. Don't open the live interview without having landed 4 of 5 yes on at least 3 consecutive reps.

If only one project gets drilled, drill A3 — that's the one he's most likely to ask about given the JD shape.
