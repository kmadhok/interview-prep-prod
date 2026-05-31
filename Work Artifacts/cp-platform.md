# CP Platform — Context Engineering Core

**Repo:** `~/Desktop/repos/cp-platform`

## What it is

A production context engineering and knowledge management platform for Walmart's Customer Spark / Customer Perception data. It consolidates 68 BigQuery tables and 1,350+ columns into a single searchable, validated, auto-maintained knowledge base — and distributes that knowledge to every downstream agent, skill, and dashboard built on top of it.

**Mission:** be the single source of truth for all CP data context, so every downstream system (cp-analytics, jira-ticket-worker, simple-cp-interaction, customer-voice-semantic-layer, kpi-monitor) gets the same accurate, drift-checked picture of the data.

## The problem it solves

Knowledge about a data asset is normally scattered across repos, Confluence pages, Slack threads, and people's heads. Every agent or skill has to re-discover the same schema, the same join paths, the same business rules. CP Platform centralizes this — and more importantly, **automates its maintenance** so context stays accurate as schemas drift.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  ACCESS LAYER                                                  │
│  MCP Server (13 tools) │ Flask UI │ Streamlit │ Python SDK     │
└────────────────┬───────────────────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────────────────┐
│  KNOWLEDGE LAYER                                               │
│  ChromaDB RAG │ SQL KB Index │ Compiled MCP JSON               │
│  In-memory schema lookup │ Join graphs │ Domain rules          │
└────────────────┬───────────────────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────────────────┐
│  INGESTION & TRANSFORMATION LAYER                              │
│  schema_extractor → diff_engine → doc_generator                │
│  → chunker → embedder → sql_kb_builder → context_compiler      │
└────────────────┬───────────────────────────────────────────────┘
                 │
┌────────────────▼───────────────────────────────────────────────┐
│  QUALITY LAYER                                                 │
│  Validators: schema, enums, joins, tables, DDL cross-refs      │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 └──▶ External: BigQuery, DDL repos, query history
```

## Ground truth files

**`context/domain.md`** (~500 lines, human-curated)

- Business definitions for every metric (panel health, survey performance, engagement, revenue)
- SQL patterns showing exactly how to calculate each metric
- Known data quirks (timestamps are STRINGS, panelist state machine, enum gotchas)

**`context/tables.md`** (~400 lines, human-curated)

- 68 table schemas, columns, types, nullability
- Confirmed join paths with SQL snippets
- PII vs non-PII classifications

**`context/schema.json`** (450KB, machine-generated daily)

- BigQuery `INFORMATION_SCHEMA.COLUMNS` snapshot
- 68 tables, 1,350+ columns with types and metadata

These three files are the **single source of truth**. Everything else is derived.

## Documentation generation pipeline

```
BigQuery Live Schema
    ↓  schema_extractor.py
context/schema.json (cached 24h)
    ↓  diff_engine.py
Drift report (undocumented tables, schema changes, obsolete docs)
    ↓  doc_generator.py  (3-tier LLM fallback: Wibey Opus → Sonnet → Gemini 2.5 Pro)
