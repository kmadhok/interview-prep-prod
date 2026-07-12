# find-contacts — Behavior Contract

The find-contacts step searches LinkedIn for recruiter/HM contacts and
writes a scored `.contacts-ledger.md` in the role folder. This contract
pins the observable end-state of a completed find-contacts run.

## Clauses

### find-contacts-C1: .contacts-ledger.md exists with >=1 scored row

The selected role's `.contacts-ledger.md` exists and has at least one scored
contact row (not just a header/divider).

**How checked:** Parse the ledger table via the shared ledger parser
(`evals/_ledger.py`); assert `rows` is non-empty.

### find-contacts-C2: Table parses with the required ledger schema

The ledger table parses and its header contains the required downstream
columns: at minimum `name`, an `email` column, and `confidence`.

**How checked:** Parse the ledger; assert the header is non-null and contains
`name`, `email` (or `email (inferred)`), and `confidence`.

### find-contacts-C3: Every email cell carries a confidence tag

Every row's email cell carries a confidence tag — one of `verified`,
`inferred`, or `flagged` — matching the ledger legend. The fixture uses the
`Medium (inferred)` style in the `Confidence` column.

**How checked:** For each parsed row, read the `confidence` cell; assert it
contains one of `verified`, `inferred`, or `flagged` (case-insensitive).

### find-contacts-C4: Every ledger contact has source provenance

Every parsed contact row has a non-empty `source` cell. This deterministic
fixture clause prevents provenance-free contacts from entering later stages.

### find-contacts-C5: Live LinkedIn identity and employer evidence

**Tier: live-only.** The selected people resolve to current LinkedIn profiles
and the target employer/role evidence is visible. When LinkedIn MCP is absent,
this clause is `BLOCKED`, never `PASS`; `--live` without supplied evidence is
`NOT_RUN`. Local clauses C1–C4 still execute.
