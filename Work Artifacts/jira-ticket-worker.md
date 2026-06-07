# BDV Skill Suite — Autonomous Jira Ticket Workflow

> ## ⚡ INTERVIEW CHEAT SHEET — Architecture (BCG X / Maan · today)
>
> *This block is the morning-of architecture anchor for the Jira agent — the #1 lead build. The full spec below is the source of truth; this is what you actually say out loud. Glance, don't read.*
>
> **One-liner:** Fully autonomous BDV ticket resolver — triage through CSV delivery, zero internal checkpoints, 10-retry self-healing budget. 400+ tickets since Jan '25 · 30–60 min → ~10 min · ~17–60 workdays saved.
>
> **The 30-second architecture (draw 6 boxes, narrate every line):**
> ```
> ticket → TRIAGE → UNDERSTAND → PLAN → EXECUTE → DELIVER → [my review] → Jira
>          (6 gates: (MCP: schema, (numbered (run SQL,    (CSVs +
>           solvable  joins, 2-3    SQL plan, dry-run +   synthesized
>           E2E?)     past queries) manifest) 10-retry)    answer)
> ```
> The pipeline is thin. The asset is **underneath** it:
> ```
>     CONTEXT LAYER  (schema · joins · business defs · 52-node join graph)
>           │ exposed via
>           ▼
>         cp-analytics MCP  ──►  every phase is THIN on top of this
> ```
>
> **The 5 design decisions Maan will probe — lead with the architectural reason, not convenience:**
>
> 1. **Why MCP, not hardcoded SQL?** — "The DB knowledge layer is reusable across every agent I build and worth a stable contract, so it's an MCP. Build the substrate once; each agent is the next thin thing on it." (*never guess a business definition — the agent must call the MCP before writing any SQL.*)
> 2. **Why a manifest + worklog (two state files)?** — `manifest.json` is the machine source of truth; `worklog.md` is the human narrative. Hierarchical context: **Summary read first on resume**, detail on demand. Lets the agent crash and resume from the exact query position without re-running completed work.
> 3. **Why self-healing with a *capped* budget?** — 10 retries shared across all queries (3 syntax · 2 timeout · 3 zero-row). Zero-row opens an **Investigation Branch**: states a hypothesis, runs a 5-min exploratory query, applies the learning. Budget = 0 → deliver partial + log blockers, never spin. "Autonomy sized for execution; the cap is the failure budget."
> 4. **Where's the human?** — **My review sits OUTSIDE the loop.** The agent is fully autonomous to CSV; I gate the *communication* to the stakeholder. *"Autonomy sized for execution, my review for communication — two failure budgets, each sized to blast radius."*
> 5. **How do you know it works? (eval — he WILL push)** — ① structural: SQL vs the **join graph, 52 nodes / 36 verified paths** ② intent: vs **313 historical queries** ③ provenance: every number traces to runnable SQL in the work log. *"Today I'm the gate; the next version moves the gate to golden-set regression."*
>
> **Gate / abstain / failure-mode lines (have all three ready — he digs until you produce them):**
> - **Gate:** "Today I'm the gate; next version → golden-set regression."
> - **Abstain:** grounded design — the agent can only cite data the SQL returned; on insufficient data it returns "insufficient data," never a fabricated number.
> - **Failure mode I worry about most:** **confident-wrong** — clean SQL on a stale flag. That's why every result is stamped with freshness metadata (frozen 30d / late-arriving 24h / streaming 1h).
>
> **Cost discipline (one line if probed):** dry-run first; if estimated scan > 50 GB, add a tighter filter before executing. 40-min timeout, auto-cancel. Never `SELECT *` on the huge transaction table.
>
> **The leverage close (the Principal-level through-line):** *"The intake bottleneck was what kept me from building anything else. Automating my own role bought me the time to build the rest of the portfolio."*
>
> **If he says "draw it"** → the 6-box pipeline + the substrate underneath. 60 sec. Narrate every box. Don't dump the substrate stats — pick 2–3 numbers max (52-node join graph, 313 queries, 400+ tickets).
>
> ---

A three-skill pipeline that takes a BDV (Walmart Data Ventures) Jira ticket from raw text to a stakeholder-ready deliverable with **zero human checkpoints**.

```
/jira-sync         → ticket pulled to disk
   ↓
/bdv-solver        → ticket solved (results/, worklog.md)
   ↓
/bdv-validator     → results validated (validation/report.md)
   ↓
/bdv-presenter     → deliverable packaged (deliverable/)
```

