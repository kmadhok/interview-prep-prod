# Public Intel on BCG X AI Factory — What Maan Won't Have to Explain

**Purpose:** Everything in this file is from public sources (BCG press, Computerworld, Fortune, sector trade press, Hack Diversity / WebProNews / DigitalDefynd analyses, the JD itself). It is the *vocabulary and product map* you should walk in already knowing. **If Maan mentions Deckster, GENE, agent-factory, forward-deployed, or "the 70," you should recognize them and not need them defined.**

**How to use this file:** Read once Sat morning. Then re-skim Sun night before the case drills. Don't quote any of it back to him performatively (he'll smell research-theater) — instead, *use the vocabulary naturally* and let it land as "Kanu actually understands the world we're operating in."

---

## The structure of the AI Factory (the three-layer assembly line)

Multiple public write-ups describe BCG's AI build org as a **tripartite assembly line**:

1. **Foundation layer — Data.** Internal knowledge lake: 100,000+ sanitized project docs, presentations, reports. Powers retrieval-augmented generation across every downstream tool. PII redaction + Responsible-AI guardrails baked in.
2. **Middle layer — Forward-deployed consultants ("FDCs").** A tech-company-style role (explicitly modeled on Palantir's FDE pattern). They sit on client engagements and build custom GPTs / agents *for that engagement*, often as bespoke tools. **Around 80% of BCG's ~36,000 custom GPTs originated from this front-line layer**, not from central platform teams.
3. **Top layer — Firmwide / centrally-built tools.** ~7–8 horizontal products everyone uses (Deckster, GENE, HR/IT self-serve, internal comms). This is the layer **AI Factory product builders most directly own**.

**Where the Product Builder role sits.** The JD says "centralized AI Factory" — that's the **top layer**, but the work loops constantly through the middle layer: AI Factory product builders *learn from* what FDCs build on the front line, then *generalize* the patterns into reusable assets the whole firm can use. The JD's "turn successful solutions into reusable assets, patterns, and accelerators that scale across similar engagements" is literally the FDC-pattern → AI-Factory-asset pipeline.

**Why this matters for the case:** When Maan throws a case at you, the implicit question behind it is almost always *"how would you operate at the seam between front-line FDC work and centrally-owned AI Factory assets?"* That seam is what he's testing.

---

## Named internal products to recognize

| Name | What it is | Adoption signal | Why it matters for the case |
|---|---|---|---|
| **Deckster** | GenAI deck builder. GPT-4o + RAG over 800–900 firm-approved templates + vision transformer for slide classification + RL layout optimizer + brand-compliance guardrails. "One-Click Draft" + "Review This" features. | Launched March 2024. **450,000+ uses.** ~40% of associates use weekly. 2–3 hrs saved per deck. 35% fewer formatting defects. | Reference example of a *centrally-built, widely-adopted* tool. If the case prompt is the "halve the deck hours" case, you're being asked to design Deckster v2 in real time. **Don't pretend you've never heard of Deckster** — name it if it fits ("this would slot next to Deckster, not duplicate it"). |
| **GENE** | Conversational/multimodal agent. GPT-4o + ElevenLabs voice. Used for ideation, podcast co-hosting, brainstorming, partner thought-leadership prep. ~200-page prime-directive prompt loaded with firm POVs. | Launched Sep 2024. 3× citation depth vs. plain ChatGPT. Used in production for the "Imagine This" podcast. | Reference example of a tool with a *novel modality* (voice). Useful if you're asked about expansion / "what would you build next." |
| **Agent-factory platform** | The underlying infra: GPT-4o endpoints behind containerized microservices, RAG over the 100k-doc knowledge lake, guardrail layer (PII, toxicity), region-specific tenants, audit logs. | Powers the whole top layer. | If asked architecture-shape questions, this is the platform you'd build *on*, not *replace*. Treat it like a given. |
| **Custom GPTs (the 36,000)** | Bespoke, per-engagement mini-agents built mostly by FDCs in ChatGPT Enterprise. ~5,000 private + ~1,000 firm-shared in one count; total inventory has grown to ~36,000 across the firm. | 18,000+ early on; now ~36,000. | **This is the raw material AI Factory product builders mine.** Pattern across many custom GPTs → generalize into a firmwide tool. If a case asks about reuse, this is the funnel you'd point to. |
| **Center for Responsible GenAI** | 150+ specialists. RATE.ai impact-assessment framework. Responsible-AI Council. PII + bias gates before any client touchpoint. Open-source FACET (feature explainability). | Cited as cutting hallucination incidents ~50% and speeding production deployment ~30%. | If Maan asks the **eval / trust** case, this is the org you'd partner with. Don't pretend trust is something you'd invent from scratch — it has owners. |
| **OpenAI partnership** | Formal collaboration since late 2023. Now extended with the Frontier AI agent platform push (Feb 2026, alongside McKinsey, Accenture, Capgemini). | n/a | Establishes GPT-4o as the default model stack at BCG. **Anthropic Claude is also in the stack** (the JD literally requires Claude Code experience), but don't assume Claude is the *default* — at BCG it's the agentic-coding tool of choice; GPT-4o is the runtime for deployed products. |

---

## The org's stated philosophy (quotes worth internalizing)

**Alicia Pittman, Global People Chair** — *"Our philosophy around genAI at BCG is 'early and often.'"* (Translation: ship fast, iterate publicly, don't over-plan.)

**Pittman on training/adoption** — *"We invested in 'the 70.' Successful AI transformations dedicate 10% to algorithms, 20% to data and tech backbone, and 70% to business and people transformation."* (Translation: **adoption is 70% of the work.** This is the single most important sentence in your prep. If you only remember one BCG-ism walking in, remember the 70.)

**Pittman on success metrics** — three KPIs: *productivity, work quality, **employee joy** (less toil).* (Translation: when you close a case on "Measure," include a qualitative beat — toil reduced, joy added — not just hours/dollars. He'll notice.)

**Scott Wilder, MD&P** — *"A custom GPT is a powerful feature… a reusable mini genAI application that users define themselves."* (Translation: end-user-defined > engineer-defined when possible. The whole assembly-line model is biased toward letting consultants build their own.)

---

## What this implies for each case archetype

| Case archetype | Public-intel angle to weave in |
|---|---|
| **A — Halve the hours / internal tool** | Position your build as **complementary to Deckster** (or whatever top-layer tool already exists), not a replacement. Mention you'd mine the existing 36K custom-GPT corpus for patterns before designing from scratch. |
| **B — Adoption diagnosis** | Lead with "the 70": adoption is 70% of the work, so the diagnosis question isn't "is the tool good" but "did we invest the 70?" Ask about the **1,200-person GenAI Enablement Network** — was the dead tool ever in their hands? If not, that's your answer. |
| **C — Eval / trustworthiness** | Mention partnering with the **Center for Responsible GenAI** and running the output through the **RATE.ai gate** before client-facing release. Shows you know there's existing infra for this, you're not inventing it. |
| **D — 4-week client scoping** | Sounds exactly like FDC work. Frame your scoping as "I'd run this like an FDC engagement — discover, MVP, eval, steering deck." Use the FDC vocabulary. |
| **E — Reusable asset** | This is literally the FDC → AI Factory pipeline. Name it. "We'd be promoting an FDC-built artifact into a firmwide asset — the abstraction tax has to be earned by at least 5 similar use cases across the 36K corpus." |
| **F — Roadmap prioritization** | Use the three-layer structure. "Top-layer products earn their slot by being above-the-line on two tests: (1) does the pattern show up in ≥5% of the 36K custom-GPT corpus, (2) can the 1,200 enablement folks distribute it?" |

---

## Things to **not** do with this intel

- **Don't recite product names performatively.** *"As we know, BCG launched Deckster in March 2024…"* — instant red flag. Use the names only when they're load-bearing in your reasoning.
- **Don't claim insider knowledge** of how the team operates day-to-day. You read public write-ups. If pushed ("how do you know that?"), say *"from public coverage of how AI Factory has scaled — happy to be corrected on the internal reality."*
- **Don't assume the JD's "Claude Code required" means Claude is the runtime.** It almost certainly means **Claude Code is the dev tool** the builder uses (vibe-coding), while **GPT-4o is the runtime** for shipped products. Match that distinction in any architecture answer: *"I'd build it with Claude Code, deploy on the GPT-4o agent-factory infra."*
- **Don't bring up the OpenAI partnership unprompted.** It's a known fact in his world; surfacing it reads as filler.

---

## One sentence to have ready if Maan asks "what do you know about AI Factory?"

> *"My read from outside: it's the central top-layer of a three-layer build org — the firmwide assets like Deckster and GENE that sit on top of the agent-factory infra, with forward-deployed consultants generating most of the raw custom-GPT pattern that AI Factory then generalizes. The hard part of the job from the outside looks less like building and more like **picking which front-line patterns are worth promoting into firmwide assets, and getting the 70% adoption work right** when you do."*

That answer signals: (1) you understand the three layers, (2) you know the FDC → asset pipeline, (3) you know "the 70," (4) you're not overclaiming inside knowledge. It's the highest-density 4-sentence answer you can give to that question.

---

---

## Addendum — what's specifically out there about the *role itself*

After a second pass, here's the honest answer: **there is very little public material on the AI Factory Product Builder role specifically.** It's a newly-posted role (LinkedIn date Apr 4 2026), the JD is brand-new language, and no current builder has posted a "day in the life" or LinkedIn thinkpiece about it yet. What does exist:

1. **The JD itself.** That's it for first-party language about the role. Posted on BCG careers + LinkedIn + ZipRecruiter; the text is identical across all three.
2. **A sibling role: "Forward Deployed AI Engineer."** Multiple postings (Boston, Munich, Milan, Amsterdam, Copenhagen, Singapore). This is the FDC role described in the assembly-line write-ups — and the *Product Builder is the centralized-tools counterpart to the FDE role*. Reading the FDE JDs helps triangulate what AI Factory considers in-scope. The Senior FDE in Boston is the closest sibling.
3. **A sibling role: "(Associate/Senior) AI Product Manager."** Different role (PM, not builder), but lives in the same org. Useful for understanding how the AI Factory splits build vs. PM responsibilities.
4. **An AI Factory Executive Director JD (London).** This is the leader role above team leads. The posting is gone (410'd when fetched 5/30), but its existence in the search index confirms the AI Factory has formal exec leadership in London — which means **US Product Builders likely report through a regional lead who reports to the London-based exec director.** Don't bring this up unless Maan does.
5. **Sylvain Duranton's "Harness Engineering" LinkedIn post (Jan 2026).** **This is the most valuable single artifact for this interview.** Duranton runs BCG X. Maan reports up through him. The post is BCG X's *current* operating philosophy on how builders should work with agentic AI:

   > *"Harness Engineering reframes the discussion from simply accelerating development to creating systems where that speed can be trusted."*

   **What this signals about how the Product Builder role is graded:**
   - **Speed is table-stakes; trust is the differentiator.** Maan will not be impressed by "I shipped fast." He will be impressed by "I shipped fast *and built the guardrails that let consultants trust the output*."
   - The post cites three pillars: **(1) clear guardrails, (2) coordinated agents, (3) more review/quality emphasis.** These map exactly to the kind of architecture answers Maan will reward.
   - Aparna Kapoor and Vincent Paca (BCG X leaders) are publicly named alongside Duranton in this post — they're likely co-architects of the AI Factory's engineering operating model. **You don't need to know them; just know the concept.**
   - A top commenter (Daniil Shestov) flagged "review fatigue at scale" as the hardest problem — i.e., human stage-gates become the bottleneck in regulated environments. **If the eval/trust case comes up, naming "review fatigue" as a real failure mode and proposing tiered review (auto-pass low-risk, sample mid-risk, human-gate high-risk) is exactly the kind of answer Duranton's post primes Maan to want.**

6. **BCG X's "The Multiplier" publication.** BCG X publishes thought-leadership at bcg.com/x/the-multiplier — there's a piece on "AI-Assisted Coding and Generative Engineering" that's gated (403'd on fetch) but it exists and Maan likely knows it. Worth noting as a reference if you want to ask him about it in your closing questions: *"I saw the Multiplier piece on generative engineering and the Harness Engineering framing from Sylvain's recent post — how do those concepts show up in day-to-day at AI Factory?"* That question will land.

### The new vocabulary to walk in with: "Harness Engineering"

**Add this term to your active vocabulary alongside "the 70" and "FDC."** It's the framing BCG X's leader chose to publicly champion in early 2026, and any builder candidate who can articulate the speed-with-trust framing fluently will sound like a peer rather than an outsider.

One-line working definition you can use: *"Harness Engineering is the practice of building the guardrails, review systems, and agent coordination that let teams ship AI fast without breaking trust — the framing Duranton has been pushing publicly since January."*

### What you should NOT claim about the role

- Don't claim it's been in market for a long time or that there's a public track record of what builders have shipped. There isn't. It's new.
- Don't pretend there's a public "AI Factory" product page on bcg.com. There isn't — AI Factory is referenced inside JDs and in third-party coverage of the assembly-line model, but BCG hasn't published a flagship public page calling it "AI Factory" yet.
- Don't conflate AI Factory with BCG X writ large. AI Factory is a unit *inside* BCG X (3,000+ people) — specifically the centralized top layer of the three-layer assembly line. Maan will notice if you treat them as synonymous.

---

## Sources (all public)

- BCG careers — JD: https://careers.bcg.com/global/en/job/57679/-Senior-AI-Factory-Product-Builder-United-States-BCG-X
- Computerworld interview with Alicia Pittman + Scott Wilder: https://www.computerworld.com/article/3491334/bcg-execs-ai-across-the-company-increased-productivity-employee-joy.html
- DigitalDefynd — 5 Ways BCG Is Using AI (Deckster, GENE, agent-factory, CO2 AI, Responsible GenAI): https://digitaldefynd.com/IQ/ways-bcg-is-using-ai/
- WebProNews — 36,000 custom GPTs / assembly line: https://www.webpronews.com/bcg-builds-ai-assembly-line-36000-custom-gpts-transform-consulting/
- Hack Diversity — inside BCG's AI product assembly line (tripartite structure, FDC layer): https://www.hackdiversity.com/inside-bcgs-ai-product-assembly-line/
- Fortune — OpenAI / BCG / McKinsey / Accenture Frontier AI partnership (Feb 2026): https://fortune.com/2026/02/23/openai-partners-with-mckinsey-bcg-accenture-and-capgemini-to-push-its-frontier-ai-agent-platform/
- BCG X careers — Forward Deployed AI Engineer JDs (for FDC role pattern): https://careers.bcg.com/global/en/job/55995/Forward-Deployed-AI-Engineer-United-States-BCG-X
- BCG GenAI Evaluator + Responsible AI: https://www.bcg.com/x/product-library/gen-ai-evaluator
- Sylvain Duranton (Global Leader, BCG X) — "Harness Engineering" LinkedIn post (Jan 2026): https://www.linkedin.com/posts/sylvain-duranton_bcgx-ai-agenticai-activity-7453318067444670464-iFLo
- BCG X — "AI-Assisted Coding and Generative Engineering" (The Multiplier): https://www.bcg.com/x/the-multiplier/ai-assisted-coding-generative-engineering
- BCG X — sibling role JD, Senior Forward Deployed AI Engineer US: https://careers.bcg.com/global/en/job/56794/Senior-Forward-Deployed-AI-Engineer-United-States-BCG-X
