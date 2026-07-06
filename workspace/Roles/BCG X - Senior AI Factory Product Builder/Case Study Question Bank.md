# Case Study Question Bank — BCG X AI Factory Product Builder (Maan / 6-1)

**Format:** Zoom Whiteboard, ~18–20 min, graded on **structure / clarity / logical reasoning** — not "right answer."
**Interviewer:** Maan Hani, Principal — PhD astrophysicist, ex-LinkedIn, recently promoted. Will weight **eval rigor + adoption + deprioritization** above feature design.
**Universal opener (memorize, say out loud first):** Clarify → Frame → Prioritize → Solution → Measure.

The cases below are ranked by likelihood. Each has: the prompt, why Maan would ask it, the trap most candidates fall into, a clarifying-question seed list, and the 1-line "winning move" that separates a 3 from a 5.

---

## Tier 1 — Most likely (one of these almost certainly shows up)

### Case A — Internal-tool product case ("halve the hours")
**Prompt (canonical):**
> *"BCG case teams spend roughly 6 hours per week building a client-status deck from a Word doc, the project plan, last week's deck, and a few Slack threads. Design an AI product to cut that in half. Walk me through how you'd scope, build, and roll it out."*

**Variants you should expect:**
- "…the weekly partner update memo…"
- "…the kickoff deck from a discovery questionnaire…"
- "…the post-meeting recap and action items from the call recording…"
- "…the financial benchmarking one-pager from a list of comparable companies…"

**Why Maan asks it:** It's the literal shape of AI Factory work. Plays to your Walmart shipped-internal-tool muscle. Tests whether you scope like a Principal (cut scope, name the user) or like an IC (jump to architecture).

**Clarifying questions to ask first (pick 2–3, not all):**
1. Which case teams — strategy, DD, ops? Different doc patterns.
2. Is the 6 hrs concentrated (one person, end of week) or distributed (many people, all week)? Changes the UX.
3. What does the *current* deck look like — is it a template, or freeform per team?
4. Are we optimizing for *time saved* or *quality lift*? Different builds.
5. Who owns "done" — the Associate, the Project Leader, or the Partner?

**Trap most candidates fall into:** Jumping to "I'd use Claude + a RAG layer over the inputs" inside 90 seconds. Maan has heard that 50 times. He wants to see scope cuts.

**Winning move:** "I'd start by *not* building the deck generator — I'd build an input-collector that scrapes the project plan + last deck + Slack threads into a structured brief. That's where the 6 hours actually go. Deck generation is the last mile, and templating already handles 60% of it." That's the Principal-level reframe.

