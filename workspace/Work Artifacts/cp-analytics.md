# CP Analytics — Autonomous Multi-Hypothesis Analysis Orchestrator

**Skill:** `cp-analytics` (paired with `cp-audit`, `cp-fix`, `cp-context-validate`)

## What it is

A fully autonomous analysis orchestration skill for Walmart Customer Perception (CP / Customer Spark) data. It transforms plain-English questions from PMs and researchers into reproducible, audited SQL analyses with charts, structured findings, and auto-generated follow-up hypotheses.

**Target users:** PMs, researchers, and analysts without SQL expertise who need systematic multi-hypothesis investigation of panelist behavior, surveys, recruitment funnels, and reward economics.

## The orchestrator pattern

The skill is a **pure orchestrator** — it never runs Bash directly, only Read/Write/Glob/Grep/Task. Each analytical idea is dispatched to a Task sub-agent with its own isolated context. This matters for three reasons:

1. **Context isolation** — large SQL results from one idea don't pollute another's reasoning
2. **Autonomy** — sub-agents execute BigQuery commands without triggering CLI safety prompts (the orchestrator stays Bash-free)
3. **Crash recovery** — `session.json` + `backlog.json` survive any failure; `/cp-analytics resume` detects mid-flight crashes and recovers

## Execution phases

```
Phase 1: LOAD          → Read domain.md, tables.md, backlog.json; scan reports/
Phase 2: PRE-PROCESS   → Auto-correct state names (COMPLETE→QUALIFIED), table names,
                         vague terms; sharpen denominators; write corrections artifact
Phase 3: EXECUTE LOOP  → Per idea: PRE-DISPATCH CHECKPOINT → DISPATCH sub-agent →
                         POST-DISPATCH VALIDATION → REFLECT scoring → depth dive
Phase 4: GENERATE      → When backlog exhausted, generate 10 deduplicated new ideas
Phase 4.5: RESUME      → Detect crashed sessions, validate partial reports, reset state
Phase 5: WRAP UP       → Session summary, update session.json status='completed'
Phase 5.5: REBUILD     → MANDATORY: regenerate INDEX.md from scratch across all dates
```

## REFLECT scoring (the depth-first decision engine)

After each idea completes, findings are scored:

**Score = Impact × Surprise × Gaps**

| Factor | Values |
|--------|--------|
| **Impact** | 1 (<1K panelists), 2 (1K-50K), 3 (50K+) |
| **Surprise** | 1 (expected), 2 (somewhat unexpected), 3 (contradicts assumptions) |
| **Gaps** | 0 (actionable, no "why?") or 1 (unanswered "why?") |

If the score is ≥4, the orchestrator **immediately** generates a depth idea (e.g., `IDEA-002 → IDEA-002-D1 → IDEA-002-D1-D2`) and executes it before moving to the next top-level idea. Depth stops at `max_depth`, when findings are directly actionable, or when no additional tables would help.

## SQL traceability as a contract

Every analysis produces `execution.json` with **complete, copy-paste executable SQL** for every query. Post-Dispatch Validation enforces this:

- Every `query` field must contain a fully-qualified table reference (`` `wmt-dsi-cally-audience-prd...` ``)
- Must NOT contain ellipses, pseudo-code, or "same as step 1"
- Must be longer than 50 characters (real SQL never is shorter)

**Violations are blocking errors** — the idea is marked `error` and doesn't proceed. This makes every number in every report traceable back to runnable SQL.

## Output contract per idea

```
reports/YYYY-MM-DD/IDEA-XXX_slug/
├── report.md           # Narrative (executive summary, methodology, findings,
│                         recommendations, data discovery, full SQL, follow-ups)
├── findings.json       # Structured findings with severity, tags, evidence chain
├── execution.json      # SQL traceability — every query in full
├── data/01_*.csv       # Per-step CSV outputs
└── charts/01_*.png     # Walmart-colored matplotlib charts (150 DPI)
```

## Idea generation (when backlog exhausted)