| Skill | Version | Role |
|-------|---------|------|
| `bdv-solver` | v4.1 | Autonomous ticket resolver — triage through CSV delivery |
| `bdv-validator` | v4.0 | Parallel validation dispatcher — 7 independent checks |
| `bdv-presenter` | v1.0 | Stakeholder deliverable packager — audience-adaptive HTML |

---

## 1. BDV Solver — Autonomous Ticket Resolver

**Skill:** `bdv-solver` (v4.1) / `bdv-ticket`
**Location:** `~/.wibey/skills/bdv-solver/`

### What it is

A fully autonomous BDV data steward agent that resolves Jira tickets end-to-end — triage through CSV delivery — with zero human checkpoints and a 10-retry self-healing budget.

Handles: panelist pulls, demographic enrichment (HHI/age/gender), feasibility/count queries, UPC lookups, store aggregations, data validation, and ad-hoc BigQuery analysis.

### Three Critical Constraints

1. **Tickets are on disk** — stored at `~/Desktop/repos/Misc/ideas/Jira_Automation/tickets/BDV-XXXX/`. No Jira MCP, browser, or fetch-ticket skill.
2. **Never guess business definitions** — must call `cp-analytics-mcp` tools before writing ANY SQL.
3. **SQL only via `run_query.py`** — script at `scripts/run_query.py` with `--dry-run`, `--output`, and `--timeout` options.

### Folder Contract

```
tickets/BDV-XXXX/
  ticket.json          (read-only)
  ticket.md            (read-only)
  attachments/         (read-only)
  worklog.md           (agent-managed, append-only narrative)
  results/
    manifest.json      (machine-readable state tracker)
    QN_name.sql        (per-query SQL)
    QN_name.csv        (per-query results)
    QN_name.meta.json  (freshness metadata)
```

### Workflow — Four Phases

#### Phase 0: TRIAGE

Read `ticket.json` and `ticket.md`, then run six gates:

| Gate | Check |
|------|-------|
| 0 | Prior work — check for existing `worklog.md` |
| 1 | Valid ticket — not spam/duplicate/closed |
| 2 | Data task — not access/permissions/infra |
| 3 | Actionable ask — WHO, WHAT, WHEN defined |
| 4 | Inputs available — attachments/UPC lists present |
| 5 | Follow-up comments — scope changes since last run |

**Output:** Triage section in `worklog.md` with complexity rating (`SIMPLE` / `MODERATE` / `COMPLEX`).

#### Phase 1: UNDERSTAND

Parse the ticket thoroughly. For every business term → `cp_get_domain_context`. For every table → `cp_get_schema`. For query patterns → `cp_search_sql`. Write an Understanding section with the interpreted ask, tables, columns, join strategy, and confidence level (`HIGH` / `MEDIUM` / `LOW`).

**Complexity-adaptive strategy:**
- **SIMPLE:** schema + 1 reference SQL
- **MODERATE:** full MCP suite for 2–3 tables
- **COMPLEX:** exhaustive — multiple `cp_search_sql` per pattern, all domain contexts, `cp_ask_docs` for edge cases

#### Phase 2: PLAN

Decompose into numbered queries (Q1, Q2, …) with question, tables, joins (via `cp_get_join_path`), expected output shape, and dependencies. Initialize `results/manifest.json` with all queries in `PLANNED` status.

> **Category Hierarchy Discovery pre-step:** If the ticket mentions categories or brands, run a discovery query first to find exact hierarchy values (e.g., `'SAMSUNG ELECTRONICS'`, not `'Samsung'`) before writing final filters.

#### Phase 3: EXECUTE

Per-query loop:
1. Write SQL to `results/QN_name.sql`
2. Dry-run via `run_query.py --dry-run` — if estimated scan > 50 GB, add a tighter filter
3. Execute via `run_query.py --output QN_name.csv --timeout 2400`
4. Validate output (row count, NULLs, sanity checks)
5. Stamp freshness metadata → `QN_name.meta.json`
6. Update `manifest.json`

#### Phase 4: DELIVER

Summarize results: each query, CSV path, row count, findings. Update manifest to `COMPLETE`. If the retry budget is exhausted, deliver partial results and log blockers.

### Self-Healing Patterns

