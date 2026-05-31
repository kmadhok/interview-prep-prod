# Website Project Content — kanumadhok.com

Source of truth for project descriptions to publish on kanumadhok.com. Iterate here first; hand to the website repo (`~/Downloads/code/my_website`) only when the content is locked.

**Author:** Kanu Madhok
**Last updated:** 2026-05-30
**Owning repo (target):** github.com/kmadhok/my_website

---

## How to use this file

- Each project has the same shape: pitch, problem, architecture, hard parts, evals, retrospective, stack, confidentiality notes, links, status.
- Sections marked `[FILL]` are gaps to verify before publishing.
- Sections marked `[CONFIDENTIAL — do not publish]` are notes for you only.
- **Priority** tells the website what to feature: P1 = bento grid hero tiles, P2 = secondary tiles, P3 = list-only.
- When you're confident in a project's content, copy it to a new `content/blog/{slug}.mdx` file in the website repo, plus a card in `components/SelectedWork.tsx`.

---

## Priority ranking — at a glance

| # | Project | Type | Priority | Why |
|---|---|---|---|---|
| 1 | CP Platform — Context Engineering Core | Walmart | P1 | The substrate everything else sits on. Best signal of "I build platforms, not scripts." |
| 2 | CP Analytics MCP Server | Walmart | P1 | MCP credibility play — fills the headline-to-experience gap. 14 tools, real distribution. |
| 3 | CP Hybrid Orchestrator (parallel dual-path) | Walmart | P1 | Novel architecture — Cube + raw SQL in parallel with reconciliation. Strong differentiator. |
| 4 | Customer Voice Semantic Layer (with auto-update loop) | Walmart | P1 | Self-improving semantic layer. Auto-PR generation from coverage gaps is unusual and impressive. |
| 5 | CP Analytics — Multi-Hypothesis Orchestrator | Walmart | P1 | Autonomous depth-first analyst. REFLECT scoring is a real research contribution. |
| 6 | Per-Dashboard Semantic Layers via CLI Agents | Walmart | P1 | New initiative — one semantic layer per dashboard, exposed through the coding CLI business teams already use. Brings governed analytics to where users already work. |
| 7 | JResolutionAgent (Jira Ticket Worker) | Walmart | P2 | Autonomous data steward, 10-retry self-healing. Hierarchical context management. |
| 7 | Text-to-SQL Copilot (Walmart, public demo) | Walmart | P2 | The public demo version. Distinct from `cp_generate_validated_sql` flagship; needs framing. |
| 8 | Text-to-Looker Copilot (Walmart, public demo) | Walmart | P2 | Second public demo, narrower scope than text-to-SQL. |
| 9 | Voice Agent Debate Platform | Personal | P2 | Multi-agent + voice stack, demo-ready. Range signal. |
| 10 | FTI Consulting RAG Proposal Generator | Capstone | P2 | Best in Show award. RAG-in-prod with client outcomes. |
| 11 | AI Job Search Automation | Personal | P2 | End-to-end agent system, dogfooded on the job hunt itself. |
| 12 | Ralph Loops | Personal | P3 | Autonomous-agent harness with 566-test coverage. |
| 13 | Join Discovery Engine | Personal | P3 | Embeddings + LLM reasoning over schema. Strong eval story but narrower audience. |
| 14 | Voice Journal | Personal | P3 | Theme-aware journaling. Less recruiter-relevant. |
| 15 | Market Dashboard (Kalshi + Odds API) | Personal | P3 | Pipeline reference project. |
| 16 | Smart Scraper | Personal | P3 | Tactical helper to AI Job Search. |

---

## Confidentiality ground rules (apply to every Walmart project below)

For every Walmart project, the rules are the same. State them once here, link from each project, don't re-litigate per section.

**Always OK to publish:**
- High-level capability descriptions ("text-to-SQL agent over an analytics warehouse")
- Architecture patterns ("dual-path orchestrator with reconciliation", "hybrid retrieval", "MCP-as-substrate")
- Generalized scale ("hundreds of thousands of panelists", "tens of millions of survey responses")
- Outcomes already on the resume ("~73% turnaround cut", "1–2 day → sub-minute")
- Stack names (Python, FastAPI, BigQuery, Cube.js, MCP, Gemini, etc.)
- Design decisions and trade-offs (the *thinking*, not the implementation)
- How you evaluated the system (methodology, not internal numbers)

**Never publish:**
- Internal table names, column names, dataset names, project IDs
- Specific tool names visible only inside Walmart (`cp_get_schema`, `cp-analytics`, `wmt-dsi-cally-audience-prd`, etc. → rewrite as "schema lookup tool", "the orchestrator skill", "the warehouse FQN")
- Supplier names, customer names, panelist counts at row level, PII
- Screenshots of internal UIs, internal Slack channels, internal repos
- Specific internal metrics not already public (e.g., the 158M task-rows figure, the 1.1M panelist count — generalize to "tens of millions of rows", "over a million panelists")
- Repo paths (`~/Desktop/repos/cp-platform`), internal mcp.json config
- Co-worker names, manager names, team org structure
- Exact LLM choices when tied to internal infra (rewrite "Wibey Opus → Sonnet → Gemini 2.5 Pro" as "tiered LLM fallback")
- The skill ecosystem names (`cp-hybrid`, `cp-analytics`, `jira-ticket-worker`, etc.) — these are internal namespaces; describe what they *do*, not what they're called

**Manager test:** if your manager Googled the published version, would they shrug ("that's just industry-standard work described well") or flinch ("that's our internal naming")? Aim for shrug.

---

# P1 — Lead with these (Walmart platform work)

---

## 1. CP Platform — Context Engineering Core for an Analytics Warehouse

**Public title:** Context Engineering Platform — A Single Source of Truth for an Analytics Warehouse

**Pitch:** A production knowledge platform that consolidates dozens of warehouse tables and over a thousand columns into a single searchable, validated, auto-maintained context layer — and distributes it to every downstream agent through one MCP server. The substrate that makes every other agent on top of it possible.

**Status:** In production internally. Public write-up describes the *pattern*.

**Confidentiality:** Don't name the warehouse, the team, internal datasets, or any of the consuming skills by their internal names. Describe the architecture and the *why*, not the specific repo layout.

### What it does

Three things, in service of one goal:

1. **Centralizes warehouse knowledge.** Markdown files with table schemas, business rules, join paths, and known data quirks. Human-curated, version-controlled, treated as the single source of truth.
2. **Auto-maintains itself.** A pipeline detects schema drift daily against the live warehouse, regenerates documentation when tables change, re-embeds the doc corpus, and runs five validators that catch silent breakage.
3. **Distributes context to every agent.** An MCP server exposes the compiled context as zero-latency in-memory lookups (schema, joins, domain rules) plus RAG-backed Q&A and historical-query search.