The orchestrator collects all existing questions, identifies gaps (tables never analyzed, under-explored categories, recommendations to validate), generates 15 candidates, deduplicates, and keeps the best 10. Each is tagged with `spawned_from='auto_generation_round_N'`. New ideas aren't executed in the same session — they're queued for the next invocation.

## The audit/fix ecosystem

Related skills that compose with cp-analytics, each doing one thing.

### cp-audit — 6-layer validator

Validates completed analyses across:

1. **SQL Schema** — column existence, types, joins, state values, timestamp parsing
2. **SQL Logic** — denominator correctness, NULL handling, GROUP BY granularity
3. **Interpretation** — numbers match CSVs, direction correct, no causation overreach
4. **Prose Arithmetic** — percentage verification, breakdown sums, "N of M" consistency
5. **Cross-Analysis** — contradictory findings across reports, metric drift
6. **Evidence Chain** — file references, CSV-finding alignment, SQL completeness
7. **Reproducibility** — billing project, table qualification, deterministic results

Verdicts: PASS / WARN / FAIL.

### cp-fix — Autonomous remediation

Consumes audit findings and fixes them in dependency order:

| Fix type | Action |
|----------|--------|
| `sql_rewrite` | re-execute → replace CSV → recalculate metrics |
| `recalculation` | recompute from CSV → update findings + report |
| `artifact_repair` | reconstruct missing SQL from report context |
| `limit_expansion` | re-execute with a broader limit |
| `narrative_rewrite` | fix causation overreach, prose arithmetic |
| `chart_regeneration` | rebuild charts with corrected data |

Snapshots originals to `.fix/pre_fix/` before modifying. Verifies every Edit/Write actually landed by re-reading and grepping. Re-dispatches cp-audit after fixes to verify resolution.

### cp-context-validate — Schema ground truth

Regenerates `schema.json` from `INFORMATION_SCHEMA.COLUMNS` on every run. Validates `domain.md` and `tables.md` against BigQuery reality (column existence, enum values, join paths, table inventory, DDL cross-reference). Prevents context drift.

## How it differs from sibling skills

| Skill | Focus | Autonomy | Output |
|-------|-------|----------|--------|
| **cp-analytics** | Multi-hypothesis exploration with depth dives | Fully autonomous | Reproducible analyses + auto-generated follow-ups |
| **cp-discovery-bq** | One-shot SQL question answering | Fully autonomous | Raw results + SQL |
| **cp-business-simple** | Self-service for non-technical users | Fully autonomous | Dashboard-ready metrics |
| **cp-hybrid** | Flexible with human checkpoints | Human-in-the-loop | Analyses + review points |
| **cp-audit** | Validates completed analyses | Fully autonomous | Verdicts + structured issues |
| **cp-fix** | Remediates audit findings | Fully autonomous | Fixed reports + re-audit |

## Key design decisions

1. **Bash-free orchestrator** — sub-agents handle all execution; the orchestrator coordinates only. Avoids constant CLI safety prompts on read-only SELECTs.
2. **SQL traceability enforced as a contract** — not optional documentation; an idea fails validation without it.
3. **REFLECT scoring drives depth-first exploration** — an automatic decision on whether to dive deeper, no human choice required.
4. **Session state in JSON, not memory** — crash recovery is a primary feature, not a bolt-on.
5. **INDEX.md regenerated from scratch every session** — prevents stale dashboards; reflects full platform state across all dates.
6. **Static context files as a RAG replacement** — `domain.md` + `tables.md` + `schema.json` passed in full to every sub-agent dispatch. No retrieval gymnastics.
7. **Composable ecosystem** — cp-analytics produces, cp-audit validates, cp-fix remediates, cp-context-validate maintains ground truth. Each skill does one thing.

## Why it matters

Most "AI analyst" tools answer one question at a time. CP Analytics treats analysis as a **systematic exploration problem**: every finding spawns hypotheses, every hypothesis becomes a queued analysis, every analysis is validated and fixed automatically. Over hundreds of completed analyses, the system builds a compounding knowledge base — and the SQL traceability contract ensures every number is auditable back to its source query.
