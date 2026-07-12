# enrich-contacts — Behavior Contract

The enrich-contacts step appends activity-sourced contacts to the ledger and
adds a hooks section referencing people already in the table. This contract
pins the observable end-state of a completed enrich-contacts run.

## Clauses

### enrich-contacts-C1: Ledger parses after enrichment

The `.contacts-ledger.md` still parses into structured rows after
enrichment — enrichment appended to the table, it did not corrupt it.

**How checked:** Parse the ledger via the shared parser
(`evals/_ledger.py`); assert `header` is non-null and `rows` is non-empty.

### enrich-contacts-C2: At least one row records enrichment provenance

At least one ledger row has a `source` cell containing `enrich`. The ledger is
the runtime artifact; eval-only marker sidecars are forbidden.

**How checked:** Require one parsed row whose source contains `enrich`.

### enrich-contacts-C3: Every hook line references a person already in the table

The ledger has a `## hooks` section whose lines reference people already in
the ledger, OR the enrichment trace contains a structured `no-activity` or
`no-hook` gap with non-empty source/detail.

**How checked:** Validate each hook line against ledger names. If no hooks
exist, scan real `runs/*/trace.jsonl` gap arrays for the explicit degradation
record. Absence of both is a failure.

### enrich-contacts-C4: Live LinkedIn activity evidence resolves

**Tier: live-only.** Activity hooks resolve to visible LinkedIn evidence.
Without LinkedIn MCP this clause is `BLOCKED`, not passed; local C1–C3 run.
