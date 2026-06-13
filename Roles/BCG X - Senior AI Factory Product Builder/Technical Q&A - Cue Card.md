# Technical Q&A — Cue Card (BCG X / Maan, Mon 6-1)

Segment 2 of the round (~10–15 min): technical / AI background. Maan = PhD astrophysics + LinkedIn product alum → he probes **"how do you know it works"** harder than anyone. Every answer must bottom out in a **gate, an abstain mechanism, or a metric** — never "I believe."

Built from the Sun 5/31 rapid-fire mock. These are *your* answers, corrected — not generic.

---

## The 3 tics to kill (this is the whole game)

1. **"I believe / I fundamentally" → "the deciding factor was…"** Belief-language is the one thing Maan reliably pounces on. Replace every instance with a decision criterion.
2. **Lead with the architectural reason, not the convenience reason.** You have the strong reason every time — say it *first*. ("Reusable contract," not "too big for a function." "Deterministic tree would explode," not "lots of if-else.")
3. **When unsure on depth, don't flee to portfolio breadth.** Answer the question asked, *fully*, then branch. Breadth-when-cornered reads as deflection.

Also: say **"MCP"** (em-see-pee), not "MCPU." Say **"every step/decision"**, not "every token" (Maan reads it literally).

---

## Q1 — "Walk me through an AI product you've shipped." (~2 min)

**Lead with the Jira Resolution Agent (A3).**

