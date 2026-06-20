# Slide Talk Track — Self-Service Analytics Agent

**Round:** Walmart Principal Data Analyst, AI-Enabled Analytics — Fri, June 19, 2026
**Format:** Behavioral + one prepared slide on something owned end-to-end (problem → steps → outcomes → tech stack)
**Panel:** Máximo Lau (Sr Manager, Ecommerce Analytics), Michael Hawkins (Director, Data & Analytics), Bashir Ghellali (unconfirmed)
**Project featured:** Self-service analytics agent over 67 BigQuery tables (achievement A1)

> **⚠️ NO-SLIDE MODE (updated 6/17).** Bashir never confirmed a slide is required, so prep on the assumption you deliver this **verbally**. Ignore the "build the slide" layout section below — keep it only as a fallback if the recruiter confirms a slide is wanted. When telling it without a visual, open with verbal signposting so the panel still gets the structure the slide used to give: *"Let me take this in four parts — the problem, what I owned, the outcome, and the stack."* Then walk the four beats below in order. Say the three anchor numbers slowly (67 tables · 23-case golden set · only AI skill in active business use) since there's no screen to point at.

---

## Why this project for this panel

It is the cleanest possible answer to the JD's actual thesis: *"move analytics from static descriptive work to AI-augmented decision intelligence, build tools not just analyses, and elevate the team."* You owned it end-to-end, it's in real business use, and it has a rigor story (evals) most analyst candidates can't tell. For an analytics-practitioner panel, lead with the **bottleneck the business felt** and the **adoption**, not the architecture — keep the architecture ready for follow-ups.

---

## The slide — build it yourself, here's the content + layout

One slide. Four quadrants + a title strip. Keep it sparse — it's a backdrop, not a script. Aim for ~7 words per bullet so you talk, not read.

**Title strip:**
> **Self-Service Analytics Agent over 67 BigQuery Tables**
> *Owned end-to-end · the only AI skill in active business use on Data Ventures*

**Quadrant 1 — PROBLEM**
- Business teams' routine asks queued on one analyst
- 67-table schema → analyst was the bottleneck
- Answers waited hours, sometimes a full day

**Quadrant 2 — WHAT I OWNED / STEPS** *(this is the "misc aspects of owning it" they asked for)*
- Framed problem with Product + DS + business stakeholders
- Designed 4 sub-agent flow: Context Researcher → SQL Drafter → Validator → Devil's Advocate
- Built 3-layer eval gate (deterministic rules → golden queries → human-in-loop)
- Drove rollout: ran HITL review week one, then stepped back

**Quadrant 3 — OUTCOMES**
- Only AI skill in active use by business teams on Data Ventures
- Approved by Sr. Director + product leadership
- Routine asks: hours/days → self-service, analyst removed from the loop
- Pattern others can adopt, not a one-off analysis

**Quadrant 4 — TECH STACK**
- BigQuery · Python · SQL
- LLM sub-agent orchestration (context-isolated validation)
- 8 deterministic SQL rules · 23-case golden-query eval suite
- Deployed as a Wibey/Claude Code skill

*Optional footer:* a tiny 4-box flow diagram of the sub-agent chain reads better than text in Q2 — if you have time to draw it.

---

## The talk track (~2.5 min, in your voice)

Pace yourself to ~45 / 45 / 40 / 30 seconds across the four beats. This is written to be *said*, not read.

**Problem (~45s)**
> "Walmart Data Ventures has the bottleneck most analytics orgs have — business teams need answers, and the analyst who knows the 67-table schema becomes the queue. A routine question would sit in someone's inbox for hours, sometimes a full day, just waiting on a person. I wanted the business teams to be able to ask the question themselves and get back an answer they could actually trust. So I designed and shipped a self-service analytics agent over those 67 tables. It's currently the only AI skill in active use by business teams on Data Ventures."

**What I owned / how I built it (~45s)**
> "I owned this end to end — problem framing through rollout. It's four sub-agents in a flow: a Context Researcher pulls the schema and relevant historical query patterns, a SQL Drafter writes the query, a Validator runs deterministic checks, and a Devil's Advocate challenges the output before anything ships. The one design choice I'd call out: the Validator and Devil's Advocate don't share the Drafter's context. If the same context that wrote the SQL also signs off on it, you get confirmation bias — it'll defend a hallucinated column. Separate contexts catch those."