Every downstream agent — analytics orchestrator, ticket resolver, KPI monitor, business-team chat, semantic-layer gap-filler — depends on this platform. Each one becomes a thin layer on top instead of a duplicated context-engineering effort.

### Why it exists

Knowledge about a data asset is normally scattered across repos, Confluence pages, Slack threads, and people's heads. Every new agent has to re-discover the same schema, the same join paths, the same business rules. Worse, schemas drift silently — a column type changes upstream, and three agents start producing subtly wrong numbers without anyone noticing.

Centralizing and auto-maintaining this context is what makes a multi-agent ecosystem actually possible. Without it, every new agent is a one-off that ages out within months.

### Architecture

Four layers, dependency direction always inward:

```
ACCESS LAYER         MCP server (over a dozen tools) │ Web UI │ Python SDK
                                  ↓
KNOWLEDGE LAYER      Vector index (RAG) │ SQL knowledge base │ Compiled JSON
                                  ↓
INGESTION LAYER      schema extractor → diff engine → doc generator →
                     chunker → embedder → context compiler
                                  ↓
QUALITY LAYER        5 daily validators (schema, enums, joins, tables, DDL cross-ref)
                                  ↓
                     External: warehouse, DDL repos, query history
```

### Key design decisions

**Markdown as the source of truth.** Schemas, joins, and domain rules live as human-curated markdown. Embeddings, JSON, and compiled artifacts are all derived and regenerable. The SoT is what humans can read and review.

**Compiled artifacts for hot paths.** Markdown → JSON at build time. Schema lookups, join-path lookups, and domain context queries are zero-latency in-memory dict reads. The slow path (RAG, BQ execution) is reserved for genuinely open-ended questions.

**Tiered LLM fallback for doc generation.** Doc regeneration never fails because of a single provider's outage or rate limit.

**Drift detection as a first-class concern.** Five validators run daily against the live warehouse. Drift triggers auto-doc-regen. Context never silently goes stale.

**RAG + validation layering.** RAG retrieves chunks, an LLM synthesizes a grounded answer, MCP tools validate against live data. Speed of RAG, precision of structured tools.

### The hard parts

**Designing a context system that survives schema drift.** Most "schema docs" rot within weeks. The auto-detection + auto-regeneration loop was the only sustainable answer. Building the diff engine + doc generator pipeline so that drift produced a *PR-able* doc change (not a silent overwrite) took multiple iterations.

**Doc chunking strategy.** Naive markdown chunking by paragraph produced chunks that lost critical context (a column description without its table). Built a chunker with eight semantic section types so each chunk is self-contained.

**Resolving table-name ambiguity.** Users (and agents) ask for "the rewards table" — there's no table literally called that. Built a resolution chain: strip prefix → exact match → alias lookup → singular/plural → partial substring. Single function, called everywhere.

**Knowing when to invalidate the cache.** Three caches (schema, joins, domain) load lazily on first access. Daily pipeline runs invalidate; manual `refresh` triggers invalidate. Got this wrong once and served stale schema for half a day.

### How I evaluated it

- **Schema accuracy:** daily validator catches drift; PR rate from auto-regeneration is the proxy metric for how much drift is happening.
- **Retrieval quality:** held-out set of warehouse questions with known-correct answers, scored on RAG accuracy and citation faithfulness.
- **Latency:** target was sub-second for schema/join lookups, single-digit seconds for RAG, sub-30s for end-to-end execution. All met after the in-memory cache redesign.
- **Downstream adoption:** the real metric. Number of skills built on the platform vs. number of skills doing their own context discovery. The former grew, the latter shrank to zero.

### What I'd do differently

- **Move ingestion to event-driven.** Currently daily cron. A trigger on warehouse schema-change events would catch drift in minutes instead of up to 24 hours.
- **Native user-feedback loop into RAG.** Thumbs-up/down per answer, fed back into chunk ranking. Currently RAG quality is improved manually.
- **Tighter cost telemetry** per consuming agent. Hard to attribute LLM spend back to which skill is generating the most load.

### Stack

Python, FastMCP (stdio), Flask, BigQuery, ChromaDB, Gemini embeddings, hybrid RAG (vector + BM25 + RRF fusion), 8-type semantic chunker, markdown SoT, JSON-compiled hot paths, 5-validator daily pipeline.

### Links

- Demo: [FILL — is there a sanitized public version we can stand up?]
- Architecture diagram: [FILL — extract from internal doc, sanitize, redraw]
- Repo: [FILL — internal only, available on request]
- Deeper write-up: this page

---

## 2. MCP Server for Analytics Warehouse Context

**Public title:** An MCP Server That Distributes Warehouse Context to Every Agent

**Pitch:** Built on top of the context-engineering platform above — a FastMCP server (stdio transport) that exposes warehouse schema, joins, domain rules, RAG Q&A, historical-query search, and a flagship validated-SQL-generation tool over a single uniform interface. Every internal AI agent that touches the warehouse consumes context through these tools.

**Status:** In production. Sole distribution surface for warehouse context across the org's agent ecosystem.

**Confidentiality:** Don't name the specific tools, the internal namespace, or the consuming skills. Describe what each tool *category* does.

### What it does

A FastMCP stdio server exposing roughly a dozen tools across five categories:

1. **Read-only context tools** — schema, join paths, domain rules, accumulated cross-analysis knowledge, backlog access. Zero-latency in-memory hits.
2. **Execution tools** — write SQL to disk *before* BQ execution (provenance guarantee), then run with a generous timeout and structured result return.
3. **Discovery / RAG tools** — RAG Q&A over warehouse docs, semantic search over a corpus of historical queries.
4. **Reporting workflow tools** — scaffold report directories, build deterministic execution manifests, generate branded charts, validate output contracts.
5. **Maintenance tools** — trigger pipeline refresh, rebuild caches.

Plus a flagship tool: a full Gemini-validated NL→SQL→execution pipeline in a single call. Generate with one model, validate via function-calling with another (schema checks, join verification, domain-rule enforcement, dry-run), then execute.

### Why it exists

