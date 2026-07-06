# CP Hybrid — Two-Path Customer Voice Analytics Orchestrator

> ## ⚡ INTERVIEW CHEAT SHEET — Architecture (BCG X / Maan · today)
>
> *Morning-of architecture anchor for the hybrid orchestrator / self-growing semantic layer. This is a **depth-reserve build** — a one-liner you mention only if relevant, never one of the two leads (Jira + Analyst). But if Maan probes "how do you trust a metric?" or "what about the semantic layer?", this is the build that wins the room. Glance, don't read.*
>
> **One-liner:** A dual-backend analytics orchestrator — runs the **Cube.js semantic layer and raw BigQuery SQL in parallel**, reconciles the two answers, and turns every disagreement into labeled data for the semantic layer.
>
> **The 30-second architecture (drawable):**
> ```
> question → ORCHESTRATOR
>               │ dispatches BOTH in one message (parallel, not sequential)
>        ┌──────┴──────┐
>        ▼             ▼
>   Cube.js          raw SQL          ← two independent paths, same question
>   (curated         (exploratory
>    semantic layer)  ground truth)
>        └──────┬──────┘
>               ▼
>        RECONCILE — 5-category classifier
>        (verified · divergent · ambiguous · coverage-gap · both-error)
>               │ coverage gap →
>               ▼
>        cp-hybrid-propose → human approves YAML edit → PR → semantic layer grows
> ```
>
> **The 4 design decisions Maan will probe — lead with the architectural reason:**
>
> 1. **Why two paths at all?** — "A semantic layer gives curated, governed answers; raw SQL gives exploratory truth. Running both and reconciling means a disagreement *exposes a modeling bug* instead of silently shipping a wrong number. The divergence is the signal." Reconcile to a **0.5% tolerance**.
> 2. **Why a *fixed* 5-category classifier, not free-form reconciliation?** — A strict taxonomy (verified / divergent / ambiguous / coverage-gap / both-error) keeps the orchestrator deterministic. "New category? You extend the spec doc, you don't let the LLM invent one mid-run." Deterministic where I can verify; agent only where input varies.
> 3. **Why is the auto-improve loop *gated*?** — Coverage gaps feed `cp-hybrid-propose`, which drafts a Cube.js YAML edit — but **a human approves every edit before it merges.** *"The capability to self-improve is built; deployment is deliberately gated behind an env flag until the org trusts the loop."* Capability ready, trust earned incrementally.
> 4. **Why durable-local + best-effort BQ mirror (two stores)?** — File-locked JSONL is the canonical record (atomic, survives network loss); the BQ mirror enables cross-session observability without coupling the user's UX to the network. Local write succeeds first, always.
>
> **Gate / abstain / failure-mode lines (have all three):**
> - **Gate:** the human approves every semantic-layer edit; cp-hybrid only *detects and recommends*. A dedup ledger stops processed gaps from re-surfacing (no review fatigue).
> - **Abstain:** when both paths error it returns `both_error` and asks the user to retry — it never fabricates a reconciled number. When the question is ambiguous it presents both answers and asks for intent, rather than picking one.
> - **Failure mode I worry about most:** **confident-wrong from a single path** — a clean Cube measure built on a wrong filter. The whole point of the second path is to catch exactly that before it reaches a stakeholder.
>
> **The self-monitoring detail Maan will appreciate (PhD scientist — likes built-in instrumentation):** the orchestrator checks its *own* parallelism. If `cube_latency + raw_latency ≈ total` (instead of `max + overhead`), the dispatch accidentally went sequential — it records `parallelism_degraded: true`. The system measures whether it actually did the thing it claims to do.
>
> **The substrate through-line (ties it back to the platform thesis):** *"Same context substrate as the Jira agent and the analyst — but here validation sits between two paths, and disagreements become training data. One reusable layer; this is just the next thin thing on top of it."*
>
> **If he says "draw it"** → the fork-and-reconcile diagram above. 5 boxes, 60 sec. The money beat is the **coverage-gap → human-gated PR loop** — that's what makes it a *self-growing* semantic layer, not just a checker.
>
> ---

