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

### enrich-contacts-C2: >=1 row marked with an activity source when enriched

When the fixture-run marker file `.eval-enriched` exists (the convention that
signals an enrichment run completed), at least one ledger row is marked with
an activity source — i.e. the `source` cell references "enrich" (or an
activity marker) rather than only "search". If `.eval-enriched` is absent,
this clause passes vacuously (enrichment was not expected).

**How checked:** If `.eval-enriched` exists in the role folder, assert at
least one parsed row has a `source` cell containing "enrich" (lowercased).
Otherwise vacuous pass.

### enrich-contacts-C3: Every hook line references a person already in the table

Every line under a `## hooks` (or similar) section references a person who
already appears in the ledger's `name` column — enrichment hooks never
invent new people.

**How checked:** Find the `## hooks` section; for each non-empty line in it,
assert at least one ledger name appears in the line. If there is no hooks
section, the clause passes vacuously (enrichment may not always add hooks).
