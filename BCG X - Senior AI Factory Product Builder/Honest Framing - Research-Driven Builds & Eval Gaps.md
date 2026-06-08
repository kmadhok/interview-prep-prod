# Honest Framing — Research-Driven Builds & Eval Gaps (Patrick Freyer)

**Companion to `Resume Deep-Dive Question Bank`.** That file lists the gaps Patrick will hunt. This file is *how you answer them* — without faking rigor you don't have, and without underselling the way you actually work.

> **The whole point:** the way you build — read the research, prototype the architecture fast, ship it to automate yourself, move on — *is* the forward-deployed builder profile. It's not a weakness to manage. The only failure modes are (a) apologizing for it and (b) faking rigor you didn't do. Avoid both and this becomes your strongest material.

---

## Two principles that make all of this cohere

**1. Rigor scales with blast radius.**
When you're the only consumer and you review every output, a 100-case eval harness is over-engineering. The eval you built — *you as the gate* — is the *right* amount of rigor for a self-automation tool. Patrick isn't testing "why didn't you build more." He's testing "do you know what you'd add as more people depend on it." You do. (This is your existing "two budgets sized to blast radius" instinct — use it explicitly.)

**2. Describe the design freely. Claim precisely.**
You can talk about what good eval/architecture looks like all day — that demonstrates understanding, which is the point. Just never let him leave believing you *built* something you didn't. Mark the tense every time it could be misheard:
- ✅ "The eval I'd want here is…"
- ✅ "Today it's me reviewing; the harness I'd add is…"
- ❌ "It validates against a golden set" *(when you mean you'd build that)*

Voluntarily drawing that line reads as senior. Getting caught blurring it is the one thing that actually sinks you with a builder.

---

## The 3-part move (use on any thin spot)

Not did-vs-would — it's three beats:

1. **What you did (real):** the decision + the *mechanism* you reasoned from. Cite the source if it was a paper/podcast.
2. **The honest gap:** what you didn't test, and the real reason (your bar was leverage, not proof).
3. **The experiment you'd run:** the specific test that would validate it, with the metrics. This is the part that turns a gap into evidence of judgment.

A "would" answer with named metrics beats a "did" answer that's vague. Always land beat 3.

---

## Words to use / avoid

| Use | Avoid |
|---|---|
| "I right-sized it for a tool only I use." | "This part's a bit undercooked." |
| "My bar was 'do I trust it enough to step back.'" | "I didn't really have time to test it." |
| "The experiment I'd run is…" | "I'm sure it's better." / "I fundamentally believe…" |
| "Today I'm the gate; the harness I'd add is…" | (implying an eval exists when it doesn't) |
| "I read the [paper]; the mechanism that sold me is…" | "It uses a state-of-the-art architecture." |

---

## Filled scripts (drill these out loud)

### A1 — Devil's Advocate / isolated-context sub-agents (the recursive-LM build)

> **Did:** "I built the validator and devil's-advocate as separate sub-agents with isolated context after reading the recursive-language-models work. The mechanism that sold me is context rot — when one model writes the SQL and critiques it in the same window, attention dilutes and it defends its own output. Separate contexts catch hallucinated columns and bad joins the drafter would rationalize.
>
> **Gap:** I'll be straight with you — I implemented it from the paper's reasoning. I haven't run my own head-to-head against a single-agent baseline. My bar was 'do I trust it enough to step back as the reviewer,' not 'is it provably optimal.'
>
> **Would:** If I were hardening this for the org, the experiment is a golden-question set, single-agent vs. sub-agent flow, measuring hallucinated-column rate and answer-match against latency and token cost. That's the test that tells you whether the extra calls earn their keep."

*Why it lands:* reads primary research, reasons from mechanism, names the validating experiment, honest about what's done. Better than "I tested everything."

### Eval-as-human-in-the-loop (applies to Jira agent, analytics agent, most builds)

> "Most of these I built to automate my own job, so the eval is me as the gate — I review the work-log artifacts, and that's been enough to trust the output and move to the next build. I sized the rigor to the blast radius on purpose: when I'm the only consumer and I review every output, a big eval harness is over-engineering. The honest line is the eval scales with who's downstream — the moment this serves the org instead of me, the gate moves from me to golden-set regression plus abstain-on-low-confidence, and I can walk you through exactly what that looks like."

### Geo-resolution agent (describe eval as design — don't overclaim)

> **Describe freely:** "The eval that matters for geo-resolution is precision on a labeled set of known addresses, plus an abstain path when confidence is low so it never confidently returns a wrong location.
>
> **If he asks 'did you build that':** No — today it's spot-check. That's the harness I'd build, and here's how: [labeled set + precision/recall + abstain threshold]."

### Architecture chosen from research, not benchmarked (general)

> "I want to be honest about how I work — a lot of these architectures come from papers, X, or podcasts where someone's shown a mechanism that should help. I implement from that reasoning and ship. What I *haven't* always done is benchmark mine against the simpler baseline. I know which experiment would settle it for each one, and that's the work I'd prioritize the moment the tool has real users beyond me."

### Mixed agent / skill / human reality (when he asks "is this fully autonomous?")

> "It's deliberately not all one autonomous loop. There's agent work, there's skill/deterministic work, and there's me doing the judgment call to move on. I put the LLM where input varies and judgment helps, deterministic where I can verify, and kept myself in the loop where the blast radius made that the responsible choice. The mix is the design, not a shortcut."

---

## One-line anchors for the day

- "Rigor scales with blast radius — I built the eval the tool deserved, and I know the scaling path."
- "Describe the design, claim precisely."
- "Did, gap, would — always land the experiment."
- "I read the [paper]; the mechanism that sold me is… — I haven't A/B'd it; the test I'd run is…"

---

*Pulls the gap list from `Resume Deep-Dive Question Bank - Patrick Freyer.md` and the blast-radius/HITL framing from `Interview Cheat Sheet.md`. Honor code: this is honest framing, not spin — every claim here keeps you on the true side of what you actually built.*