**Skill:** `cp-hybrid` (v0.1)
**Location:** `~/.wibey/skills/cp-hybrid/`

## What it is

A **hybrid analytics orchestrator** that answers Customer Voice questions by running **Cube.js semantic layer queries and raw BigQuery SQL queries in parallel**, then reconciling their answers. It surfaces verified results, flags divergences with diagnostics, and detects coverage gaps that feed a model-improvement workflow.

**Value proposition:**
- Verifies metric consistency across two independent paths
- Surfaces divergences with diagnostic reasoning (filter mismatch, join cardinality, grain)
- Detects coverage gaps and routes them to product-team review
- Requires zero GCP credentials from the user — everything flows through authenticated backends

---

## Workflow — 5 Steps

### Step 1: JWT Mint

Before sub-agent dispatch, mint short-lived tokens for both backends:

```bash
TOKEN=$(node -e "console.log(require('jsonwebtoken').sign({sub:'$USER',role:'analyst'},'dev-secret-change-me',{expiresIn:'600s'}))")
export CUBEJS_API_SECRET="dev-secret-change-me"
export BQ_PROXY_TOKEN="$TOKEN"
```

### Step 2: Parallel Sub-Agent Dispatch

Two sub-agents run **concurrently in a single tool-call batch**:

| Agent | Backend | Path | Token |
|-------|---------|------|-------|
| `customer-voice-semantic-layer` | Cube.js (`localhost:4000`) | Semantic layer | `CUBEJS_API_SECRET` |
| `cp-discovery-bq` | bq-proxy (`localhost:5000`) | Raw SQL | `BQ_PROXY_TOKEN` |

**Parallelism requirement:** Both must be in the **same message**. Separate messages execute sequentially and double latency.

**Latency diagnostic:** If `cube_latency_ms + raw_latency_ms ≈ total_latency_ms` (instead of `max(...) + overhead`), record `parallelism_degraded: true` in the reconciliation record for monitoring.

### Step 3: Reconciliation — 5-Category Classifier

| Category | Cube | Raw | Action |
|----------|------|-----|--------|
| `SAME_INTENT_SAME_RESULT` | ok | ok (≈) | Present A: "✓ verified by both paths" |
| `SAME_INTENT_DIFFERENT_RESULT` | ok | ok (≠) | Present BOTH + diagnostic checklist (filters, joins, grain, nulls) |
| `AMBIGUOUS_QUESTION` | ok | ok (≠) | Present BOTH + ask user to clarify intent |
| `COVERAGE_GAP` | error | ok | Present B: "⚠ exploratory — not in cube model" |
| `LLM_FAILURE` | error | error | Surface both errors; ask user to retry |

> **Strict rule:** Never invent new categories in the orchestrator — extend `docs/architecture/reconciliation.md` instead.

### Step 4: User-Facing Response

**Verified:**
```
**Active panelists: 773,142**  ✓ verified by both paths

Cube.js:  Panelists.active_count = 773,142    (1.2s)
Raw SQL:  COUNT(panelist_id) WHERE state='REGISTERED' = 773,142    (3.5s, 1.4 GB)
```

**Divergent:**
```
**⚠ Two paths disagree on 'completion rate this month'**

Cube.js:  Tasks.completion_rate = 56.7%
Raw SQL:  COUNT(state IN (...)) / COUNT(*) = 58.1%

Likely cause: cube measure includes 'OQ' state, raw SQL includes only
'QUALIFIED' + 'COMPLETED'. (Difference: 1.4 percentage points.)
```

### Step 5: Trace Logging (Phase 2 Observability)

Every run emits structured records for audit + model improvement.