| Failure | Max Retries | Action |
|---------|-------------|--------|
| Syntax error | 3 | Fix SQL, re-run |
| Timeout | 2 | Add tighter date filter |
| 0 rows | 3 | Open Investigation Branch → adjust filter |
| Budget = 0 | — | Skip remaining queries, deliver partial |

**Total retry budget: 10** — shared across all queries. Dry-runs and MCP calls don't consume retries.

### CP Analytics MCP — Knowledge Layer

| Tool | Purpose | Phase |
|------|---------|-------|
| `cp_get_domain_context` | Business rules (e.g., "what does 'active panelist' mean?") | UNDERSTAND |
| `cp_get_schema` | Full table schemas + column descriptions | UNDERSTAND |
| `cp_search_sql` | 2–3 similar historical queries for pattern reference | UNDERSTAND |
| `cp_get_join_path` | Direct or multi-hop join SQL between tables | PLAN |
| `cp_ask_docs` | Edge case clarifications | UNDERSTAND (complex tickets) |
| `cp_generate_validated_sql` | Validated SQL generation | EXECUTE |

**Server config** (`~/.wibey/.mcp.json`):
```json
{
  "mcpServers": {
    "cp-analytics-mcp": {
      "type": "stdio",
      "command": "python3",
      "args": ["/Users/k0m0oxq/Desktop/repos/cp-platform/mcp/server.py"]
    }
  }
}
```

### BigQuery Environment

**Project:** `wmt-dsi-cally-audience-prd` · **Dataset:** `us_dv_custper_data_tables`

| Table | Notes |
|-------|-------|
| `market_research_panelist_demographic_mapped` | Demographics |
| `market_research_panelist` | Panelist master |
| `us_panel_demographic_txn_flatten_data` | Transactions — HUGE, ALWAYS date-filter |
| `market_research_survey_response` | Survey responses |
| `wmt-de-projects.ww_dv_shopper_app.sb_omni_upc_hrchy` | UPC hierarchy |

**SQL gotchas:**
- Timestamps are strings → `PARSE_DATE('%Y-%m-%d', col)`
- LPAD UPCs to 13 chars → `LPAD(CAST(upc AS STRING), 13, '0')`
- Active panelists → `state = 'REGISTERED'`
- Use `COUNT(DISTINCT panelist_id)`, not `COUNT(*)`
- Backtick fully-qualified names → `` `project.dataset.table` ``
- Income is a string range (e.g., `"50000-64999"`)
- Period notation: P3M, P6M, P12M, P18M

### RAG Architecture — Worklog

**Hierarchical context management** (GCC-inspired):

```markdown
# Worklog: BDV-XXXX

## Summary (ALWAYS READ FIRST ON RESUME)
- Status, complexity, ask, progress, key findings, next action, blockers

## Triage / Understanding / Plan / Execution Log / Delivery
[Detail sections, read on-demand]
```

The Summary is the entry point on resume — coarse metadata first, drill into detail only if needed.

- **Investigation Branches:** When a query returns 0 rows or unexpected results, an investigation block opens with a hypothesis, runs 5-minute exploratory queries, documents findings, and applies the learnings. Investigation branches are **never compressed** during rolling compression — they encode debugging knowledge.
- **Synthesis Checkpoints:** When Q2 depends on Q1, the dependency is documented explicitly:

```markdown
### Synthesis: Q1 → Q2
**From Q1:** Top 5 states: TX, CA, NY, FL, PA
**Feeds into Q2:** These values hardcoded into Q2 WHERE clause
```

For COMPLEX tickets (5+ queries), the worklog is compressed every 3 queries to prevent context degradation.

### Manifest.json Schema

The machine-readable source of truth:

```json
{
  "ticket_key": "BDV-XXXX",
  "ticket_status": "In Progress",
  "phase": "EXECUTE",
  "triage_result": "PROCEED",
  "complexity": "MODERATE",
  "retry_budget_remaining": 10,
  "queries": [
    {
      "id": "Q1",
      "name": "panelist_count",
      "status": "complete|failed|timeout|uncertain|planned",
      "row_count": 514,
      "bytes_scanned": "512MB",
      "retries_used": 0,
      "depends_on": null,
      "solved_at": "2026-06-01T14:32:00Z",
      "sources": [{"table_fqn": "...", "classification": "frozen", "last_modified": "..."}]
    }
  ],
  "sources_union": [],
  "investigations": [],
  "syntheses": [],
  "deliverables": [],
  "blockers": [],
  "next_action": "",
  "last_updated": "2026-06-01T14:32:00Z"
}
```

