# find-contacts — Behavior Contract

The find-contacts step searches LinkedIn for recruiter/HM contacts and
writes a scored `.contacts-ledger.md` in the role folder. This contract
pins the observable end-state of a completed find-contacts run.

## Clauses

### find-contacts-C1: .contacts-ledger.md exists with >=1 scored row

`workspace/Roles/Acme - Senior Agent Builder/.contacts-ledger.md` exists
and its table has at least one scored contact row (a data row, not just a
header/divider).

**How checked:** Parse the ledger table via the shared ledger parser
(`evals/_ledger.py`); assert `rows` is non-empty.

### find-contacts-C2: Table parses with the fixture columns

The ledger table parses and its header row contains the columns the fixture
ledger uses: at minimum `name`, `email`, and `confidence`.

**How checked:** Parse the ledger; assert the header is non-null and contains
`name`, `email` (or `email (inferred)`), and `confidence`.

### find-contacts-C3: Every email cell carries a confidence tag

Every row's email cell carries a confidence tag — one of `verified`,
`inferred`, or `flagged` — matching the ledger legend. The fixture uses the
`Medium (inferred)` style in the `Confidence` column.

**How checked:** For each parsed row, read the `confidence` cell; assert it
contains one of `verified`, `inferred`, or `flagged` (case-insensitive).
