---
title: "Context Engineering for Multi-Agent Analytics — Why Your Agents Need a Substrate"
slug: context-engineering-platform
date: 2026-05-30
author: Kanu Madhok
summary: "Most multi-agent systems fail not because the agents are bad, but because the context layer rots. Here's how I built a self-maintaining context platform that became the substrate for every analytics agent on top of it."
tags: [ai-agents, context-engineering, rag, mcp, analytics, platforms]
status: draft
---

# Context Engineering for Multi-Agent Analytics — Why Your Agents Need a Substrate

When a production multi-agent system breaks, the agents get blamed first.

The reasoning was wrong. The tool calls were brittle. The prompts drifted. The retrieval missed.

After building seven interlocking agents for analytics work — autonomous analysts, ticket resolvers, semantic-layer gap-fillers, dual-path orchestrators, KPI monitors, business-team copilots — I think that's backwards. The agents are usually fine. What rots, quietly, is the context layer underneath them.

Schemas drift. Domain rules change. The "active user" definition gets updated in one place and not the others. Three agents start producing subtly wrong numbers and nobody notices for weeks, because each agent is technically doing what it was told. The agent isn't broken. The substrate is.

This post is about the substrate I built to fix that. There's no shiny UI, no demo video. But every interesting agent I've shipped sits on top of it, and none of them work without it.

## The problem

You have an analytics warehouse. Dozens of tables. Over a thousand columns. Business rules about what counts as an "active" user, which timestamps are reliable, which joins are valid, what each enum value actually means. Some of this is documented in a wiki. Some is in people's heads. Some is in old Slack threads. Some was written down once and is now wrong because the schema changed three weeks ago.

You want to build agents on top of this warehouse — agents that can answer natural-language questions, resolve tickets, monitor KPIs, generate reports. You quickly hit three problems:

**One: every agent re-discovers the same context.** Each new agent re-implements schema lookup, join inference, business-rule encoding. You write the same retrieval logic five times. The fifth one is worse than the first because the institutional memory of why-this-is-hard is gone.

**Two: the context goes stale.** Someone renames a column upstream. None of the documented context updates. Agents keep producing answers that *look* right but reference a column that no longer exists — or worse, a column that exists but now means something different. The silent failures are the ones that hurt.

**Three: agents can't compose.** Without a shared, versioned, validated context layer, two agents looking at the same question produce two different answers, and there's nothing to reconcile them against.

The obvious move is to give each agent its own copy of the context. That just gets you the silent-drift problem at five times the scale. What actually works is to centralize the context, automate its maintenance, and make it boring to consume.

## The platform — architecture

Four layers, top to bottom, dependency direction always inward.

```
┌─────────────────────────────────────────────────────────────┐
│  ACCESS LAYER                                                │
│  MCP server (12+ tools)  │  Web UI  │  Python SDK            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  KNOWLEDGE LAYER                                             │
│  Vector index (RAG)  │  SQL knowledge base  │  Compiled JSON │
│  In-memory schema  │  Join graphs  │  Domain rules           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  INGESTION & TRANSFORMATION LAYER                            │
│  schema extractor → diff engine → doc generator              │
│  → chunker → embedder → context compiler                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  QUALITY LAYER                                               │
│  Validators: schema, enums, joins, table inventory, DDL      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       └──▶ External: warehouse, DDL repos, query history
```

The downward arrows are the build pipeline. The upward arrows are how consumers access it. Consumers depend on the platform; the platform depends on the data sources; never the reverse.

Nothing about this topology is novel — it's standard knowledge-engineering layering. What makes it work in practice is the *maintenance discipline* baked into it, which I'll get to.

## The source of truth

Three files, three layers of trust.

**Human-curated markdown** is the source of truth. Two files — one describing tables, one describing domain rules — live in version control. Written by humans, reviewed by humans, treated as the canonical reference for everything else. Anything that disagrees with these files is wrong by definition.

**Machine-generated schema snapshot** is the live reflection of the warehouse, pulled daily from `INFORMATION_SCHEMA`. Ground truth for *what actually exists right now*.

**Compiled artifacts** — JSON for hot paths, vector indexes for RAG, knowledge graphs for multi-hop join resolution — are derived from the markdown and the schema snapshot. The pipeline regenerates them. Nobody edits them by hand. If something looks wrong in a compiled artifact, you fix the markdown source and rebuild.

The reason this matters: "where do I change X?" is trivially answerable. Updating a business rule? Edit the markdown. Adding a new table? It'll show up in the next pipeline run, and the diff engine will flag that the markdown is missing. There's exactly one place to make any kind of change, and the system tells you what's stale.

## The maintenance loop — what keeps it from rotting

Most context systems work fine on day one and rot by day ninety. The platform's whole job is to fight that automatically.

**A diff engine** runs daily, comparing today's schema snapshot to yesterday's. New tables, dropped tables, changed column types, new columns on existing tables — all flagged.