`worklog.md` is the human-readable narrative. Both files are updated atomically.

### Freshness Metadata

Each per-query `QN_name.meta.json` stamps:
- `solved_at` — ISO 8601 execution timestamp
- `sources[]` — each table with:
  - `table_fqn` — fully qualified name
  - `classification` — `frozen` (30-day budget) | `late_arriving` (24h) | `streaming` (1h)
  - `last_modified` — from BigQuery `__TABLES__` metadata

### Resume Protocol

If `worklog.md` exists when the skill starts:
1. Read the Summary section (fast scan) + `manifest.json`
2. Determine the current phase and query position
3. Log a resume entry to the worklog
4. Check for scope changes in ticket comments
5. Continue from the exact position — do **not** re-execute `COMPLETE` queries

### Ticket Types (10 Categories)

| # | Type | Example |
|---|------|---------|
| 1 | Panelist Enrichment | Add demographics to panelist list |
| 2 | UPC Lookup | Find panelists who purchased SKU X |
| 3 | Store Aggregation | Purchases by store/region |
| 4 | Demographics Match | Filter by HHI, age, gender |
| 5 | Date Range Filter | Activity within P3M/P6M/P12M |
| 6 | Count/Segmentation | How many panelists match criteria |
| 7 | Data Validation | Verify completeness or correctness |
| 8 | Feasibility/Pool Sizing | Is N-size achievable? |
| 9 | Panelist Pull | Extract matching panelist IDs |
| 10 | Ad-Hoc Query | One-off analytical asks |

### Scope Boundaries

**In Scope:** SQL extraction, BigQuery analytics, data validation, category/hierarchy analysis, metric computation.

**Out of Scope:** UPC recruitment (`/upc-recruitment`), demographic recruitment (`/demographic-recruitment`), pipeline creation, access provisioning, non-SQL tooling.

### Reference Files

```
bdv-solver/
  SKILL.md                       Main skill definition + trigger conditions
  references/
    execution-spec.md            Full per-phase execution workflow
    mcp-setup.md                 CP Analytics MCP config + tool reference
    quick-reference.md           Lookup tables (tables, columns, patterns)
    resume-protocol.md           Resume detection + state management
    tables-and-sql.md            SQL patterns + cost controls
    ticket-types.md              Ticket classification taxonomy
    triage-spec.md               Six triage gates (full spec)
    worklog-template.md          Worklog + manifest schema templates
```

### Cost & Resource Controls

- **40-min default timeout** (`run_query.py` polls every 5s, auto-cancels)
- **5-min timeout** for exploratory/investigation queries
- **Dry-run first** — if estimated scan > 50 GB, add a tighter filter
- **SELECT specific columns** — never `SELECT *` on large tables
- **BigQuery job ID logged** for audit trail

### Key Architectural Takeaways

1. **Hierarchical context management** — Summary for resume, detail on demand
2. **MCP as knowledge interface** — no hardcoded business logic or schemas
3. **Metadata-driven state** — `manifest.json` source of truth, `worklog.md` narrative
4. **Self-healing loops** — automatic retry with adjustment, capped budget
5. **Investigation branches** — exploratory queries encoded as debugging knowledge, never compressed
6. **Synthesis checkpoints** — data dependencies documented between queries
7. **Scope clarity** — flags out-of-scope tickets before investing execution time
8. **Append-only audit trail** — superseded queries kept with `superseded` status for full traceability
9. **Freshness metadata** — every result stamped with data classification and staleness budget

---

## 2. BDV Validator — Parallel Validation Dispatcher

**Skill:** `bdv-validator` (v4.0)
**Location:** `~/.wibey/skills/bdv-validator/`

### What it is

A **dispatcher skill** that validates a solved BDV ticket by launching 7 parallel sub-agents — each running an independent check and writing results to disk. The skill itself does not validate; it orchestrates, collects, and assembles.

**Critical constraints:**
- The skill itself runs NO MCP tools, reads NO SQL, executes NO queries — only dispatches
- Sub-agents require YOLO mode
- First tool call creates directories; second dispatches all 7 agents in parallel

### Workflow

