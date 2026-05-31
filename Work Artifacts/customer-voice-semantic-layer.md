# Customer Voice Semantic Layer — Hybrid Orchestrator with Auto-Updating Model

**Repo:** `~/Desktop/repos/customer-voice-semantic-layer`

## What it is

A governed Cube.js semantic layer over Customer Voice / Customer Spark BigQuery data, paired with a raw SQL path and a reconciliation engine that auto-improves the model over time.

**Scale:**

- 1.1M panelists (~773K active)
- 158M task rows
- 32K surveys
- 23 cube definitions across 5 domains

## The Hybrid Orchestrator

Every user question dispatches two parallel sub-agents simultaneously:

```
User question ("How many active panelists?")
    ↓
cp-hybrid orchestrator skill (LLM)
    │
    ├─→ Path A: customer-voice-semantic-layer skill
    │       └─→ Cube.js (port :4000)
    │           Governed, pre-modelled, fast,
    │           row-capped at 5K, PII-protected
    │
    └─→ Path B: cp-discovery-bq skill
            └─→ bq-proxy (port :5050)
                Raw SQL, context-engineered, unrestricted
    ↓
Reconciliation classifier (0.5% tolerance)
    ↓
Confidence-badged answer
```

**Why dual paths?** A Cube-only system means you don't know what questions you can't answer. A raw-SQL-only system requires user GCP credentials and produces risky LLM-generated queries. Hybrid is best of both — no user permissions required.

## Reconciliation verdicts

Every answer is tagged with one of:

| Verdict | Meaning |
|---------|---------|
| `SAME_INTENT_SAME_RESULT` | ✓ verified by both paths |
| `COVERAGE_GAP` | ⚠ Cube didn't cover this; raw path used |
| `AMBIGUOUS_QUESTION` | question was unclear; results differ |
| `SAME_INTENT_DIFFERENT_RESULT` | ! paths disagreed; diagnostic shown |
| `LLM_FAILURE` | one path errored |

Numeric tolerance: **0.5% relative difference**.

## The Auto-Update Loop (Phase 3)

Every orchestrator run writes structured trace records to `~/.wibey/logs/cp-hybrid/coverage-gaps.jsonl`. A weekly driver reads this log and:

1. **Clusters gaps** by `(missing_from_cube, raw_table, columns_used)` → deterministic SHA256 `cluster_id`
2. **Triggers** when the same concept appears ≥3 times from ≥2 distinct users in 7 days
3. **Synthesizes** a candidate YAML measure via the `cube-gap-filler` skill, seeded with raw SQL + expected value + table FQN
4. **Validates** that the YAML parses and conforms to style (`validate_cube.py`)
5. **Equivalence test** — loads proposed YAML into local Cube, compiles to SQL, executes against BigQuery, compares value to reference raw SQL. Must match within 0.5%.
6. **Opens a draft PR** on the semantic layer repo with full provenance: cluster ID, redacted user questions, equivalence proof table, failure logs

## Safety rails

- All PRs are **draft** (a human must mark Ready for Review)
- **Max 2 PRs/day** so reviewers aren't overwhelmed
- **No PR without equivalence proof** — numerical match is non-negotiable
- **Hard constraints:** only ADD new measures (never modify existing), only `model/*.yml` files touched, never delete
- **CI guard workflow** asserts PR is draft, body has an equivalence table, no removals
- Behind env flag `CP_AUTO_IMPROVE_ENABLED=true` (default off)
- Privacy redaction on user questions before logging

## Result

The Cube model converges toward the actual user question space without manual guessing. The semantic layer becomes self-improving — every coverage gap a user hits is a candidate for being modelled into the layer next week.

## What's modelled

23 cubes across 5 categories:

| Category | Coverage |
|----------|----------|
| Panelist lifecycle | REGISTERED, INVITED, and other lifecycle states |
| Task/survey pipeline | 158M rows — completion, response, dropout rates |
| Rewards & billing | CPC, margin |
| Recruitment & audience | waitlist, audiences, projects |
| Operational & data quality | operational health, data quality checks |