**A doc generator** picks up the diff and regenerates documentation for any table that changed. It uses a tiered LLM fallback across multiple providers so doc regeneration never dies on a single outage or rate-limit. Generated docs land in a v2 directory; a human reviews and decides whether to promote them into the curated markdown.

**Five validators** run daily and produce a structured report:

| Check | What it does |
|---|---|
| Schema validator | Live warehouse columns vs. documented columns — flags missing, added, type-changed |
| Enum validator | Documented enum values vs. `SELECT DISTINCT` results from production |
| Join validator | Executes every documented join path to confirm it still works |
| Table inventory validator | Counts tables in scope vs. documented tables |
| DDL cross-reference validator | Compares warehouse schema against DDL stored in engineering repos |

Validator output feeds back into the next doc-generator run for auto-correction. Drift triggers documentation; documentation triggers re-embedding; re-embedding updates the RAG index. The loop closes itself.

The point isn't the validators. It's that I never have to remember to maintain this. The pipeline does. My job is to fix whatever the validators flag, not to remember what to check.

## How agents actually consume it

Three access patterns, because different consumers want different things.

**For agents: an MCP server.** Most consumers are LLM agents — the autonomous analyst, the ticket resolver, the dual-path orchestrator, the semantic-layer gap-filler. They hit a single MCP server with roughly a dozen tools across five categories:

- **Read-only context tools** — schema lookup, join paths, domain rules, accumulated cross-analysis knowledge. Zero-latency in-memory hits from the compiled JSON.
- **Execution tools** — write the proposed SQL to disk *before* running it (provenance guarantee), then execute with a generous timeout and a structured result.
- **Discovery / RAG tools** — RAG Q&A over the docs corpus, semantic search over historical queries.
- **Reporting workflow tools** — scaffold report directories, build deterministic execution manifests, generate branded charts, validate output contracts.
- **Maintenance tools** — trigger pipeline refresh, rebuild caches.

Plus the flagship: a full natural-language → validated SQL → execution pipeline. One model generates SQL, another validates via function-calling (schema checks, join verification, domain-rule enforcement, dry-run), then executes. More on this in a minute — it's the single most-used thing the platform exposes.

**For humans: a Flask web UI.** A local web app with a toggle between "ask about data" and "find SQL." RAG-powered Q&A with collapsible source citations and an audit trail. Mostly for analysts sanity-checking what the agents are seeing.

**For programmatic use: a Python SDK.** Power users build their own workflows on the platform's primitives without going through MCP.

All three surfaces read from the same compiled artifacts. One source of truth, three ways to reach it.

## The flagship: natural language → validated SQL

This tool gets called more than anything else, and it taught me the most about why "just ask an LLM for SQL" doesn't survive in production.

The first version was the obvious one: take the question, retrieve relevant schema, ask an LLM for SQL, run it. Accuracy landed around sixty percent. Not catastrophic, but not trustworthy. The model would hallucinate joins, mis-specify aggregations, get filter logic subtly wrong. Users couldn't tell when it was wrong, so they didn't trust *any* of the answers — which is the worst place a production tool can sit.

The fix wasn't a better generation prompt. It was a separate validation loop.

The architecture now is two models doing two jobs:

1. **Model A generates SQL** from RAG context — roughly 150K characters of schema, domain rules, and similar past queries.
2. **Model B validates it via function-calling** — schema existence checks, join verification against documented join paths, domain-rule enforcement, a BigQuery dry-run for cost and correctness. When validation fails, the validator returns a structured error and the generator gets another turn with that error as input. Capped at a small number of turns.
3. **Model B executes** the validated SQL.

The output is the SQL block, a validation summary (turns used, tools called, fixes applied, valid/executed flags), an execution preview, and a full timing breakdown.

Accuracy went from sixty percent to ninety-five on a hand-curated eval set of about 150 real user questions with gold-standard answers.

Three lessons from building this:

- **Generation and validation should be separate model calls.** One prompt trying to do both produces neither well.
- **Function-calling is what makes validation real.** It forces the validator to ask structured questions — does this column exist? is this join documented? what's the dry-run cost? — instead of vibing on SQL correctness.
- **Cap the retry loop.** Without a cap, a stubborn-wrong model burns latency and cost chasing a bad approach. With a cap, failures surface honestly.

End-to-end the tool runs in about sixty seconds and replaces ten-plus minutes of hand-written SQL per question.

## The hard parts (the lessons I paid for)

Five things that took multiple iterations.

**Doc chunking.** Naive markdown chunking by paragraph produced chunks that lost critical context — a column description without its table, a domain rule without the metric it modified. I ended up writing a chunker with eight distinct semantic section types so each chunk is self-contained: a chunk about a table includes the table name, a chunk about a metric includes the table it lives on, a chunk about a join includes both sides. Retrieval quality jumped immediately, and the LLM stopped getting confused about which table it was looking at.