1. **Prerequisite check** — confirm `ticket.json`, `worklog.md`, `results/manifest.json` exist
2. **Parallel dispatch** — launch 7 sub-agents in a single tool call
3. **Collect** — read 7 check artifact files from `validation/`
4. **Assemble** — compute overall verdict, write `validation/report.md`

### The 7 Checks

| # | Check | Validates |
|---|-------|-----------|
| 1 | Completeness | Did the solver answer WHO/WHAT/WHEN? Deliverables exist? |
| 2 | Definition Accuracy | Are business definitions correct per MCP? *(most critical)* |
| 3 | SQL Quality | Well-formed, cost-safe, follows patterns? |
| 4 | Result Verification | Results correct AND still reflective of current source? |
| 5 | Worklog Quality | Is solver documentation complete and useful? |
| 6 | End-to-End Coherence | Does ticket→plan→SQL→CSV→delivery tell one story? |
| 7 | Process Analysis | Did the solver actually follow the correct process? (JSONL ground truth) |

### Check Artifact Schema

Every sub-agent writes a check file with this exact structure:

```markdown
# Check N — Name
**Status:** PASS | WARN | FAIL | INCONCLUSIVE
**Date:** YYYY-MM-DD
**Ticket:** BDV-XXXX

## Finding
[1-2 sentence summary]

## Evidence
[Citations: file references, MCP responses, SQL quotes, JSONL entries]

## Steps Taken
[Numbered list of actions with exact tool calls]

## Recommendation
[PASS: "None"; WARN/FAIL: actionable item; INCONCLUSIVE: blocker]
```

### Check 2 — Definitions (Most Critical)

Verifies every SQL definition against MCP ground truth:
1. Extract tables, WHERE filters, JOINs, aggregations from `.sql` files
2. Verify tables via `cp_get_schema`
3. Verify business terms via `cp_get_domain_context`
4. Verify joins via `cp_get_join_path`
5. Build a SQL-vs-MCP comparison table

**Fail conditions:** wrong table, wrong filter, wrong join, or fabricated definition.

### Check 4 — Result Verification (Most Complex)

Produces **two independent verdicts**:

| Verdict | Cost | What it checks |
|---------|------|----------------|
| Internal Consistency | Free | Saved CSVs agree with each other |
| Source Consistency | $$ | Saved CSVs match a live source re-run |

**Overall status = the worse of the two.**

**Tolerance tiers:**

| Metric type | PASS | WARN | FAIL |
|-------------|------|------|------|
| Monetary | ±0.5% | 0.5–2% | >2% |
| Count | ±2% | 2–10% | >10% |
| Percentage | ±0.5pp | 0.5–2pp | >2pp |

**Staleness check:** compute `solve_age_days`, query source `__TABLES__`, classify (frozen 30d / late_arriving 24h / streaming 1h).

**Cost guard:** dry-run before executing; skip re-runs >5 GB unless a monetary headline mandates it.

### Check 3 — SQL Quality Anti-Patterns

| Pattern | Verdict |
|---------|---------|
| `SELECT *` | FAIL |
| Unfiltered large table | FAIL |
| Dry-run >100 GB | FAIL |
| Dry-run >50 GB | WARN |
| Missing backticks | WARN |
| UPC not LPAD'd | WARN |
| `COUNT(*)` instead of `COUNT(DISTINCT)` | WARN |

### Check 7 — Process Analysis (JSONL Ground Truth)

**Critical:** Never `Read` JSONL files (50K–100K+ lines). Use `Grep` exclusively.

1. `Glob` session files → `Grep` for ticket ID
2. Extract MCP calls (`mcp__plugin__wibey_cp-analytics-mcp__`)
3. Extract SQL executions (`run_query.py`)
4. Build an ordered timeline
5. Verify the expected order: Read ticket → MCP → SQL → Bash → Read CSV
6. Scan for guessing language ("I'll assume", "likely", "probably")
7. Compute metrics: MCP calls, SQL executions, dry-runs, retries, guessing signals

**FAIL:** no MCP calls, fabricated claims, or SQL before MCP.
**INCONCLUSIVE:** session logs not found.

### Reference Files

```
bdv-validator/
  SKILL.md                       Dispatcher logic + 7-agent launch contract
  references/
    artifact-schema.md           Check file format (required for every agent)
    check-1-completeness.md      WHO/WHAT/WHEN ask mapping
    check-2-definitions.md       MCP-verified definition accuracy
    check-3-sql-quality.md       Anti-patterns + dry-run cost gates
    check-4-result-verification.md  Internal + source consistency (dual verdict)
    check-5-worklog-quality.md   Required sections + substantiveness
    check-6-coherence.md         End-to-end pipeline trace
    check-7-process-analysis.md  JSONL session log ground truth
```