The retrieval + validation logic inside the first text-to-SQL prototype was duplicated work — every agent that talks to the warehouse needs the same primitives. MCP was the right abstraction because it standardizes tool-calling across clients. Build once, reuse from every agent host (the orchestrator skills, the ticket worker, the semantic layer's gap-filler, the Slack bot, business chat copilots).

### Architecture

- **Transport:** stdio (JSON-RPC). Logging on stderr only; stdout reserved for protocol.
- **State:** stateless per call except for lazy-loaded JSON caches that persist for the process lifetime. First call ~5–10ms, subsequent ~0ms.
- **Backing:** the context platform's compiled artifacts (schema, joins, domain sections, graph) for in-memory hits; subprocess wrappers for execution scripts; ChromaDB for RAG; hybrid vector + BM25 + RRF for SQL search.
- **Resolution:** every table-name input runs through a 6-step resolver (strip FQN → exact match → strip prefix → alias → singular/plural → substring) so callers don't have to know exact internal names.

### The hard parts

**HTTP vs. stdio transport choice.** Most MCP examples are stdio for one client. Picked stdio anyway because (a) every consumer is a local skill, (b) stdio is dead-simple to debug, (c) a single MCP host can multiplex. Would revisit if cross-host consumers showed up.

**Tool granularity.** Early version had one tool: "query the warehouse." Too coarse — agents couldn't decompose. Split into the five categories above, and agents started composing them naturally (search → schema → validated SQL → execute).

**Provenance for executed SQL.** Easy to lose track of what query produced what CSV. Solved by writing SQL to disk *before* execution, logging the BQ job ID, and providing a deterministic `build_execution` tool that compiles the audit log into a single manifest after the fact.

**Schema versioning.** When the warehouse evolves, every consuming agent needs the update. The lazy cache pattern + a `refresh` tool gives a clean invalidation story — and the daily pipeline + drift validators catch the cases where humans forget.

**The flagship "validated SQL" tool.** Generating SQL is one model call; *validating* it (schema check, join verification, domain-rule check, dry-run, fix-and-retry) is a loop with function-calling. Got it from 60% to 95% accuracy by adding the validation loop with retries on failures. The flagship runs ~60s end-to-end and replaces 10+ minutes of manual work.

### How I evaluated it

- **Accuracy on the flagship NL→SQL tool:** hand-curated ~150 real user questions with gold answers. Compared execution results row-by-row. Validation loop pulled accuracy from ~60% (single-shot generation) to ~95% (with validate-and-retry).
- **Adoption:** number of skills built on the MCP vs. doing their own context discovery. The MCP server became the sole consumption path within months.
- **Cost telemetry:** bytes billed per tool call, tracked over time. Caught a few cases where the agent was generating wasteful joins that returned right answers via expensive paths.

### What I'd do differently

- **PII allow-list on sample-row tools.** The schema tool returns sample rows alongside columns — for any table with PII, that's a problem. Added a column-level allow-list after the fact; should have been there from day one.
- **Session-level rate limiting.** A bad agent can spam the search tool dozens of times per session. Per-session token bucket would prevent runaway cost.
- **HTTP transport in parallel for cross-host consumers** if/when that demand shows up.

### Stack

Python, FastMCP, BigQuery, ChromaDB, hybrid retrieval (Gemini embeddings + BM25 + RRF), tiered LLM fallback for the validated-SQL flagship, subprocess execution wrappers, JSON-RPC over stdio.

### Links

- Demo: [FILL]
- Architecture diagram: [FILL — sanitized]
- Repo: [FILL — internal only, available on request]

---

## 3. Hybrid Orchestrator — Dual-Path Question Answering with Reconciliation

**Public title:** A Parallel-Architecture Orchestrator That Answers Every Question Two Ways and Reconciles

**Pitch:** A novel orchestrator pattern: every user question dispatches *two parallel sub-agents simultaneously* — one path through a governed semantic layer, one through raw SQL — and a reconciliation classifier compares the answers, tags the verdict, and decides what to surface. Best-of-both: semantic-layer governance + raw-SQL completeness, without forcing the user to pick.

**Status:** In production internally for business and product teams via their CLI agents.

**Confidentiality:** This is the public-facing architecture description. Don't name the semantic layer product internally, the ports, or the specific consuming teams.

### What it does

User asks "how many active panelists do we have?" The orchestrator runs two sub-agents in parallel:

- **Path A — Governed semantic layer.** Cube.js model, pre-modelled measures, row-capped, PII-protected. Fast, safe, but only answers what's been modelled.
- **Path B — Raw SQL through a query proxy.** Context-engineered, no row cap, unrestricted SQL surface. Powerful, but generates LLM-written queries that need verification.

Both return. A reconciliation step compares the results — within 0.5% relative tolerance — and tags the answer with one of five verdicts:

| Verdict | Meaning |
|---|---|
| `SAME_INTENT_SAME_RESULT` | Both paths agreed. High confidence. |
| `COVERAGE_GAP` | Semantic layer didn't cover this; raw path used. Triggers auto-improvement (see below). |
| `AMBIGUOUS_QUESTION` | Question was unclear; paths interpreted differently. Surface both. |
| `SAME_INTENT_DIFFERENT_RESULT` | Paths disagree. Show the diagnostic. |
| `LLM_FAILURE` | One path errored. |

The user gets a confidence-badged answer they can trust, or an explicit "I'm not sure — here's why."

### Why it exists

Semantic-layer-only systems have a fatal flaw: you never know what questions you *can't* answer. Raw-SQL-only systems require user credentials and produce LLM-generated queries that nobody validated. The dual-path pattern is the only way to get governance *and* completeness without forcing a tradeoff. The reconciliation classifier turns "two answers" into one trustable answer with explicit confidence.

The bigger win: every coverage gap is now a *signal*, not a problem. See the auto-update loop in the next project.

### Architecture

```
User question ("How many active panelists?")
    ↓
Hybrid orchestrator (LLM-controlled dispatch)
    │
    ├─→ Path A: Semantic-layer skill → Cube.js (governed, row-capped, PII-safe)
    │
    └─→ Path B: Raw-SQL discovery skill → query proxy (context-engineered, unrestricted)
    ↓
Reconciliation classifier (0.5% tolerance, intent matching, verdict tagging)
    ↓
Confidence-badged answer + structured trace record to coverage-gap log
```

### The hard parts

**Reconciliation across two heterogeneous answer shapes.** Path A returns Cube measure results in a typed schema. Path B returns raw rows from whatever SQL the model wrote. Comparing them required normalizing both to a common intent representation first — and the intent classifier was the hardest piece, because "23,400 active panelists" and "23,396 active panelists" might be the same question answered with slightly different filters (which is fine) or genuinely different definitions of "active" (which is not).

**The 0.5% tolerance was a calibration problem.** Too tight → false disagreements. Too loose → real bugs slipped through. Settled on 0.5% relative after looking at the natural variance across legitimate semantic differences.

**Privacy redaction before logging.** Every reconciliation produces a structured trace record stored for the auto-update loop (next project). User questions can contain PII, account names, supplier names — all of it gets redacted server-side before any record hits disk.

**Latency budget when running two paths.** Doing both in parallel ate ~1.5× the latency of a single-path system, not 2×, but still required streaming and aggressive timeouts on the raw-SQL path (which can run away).

### How I evaluated it

- **Verdict distribution:** what % of questions land in each of the five verdicts. Healthy ratio is high `SAME_INTENT_SAME_RESULT` + reasonable `COVERAGE_GAP`. Spike in `SAME_INTENT_DIFFERENT_RESULT` is the alarm.
- **User confidence:** subjective but tracked — do users trust the badged answers and act on them, or do they spot-check externally?
- **Auto-update yield:** how many coverage gaps eventually turned into modelled measures (next project).

### What I'd do differently

- **Streaming reconciliation.** Currently both paths return fully before reconciliation. Streaming partial results would let the orchestrator surface "high confidence so far, still verifying" mid-answer.
- **Path C for narrative answers.** Some questions ("why did completion rate drop?") aren't reducible to a single number. A third path that does narrative synthesis would fit naturally into the same reconciliation frame.

### Stack

Python, Cube.js (semantic-layer path), BigQuery (raw-SQL path), MCP for context injection on both paths, reconciliation classifier (LLM-as-judge with structured output), JSONL trace logging with PII redaction.

### Links

- Demo: [FILL — sanitized internal recording or rebuild against a generic dataset]
- Architecture diagram: [FILL]
- Repo: [FILL]

---

## 4. Customer Voice Semantic Layer — With an Auto-Update Loop

**Public title:** A Self-Improving Semantic Layer That PRs Its Own New Measures

**Pitch:** A governed Cube.js semantic layer over a large customer-research warehouse — paired with a coverage-gap clustering engine that detects which questions the layer *can't* answer, synthesizes candidate new measures from real user traffic, proves them numerically equivalent to ground-truth raw SQL, and opens draft PRs for human review. The layer becomes self-improving: every question users ask is a candidate for being modelled into the layer next week.

**Status:** In production. Auto-update loop behind a feature flag (default off).

**Confidentiality:** Don't quote internal cube names, internal team names, or specific scale numbers (rewrite "1.1M panelists" → "over a million panelists", "158M task rows" → "tens of millions of survey responses").

### What it does

Two halves:

**Half 1 — The semantic layer itself.** A Cube.js model spanning over a million panelists, tens of millions of task rows, and tens of thousands of surveys, organized into roughly two dozen cubes across five domains (panelist lifecycle, task/survey pipeline, rewards & billing, recruitment, operational data quality). PII-protected, row-capped, pre-modelled. Consumed by the dual-path hybrid orchestrator above.

**Half 2 — The auto-update loop.** Every time the orchestrator hits a `COVERAGE_GAP` verdict, a structured trace gets logged. A weekly driver:

1. **Clusters** the gaps by `(missing_concept, raw_table, columns_used)` with deterministic SHA256 cluster IDs.
2. **Triggers** when the same concept appears at least 3 times from 2+ distinct users within 7 days.
3. **Synthesizes** a candidate YAML measure via an LLM, seeded with the working raw SQL + expected value + table FQN.
4. **Validates** that the YAML parses and conforms to style.
5. **Proves equivalence** — loads the proposed YAML into a local Cube, compiles to SQL, executes against the warehouse, compares the value to the reference raw SQL. Must match within 0.5%.
6. **Opens a draft PR** on the semantic layer repo with full provenance: cluster ID, redacted user questions, equivalence proof table, failure logs.

The Cube model converges toward the actual user question space without manual guessing.

### Why it exists

Manually maintained semantic layers always lag the questions users actually ask. Maintainers guess what to model next; users hit gaps; gaps are reported in Slack; maintainers eventually add them; repeat. The auto-update loop makes that feedback loop weekly and deterministic — and the equivalence proof means no PR ever lands without numerical evidence it returns the right answer.

This is the rare case where "AI generates PRs" can actually be safe, because the equivalence test is a hard mathematical gate, not a soft "looks good to me."

### Safety rails

- All PRs are **draft** — a human must mark Ready for Review
- **Max 2 PRs/day** so reviewers aren't overwhelmed
- **No PR without equivalence proof** — numerical match is non-negotiable
- **Hard constraints:** only ADD new measures (never modify existing), only model files touched, never delete
- **CI guard workflow** asserts PR is draft, body contains an equivalence table, no removals
- Behind env flag (default off)
- Privacy redaction on user questions before any logging

### The hard parts

**The cluster ID has to be deterministic.** Same concept arriving from different phrasings has to hash to the same cluster, or every gap becomes a fresh cluster and the threshold never trips. Cluster key is `(missing_concept_normalized, raw_table_FQN, sorted_columns_used)` — small enough to collide on genuine duplicates, specific enough to not over-cluster.

**The equivalence test is the whole game.** Without a hard numerical gate, generated YAML measures would land bugs into the semantic layer. Built the equivalence test as: load YAML → compile via Cube → execute generated SQL → execute reference raw SQL → compare values within 0.5%. If any step fails, no PR.

**PR review fatigue.** Maintainers will rubber-stamp a flood of auto-PRs. The 2-PRs/day cap + draft-only + required-equivalence-table forces reviewer engagement instead of allowing reflexive merge.

**Privacy redaction.** User questions logged for cluster analysis can contain PII, account names, internal identifiers. Built a redaction pass that runs before anything hits disk.

### How I evaluated it

- **Equivalence test pass rate:** what % of synthesized YAML measures pass the equivalence gate. If it's too low, the LLM synthesis prompt needs work. If it's near 100%, the gate is too loose.
- **PR acceptance rate:** of the equivalence-passing PRs, what % get marked Ready and merged? Tracks reviewer trust.
- **Cluster growth over time:** healthy system has fewer coverage gaps in week N+1 than week N as the layer absorbs the patterns.

### What I'd do differently

- **A "rejected cluster" feedback channel.** When a reviewer rejects a PR, capture *why* and feed it back into the synthesis prompt — currently the LLM doesn't learn from rejections.
- **Multi-cube proposals.** Some gaps need a new dimension or join across cubes, not just a measure. Current synthesizer only generates measures.

### Stack

Cube.js, BigQuery, MCP for context injection on cube synthesis, LLM-as-judge for cluster matching, equivalence test harness (YAML → Cube compile → BQ execute → compare), draft PR automation with provenance manifests.

### Links

- Demo: [FILL — likely a sanitized walkthrough of one auto-PR end-to-end]
- Architecture diagram: [FILL]
- Repo: [FILL]

---

## 5. Multi-Hypothesis Autonomous Analysis Orchestrator

**Public title:** A Depth-First Autonomous Analyst That Generates Its Own Follow-Up Questions

**Pitch:** A pure-orchestrator skill that turns plain-English questions into reproducible, audited SQL analyses with charts, structured findings, and *automatically-generated follow-up hypotheses*. Scores every finding on Impact × Surprise × Gaps; high-scoring findings spawn depth-dive analyses immediately. SQL traceability is enforced as a contract — every number in every report is runnable.

**Status:** In production internally. Has executed dozens of multi-hypothesis analyses end-to-end.

**Confidentiality:** Don't name the internal skill, don't quote specific report titles or panelist counts, don't show actual `wmt-dsi-cally...` FQNs.

### What it does

User asks a research question ("are reward economics aligned with panelist engagement?"). The orchestrator:

1. **Loads context** — domain rules, table catalog, prior backlog of explored hypotheses.
2. **Pre-processes** — auto-corrects state-name typos, sharpens vague terms, normalizes denominators.
3. **Executes a loop** — per idea: pre-dispatch checkpoint → dispatch a sub-agent in an isolated context → post-dispatch validation → REFLECT scoring → optional depth dive.
4. **Generates new ideas** when the backlog runs dry — collects gaps, surfaces under-explored areas, generates candidates, deduplicates, queues the best 10.
5. **Resumes from crashes** — every state hop is persisted; a `resume` command detects mid-flight crashes and validates partial reports before continuing.
6. **Wraps up** with a session summary and a rebuilt INDEX across all dates.

Every finding produces a directory with: narrative report, structured findings JSON, full executable SQL, per-step CSVs, branded charts.

### The REFLECT scoring engine

After each idea completes, findings get scored:

**Score = Impact × Surprise × Gaps**

| Factor | Values |
|---|---|
| Impact | 1 (small population), 2 (medium), 3 (large) |
| Surprise | 1 (expected), 2 (somewhat unexpected), 3 (contradicts assumptions) |
| Gaps | 0 (actionable) or 1 (unanswered "why?") |

If score ≥ 4, the orchestrator **immediately** generates a depth-dive idea and executes it before moving to the next top-level idea. Depth chains until findings are directly actionable, no additional tables would help, or `max_depth` hits.

This is the difference between "AI analyst that answers one question" and "AI analyst that *investigates*." Most tools stop at the first interesting result. This one drills.

### Why it exists

Most "AI analyst" tools answer one question at a time. Treating analysis as a *systematic exploration problem* — where every finding spawns hypotheses, every hypothesis becomes a queued analysis, every analysis is validated — produces a compounding knowledge base over dozens of completed analyses. The depth-first REFLECT loop is what turns "fast answers" into "real research."

### Key design decisions

**Pure orchestrator pattern.** The skill never runs Bash directly. Every analytical idea is dispatched to a sub-agent with its own isolated context. Three benefits: (1) large SQL results from one idea don't pollute another's reasoning, (2) sub-agents execute without CLI safety prompts because the orchestrator stays Bash-free, (3) crash recovery is trivial because all state lives in JSON files.

**SQL traceability as a hard contract.** Every analysis produces an `execution.json` with complete copy-paste-runnable SQL for every query. Post-dispatch validation enforces it — no ellipses, no pseudo-code, must contain fully-qualified table references, must be longer than 50 characters. Violations are blocking errors. Every number in every report is traceable back to runnable SQL.

**Session state in JSON, not memory.** Crash recovery is a primary feature, not a bolt-on.

**INDEX rebuilt from scratch every session.** Prevents stale dashboards. The cross-session view always reflects current state.

**Static context as a RAG replacement.** Domain rules + table catalog + schema get passed *in full* to every sub-agent dispatch. The context platform makes this cheap (compiled JSON, no retrieval gymnastics).

### The audit + fix ecosystem

The orchestrator composes with two sibling skills:

- **Audit** — a 6-layer validator running across SQL schema, SQL logic, interpretation, prose arithmetic, cross-analysis consistency, and evidence-chain completeness. Verdicts: PASS / WARN / FAIL.
- **Fix** — consumes audit findings and remediates in dependency order. SQL rewrite → re-execute → replace CSV → recalculate. Narrative rewrite for causation overreach. Chart regeneration. Snapshots originals before modifying. Verifies every edit landed by re-reading.

Each skill does one thing. Compose them and you get: orchestrator produces, audit validates, fix remediates.

### The hard parts

**Depth-first vs. breadth-first.** Naive backlog execution does everything breadth-first. REFLECT scoring + immediate depth-dive generation was the unlock for actually-useful investigation — but tuning the scoring rubric took multiple iterations. Too eager → infinite depth chains. Too conservative → never drills.

**Idea deduplication.** Auto-generated follow-ups duplicate existing backlog items constantly. Dedup runs over title similarity + tag overlap + content embedding distance. Hard to tune without false positives.

**The SQL traceability contract.** The first version trusted the LLM to include SQL "more or less". Half the time it produced "same as step 1" or "see above." Making it a blocking validation gate forced the contract: real SQL or no advancement. Quality went up overnight.

**Crash recovery without re-running expensive queries.** Resume has to detect "this idea was mid-execution when we crashed" vs. "this idea was fully done, just not marked completed" — and not re-bill BigQuery for queries that already ran.

### How I evaluated it

- **Findings actionability rate:** % of REFLECT-scored findings that lead to a concrete next action (vs. "interesting, but so what?").
- **SQL traceability compliance:** % of reports passing the SQL contract on first dispatch. Tracks LLM behavior over prompt iterations.
- **Depth-dive yield:** when depth dives fire, do they produce findings that the top-level analysis missed? Yes, ~70% of the time.
- **Audit pass rate:** % of generated reports that pass the 6-layer audit on first run. Increases over time as the orchestrator's output prompts get refined.

### What I'd do differently

- **Multi-modal findings.** Currently every finding ends up as text + CSV + chart. Some questions are better answered with a map or a flow diagram.
- **Adaptive REFLECT weights.** Impact × Surprise × Gaps is one-size-fits-all. Different research domains weight these differently.

### Stack

Python, MCP context injection, sub-agent dispatch via Task tool, JSON-as-state-machine, deterministic SQL traceability contracts, 6-layer audit validator, autonomous remediation skill, matplotlib for branded charts, BigQuery execution with cost controls.

### Links

- Demo: [FILL — sanitized walkthrough of one multi-hypothesis session]
- Architecture diagram: [FILL]
- Repo: [FILL]

---

---

## 6. Per-Dashboard Semantic Layers Accessible Through Business-Team CLI Agents

**Public title:** Per-Dashboard Semantic Layers — Bringing Governed Analytics Into the CLI Where Business Users Already Work

**Pitch:** A new initiative: instead of one monolithic semantic layer for the whole warehouse, build *one semantic layer per dashboard I support*, and expose each layer through the coding CLI agent that business and product teams already use. The result: a PM asking "what was last week's completion rate" gets the answer inline in their CLI, against a governed model scoped exactly to the dashboard they care about — no switching tools, no asking an analyst, no risk of querying the wrong source.

**Status:** In active development.

**Confidentiality:** Don't name the dashboards, the consuming teams, the CLI agent product, or the internal Cube model names. Describe the *pattern* and the *why*.

### What it does

Each dashboard I'm responsible for gets its own Cube.js semantic layer — scoped narrowly to that dashboard's metrics, dimensions, and access patterns. The layers are registered with the coding CLI agent that business and product teams already have installed. A user types `> What was last week's completion rate by region?` in their CLI, the agent routes to the right semantic layer, executes a governed query, and returns the answer inline with the underlying query for auditability.

### Why it exists

Two problems with how business teams interact with analytics today:

1. **Tool-switching tax.** Business users live in their CLI, Slack, and Looker. Getting an analytics answer means context-switching to a dashboard, navigating to the right view, applying filters, sometimes pinging an analyst. Most never bother.
2. **Governance vs. accessibility tradeoff.** Raw warehouse access is powerful but ungoverned — users can write a wrong query and trust the result. Dashboards are governed but limited to what's been pre-built. A semantic layer per dashboard, accessible inline in the CLI, gives you both: the user asks in natural language, the answer is governed by the same model that powers the dashboard, and they never leave their tool.

The per-dashboard scoping matters because **monolithic semantic layers don't work for self-serve**. A unified model for the whole warehouse has too many measures and dimensions for an LLM to ground correctly; queries take forever to validate; coverage gaps multiply. One layer per dashboard means the LLM has a small, focused surface to reason over — and the user gets answers that are *guaranteed consistent* with the dashboard they're looking at.

### Architecture

```
Business user's CLI agent (the fork of Claude Code business teams already use)
                  ↓
        Semantic-layer router (which dashboard does this question belong to?)
                  ↓
    ┌─────────────┼─────────────┐
    ↓             ↓             ↓
Dashboard A    Dashboard B    Dashboard C
Cube model     Cube model     Cube model
    ↓             ↓             ↓
    └─────────────┼─────────────┘
                  ↓
              BigQuery
                  ↓
        Inline answer in CLI + underlying SQL for audit
```

Each per-dashboard Cube layer is informed by the central context-engineering platform (Project 1) — same source-of-truth for schema, joins, and domain rules — but the model is *narrowly scoped* to the dashboard's domain. Less surface area, less LLM confusion, better grounding.

### Key design decisions

**One layer per dashboard, not one layer per data source.** The unit of governance is the dashboard, not the warehouse. A dashboard is what users already trust; users already understand what questions it can answer. The semantic layer behind it should match that scope exactly.

**CLI as the access surface, not a new web app.** Business teams already have a coding CLI installed for other reasons. Adding semantic-layer access *into the tool they already open* removes every adoption barrier. Versus standing up yet another UI nobody opens.

**Inline answers with the underlying query exposed.** Every CLI response includes the generated SQL. Users who want to verify can; users who don't want to don't have to. The trust gradient is visible.

**Same context-platform substrate as everything else.** The per-dashboard models pull schema, joins, and domain rules from the central context platform (Project 1). No duplicated context engineering. Add a new dashboard, generate its scoped model from the substrate.

### The hard parts

**Routing across dashboards.** A user might ask a question that could be answered by Dashboard A *or* Dashboard B with slightly different numbers. The router has to pick — or, when genuinely ambiguous, ask. Solved with intent classification over dashboard descriptions plus an explicit "do you mean the X dashboard or the Y dashboard?" clarification path when confidence is low.

**Keeping per-dashboard models consistent with the central source of truth.** When the central context platform updates a table definition or a domain rule, every per-dashboard model needs to see it. Wired the per-dashboard Cube generators to pull from the central compiled-context artifacts at build time, so updates propagate.

**Knowing when to surface "the dashboard already shows this."** Some user questions are literally answered by an existing chart on the dashboard. The right answer is sometimes a link to the chart, not a re-derived query. The router has a path for that.

### How I evaluated it

[In development. Planned metrics: adoption (number of CLI queries per dashboard per week), trust (% of queries where users accept the answer without checking the SQL), accuracy against a held-out gold set of dashboard-specific questions.]

### What I'd do differently

[Too early to say — capture as the system matures.]

### Stack

Cube.js (per-dashboard models), the central context-engineering platform as the substrate (Project 1), a coding CLI agent product as the access surface, BigQuery as the execution target.

### Links

- Architecture diagram: [FILL]
- Demo: [FILL — once a dashboard is live, record a sanitized CLI session]

---

# P2 — Range and depth

---

## 7. JResolutionAgent — Autonomous Ticket Resolver for a Data Team

**Public title:** JResolutionAgent — End-to-End Autonomous Resolution of Data-Stewardship Tickets

**Pitch:** A fully autonomous data-steward agent that resolves analytics tickets from triage through CSV delivery — zero human checkpoints, 10-retry self-healing budget, hierarchical context management inspired by Git Context Controller. Handles UPC-list panelist pulls, demographic enrichment, feasibility queries, database health checks, complex investigations.

**Status:** In production. Resolves real tickets end-to-end.

**Confidentiality:** Don't name the internal ticket project, don't quote the BDV ticket IDs, don't expose worklog formats verbatim.

### What it does

A ticket lands. The agent runs:

1. **Triage** — six gates to decide if this is a real, actionable, data-task ticket worth working.
2. **Understand** — gathers context via MCP tools (schema, joins, domain rules, similar past queries) with complexity-adaptive depth. Parses attachments. Assigns confidence.
3. **Plan** — numbered query decomposition (Q1, Q2, ...) with tables, joins, dependencies, expected shape.
4. **Execute** — per-query loop: dry-run → execute → validate → self-heal. 10-retry budget across the session.
5. **Deliver** — summarizes results, lists CSVs, updates the manifest.

### Why it exists

A meaningful chunk of an analytics team's time goes to repetitive ticket work: UPC list → panelist count, demographic breakdown, feasibility check for a survey design. The work is technical but pattern-heavy. An agent that knows the schema, the join paths, the domain quirks, and has a self-healing retry budget can resolve these end-to-end while the team focuses on actual research.

### Architecture highlights

**Hierarchical context management inspired by GCC (Git Context Controller).**

```
# Worklog: TICKET-XXXX

## Summary (ALWAYS READ FIRST ON RESUME)
Status, complexity, ask, progress, key findings, next action, blockers

## Triage / Understanding / Plan / Execution Log / Delivery
[Detail sections, read on-demand]
```

The Summary is the entry point on resume — coarse metadata first, drill in only if needed. Mirrors how good retrieval systems work: cheap-to-read summary on top, expensive details on demand.

**Investigation Branches for unexpected results.** When a query returns 0 rows or surprising numbers, the agent opens an investigation block with an explicit hypothesis, runs 5-minute exploratory queries, documents findings, and applies learnings to subsequent queries. Investigation branches are *never compressed* in rolling context compression — they encode debugging knowledge that's worth keeping.

**Synthesis Checkpoints between dependent queries.** When Q2 depends on Q1 results, the agent explicitly documents the data dependency:

```
### Synthesis: Q1 → Q2
From Q1: Top 5 states: TX, CA, NY, FL, PA
Feeds into Q2: hardcoded into WHERE clause
```

**Self-healing retry patterns** with capped budgets per failure mode:

| Failure | Retry budget | Action |
|---|---|---|
| Syntax error | 3 | fix SQL, re-run |
| Timeout | 2 | tighter date filter |
| 0 rows | 3 | Investigation Branch → adjust |
| Budget exhausted | — | partial delivery |

**State machine.** A manifest JSON is the machine-readable source of truth (queries, status, retries, dependencies, row counts, bytes scanned). Worklog markdown is the human-readable narrative. Both updated atomically.

### The hard parts

**Knowing when to stop retrying.** Open-ended retry budgets produce runaway agents. Per-failure-mode caps + a session-level budget were the right shape, but tuning the caps took watching real ticket failure modes.

**Investigation Branches without becoming a research project.** The agent could chase an interesting "0 rows" result for hours. Capped exploratory queries at 5 minutes each and bounded the branch depth.

**Append-only audit trail through query supersession.** When Q1's initial result turns out wrong (user feedback corrects a misunderstanding), Q1 is marked `superseded` but kept for audit. Q2 supersedes it. The whole chain stays in the manifest. Tracing what the agent originally believed vs. what it ended up delivering becomes trivial.

### A real example (sanitized)

Initial assumption: column X empty → return all qualified rows. User feedback: "9 should be excluded (opted out of video)." Investigation: column X is 100% null because opt-in is a *panelist-level preference*, not a survey answer. Solution: Q2 joined the panelist preference table to filter on the opt-in flag. Result: correct count (vs. original count), with Q1 marked superseded but kept for audit.

This is the agent self-correcting on user feedback with a full audit trail.

### How I evaluated it

- **End-to-end resolution rate:** % of triaged tickets that close without human intervention.
- **Self-healing success rate:** % of failed queries that succeed within the retry budget.
- **Audit completeness:** every closed ticket has a complete manifest + worklog + CSVs. Validated by spot-check.

### What I'd do differently

- **Cross-ticket learning.** Each ticket is currently self-contained. A cross-ticket memory layer would let the agent recognize patterns ("this is the third UPC-list ticket for the same category — apply the same join path").
- **User-facing "why" explanations.** The agent delivers CSVs but doesn't always explain *why* a count differs from what the requester expected. A "delta explanation" step would close that loop.

### Stack

Python, MCP for context injection, hierarchical context management (Summary-on-top pattern), JSON-as-state-machine, BigQuery execution with cost controls, retry budget bookkeeping per failure mode, append-only audit trail with query supersession.

### Links

- Demo: [FILL — sanitized walkthrough of a real ticket resolution]
- Architecture diagram: [FILL]

---

## 7. Text-to-SQL Copilot (Public Demo Version)

**Pitch:** A self-serve analytics copilot that turns natural language into executable BigQuery SQL — grounded in schema and historical query patterns, with guardrails and eval coverage. The publicly-deployable cousin of the internal `validated SQL` flagship.

**Status:** Live demo at https://sql-rag-frontend-simple-481433773942.us-central1.run.app

**Note on framing:** This is the *public version* — generic schema, public dataset, simplified architecture compared to the internal flagship (which has the full validate-and-retry loop, MCP-distributed context, etc.). On the website, position this as "live demo of the pattern; the production version at Walmart adds X, Y, Z and ships at scale."

### What it does

[Same as previous version — see prior file structure for full content. Keeping concise here to avoid repetition.]

Type a question in English. It returns SQL, runs it, shows the result with a one-line explanation. If ambiguous, asks a clarifying question.

### Architecture

React frontend, FastAPI on Cloud Run, hybrid retrieval (FAISS + BM25 over schema + query corpus), Gemini for query synthesis + GPT for explanation (split intentionally), BigQuery execution with dry-run cost gates, Firestore for sessions.

### The hard parts

- **Schema grounding without flooding context** — retrieval picks 5–8 most relevant tables, not all of them.
- **Join validation** — LLMs hallucinate joins. Built a join-key validator.
- **Cost-aware execution** — dry-run estimator before execute.
- **Generation/explanation split** — single-model conflated; two-model fixed explanation drift.

### How I evaluated it

Hand-curated eval set of ~150 questions with gold-standard SQL. Three metrics: execution accuracy, schema correctness, cost overhead. 95% accuracy figure is from the latest run.

### Stack

Python, FastAPI, React, BigQuery, FAISS, BM25, OpenAI embeddings, Gemini, GPT-4o, Cloud Run, Firestore, Docker.

### Links

- Live demo: https://sql-rag-frontend-simple-481433773942.us-central1.run.app
- Architecture diagram: [FILL]

---

## 8. Text-to-Looker Copilot (Public Demo Version)

**Pitch:** Natural language → Looker queries. Same idea as text-to-SQL but for teams whose source of truth is LookML, not raw warehouse SQL.

**Status:** Live demo at https://text-looker-sql-e8ab5918bcfc.herokuapp.com

[Keep prior content — single-shot Gemini with structured JSON output against LookML metadata; FAISS over LookML field labels; respects Looker's Explore-based join model.]

### Stack

Python, FastAPI, React, FAISS, OpenAI embeddings, Gemini, Looker API, Heroku.

### Links

- Live demo: https://text-looker-sql-e8ab5918bcfc.herokuapp.com

---

## 9. Voice Agent Debate Platform

**Pitch:** Voice-first platform where two AI agents debate a topic from opposing viewpoints — speech-to-text in, agentic reasoning + tool use in the middle, text-to-speech out, all in real time.

**Status:** Live demo at https://doctor-simulation-ab9928fd6e67.herokuapp.com

**Note:** The `doctor-simulation` URL slug is a legacy from an earlier prototype. Consider re-deploying under a cleaner URL before featuring prominently. [FILL — re-deploy?]

[Keep prior content — Whisper in, multi-agent orchestration with shared scratchpad + turn-taking, TTS out. Hard parts: turn-taking that doesn't feel like tennis, interruption handling, latency stacking.]

### Stack

Python, FastAPI, WebSockets, OpenAI Whisper, OpenAI TTS, GPT-4o, React, Heroku.

### Links

- Live demo: https://doctor-simulation-ab9928fd6e67.herokuapp.com

---

## 10. FTI Consulting RAG Proposal Generator

**Pitch:** RAG-powered proposal-writing assistant built during my UChicago MS ADS capstone with FTI Consulting. Won Best in Show.

**Status:** Capstone, 2024. Archived but documented.

**Confidentiality:** FTI capstone — corpus, client names, internal proposal structure stays private. Architecture pattern + the award are fine.

[Keep prior content — RAG over past proposals + bios + case studies, generation with strict citation, hard parts around citation faithfulness and domain language. FILL the eval methodology from your capstone slides.]

### Stack

Python, LangChain, OpenAI, FAISS or Pinecone (verify), React, [FILL — deployment].

### Links

- Capstone deck: [FILL]
- Award: UChicago MS ADS Capstone 2024, Best in Show

---

## 11. AI Job Search Automation

**Pitch:** End-to-end agent system that runs my job search: scrapes Gmail for postings + recruiter messages, extracts structured data with GPT, surfaces relevant contacts at target companies via MCP, tailors resumes per role.

**Status:** Actively used by me, daily.

[Keep prior content — multi-agent (Gmail scraper, JD extractor, contact finder, resume tailor, outreach drafter), markdown as storage for git+Obsidian, jittered LinkedIn calls to avoid bot detection.]

### Stack

Python, Claude Code, custom MCP servers (LinkedIn, Gmail, job tracker), markdown as storage, Obsidian as reader.

### Links

- Repo: [FILL — private? if so, "available on request"]

---

# P3 — Builder portfolio (range signal)

---

## 12. Ralph Loops

**Pitch:** Autonomous AI dev framework for Claude Code with intelligent exit detection, rate limiting, and circuit breaker. 566 tests, 100% pass rate.

[FILL out the architecture once you've reviewed the repo. Capture: what made exit detection hard, what circuit-breaker thresholds you picked and why, how the test pyramid is structured.]

### Stack

[FILL]

### Links

- Repo: [FILL]

---

## 13. Join Discovery Engine

**Pitch:** ML tool that auto-discovers valid join relationships across BigQuery tables using FAISS embeddings, statistical sampling, and LLM reasoning. Turns "which two columns can I join on" from a 20-minute scavenger hunt into a one-call answer.

[Keep prior content — column profiling, candidate generation via embeddings + value-distribution similarity, statistical sampling validation, LLM semantic judgment as final gate.]

### Stack

Python, FAISS, OpenAI embeddings, GPT-4o, BigQuery, pandas.

### Links

- Repo: [FILL]

---

## 14. Voice Journal

**Pitch:** AI-powered journaling app with voice input, theme-aware reflections, and goal tracking.

[FILL — your motivation, the theme-extraction approach, deployment status.]

### Stack

Next.js, FastAPI, OpenAI Whisper, [FILL — DB?].

### Links

- Repo: [FILL]
- Demo: [FILL — if deployed]

---

## 15. Market Dashboard (Kalshi + Odds API)

**Pitch:** Live data pipelines for Kalshi prediction markets and Odds API with FastAPI governance, React dashboards, and BigQuery analytics.

[FILL — motivation, ingestion pattern, governance layer.]

### Stack

FastAPI, React, BigQuery, [FILL — scheduler?].

### Links

- Repo: [FILL]

---

## 16. Smart Scraper

**Pitch:** Dynamic apartment scraping with auto-generated schemas and multi-fallback strategies. 100–1000x faster than pure-LLM extraction.

[Keep prior content — deterministic by default, LLM as fallback, designed to plug into AI Job Search for "where would I live near this office".]

### Stack

Python, Playwright or BeautifulSoup [FILL — which?], GPT for fallback.

### Links

- Repo: [FILL]

---

# Cross-cutting themes worth a home-page section

These show up across multiple projects and would land well as a short "How I think about building" section on the home page.

### On context engineering

Every multi-agent system above depends on a shared, validated, auto-maintained context layer. Without it, every new agent re-discovers the same schema and drifts silently when sources change. With it, new agents become thin wrappers, not duplicated infrastructure.

### On evals

Every agent system above ships with an eval harness. An agent without measurement isn't shipped. Hand-curated gold sets > synthetic evals for anything user-facing. The flagship NL→SQL system went from 60% → 95% accuracy by adding a validate-and-retry loop on top of generation.

### On retrieval

Hybrid (dense + sparse + reranker) beats either alone for any non-trivial corpus. Schema and metadata beat raw chunks when the data has structure. For warehouse work, compiled JSON for hot paths beats RAG for cold paths.

### On agent design

Pure orchestrators that never run Bash directly compose better. Tool granularity matters: one coarse tool fails, three or four composable ones compose into agentic workflows. State in JSON files, not in memory. Crash recovery as a primary feature, not a bolt-on.

### On parallel architectures

Some questions need two answers compared. The dual-path orchestrator (semantic layer + raw SQL with reconciliation) is the only way I've found to get governance *and* completeness without forcing the user to pick. The reconciliation classifier is the keystone — without it, two answers is just confusion.

### On self-improving systems

The auto-update loop on the semantic layer is what makes the whole stack interesting: every coverage gap users hit is a signal, not a problem. Cluster gaps → synthesize candidate measures → prove equivalence → draft PR. The numerical equivalence gate is what makes "AI generates PRs" safe.

### On personal vs. work projects

The pattern that works in a personal project usually works at work — with two changes: (1) confidentiality discipline around data and internals, (2) eval coverage you can defend to a stakeholder. The AI Job Search system above uses the same MCP-orchestrated agent pattern as the Walmart ticket worker.

---

# Open questions before publishing

1. **CP Platform / MCP Server / Hybrid / Semantic Layer / Analytics Orchestrator (Projects 1–5):** these are the headliners but the most confidentiality-sensitive. Confirm the manager-test framing per project. Decision: do we publish all five, or pick the top 2–3? Recommendation: publish all five — they tell a coherent story about platform thinking. But surface the question to your manager first if you want explicit cover.
2. **The flagship `cp_generate_validated_sql` tool vs. the public text-to-SQL demo (Project 7):** these are different things and the page should make that clear. The demo is "the pattern, live"; the flagship is "the production version at scale." Confirm framing.
3. **Voice Agent URL slug:** re-deploy under a non-`doctor-simulation` URL? Yes/no.
4. **Repo visibility:** which personal projects are public on GitHub vs. "available on request"? Make a call per project.
5. **Architecture diagrams:** every P1 project needs one. Pick a format and commit (draw.io, Excalidraw, hand-drawn).
6. **First article to publish:** I'd start with **CP Platform (Project 1)** because it's the substrate everything else sits on — once that article exists, the next four can link back to it for the shared architecture context. Alternative: lead with the **Hybrid Orchestrator (Project 3)** because it's the most novel pattern and likely the best recruiter-bait. Your call.
7. **New projects you mentioned:** the per-dashboard semantic layers accessible through business-team CLI agents and the CP Hybrid skill on YB — these are either already covered by Projects 3 and 4 above (rephrased into their current form), or they're new variants. Confirm: are these new instances of the same patterns, or genuinely new architectures worth their own sections?

---

# Hand-off to website repo

When content is locked:

1. Add a `/blog` or `/projects/{slug}` route in `app/` with MDX rendering.
2. One MDX file per project under `content/blog/` (currently empty).
3. Update `components/SelectedWork.tsx` to use the priority ranking above — promote Projects 1–5 to hero tiles, rest as secondary.
4. Update `components/AboutSection.tsx` to match the LinkedIn About voice (context engineering + multi-agent platforms + evals).
5. Strip dead nav links (`Blog`, `Portfolio`) until the routes exist.
6. Add architecture diagrams to `public/images/projects/`.
7. Deploy.