**Trace ID stickiness:** Reuse `WIBEY_SESSION_ID` if set; otherwise `uuidgen`. Both sub-agents propagate it via the `X-Trace-Id` header.

**Record kinds:**

| Kind | Emitted by | Purpose |
|------|------------|---------|
| `path_execution` | Each sub-agent | Per-path latency, success, bytes scanned |
| `reconciliation` | Orchestrator | Final verdict, values, delta, reasoning |
| `decision` | Orchestrator | Divergence diagnostic OR coverage-gap recommendation |

**Valid verdicts:** `verified`, `divergent`, `cube_only`, `raw_only`, `both_error`.

---

## Data Flow & Storage

### Local JSONL (Source of Truth)

```
~/.wibey/logs/cp-hybrid/
  trace.jsonl              All records — durable, file-locked
  divergences.jsonl        Mirror: divergence decisions → weekly backlog
  coverage-gaps.jsonl      Mirror: coverage-gap decisions → model improvements
  processed-gaps.jsonl     Dedup ledger (prevents gap re-surfacing)
  rollups/
    2026-06-01.json        Daily aggregate
    2026-W22.md            Sunday weekly digest
```

All writes are atomic via `fcntl.flock()` — safe across concurrent sessions.

### BigQuery Mirror (Best-Effort)

After the local write succeeds, `log_trace.py` POSTs to bq-proxy:

| Table | Records |
|-------|---------|
| `wmt-de-projects.sbx_kanu.customer_voice_semantic_layer_trace` | All reconciliation records |
| `wmt-de-projects.sbx_kanu.customer_voice_semantic_layer_additions` | Coverage gaps as `gap_detected` events |

**Best-effort contract:** Expired tokens or proxy outages log warnings to stderr but never block. Local JSONL is always written first and is the canonical record.

---

## Implementation

### `scripts/log_trace.py` — Trace Logging Engine

**Atomic JSONL writer + selective BQ mirror.**

| Feature | Detail |
|---------|--------|
| File locking | `fcntl.flock()` for concurrent-safe append |
| Auto-enrichment | Adds `ts`, `host`, `os_user`, `trace_id` to every record |
| Selective mirror | Hoists known columns to BQ schema; remainder as JSON blob |
| Decision routing | Divergence → `divergences.jsonl`; coverage gap → `coverage-gaps.jsonl` + `additions` table |
| Best-effort BQ | Failures → stderr warning; never raises |

**Usage:**
```bash
log_trace.py --trace-id <id> --kind <reconciliation|decision|path_execution> --json '<JSON>'
```

**Environment:**
- `CP_HYBRID_LOG_DIR` — override log directory (default `~/.wibey/logs/cp-hybrid`)
- `BQ_PROXY_URL` — proxy endpoint (default `http://localhost:5000`)
- `BQ_PROXY_TOKEN` — JWT (no BQ mirror if unset)
- `CP_HYBRID_BQ_OFF=1` — disable BQ mirror (used in tests)

### `scripts/cp_hybrid_rollup.py` — Daily + Weekly Aggregation

| Feature | Detail |
|---------|--------|
| Time window | `--since 24h` or `--since 7d` |
| Verdict tally | `{verified, divergent, cube_only, raw_only, both_error}` |
| Latency percentiles | P50/P95 for Cube and raw paths |
| Top divergences | Ranked causes (filter mismatch, join cardinality, etc.) |
| Top coverage gaps | Ranked missing concepts |
| Sunday digest | Auto-emits weekly markdown (`YYYY-Www.md`) |

**Sample output:**
```json
{
  "verdict_counts": {"verified": 18, "divergent": 5, "cube_only": 2},
  "cube_latency_ms": {"p50": 1234, "p95": 3456, "n": 25},
  "raw_latency_ms":  {"p50": 2100, "p95": 5200, "n": 25},
  "top_divergence_causes": [
    {"cause": "filter mismatch", "n": 3},
    {"cause": "join cardinality", "n": 2}
  ],
  "top_coverage_gaps": [
    {"missing": "survey_response_time", "n": 2}
  ]
}
```