**Measure (don't skip):** hours saved per case team per week (target: 3 hrs, i.e. the 50% ask), % of decks where the AI draft is shipped with <10 min of edits, adoption % of case teams using it in month 2.

---

### Case B — Adoption diagnosis ("we shipped 3 tools, they use 1")
**Prompt (canonical):**
> *"AI Factory shipped three internal tools to consulting teams last quarter. Adoption data shows one is widely used, one is used by ~20% of teams, and one is essentially dead. A partner is asking what to do. How would you diagnose and what would you recommend?"*

**Why Maan asks it:** This is the work he actually does as a Principal — adoption diagnosis, not feature design. The case rewards candidates who refuse to build before they understand. **He'll weight this case heavily if it shows up.**

**Clarifying questions:**
1. What are the three tools (functionally)? Need this to spot the pattern.
2. What does "use" mean — opened once, used weekly, used in client deliverables?
3. Were the three rolled out the same way (top-down vs opt-in vs embedded)?
4. Are the three solving the same kind of problem, or different kinds?
5. Have we talked to non-adopters, or just looked at usage logs?

**Trap:** Jumping to a feature ("I'd add a Slack integration to the dead one"). Maan's pen-down moment. Adoption isn't fixed by features 80% of the time — it's fixed by fit, distribution, and trust.

**Frame to draw on the whiteboard (2×2 or tree):**
- **Demand axis:** does it solve a problem teams feel weekly? (frequency × pain)
- **Trust axis:** do teams trust the output enough to put in front of a partner? (eval rigor × failure cost)
- The dead tool is almost always low-demand or low-trust. The 20% tool is usually high-demand but low-trust. The winner is both.

**Winning move:** "Before I'd build anything, I'd kill the dead tool publicly — the cost of leaving it up is teams assuming AI Factory ships dead software. Then I'd interview 5 teams from the 20% tool's *non-adopters* — not the users — and figure out whether it's a trust problem (eval) or a fit problem (wrong job). The fix follows the diagnosis." Sunsetting + non-adopter interviews = Principal-level moves.

**Measure:** weekly active case teams (not individual users), pull-through rate (asked once, used again within 2 weeks), partner-visible artifact rate.

---

### Case C — Eval / trustworthiness case ("partner says it's not trustworthy")
**Prompt (canonical):**
> *"A senior partner ran one of our AI-generated outputs past a client and got embarrassed by a hallucination. He's saying the tool isn't trustworthy enough for client-facing work. What's your evaluation strategy to get this to a place where he'd put it in front of a client again?"*

**Why Maan asks it:** PhD bait. He'll know within 60 seconds whether you actually think about eval or just say "I'd add a confidence score." Strongest signal you can send him on the technical bar.

**Clarifying questions:**
1. What was the hallucination — fabricated fact, wrong citation, plausible-but-wrong reasoning? Different mitigations.
2. Was it caught by the consultant before the partner, or did it reach the partner unchecked? Tells you if the issue is *eval* or *workflow*.
3. What's the failure cost — embarrassing vs legal vs reputational? Sets the bar.
4. Is the tool retrieval-grounded, generative, or both?
5. What's "trustworthy" mean to the partner in measurable terms — accuracy %, citation rate, abstention rate?

**Trap:** Reaching for "LLM-as-judge" or "human review" as the whole answer. Eval is a *system*, not a tool.

**Frame (draw a 4-layer stack, top-down):**
1. **Golden set** — 50–100 hand-graded examples of the partner's actual use cases, with rubric (accuracy, citation, completeness). Regression gate.
2. **LLM-as-judge** — for natural-language fidelity at scale. Cheap, noisy, useful for trend lines.
3. **Tool-use enforcement + retrieval grounding** — no claim without a citation; abstain if no source.
4. **Human-in-the-loop pilot** — 2 weeks of consultant-reviewed outputs before any client touchpoint, with a 95% pass-rate gate before re-enabling client mode.

**Winning move:** "I'd define 'trustworthy' in measurable terms with the partner first — usually it's *citation rate + abstention rate*, not raw accuracy. Then I'd build the regression gate so we can never ship a model update that lowers either. The partner cares less about being right and more about not being wrong in front of a client — those aren't the same metric."

**Measure:** golden-set pass rate (target 95%), citation rate (target 100% for factual claims), abstention rate when low-confidence (target — non-zero, signals the model knows what it doesn't know), zero unflagged hallucinations in 2-week pilot.

---

## Tier 2 — Plausible (1 in 4 chance)

### Case D — Forward-deployed scoping ("client wants GenAI for X — scope the first 4 weeks")
**Prompt (canonical):**
> *"A pharma client wants to use GenAI to summarize clinical trial documents for their internal medical-affairs team. The partner has 4 weeks before a steering committee. How would you scope and run the first 4 weeks?"*

**Variants:**
- Financial services — earnings-call summarization for investment bankers
- Insurance — claims-document triage
- Public sector — RFP response generation

**Why Maan asks it:** Tests whether you think like a forward-deployed engineer (discovery → MVP → eval → adoption plan) or just an IC who builds. BCG X cases are *always* under time pressure with a partner deadline — he wants to see you ruthlessly cut scope to hit week 4.

**Clarifying questions:**
1. What's the *decision* the steering committee is making in week 4 — go/no-go, expand scope, secure funding? Reverse-engineer from that.
2. Who's the user — one medical-affairs lead, a team of 20, a whole function?
3. What's the data access situation (PHI, on-prem, cloud-allowed)? Often the actual blocker.
4. Is there an existing manual workflow we can shadow, or are we greenfielding?
5. What does the client define as "success" — and is it the same as what the partner defined?

**4-week shape to draw:**
- **Week 1:** Discovery — shadow 3 users, define 5 golden documents, get data access unblocked.
- **Week 2:** MVP — minimum useful summarizer, hardcoded prompts, single-doc input. Show, don't tell.
- **Week 3:** Eval + iterate — golden-set scoring with the medical-affairs lead in the room, 3 iteration loops on prompts/retrieval.
- **Week 4:** Steering deck — adoption plan (3-team pilot in Q2, success metrics, scale path), live demo on a real document, ask for the pilot budget.

**Winning move:** "I'd put the steering-committee demo on the calendar *for week 3*, not week 4 — so we have a week of buffer to fix what the dry run breaks. Partners hate surprises in the room."

**Measure:** week-4 go/no-go decision (binary), summarization time per doc (baseline vs MVP), medical-affairs lead's qualitative pass on 5 golden docs.

---

### Case E — Cross-engagement reuse ("turn this into a reusable asset")
**Prompt (canonical):**
> *"A team just shipped a custom AI tool for one client — a pricing-recommendation agent. Two other case teams in different industries are asking if they can use it. How would you turn it into a reusable AI Factory asset?"*

**Why Maan asks it:** This is literally in the JD's responsibility list — *"turn successful solutions into reusable assets, patterns, and accelerators."* If he asks it, he's testing whether you understand the *abstraction* tax (what becomes config vs what stays hardcoded).

**Clarifying questions:**
1. How different are the three industries' pricing problems — same shape (elasticity-based) or different shape (auction vs negotiated vs list)?
2. Did the original team write it to be reusable, or one-off?
3. Who owns it after we generalize — the original team, AI Factory, or a hand-off?
4. What's the cost of *failed* reuse — a team builds on it and it doesn't fit?

**Frame (split into 3 layers):**
- **Pattern** (always reusable) — how to think about pricing-rec problems, decision flow, eval approach. Living doc.
- **Toolkit** (reusable with config) — prompt templates, eval harness, MCP server skeleton. Pip-installable equivalent.
- **Reference implementation** (clone-and-modify) — the original code as a starting point, with a 1-page "what to change."

**Winning move:** "I'd resist building a 'pricing-rec platform.' Three teams isn't enough signal to know what the right abstraction is — premature platforms die. I'd ship the pattern + toolkit, let the two new teams clone-and-modify, and revisit platformization after team 5 or 6."

**Measure:** time-to-MVP for the second team (baseline: from-scratch), reuse coverage % (how much of the toolkit they actually used vs replaced), pattern-doc views/forks.

---

### Case F — Prioritization under constraint ("you have 2 builders for 4 quarters, what do you ship?")
**Prompt (canonical):**
> *"You're leading AI Factory's North American product roadmap for next year. You have a backlog of 12 ideas, 2 builders, and a 4-quarter year. Walk me through how you'd prioritize."*

**Why Maan asks it:** Principal-level scoping. He just got promoted into this exact decision space — he'll grade you on whether you'd be a useful peer.

**Clarifying questions:**
1. Are the 12 ideas teams have asked for, or ideas AI Factory generated? Demand-pull vs supply-push lens.
2. What's the baseline — does AI Factory have any shipped, adopted assets today?
3. What's leadership's definition of success — adoption breadth, depth, partner-visibility?
4. Are the 2 builders fungible or specialized?

**Frame (2×2 to draw):**
- X: **adoption breadth** (how many teams could use it — proxied by problem frequency)
- Y: **build cost** (weeks of builder time)
- Quadrant the 12 ideas. Top-left (high breadth, low cost) = ship first. Bottom-right = kill or defer.

**Winning move:** "I'd kill 3–4 ideas outright before sequencing the rest. The hardest part of a roadmap isn't picking what to do — it's saying no in public so the teams who asked know we heard them and aren't doing it." Then propose a quarterly rhythm: Q1 ship 2 top-left, Q2 measure adoption + ship 1 more, Q3 re-prioritize based on Q1–Q2 signal, Q4 platformize what worked.

**Measure:** ships per quarter, adoption % by quarter, % of original backlog still relevant at end of year (will be <50%, and that's healthy).

---

## Tier 3 — Long-tail (be ready to wing if any of these shows up)

### Case G — Build vs buy
*"A vendor is pitching us an off-the-shelf 'AI for consultants' platform for $200K/year. Build vs buy?"*
**Frame:** strategic fit (does the vendor own the data we'd give it?) → cost over 3 years (vendor + integration + switching) → opt-out cost (lock-in) → team capability (do we *want* to build this muscle?). **Winning move:** "Buy to learn, build to own — I'd run a 90-day vendor pilot to learn what 'good' looks like, then make the build call with data."

### Case H — Failure post-mortem
*"AI Factory shipped a tool that caused a real client problem — a generated number was wrong and made it into a client deck. Walk me through the post-mortem."*
**Frame:** facts (what happened, timeline) → root cause (5-whys: was it model, retrieval, workflow, or human?) → blast radius (other tools at risk?) → fix (immediate + structural) → trust repair (communication to partner, eval gate before re-enable). **Winning move:** lead with the *trust-repair plan*, not the technical fix.

### Case I — Org-design adjacent
*"Should AI Factory be centralized or distributed across BCG practice areas?"*
**Frame:** centralization wins on (reuse, eval rigor, talent density); distribution wins on (proximity to clients, domain fit, speed). Hybrid is usually right — central platform, embedded builders. **Winning move:** name the *anti-pattern* — "what kills both models is when nobody owns adoption. I'd build the org around an adoption owner per practice."

### Case J — Cost / unit economics
*"Our LLM bill is $X/month and growing. What would you do?"*
**Frame:** profile cost (which workflows? which model tier?) → easy wins (caching, smaller models for routing, batch) → structural (RAG to cut tokens, fine-tune for hot paths, agent-step pruning) → revisit (is this even the right problem — or is the value justifying the cost?). **Winning move:** "Before I cut cost, I'd check whether the value justifies it — a $200K LLM bill that saves $2M in consultant hours is a buy, not a cut."

### Case K — Quick sanity-check
*"Roughly how would you sanity-check whether an idea is worth building before writing any code?"*
Not a full case — a probe. 60-second answer: (1) is there a user who'll use it weekly? (2) is the value $-quantifiable? (3) can I build a paper prototype in a day that shows the workflow? (4) does someone already do this manually I can shadow? If 3 of 4 are no, don't build.

---

## Anti-patterns to avoid in *any* case

- **Jumping to architecture before clarifying scope.** Maan will let you, then ask "what would you cut?" and you'll have nothing.
- **Listing tools instead of reasoning** ("I'd use LangChain, Pinecone, Claude, and an MCP server"). Says nothing. Replace with "I'd use X because Y; if Y weren't true I'd use Z."
- **Skipping Measure.** Maan will notice. End every case on metrics + adoption gate.
- **Defending your first answer when he pushes back.** He's testing whether you update on new info. Say "good push — that changes my answer because…" not "well, I'd still…"
- **Whiteboard paragraphs.** 2–3 word labels only. Talk the rest.
- **Going silent while drawing.** Narrate every line. He's grading the reasoning trace.

---

## Two questions to ask Maan inside the case (signals seniority)

If the prompt leaves something genuinely ambiguous, asking one of these mid-case is a positive signal — it shows you're not just executing:

1. *"Before I go further — am I optimizing for time-to-first-ship or for the right long-term asset? Different answer."*
2. *"What's the partner's actual definition of success here — is it adoption, hours saved, or something visible to the client?"*

Don't ask more than 2 mid-case clarifying questions total — beyond that, it reads as stalling.

---

## Pre-interview drill plan (Sunday)

Run these 3 cases out loud, 25 min each, on a Zoom Whiteboard sandbox:

1. **Case A** (Internal tool — halve the hours) — drills your strongest muscle, builds confidence
2. **Case B** (Adoption diagnosis) — drills the muscle you don't yet have (resist jumping to a feature)
3. **Case C** (Eval strategy) — drills the muscle Maan will weight hardest

**Self-grade rubric per drill:**
- Did I say the 5-step structure out loud at the start? (Y/N)
- Did I ask 2–3 clarifying questions before drawing? (Y/N)
- Did I name something I'd *cut* or *deprioritize*? (Y/N — this is the Maan-specific tell)
- Did I close on Measure with a specific target number? (Y/N)
- Did I narrate every line I drew? (Y/N)

4 of 5 yes = ready. Below that = one more rep.