**Table-name resolution.** Users and agents ask for "the rewards table." There is no table literally called that. I built one resolution chain — strip the fully-qualified prefix, try exact match, strip a common prefix, try alias lookup, try singular/plural variants, try partial substring match — and called it from everywhere. One function, all callers route through it. Saves the LLM from needing to know the exact internal naming convention.

**Lazy cache invalidation.** Three caches (schema, joins, domain rules) load lazily on first access and persist for the process lifetime. First call costs about 5–10ms to parse the JSON; everything after is a zero-latency dict read. The daily pipeline invalidates the underlying files; a manual `refresh` tool invalidates on demand. I got this wrong once and served stale schema for half a day — added an explicit cache-bust step in the refresh pipeline after that.

**Provenance for executed SQL.** With dozens of analyses running, it's easy to lose track of which query produced which CSV. The fix: write every SQL string to disk *before* the warehouse touches it, log the BigQuery job ID, and expose a `build_execution` tool that compiles the per-query logs into a single manifest after the fact. Every number in every report traces back to runnable SQL.

**Layering RAG and validation.** RAG alone is fast but unreliable. Structured tool calls alone are reliable but slow. Layering them — RAG for "what does the user probably mean," structured tools for "is this definitely right" — got the speed of the first with the precision of the second. This pattern shows up in every agent built on the platform.

## How I evaluated it

Four metrics actually matter for this kind of platform.

- **Schema accuracy.** The daily validator catches drift; the PR rate from auto-regeneration is the proxy for how much drift is happening. If it spikes, something upstream is moving faster than the team realizes.
- **Retrieval quality.** A held-out set of warehouse questions with known-correct answers, scored on RAG accuracy and citation faithfulness. Re-run on every chunker or embedder change.
- **End-to-end latency.** Target: sub-second for schema/join lookups, single-digit seconds for RAG, sub-30s for end-to-end execution. All met after the in-memory cache redesign.
- **Downstream adoption.** The realest one. Number of agents built on the platform vs. number of agents doing their own context discovery. The first number grew steadily; the second went to zero. Once the platform existed, nobody wanted to re-invent it.

## What I'd do differently

Three things, in priority order.

**Move ingestion to event-driven.** The pipeline runs on a daily cron today, so drift can take up to twenty-four hours to detect. Wiring it to upstream schema-change events would compress that to minutes — worth doing as soon as the underlying event stream exists.

**A real feedback loop into RAG ranking.** Thumbs up/down per answer, fed back into chunk ranking. Right now RAG quality improves through manual prompt iteration. Letting the system learn from real usage would compound.

**Per-agent cost telemetry.** It's harder than it should be to attribute LLM spend back to which downstream agent is generating the load. Per-caller cost tags would make optimization decisions much easier.

## The takeaway

If you're building multi-agent systems on top of a real data warehouse, the agents are the visible part — but the substrate decides whether they still work in six months. Context rot kills more agentic systems than bad prompts do. It's slower, quieter, and harder to debug after the fact.

What worked for me: centralized markdown source of truth, automated drift detection, layered access (zero-latency for hot paths, RAG for cold paths, validated tool-calls for the things that have to be right), and a single MCP surface so every consumer reads from the same compiled artifacts. The agents on top get thin — most of them are 200 lines of orchestration glue around half a dozen tool calls.

That's the whole point. The platform is what you keep maintaining; the agents are leaves you can rewrite cheaply, because the substrate doesn't move under them.

---

*This is the first in a series on the analytics agent ecosystem I've built. Next: [The Semantic Layer Was an Eval Decision](/articles/semantic-layer-evolution) — how the text-to-data system on top of this substrate got rebuilt twice in six weeks, and why eval difficulty turned out to be an architecture signal.*

---

## Confidentiality pre-publication checklist

Before this article goes anywhere public, verify each line:

- [ ] No internal product names (Wibey, YB, cp-platform, cp-analytics-mcp, cp-hybrid, cp-analytics, cp-audit, cp-fix, jira-ticket-worker, customer-voice-semantic-layer, etc.)
- [ ] No internal team names, manager names, or coworker names
- [ ] No fully-qualified table references (`wmt-dsi-cally-audience-prd...` etc.)
- [ ] No specific column or table names from the warehouse
- [ ] No specific dashboard names or supplier names
- [ ] No internal repo paths (`~/Desktop/repos/...`)
- [ ] No internal Slack channel or mcp.json config references
- [ ] No row-level scale numbers that aren't already public (1.1M panelists, 158M task rows, etc. — generalize to "over a million users", "tens of millions of records")
- [ ] No screenshots of internal UIs
- [ ] Manager test: would my manager shrug or flinch?

Current sanitization status: every internal name and number has been generalized. Only public-shape architecture, methodology, and lessons remain. The Confidentiality Ground Rules in `Website Project Content.md` were applied throughout.