docs/v2/*.md (auto-generated from DDL + schema + prompt template)
    ↓  chunker.py  (8 semantic section types)
~226 chunks
    ↓  embedder.py  (Gemini embeddings, 3072 dims)
stores/.chroma/ (ChromaDB persistent index)
```

This runs **weekly** on a Monday cron — schema drifts, the platform auto-detects, auto-generates new docs, re-embeds. No manual maintenance.

## SQL knowledge base pipeline

```
BigQuery JOBS_BY_USER (180 days history)
    ↓  sql_kb_builder.py
Dedupe → filter to SELECT-only on CP datasets → extract tables, joins, aggregations
    ↓  Gemini-generated natural language descriptions
stores/.sql_kb/queries.json (~313 queries with embeddings)
    ↓  sql_kb_search.py
Hybrid search: vector (Gemini embeddings) + BM25 (keyword) + RRF fusion
    ↓
Ranked similar past queries — agents ask "find queries that calculate
completion rates" and get real, tested SQL examples
```

## Context compilation (markdown → JSON for fast MCP lookups)

`context_compiler.py` converts human-curated markdown into in-memory JSON:

| Input | Output | Used by |
|-------|--------|---------|
| `context/tables.md` | `mcp/schema.json` (16 tables, full columns) | `cp_get_schema` |
| `context/tables.md` | `mcp/joins.json` (36+ confirmed paths) | `cp_get_join_path` |
| `context/domain.md` | `mcp/domain_sections.json` (89 sections) | `cp_get_domain_context` |
| Schema + joins | `mcp/graph.json` (52 nodes, 63 edges) | knowledge graph traversal |

These compiled artifacts mean **zero-latency schema lookups** — pure in-memory JSON, no DB round-trip.

## The MCP server (13 tools)

This is how every other project consumes the platform:

| Tool | Purpose | Latency |
|------|---------|---------|
| `cp_get_schema(table)` | Columns, types, quirks | ~0ms |
| `cp_get_join_path(a, b)` | SQL join snippet | ~0ms |
| `cp_get_domain_context(topic)` | Business rule explanation | ~0ms |
| `cp_query(sql)` | Execute against BigQuery | ~15-20s |
| `cp_ask_docs(question)` | RAG answer from ChromaDB | ~1-5s |
| `cp_search_sql(query, top_k)` | Find similar historical SQL | ~1-5s |
| `cp_build_execution(...)` | Generate execution.json scaffold | ~2s |
| `cp_create_chart(...)` | Walmart-branded matplotlib chart | ~5s |
| `cp_validate(...)` | Report completeness check | ~1s |
| `cp_init_report(...)` | Scaffold report directory | ~0ms |
| `cp_get_gcc_context(...)` | Accumulated knowledge | ~0ms |
| `cp_get_backlog(...)` | Backlog access | ~0ms |
| `cp_refresh_knowledge(scope)` | Trigger pipeline | varies |

**Total latency for full schema + doc + BQ execution:** ~20-25s vs ~10 minutes manually.

## Validation layer (drift detection)

Five daily checks against live BigQuery:

| Check | What it does |
|-------|--------------|
| `check_schema.py` | BQ schema vs tables.md — catches new/changed/dropped columns |
| `check_enums.py` | Documented enum values vs `SELECT DISTINCT` results |
| `check_joins.py` | Tests every confirmed join path by executing it |
| `check_tables.py` | Table inventory count |
| `check_ddl.py` | Cross-references BQ schema against Azure SQL DDL in engineering repos |

Output: `context/validation.log` — JSON with per-check results. Drift feeds into the next `doc_generator.py` run for auto-correction.

## Three access patterns

### 1. MCP Server (for AI agents)

13 tools, stdio transport, zero-latency in-memory JSON for schema/joins/domain. Used by every Wibey skill that touches CP data.

### 2. Flask Web UI (for humans)

`localhost:5001`. Mode toggle between "Ask about data" and "Find SQL". RAG-powered Q&A with collapsible source citations and full audit trail.

### 3. Python SDK (programmatic)

```python
from knowledge.embedder import query_similar
from knowledge.sql_kb_search import search
from knowledge.schema_extractor import get_schema
from validators.run_all import run_all
```

## Downstream consumers

The platform powers everything else built on top of it:

| Consumer | What it consumes |
|----------|------------------|
| **cp-analytics** | `domain.md`, `tables.md`, `schema.json` as ground truth dispatched into every sub-agent |
| **jira-ticket-worker** | `cp_get_schema`, `cp_get_join_path`, `cp_search_sql`, `cp_get_domain_context` MCP tools |
| **simple_cp_interaction** | Compiled markdown context (auto-generated via `compile_from_source.py`) |
| **customer-voice-semantic-layer** | Cube.js model informed by cp-platform's schema; cube-gap-filler uses validated joins |
| **kpi-monitor** | Queries BQ tables that cp-platform documents and validates daily |
| **Slack integrations** | `/cp` command Slack bot |
| **cp-business, cp-discovery, cp-hybrid** | Domain context + RAG answers |

**Distribution mechanism:** MCP server registered in `~/.wibey/mcp.json`, Wibey skill registry, Code Puppy agent marketplace, Python library imports.

## Architecture experiments (18 in evaluation)

The platform isn't static — it includes a structured experimentation framework scoring approaches on **accuracy, latency, cost, consistency**:

- **Phase 1 — Baselines:** Full context stuffing (660K tokens), raw RAG, full MCP agent
- **Phase 2 — Quick Wins:** Partial stuffing, RAG for historical SQL, prioritized ordering
- **Phase 3 — RAG Optimization:** Chunk size sweeps (256/512/1024/2048), hybrid search, reranking, query decomposition
- **Phase 4 — Agent Architecture:** Structured plan vs RAG-as-tool vs consolidated tools, sqlglot SQL parser, parallel tool execution
- **Phase 5 — System Design:** RAG-Generate → MCP-Validate two-stage, tiered router (simple → RAG, complex → MCP), cached MCP + enriched RAG

## Pipeline orchestration

**Daily 6 AM:**

```bash
python -m pipeline.refresh --scope schema,validate
```

**Weekly Monday 7 AM:**

```bash
python -m pipeline.refresh --scope docs,sql_kb,compile
```

**Manual:**

```bash
python -m pipeline.refresh --scope all --force
python -m validators.run_all
python -m knowledge.context_compiler
python web/app.py        # Flask UI on :5001
python mcp/server.py     # MCP stdio
```

## Critical design decisions

1. **Single Source of Truth pattern** — markdown is the SoT; JSON, embeddings, indexes are all derived/regenerable.
2. **Dependency direction is always inward** — consumers depend on platform, platform depends on data sources. Never the reverse.
3. **RAG + Validation layering** — RAG retrieves chunks, LLM synthesizes grounded in context, MCP tools validate against live data. Speed of RAG, precision of structured tools.
4. **Three-tier LLM fallback** — Wibey Opus → Sonnet → Gemini 2.5 Pro. Doc generation never fails due to timeout or unavailability.
5. **Compiled artifacts for hot paths** — schema/joins/domain compiled from markdown to JSON for zero-latency MCP lookups; ChromaDB and SQL KB for semantic search.
6. **Drift detection as a first-class concern** — every check is a daily cron; drift triggers auto-doc-regen.

## Current scale

| Metric | Count |
|--------|-------|
| Tables catalogued | 68 |
| Columns documented | 1,350+ |
| Tables with full v2 documentation (auto-expanding) | 24 |
| Chunks in ChromaDB | 226 |
| SQL queries indexed in knowledge base | 313 |
| Join paths verified | 36+ |
| Domain sections indexed | 89 |
| Daily validation checks | 5 |
| MCP tools exposed | 13 |
| cp-analytics analyses powered by the platform | 57 |

## Why it matters

Every other system built on top of this — cp-analytics, jira-ticket-worker, simple-cp-interaction, the semantic layer, the KPI monitor — is a **context-injection system at heart**. They all depend on having accurate, current, structured knowledge of the CP data. CP Platform is what makes that possible. Without it, every consumer would have to re-discover schemas, drift would silently break SQL, and join paths would be guessed from training data.

It's the substrate that makes the whole ecosystem work. Build the substrate once, and every new agent or skill becomes a thin layer on top instead of a duplicated context engineering effort.
