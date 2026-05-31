# CP Analytics MCP Server — Complete Reference

**Repo:** `~/Desktop/repos/cp-platform/`
**Server entry:** `cp-platform/mcp/server.py` (1,133 LOC, FastMCP, stdio transport)
**Registered as:** `cp-analytics-mcp` in `~/.wibey/mcp.json`
**Scope:** 14 tools + 4 resources, single-process stdio MCP server, in-memory schema cache, BigQuery execution via `scripts/run_query.py`

## What it is

A FastMCP server that exposes Walmart Customer Spark / Customer Perception data context and execution as MCP tools over stdio. Built on top of cp-platform's compiled context artifacts (`schema.json`, `joins.json`, `domain_sections.json`, `graph.json`) so schema lookups are zero-latency in-memory hits, and on top of `scripts/run_query.py` so every BigQuery execution is automatically captured to disk before run (no "lost SQL" problem).

This MCP server is the **single distribution surface** every other Wibey skill / agent uses to consume CP data context — `cp-analytics`, `jira-ticket-worker`, `simple-cp-interaction`, `kpi-monitor`, `cp-business`, `cp-discovery`, `cp-hybrid`, and the Cube semantic layer's gap-filler. If it's data work and it touches CP, it goes through these 14 tools.

## Architecture

```
                ┌──────────────────────────────────┐
                │   Wibey / Claude Code agents     │
                │   (MCP client over stdio)        │
                └────────────────┬─────────────────┘
                                 │ JSON-RPC over stdio
                                 ▼
                ┌──────────────────────────────────┐
                │   mcp/server.py (FastMCP)        │
                │   14 tools, 4 resources          │
                ├──────────────────────────────────┤
                │  Lazy in-memory caches:          │
                │    _schema_cache  ← schema.json  │
                │    _joins_cache   ← joins.json   │
                │    _domain_cache  ← domain_sections.json │
                │  Helpers:                        │
                │    _load_json, _read_file        │
                │    _run_script (subprocess)      │
                │    _resolve_table (alias + fuzzy)│
                └────┬───────────────┬─────────────┘
                     │               │
        compiled JSON │               │ subprocess
                     ▼               ▼
    ┌────────────────────────┐  ┌────────────────────────┐
    │  context/ (markdown)   │  │  scripts/              │
    │  ↓ compile_context.py  │  │  run_query.py          │
    │  mcp/*.json (16 tables,│  │  build_execution.py    │
    │  36+ joins, 89 sections│  │  create_chart.py       │
    │  52-node graph)        │  │  validate_output.py    │
    └────────────────────────┘  └────────────────────────┘
                                         │
                                         ▼
                                   BigQuery
```

- **Transport:** stdio (JSON-RPC). Configured in `~/.wibey/mcp.json` as `python3 /path/to/server.py`.
- **Logging:** stderr only (stdout reserved for protocol).
- **State:** Stateless per-call except for lazy-loaded JSON caches (loaded once per process lifetime).

## Registration

```jsonc
// ~/.wibey/mcp.json
{
  "cp-analytics-mcp": {
    "type": "stdio",
    "command": "python3",
    "args": ["/Users/k0m0oxq/Desktop/repos/cp-platform/mcp/server.py"]
  }
}
```

## The 14 tools

### 1. `cp_get_schema(table_name: str) → str`

Returns the full schema for a CP table: columns, types, primary key, joins-to list, critical rules, notes. Uses `_resolve_table` to accept FQNs, aliases (`rewards` → `user_reward_point_detail`), singular/plural variants, and partial matches.

- **Latency:** ~0ms (in-memory)
- **Special arg:** `table_name='list'` returns the inventory of all available tables
- **Source:** `mcp/schema.json` (compiled from `context/tables.md`)

```
cp_get_schema('panelist')
→ # market_research_panelist
  FQN: ...
  Primary Key: panelistId
  Joins to: [task, demographic, ...]
  ## Columns (XX total)
    - panelistId (STRING)
    - state (STRING) — REGISTERED = active panelist
    ...
  ## Critical Rules
    ! state must be filtered for 'REGISTERED'
```

### 2. `cp_get_join_path(table_a: str, table_b: str) → str`

Returns the confirmed join path between two tables. First tries a direct lookup in `joins.json`; if there's no direct edge, falls back to `knowledge.graph` for a multi-hop shortest path with the full generated `JOIN ... ON ...` SQL chain.

- **Latency:** ~0ms direct, ~50ms multi-hop
- **Source:** `mcp/joins.json` (36+ paths) + `mcp/graph.json` (52 nodes, 63 edges)
- **Output includes:** join name, left/right keys, cardinality, match rate, SQL snippet
- **Fallback chain:** exact `a->b` → reverse `b->a` → partial substring match → graph pathfinding

### 3. `cp_get_domain_context(topic: str) → str`

Keyword + phrase search across the 89 indexed sections of `context/domain.md`. Scoring: title phrase match (+15), content phrase match (+10), keyword/title word overlap (+1 each).