### Output

`tickets/BDV-XXXX/validation/report.md` containing:
- Overall verdict: **PASS** | **WARN** | **FAIL**
- Per-check summary table
- All 7 check artifacts linked

---

## 3. BDV Presenter — Stakeholder Deliverable Packager

**Skill:** `bdv-presenter` (v1.0)
**Location:** `~/.wibey/skills/bdv-presenter/`

### What it is

Packages a validated BDV result into a stakeholder-ready deliverable with audience-adaptive language, self-contained HTML, and an AI-slop scrubber pass.

**Critical constraints:**
- NEVER rewrites original artifacts (`results/`, `attachments/` are read-only)
- NEVER issues pass/fail verdicts (that is the validator's job)
- REFUSES to build on stale/unvalidated results unless `--force`
- No Playwright, no Jira MCP, no fetch-ticket

### Workflow — 8 Phases

| Phase | Action |
|-------|--------|
| 0 | Precheck + validation gate (STOP if FAIL or Check 4 WARN/FAIL) |
| 1 | Re-extract ask from `ticket.md/json` (NOT from solver's worklog) |
| 2 | Detect audience (business default; engineer if ≥2 eng signals) |
| 3 | Inventory + copy artifacts → `deliverable/artifacts/` |
| 4 | Generate README.md + ask-coverage.md + stakeholder-notes.md |
| 5 | Render self-contained HTML with inline SQL evidence |
| 6 | Dispatch slop-scrub sub-agent; re-render HTML |
| 7 | Hand-off summary printed to user |

### Phase 0 — Validation Gate (Enforced)

| Condition | Action |
|-----------|--------|
| `validation/report.md` missing | STOP — tell user to run `/bdv-validator` |
| Overall == FAIL | STOP unless `--force` |
| Check 4 Source Consistency == WARN or FAIL | STOP unless `--force` |
| `solved_at` missing or staleness budget exceeded | STOP unless `--force` |

### Phase 1 — Ask Extraction Rules

Re-derive the **literal** ask independent of solver interpretation:
1. Quote verbatim — no paraphrasing
2. Split compound questions
3. Include implicit asks ("we need to understand X" → "What is X?")
4. Preserve order
5. Each acceptance criterion is a separate ask
6. **Ignore solver narrative** in `worklog.md`

**Drift check:** Compare against the worklog Understanding. If the solver diverged, surface it in Caveats — do not silently align.

### Phase 2 — Audience Detection

**Default: business** (~99% of BDV tickets). Override to engineer if ≥2 engineer signals AND zero business signals.

| Signal | Business | Engineer |
|--------|----------|----------|
| Reporter | PM, researcher | Data engineer |
| Labels | product, research | engineering, data-eng |
| Body | "we need to understand" | technical spec |
| Attachments | docs, screenshots | .sql, DDL |

**Tone differences:**
- **Business:** plain language, define every term, no table names in prose, lead with the answer, thousands separators, omit Artifacts/Validation/How-To-Read sections
- **Engineer:** technical detail welcome, reference tables/columns, SQL snippets OK, schema-quirk caveats

### Folder Versioning

Prior deliverables are never overwritten (the user may have shared them):

```
deliverable/      → first run
deliverable-v2/   → second run
deliverable-v3/   → third run
...
```

**Algorithm:** list existing `deliverable*` folders, parse the highest N, use N+1.

### Generated Documents

**README.md** — engineer template (business strips Artifacts/Validation/How-To-Read):
```
# BDV-XXXX — <Summary>
**Requested by:** X  |  **Delivered:** YYYY-MM-DD  |  **Validation:** PASS/WARN

## TL;DR  (headline bullets)
## The Ask  (verbatim questions)
## What We Found  (1 paragraph per question + cited artifact)
## Artifacts  (file table)
## Validation Status  (✅/⚠️/❌ + freshness: solved_at, source last_modified, staleness budget)
## How To Read This
## Coverage & Caveats  (links to ask-coverage.md + stakeholder-notes.md)
```

**ask-coverage.md** — gap-aware coverage table:
```
| # | Question | Answered By       | One-line Answer |
| 1 | <verbatim> | artifacts/Q1.csv | <answer>        |
| 3 | <verbatim> | GAP              | <why unanswered>|
```

**stakeholder-notes.md** — Assumptions, Definitions, Caveats, Suggested Follow-ups.

### Authoring Rules

- No emoji in body text (status icons in header only)
- No hedging in the TL;DR ("may", "might", "could")
- No filler ("It is important to note that…")
- All numbers carry units ("12.4%", "1,247 panelists")
- Every claim cites an artifact

### HTML Rendering

Self-contained — no external CSS/JS. Methods:
1. **Python `markdown` module** (preferred) via Bash, with `tables` + `fenced_code` extensions
2. Hand-rendered fallback

**Inline SQL evidence blocks** — for each finding, render a collapsible block:
```html
<details>
<summary>SQL — Q#: <description></summary>
<pre><code>-- Full SQL from artifacts/Q#_*.sql
SELECT ...
</code></pre>
</details>
```

For the **business audience**, SQL blocks REPLACE CSV file references as the provenance layer.

**Verification:** file non-empty, no `<script>`, no external `href`/`src`, all 3 sections present, every finding has ≥1 SQL block.

### Phase 6 — Slop Scrub

A dispatched sub-agent strips AI-slop from the generated docs:

| Cut | Preserve |
|-----|----------|
| Filler openers ("It is important to note that…") | All numbers, units, dates, filenames |
| Hedging in headlines ("may", "might", "could") | Document structure |
| Empty intensifiers ("very", "really") | Verbatim ticket questions |
| Generic phrasings ("a number of" → count) | Real caveats (sample size, date range) |
| Repeated headers | Validation Status section |
| Bullet bloat (>5 tautological items) | — |

**Tone targets:**
- Business: a busy PM grasps the headline in 10 seconds; sentences ≤25 words; paragraphs ≤4 sentences
- Engineer: same brevity, technical detail welcome

Output overwrites the 3 Markdown files in place; HTML is then re-rendered.

### Phase 7 — Hand-off

Prints to user:
- Deliverable folder path
- Ask coverage (N of M answered, gaps flagged)
- Validation status (Overall + Check 4 Source Consistency)
- Freshness (solved_at + oldest source last_modified)
- Any Phase 0 gate bypass notes

### Reference Files

```
bdv-presenter/
  SKILL.md                       8-phase orchestrator + gate enforcement
  references/
    ask-extraction.md            Literal ask derivation (no solver bias)
    audience-detection.md        Business vs engineer routing rules
    versioning.md                deliverable-vN folder algorithm
    readme-template.md           README + ask-coverage + stakeholder-notes templates
    html-rendering.md            Self-contained HTML + inline SQL evidence
    slop-scrub-spec.md           AI-slop removal rules
```

### Folder Contract

```
tickets/BDV-XXXX/
  ticket.json, ticket.md, attachments/    [INPUT]
  worklog.md, results/                    [INPUT — read-only]
  validation/report.md                    [INPUT — optional but gated]
  deliverable/ (or -v2, -v3, ...)         [OUTPUT]
    README.md, README.html
    ask-coverage.md
    stakeholder-notes.md
    artifacts/                            [COPIES of result files]
```

---

## Cross-Skill Architecture

### Pipeline Invariants

1. **Solver → Validator → Presenter** — strict order; the presenter's Phase 0 gate enforces that the validator ran first
2. **Validation verdict propagation** — Check 4 Source Consistency surfaces independently in the presenter hand-off
3. **Append-only audit** — solver superseded queries kept; validator artifacts immutable; presenter versions never overwrite
4. **Read-only inputs** — each downstream skill treats upstream artifacts as immutable

### Shared Architectural Patterns

| Pattern | Solver | Validator | Presenter |
|---------|--------|-----------|-----------|
| MCP as knowledge layer | ✅ understanding | ✅ check 2 verification | ❌ (uses solver outputs) |
| Parallel sub-agent dispatch | ❌ | ✅ 7 agents | ✅ 1 slop-scrub agent |
| Machine + human state files | manifest.json + worklog.md | per-check artifacts + report.md | versioned deliverable + HTML |
| Cost gates | dry-run + 50 GB filter | dry-run + 5 GB skip | n/a |
| Freshness metadata | stamps on solve | verifies vs budget | surfaces in hand-off |
| Append-only / versioned | superseded queries | immutable artifacts | deliverable-vN |