**Outcomes + rigor (~40s)**
> "The thing I'm proudest of isn't the agent, it's that the business actually trusts it — and that came from the eval design. Three layers, cheapest first: 8 deterministic SQL rules catch structural mistakes for free, a 23-case golden-query suite checks real business questions against known-good answers, and human-in-the-loop review at rollout — I was the gate for the tricky outputs in week one, then stepped back. Nothing ships unless all layers clear; otherwise it escalates instead of guessing. That's why it got approved by the Sr. Director and product leadership and why people kept using it."

**What it changed / what's next (~30s)**
> "It took the analyst out of the loop for routine asks — that's the shift from static reporting to self-service the team's trying to make. And it's a pattern, not a one-off: I built a hybrid orchestrator on top of it that routes the same question through the agent and a CubeJS semantic layer in parallel and uses the disagreements to refine definitions over time. That's the direction I'd push the whole analytics function — analysts building reusable tools, not re-answering the same question."

---

## Per-interviewer tailoring

**Máximo Lau — Sr Manager, Ecommerce Analytics (people-manager + practitioner lens).** He leads ~7 analysts and lives the analyst-as-queue problem daily. Lean into the bottleneck framing and the *stakeholder translation* work — "I sat with Product and DS to turn vague asks into agent-ready specs." If he probes craft, go to the deterministic SQL rules (no SELECT *, every join needs a key, no cross-table aggregation without a date filter) — that's analyst-craft he'll recognize. Likely owns "how do you work with ambiguity / stakeholders" behaviorals.

**Michael Hawkins — Director, Data & Analytics (AI-transformation + people-analytics lens).** Public signal is genuine enthusiasm about AI transforming analytics. For him, foreground **adoption and team uplift**: only AI skill in real use, and the pattern others can adopt. Connect to the JD's coaching/advisor mandate — "the win isn't the tool, it's moving the team off static reporting." He's the likely hiring-manager/skip-level; this is where the "why this role, principal-IC ownership" narrative lands.

**Bashir Ghellali — unconfirmed.** No public profile found as of 6/9. If you can share his LinkedIn or team, I'll tailor. Default: keep both a business angle and a technical angle ready.

---

## Anticipated follow-ups (have a crisp answer ready)

- **"How do you know the agent's answers are right?"** → The 3-layer eval gate; golden queries check the *result*, not the SQL, because there are many correct queries for one question. Failures escalate, they don't ship.
- **"What happens when it's wrong / how do you handle hallucinated joins?"** → Context-isolated Validator + Devil's Advocate; deterministic rules below the LLM catch the cheap failures so the LLM-eval only handles the interesting ones.
- **"How did you get business teams to actually trust and adopt it?"** → HITL week one — I reviewed the tricky outputs before stepping back, so trust was earned on real asks, not promised. Plus Sr. Director/product sign-off.
- **"How is this a 'principal'-level contribution vs. a good analysis?"** → It's a reusable pattern + eval discipline the team can extend (the hybrid orchestrator is built on top), and it changed how the business gets answers — not a single deliverable.
- **"What would you do differently / what's the limitation?"** → Silent-agreement failure mode (both backends wrong the same way); mitigated with a periodic third-source golden regression. Next: auto-refinement loop so the human approves refinements rather than authoring them.
- **"What was the hardest part of owning it?"** → The translation layer — getting Product and DS to agree on what a "right answer" even was for ambiguous asks. That's what the golden set encodes.

---

## Delivery reminders

- It's a *behavioral* round — they care as much about **how you owned it** (judgment, stakeholders, tradeoffs) as the tech. Don't let it become a systems-design monologue.
- Use real numbers, don't inflate: "only AI skill in active use," "67 tables," "8 rules," "23 golden cases" — all verified. Don't upgrade "active use" to "org-wide rollout."
- Practice the open and close cold — those are what they remember.
- Bring one sentence of *team uplift* — it's the JD's whole back half and most candidates skip it.