- **Special arg:** `topic='list'` returns all available section titles
- **Source:** `mcp/domain_sections.json`
- **Use for:** business rules, metric definitions, data quirks (timestamps, panelist state machine, enum gotchas)

### 4. `cp_query(sql, step_id, purpose, output_dir, save_csv='', max_results=10000) → str`

Executes SQL against BigQuery via `scripts/run_query.py`. The SQL is written to `output_dir/queries/{step_id}.sql` **before** execution (provenance guarantee). Logs to `.query_log.jsonl`. CSV results are optional via the `save_csv` path.

- **Timeout:** 2,700s (45 min)
- **Return codes:** 0 = success, 2 = timeout, other = error (all leave SQL on disk)
- **Output:** rows returned, bytes billed, SQL path, CSV path, 3000-char preview

### 5. `cp_build_execution(output_dir, idea_id, title) → str`

After all `cp_query` calls for an analysis are done, builds a deterministic `execution.json` from `.query_log.jsonl` + `queries/*.sql` files. Produces the full SQL-in-every-step audit record + `.sql_queries_section.md` for inclusion in reports.

- **Runs:** `scripts/build_execution.py`
- **Timeout:** 120s

### 6. `cp_create_chart(...) → str`

Walmart-branded matplotlib chart generation via `scripts/create_chart.py`. Supports `bar`, `grouped_bar`, `stacked_bar`, `line`, `scatter`, `heatmap`, `funnel`, `pie`. Y-axis formats: `number | pct | currency | compact`. Sort modes: `value | label | tier | none`.

- **Params:** `data_file, chart_type, x, y, title, output, data_labels, horizontal, sort_by, color_by, y_format, subtitle, group_by, figsize`
- **Timeout:** 60s

### 7. `cp_validate(output_dir) → str`

Checks that a report directory meets the output contract: `report.md`, `findings.json`, `execution.json`, `data/*.csv`, `queries/*.sql`, `.query_log.jsonl`. Catches summarized-instead-of-real SQL. Returns structured PASS/FAIL with per-check status, errors, and warnings.

- **Runs:** `scripts/validate_output.py`
- **Returns:** parsed JSON validation report

### 8. `cp_get_gcc_context(scope='overview', category='', idea_id='') → str`

Reads from `.gcc/` (Git Context Controller) — the accumulated cross-analysis knowledge store. Scope modes:

| scope | returns |
|-------|---------|
| `overview` | `.gcc/main.md` summary |
| `category` | All files under `.gcc/branches/{category}/` |
| `idea` | All files mentioning a specific `IDEA-NNN` ID |
| `patterns` | `metadata.yaml` of known data patterns |
| `tables` | Aggregated table usage statistics |
| `full` | Everything (`.md`, `.yaml`, `.json`) under `.gcc/` |

### 9. `cp_get_backlog(status='all', category='', limit=20) → str`

Reads `ideas/backlog.json`, filters by `status` (`pending | completed | error | in_progress | all`) and `category` (`lifecycle | surveys | billing | ...`). Returns a formatted table of ID / Status / Category / Title.

### 10. `cp_init_report(idea_id, title, date='') → str`

Scaffolds a new report directory under `reports/{date}/{idea_id}_{slug}/` with `data/`, `charts/`, and `queries/` subdirs. The slug is auto-generated from the title (lowercased, non-alphanumeric stripped, words joined by `_`).

### 11. `cp_search_sql(query, top_k=5) → str` *(async)*

Searches the SQL knowledge base (~313 historical BQ queries indexed from 180 days of `JOBS_BY_USER`) for queries semantically similar to a natural-language description. Uses `knowledge.sql_search` — hybrid vector (Gemini embeddings) + BM25 + RRF fusion.

- **Returns:** a ranked list with score, plain-English summary, tables used, and the first 500 chars of SQL

### 12. `cp_ask_docs(question) → str` *(async)*

RAG Q&A over the ChromaDB index of `docs/v2/*.md` (~226 chunks). Calls `web.rag_engine.ask(question)`, which retrieves top-k chunks, builds a grounded prompt, invokes the LLM (Wibey Opus → Sonnet → Gemini fallback), logs the full query lifecycle, and returns the answer.

### 13. `cp_generate_validated_sql(question, max_results=100) → str`

**The flagship tool.** Full Gemini-validated NL→SQL→execution pipeline:

1. Gemini 2.5 Pro generates SQL from RAG context (~150K chars)
2. Gemini 2.5 Flash validates via function calling — schema checks, join verification, domain rule enforcement, BQ dry-run
3. Flash executes the validated SQL against BigQuery

**Returns:** the generated SQL block, a validation summary (turns, tools called, fixes applied, valid/executed flags), an execution preview, and a full timing breakdown (retrieval / generation / validation / total).

- **Latency:** ~60s
- **Backed by:** `rag_validate.strategies.gemini_validated.pipeline.run`
- **Use first** for any NL data question; then drill in with `cp_query`, `cp_get_schema`, `cp_get_join_path`

### 14. `cp_refresh_knowledge(scope='all') → str` *(async)*