### Tests

| File | Coverage |
|------|----------|
| `test_log_trace.py` | Append correctness, unknown-kind rejection, divergence/gap mirroring, 8-thread concurrent-write safety (20 records, no corruption) |
| `test_cp_hybrid_rollup.py` | Verdict aggregation, time-window filtering, divergence cause ranking |

---

## Integration: `cp-hybrid-propose` Feedback Loop

Coverage gaps create a closed-loop model-improvement workflow:

```
cp-hybrid detects gap
  ↓ writes coverage-gaps.jsonl + additions table
cp-hybrid-propose reads v_pending_additions
  ↓ shows gap + proposed Cube.js YAML edit to product team
Human approve / reject / edit / skip
  ↓ approved edits
PR draft on model-improvement/<date>-<slug> branch
  ↓ merge
processed-gaps.jsonl ledger updated (prevents re-surfacing)
```

The **human is always the gate** — cp-hybrid only *detects* and *recommends*. The dedup ledger ensures rejected/processed gaps don't resurface unless explicitly cleared.

---

## Architecture Patterns

| Pattern | Why it matters |
|---------|----------------|
| **Two-path verification** | Semantic layer for curated answers + raw SQL for exploratory truth. Divergences expose modeling issues. |
| **Fixed category classifier** | 5 categories only — a strict taxonomy prevents ad-hoc reconciliation logic |
| **Durable local + best-effort mirror** | Local JSONL is canonical; BQ enables cross-session observability without coupling user UX to the network |
| **Trace ID stickiness** | `WIBEY_SESSION_ID` propagates via `X-Trace-Id` headers to correlate sub-agent records |
| **Coverage-gap feedback loop** | Detected gaps flow to product review → approved edits → Cube model improvements |
| **Parallelism enforcement** | Sub-agents MUST dispatch in a single message; latency sum vs. max is a self-check signal |

---

## Safety & Security

- **No GCP credentials** required from the user — the Cube.js token + bq-proxy JWT handle all access
- **Never expose internal SQL** unless the user asks for "the query"
- **Aggregate data only** — never return individual panelist records
- **Bounded retries** — surface clear errors after 2 failed attempts; don't loop silently

---

## Service Endpoints

| Service | URL | Auth |
|---------|-----|------|
| Cube.js | `http://localhost:4000/cubejs-api/v1/load` | `CUBEJS_API_SECRET` |
| bq-proxy | `http://localhost:5000/sql` | `BQ_PROXY_TOKEN` (JWT) |

---

## Directory Structure

```
~/.wibey/skills/cp-hybrid/
  SKILL.md                       Orchestrator workflow + reconciliation logic
  scripts/
    log_trace.py                 Atomic JSONL writer + BQ mirror
    cp_hybrid_rollup.py          Daily/weekly aggregation
    test_log_trace.py            Trace logging tests
    test_cp_hybrid_rollup.py     Rollup aggregation tests
```

---

## Sample Prompts

- "How many active panelists do we have?"
- "Show completion rates by task type this quarter"
- "Compare panel size by state — make sure both paths agree"

---

## Key Architectural Takeaways

1. **Parallel two-path orchestration** — Cube + raw SQL run concurrently; reconciliation classifies the result
2. **Strict 5-category taxonomy** — verified, divergent, ambiguous, coverage-gap, failure
3. **Durable local logging with best-effort BQ mirror** — file-locked JSONL is canonical
4. **Distributed tracing** — `X-Trace-Id` propagation correlates orchestrator + sub-agent records
5. **Closed-loop model improvement** — coverage gaps feed `cp-hybrid-propose` → product review → PR
6. **Self-monitoring parallelism** — a latency-sum heuristic flags accidentally-sequential dispatch
7. **Dedup ledger** — processed gaps never resurface, preventing review fatigue
