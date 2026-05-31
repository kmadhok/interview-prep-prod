# Jira Ticket Worker — Autonomous BDV Ticket Resolver

**Skill:** `jira-ticket-worker` (v3.0) / `bdv-ticket`

## What it is

A fully autonomous BDV (Walmart Data Ventures) data steward agent that resolves Jira tickets end-to-end — triage through CSV delivery — with zero human checkpoints and a 10-retry self-healing budget.

Handles: manual recruitment pulls (UPC list → panelist IDs), demographic enrichment (HHI/age/gender), feasibility/count queries, database health checks, complex investigations.

## The MCP context injection

Uses `cp-analytics-mcp` tools as the knowledge layer:

| Tool | Purpose | Phase |
|------|---------|-------|
| `cp_get_domain_context` | Business rules ("what does 'active panelist' mean?") | UNDERSTAND |
| `cp_get_schema` | Full table schemas + column descriptions | UNDERSTAND |
| `cp_search_sql` | 2-3 similar historical queries for pattern reference | UNDERSTAND |
| `cp_get_join_path` | Direct or multi-hop join SQL between tables | PLAN |
| `cp_ask_docs` | Edge case clarifications | UNDERSTAND (complex tickets) |

**Complexity-adaptive strategy:**

- **SIMPLE:** schema + 1 reference SQL
- **MODERATE:** full suite for 2-3 tables
- **COMPLEX:** exhaustive — multiple `cp_search_sql` per pattern, all domain contexts

## RAG architecture

**Hierarchical context management** inspired by GCC (Git Context Controller):

```markdown
# Worklog: BDV-XXXX

## Summary (ALWAYS READ FIRST ON RESUME)
- Status, complexity, ask, progress, key findings, next action, blockers

## Triage / Understanding / Plan / Execution Log / Delivery
[Detail sections, read on-demand]
```

The Summary section is the entry point on resume — coarse metadata first, drill into details only if needed. Mirrors ChromaDB retrieval patterns.

## Context injection methods (beyond MCP)

**Static reference files** (pre-cached knowledge):

- Fully qualified BigQuery paths
- Key table dimensions ("transaction table is HUGE — ALWAYS date-filter")
- Domain gotchas (timestamps are strings, LPAD UPCs)
- 10 ticket types with keywords and SQL patterns

**Investigation Branches** (dynamic exploration):

When a query returns 0 rows or unexpected results, opens an investigation block with a hypothesis, runs 5-min exploratory queries, documents findings, and applies learnings to subsequent queries. Investigation branches are NOT compressed during rolling compression — they encode debugging knowledge.

**Hierarchy/Brand Discovery pre-step** (category-triggered):

For tickets mentioning categories or brands, runs a discovery query first to find exact hierarchy values (e.g., `'SAMSUNG ELECTRONICS'`, not `'Samsung'`) before writing final filters.

**Synthesis Checkpoints** (between-query context):

When Q2 depends on Q1 results, explicitly document the data dependency:

```markdown
### Synthesis: Q1 → Q2
**From Q1:** Top 5 states: TX, CA, NY, FL, PA
**Feeds into Q2:** These values hardcoded into Q2 WHERE clause
```

## Workflow

```
Phase 1: TRIAGE      → 6 gates: prior work, valid ticket, data task,
                       actionable ask, inputs available, comments
Phase 2: UNDERSTAND  → MCP knowledge gathering, attachment parsing,
                       confidence level assignment
Phase 3: PLAN        → Numbered query decomposition (Q1, Q2, ...) with
                       tables, joins, dependencies, expected shape
Phase 4: EXECUTE     → Per-query loop: dry-run → execute → validate →
                       self-heal (10-retry budget)
Phase 5: DELIVER     → Summarize, list CSVs, update manifest
```

## Self-healing patterns

| Failure | Retry budget | Action |
|---------|-------------|--------|
| Syntax error | max 3 retries | fix SQL, re-run |
| Timeout | max 2 retries | add tighter date filter |
| 0 rows | max 3 retries | Investigation Branch → adjust filter |
| Retry budget hits 0 | — | skip remaining queries, deliver partial results |

## State machine

`manifest.json` is the machine-readable source of truth:

```json
{
  "queries": [
    {"id": "Q1", "status": "complete|failed|timeout|uncertain", "retries_used": 0,
     "depends_on": "Q0|null", "row_count": 514, "bytes_scanned": "512MB"}
  ],
  "retry_budget_remaining": 10,
  "phase": "EXECUTE"
}
```

`worklog.md` is the human-readable narrative. Both are updated atomically.

## Cost & resource controls

- **40-min default timeout** (`run_query.py` polls every 5s, auto-cancels)
- **5-min timeout** for exploratory queries
- **Dry-run first** — if estimated scan > 50GB, add a tighter filter
- **SELECT specific columns** — never `SELECT *` on large tables
- **BigQuery job ID logged** for audit

## Real example: BDV-6665

| Stage | Detail |
|-------|--------|
| Initial assumption | Q12 column empty → return all 523 qualified completes (Q1) |
| User feedback | "9 should be excluded (opted out of video)" |
| Investigation | Q12 is 100% NaN because opt-in is a panelist-level preference, not a survey answer |
| Solution | Q2 joined `market_research_panelist_preference.video_activity_opt_in_flag = TRUE` |
| Result | 514 rows correct (vs 523 originally) |

Q1 was marked `superseded` but kept for audit. Demonstrates self-correction with a full audit trail.

## Key architectural takeaways

1. **Hierarchical context management** — Summary for resume, detail on demand
2. **MCP as knowledge interface** — no hardcoded schemas
3. **Metadata-driven state** — `manifest.json` is source of truth, `worklog.md` is narrative
4. **Self-healing loops** — automatic retry with adjustment, capped budget
5. **Investigation branches** — exploratory queries encoded as learning
6. **Synthesis checkpoints** — data dependencies documented between queries
7. **Scope clarity** — flags out-of-scope tickets for other skills
8. **Append-only audit trail** — queries superseded but kept for audit