- **Problem, in numbers:** I run data analytics / readiness / stewardship for ~30 people across business + technical. Since Jan 2025, 400+ Jira tickets. Each took 30–60 min, sometimes a full day.
- **Build:** a context layer + agent architecture on top, producing persistent artifacts — a traceable work log of **every step/decision/SQL** the agent took.
- **Outcome:** ~10 min/ticket now. ~17 workdays saved on the low end, 50–60 on the high end.
- **Close on the gate (don't hand off):** "…and I review that work log before it reaches the stakeholder — **today I'm the gate**." (Plants the gate → sets up the eval question on your terms.)

❌ Don't close with "I'd love to go into details if you're interested" — it hands him the wheel mid-pitch.

**The "failure budgets" upgrade (pull this from the Walmart prep — it's a Principal-level line):**
> "The agent itself is fully autonomous — zero internal checkpoints. My review sits **outside** the agent loop, on purpose: the cost of a wrong message to a stakeholder is much higher than the cost of a failed BigQuery retry. So I sized the agent's autonomy for **execution** and my review for **communication** — two different failure budgets, each sized to its blast radius."

This reframes HITL as a *deliberate workflow decision*, not an agent-design limitation. It's the sharpest single line in the whole Walmart file. Use it on Q1 or Q3.

---

## Q2 — "How do you actually know it works? What's your eval?" ⭐ highest-probability question

**Answer the question fully BEFORE branching to other projects.** Lead with the mechanism, not the portfolio.

**Three layers (this is the upgraded version — pulled from the Walmart prep, has the concrete mechanism):**
1. **Structural correctness:** the agent's SQL is checked against the context layer's **join knowledge graph (52 nodes, 63 edges, 36+ verified join paths)** — joins, columns, query shape all validated against what the schema says is legal. Not "does it look right" — "is this join path one the graph confirms exists."
2. **Intent matching:** the proposed answer is compared against **how this team answered similar questions before** (retrieval over 313 historical queries). If the shape is wildly different from precedent, that's a flag.
3. **Provenance:** every decision, every SQL query, the data touched — logged. So "correct" is *checkable*: did it pull the right source, does the answer trace to it.

- **Name the gate + own the gap:** "Today I'm the gate — I review the work log before it reaches the stakeholder. The honest gap: that's manual. The next version moves the gate to **golden-set regression** so it flags when a new ticket diverges from a known-good pattern instead of relying on me."

**Define "correct" when pushed:** join path is graph-verified + answer traces to a real source + shape matches precedent.

❌ Tics that showed up here: burying the answer under "a variety of other things I've built"; not defining "correct." Lead with the join-graph mechanism — it's specific and it lands.

---

## Q3 — "What does it do when it's not sure?" (abstain / low-confidence)

Name it as a **router with a confidence gate + human fallback**:
- **Complexity triage up front:** simple path auto-resolves; complex/uncertain tickets get flagged.
- On the complex path it gathers more context via the **MCP** (which tables, which joins could be useful), assembles what it knows.
- **Grounded generation — the key move:** "It's not just *instructed* not to fabricate — it's architecturally grounded. The answer can only cite data the SQL actually returned, so there's no surface to invent a number. Worst case it returns **'insufficient data' and abstains** — it never returns a wrong number."

Magic words: **abstain**, **grounded**. The distinction Maan cares about: *I told it to behave* (weak) vs. *it structurally can't misbehave* (strong).

---

## Q4 — "Why an agent and not a deterministic pipeline? A real tradeoff."

**Lead with the decision rule:** "Agent where the input *varies*, deterministic where I can *verify*."
1. **Why the deterministic path failed here:** tickets don't follow a fixed shape — a deterministic tree would've been an unmaintainable explosion of if-else branches. Reasoning over context handles the variance.
2. **Proof I mean it (the gold detail):** I have a **separate verifier agent** with deterministic checks — it runs the SQL and confirms the findings in the final deliverable match the queried data. Deterministic where it counts.

❌ Kill "I do believe giving an LLM context lets it reason better" → "the deciding factor was input variance." Don't sound like an agent-maximalist; you reach for the LLM only where it earns its place.

---

## Q5 — "MCP server vs. custom tool — your rule of thumb?" (30 sec)

**The dividing line is reusability + interface boundary, NOT size.**

"MCP server when the capability is **reusable across multiple agents/clients and worth a stable, standardized interface** — it's a contract other things plug into. Inline custom tool when it's specific to one agent and not worth the server overhead. My database-interaction layer is an MCP server *precisely because* every agent I build needs to talk to that DB the same way — so I expose it once instead of re-implementing it inside each agent."

❌ Not "too much context to fit in a function" (sounds accidental) → "reusable contract across agents" (sounds deliberate).

---

## Q6 — "What didn't work? What would you do differently?" ✅ your strongest answer

The honest one — **build-it-and-they-won't-come.**

- I built a RAG / NL-to-SQL app on my historical SQL queries — business teams could ask in English, get SQL + answer. A standalone React app.
- **Failure (quantify it):** adoption was near-zero — the only people who opened it were the power users I *didn't* build it for.
- **Lesson:** people don't change unless the value is obvious and frictionless. So I killed the standalone app and folded the capability into the **semantic/hybrid layer as a skill** — it hits the MCP for context so the agent builds the SQL, right where they already work.
- **Close on the lesson, not the architecture:** "Don't build a destination — embed in the workflow they already use."

This is the thread that ran through every case tonight. Maan (LinkedIn alum) has lived this exact lesson.

---

## Q7 — "If you had another month, what would you build next?" ✅

Pick **one**, tie it to moving the gate.

"Right now I gate every ticket because the general agent is probabilistic. But ~70% of tickets cluster into a few **themes** — e.g. feasibility questions. I'd build a **deterministic, evaluated sub-flow per common theme** so I can auto-resolve those with confidence and only gate the long tail — **automate the head, gate the tail**. That takes me from gating 100% of tickets to maybe ~30%, and lets me embed it directly in Jira for business-user self-serve."

Callback to "today I'm the gate" (Q1) + Pareto/min-median instincts from the cases.

---

## "Same substrate, different posture" — the platform-thinking move (Q4)

If he asks for a second project, or about how your builds relate, this is the Principal-level framing. Don't describe two agents — describe **one substrate, two postures sized to blast radius**:

- **Jira agent** — human review sits *outside* the loop. High blast radius (a wrong message to a stakeholder), so I gate communication.
- **Autonomous data analyst** — ships answers *directly* to users, validation *inside* the loop (structural check + audit/fix pass on top). Low blast radius (their own next decision), so no external gate needed.
- **Same context layer + MCP underneath both.** "Same substrate, different HITL posture, each sized for a different cost profile."

Teaching *when each pattern applies* (not just describing them) is the judgment signal Maan rewards. The reusable substrate — not the agent on top — is the asset.

---

## If he says "draw me the architecture" — the 6-box diagram (60 sec, narrate every box)

Draw left-to-right, talk while you draw, no paragraphs. This is the cp-platform shape — the thing that powers all the agents:

```
                    ┌─────────────────┐
                    │  CONTEXT LAYER  │  curated domain knowledge:
                    │  (source of     │  schema, joins, business defs,
                    │   truth)        │  + join knowledge graph
                    └────────┬────────┘
                             │ exposed through
                             ▼
 user ──► AGENT ──► MCP (tools) ──► BigQuery ──► VERIFIER ──► work log / answer
 query    (router:   schema · joins ·   (execute   (SQL results    (provenance,
          triage)    validated-SQL ·    queries)   match the       traceable)
                     RAG over history)             queried data?)
```

**Narration script (the 6 boxes, one line each):**
1. **Context layer** — the asset. Curated domain knowledge — schema, join paths, business definitions — as a source of truth that survives between calls. *"The reusable substrate is the thing I built; every agent is thin on top of it."*
2. **Agent / router** — triages the request: simple path auto-resolves, complex path gathers more context.
3. **MCP** — how the agent reaches the context layer. Tools for schema lookup, verified join paths, validated-SQL generation, and RAG over 313 historical queries. *(Deep version held in reserve: 14 tools + 4 read-only resources.)*
4. **Execution** — runs the SQL against BigQuery.
5. **Verifier** — separate deterministic check: does every number in the deliverable match what the SQL actually returned? Grounded, so it can't invent figures.
6. **Work log / answer** — provenance on every step; I review it before it ships (the gate).

**Hold in reserve — only if he probes a specific box** (don't volunteer; it eats the case clock):
- *Context layer internals:* markdown source-of-truth compiled to in-memory JSON for zero-latency lookups; 52-node/63-edge join graph; 89 domain sections; ChromaDB RAG index.
- *Self-maintaining:* 5 daily drift validators against live BigQuery (schema, enums, joins, tables, DDL) auto-trigger doc regen via a 3-tier LLM fallback. "The substrate maintains itself."
- *Flagship tool:* `cp_generate_validated_sql` — generate → validate via function-calling → dry-run → execute, ~60s.
- *Scale (pick 2-3 MAX, never the whole list):* 68 tables, 1,350+ columns, 313 indexed queries, 7+ downstream consumers, 57 analyses powered.

⚠️ **Discipline:** the diagram is 6 boxes. The reserve is for *answering a probe*, not for proving thoroughness. Maan weights the case; a stat-dump steals its clock.

---

## Failure story (if he asks) — V1 → V2, with the cognitive-mistake beat

Same as tonight's RAG-app answer, but pull the sharper reflection beat from the Walmart prep:
- **Build:** V1 text-to-SQL RAG app with its own frontend. Demoed to leadership. Technically worked.
- **The cost:** adoption near-zero — only power users I didn't build it for touched it.
- **The cognitive mistake (the upgrade):** *"My first instinct was to assume the model needed to be better, or I needed more data. What I missed was that the blocker wasn't the system — it was the surface. I'd anchored on 'make it better' before asking 'is it in the wrong place.'"*
- **Recovery (short):** tore out the frontend, rebuilt as a context layer + MCP delivered into the tool engineers already used. Same substrate now powers 7+ consumers.
- **Lesson, as the close:** "Don't build a destination — embed in the workflow. And the reusable asset usually isn't the thing the user touches; it's the substrate underneath."

Own the *specific wrong instinct*, not just the outcome — that's what makes it land.

---

## ❌ Do NOT bring from the Walmart prep

- **The "Senior DA → Principal, title is a lagging indicator" defense (Walmart Q5/Q6).** That answered a title-jump question Maan isn't asking. Off-topic for BCG.
- **The full stat dump** (226 ChromaDB chunks, 3072-dim embeddings, SHA-256 cluster_id, 18-experiment framework). Walmart had engineer panelists with time; Maan has 45 min across 3 segments and protects the case. Draw from the reservoir — 2-3 cups, not the tank.

---

## Pre-flight (Mon AM)

Read this once out loud. Drill **Q2** (lead with join-graph, not portfolio), **Q4** (agent-vs-pipeline, kill "I believe"), **Q5** (MCP = reusable contract), and the **6-box architecture** until you can draw it in 60 sec. The bar: every answer lands on a **gate, abstain mechanism, or metric**, you never say "I believe," and the architecture stays at 6 boxes unless he probes deeper.