Triggers `pipeline.refresh.run(scope)`. Scopes: `schema | validate | docs | sql_kb | compile | all`. Returns the full JSON refresh result. Used to manually rebuild the schema cache, re-run validators, regenerate docs, rebuild the SQL KB, or recompile context — the same operations the cron pipeline runs daily/weekly.

## The 4 resources

Read-only MCP resources exposing raw context files by URI:

| URI | Returns |
|-----|---------|
| `cp://domain` | Full `context/domain.md` (business rules, metric defs, quirks) |
| `cp://tables` | Full `context/tables.md` (schemas, joins, enums) |
| `cp://backlog` | Current `ideas/backlog.json` |
| `cp://index` | `INDEX.md` analytics dashboard |

## Helpers worth noting

**`_resolve_table(name, schema)`** — the table-name resolution chain:

1. Strip the FQN prefix (`project.dataset.table` → `table`)
2. Exact key match
3. Strip the `market_research_` prefix
4. Alias lookup (`rewards`, `points`, `tasks`, `surveys`, `demographics`, etc.)
5. Singular/plural variants (`-s`, `-ies`/`-y`, `-es`)
6. Partial substring match

Falls back to the original name if nothing resolves. This is why `cp_get_schema('rewards')`, `cp_get_schema('user_reward_point_detail')`, and `cp_get_schema('market_research_user_reward_point_detail')` all work.

**`_run_script(script_name, args, timeout)`** — a uniform subprocess wrapper for the four script-backed tools (`cp_query`, `cp_build_execution`, `cp_create_chart`, `cp_validate`). Captures stdout/stderr/returncode, handles `TimeoutExpired`, and runs with `cwd=cp-platform/`.

**Lazy caches:** `_schema_cache`, `_joins_cache`, and `_domain_cache` populate on first access and persist for the process lifetime. The first call is ~5-10ms (JSON parse); subsequent calls are ~0ms (dict lookup).

## Tool taxonomy

| Category | Tools |
|----------|-------|
| **Schema / context (read-only, 0ms)** | `cp_get_schema`, `cp_get_join_path`, `cp_get_domain_context`, `cp_get_gcc_context`, `cp_get_backlog` |
| **Execution / BQ** | `cp_query`, `cp_generate_validated_sql` |
| **Discovery / RAG** | `cp_ask_docs`, `cp_search_sql` |
| **Reporting workflow** | `cp_init_report`, `cp_build_execution`, `cp_create_chart`, `cp_validate` |
| **Maintenance** | `cp_refresh_knowledge` |

## Downstream consumers

| Consumer | Tools used |
|----------|------------|
| **cp-analytics** (autonomous analyst) | All 14 |
| **jira-ticket-worker** | `cp_get_schema`, `cp_get_join_path`, `cp_search_sql`, `cp_get_domain_context`, `cp_generate_validated_sql` |
| **simple-cp-interaction** | `cp_ask_docs`, `cp_search_sql`, `cp_get_schema` |
| **kpi-monitor** | `cp_query`, `cp_get_schema` |
| **customer-voice-semantic-layer / cube-gap-filler** | `cp_get_schema`, `cp_get_join_path` |
| **cp-business / cp-discovery / cp-hybrid skills** | `cp_ask_docs`, `cp_get_domain_context`, `cp_generate_validated_sql` |
| **Slack `/cp` bot** | `cp_generate_validated_sql`, `cp_ask_docs` |

## Scale & impact

- **14 MCP tools + 4 resources** exposed
- **68 BigQuery tables, 1,350+ columns** in scope
- **226 doc chunks** in ChromaDB
- **313 SQL queries** indexed in the knowledge base
- **36+ join paths** verified, **89 domain sections** indexed
- **52-node, 63-edge** join knowledge graph for multi-hop pathfinding
- **~20-25s** end-to-end for a full schema + RAG + BQ execution cycle (vs ~10 min manual)

## Why it matters

Most data-context MCPs expose schema and stop there. This server is unusual in three ways:

1. **Execution is first-class but provenance-safe.** Every `cp_query` writes SQL to disk before BQ touches it. No more "what query produced this CSV again?"
2. **The flagship tool (`cp_generate_validated_sql`) is a complete autonomous SQL agent in one call** — generates with Gemini Pro, validates with Gemini Flash function calling, dry-runs, executes. The CLI agent calling it just presents results.
3. **It's the substrate, not the leaf.** Every other CP skill built on top of it is a thin wrapper that calls 2-5 of these tools. The platform's value compounds because the MCP centralizes the access pattern.

## Source of truth

- **Server:** `cp-platform/mcp/server.py`
- **Compiled context:** `cp-platform/mcp/{schema,joins,domain_sections,graph}.json`
- **Compilation logic:** `cp-platform/mcp/compile_context.py`
- **Backing scripts:** `cp-platform/scripts/{run_query,build_execution,create_chart,validate_output}.py`
- **Existing scattered docs:** `SPEC.md §6.20` (outdated, 13 tools), `distribution/wibey_mcp_distribution.md` (6 read-only tools for WCNP deploy), inline `@mcp.tool` docstrings
- **This file:** the complete and current single-source reference
