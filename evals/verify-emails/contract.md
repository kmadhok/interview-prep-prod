# verify-emails — Behavior Contract

The verify-emails step writes `Verified Emails.md` with a status per address.
This contract pins the observable end-state of a completed verify-emails run.

## Clauses

### verify-emails-C1: Verified Emails.md exists

`workspace/Roles/Acme - Senior Agent Builder/Verified Emails.md` exists in
the eval workspace.

**How checked:** `Path(role / "Verified Emails.md").exists()`.

### verify-emails-C2: Every entry line has a status

Every table row in `Verified Emails.md` that carries an email address has a
status cell with one of `verified`, `inferred`, or `flagged`.

**How checked:** Parse the markdown table; for each row containing an email
cell, assert the row contains one of the three status words
(case-insensitive).

### verify-emails-C3: Every address appears in the ledger or ends with a ledger domain

No email is invented. Every address in `Verified Emails.md` either appears
verbatim in the `.contacts-ledger.md`, or ends with a domain that does — the
derived-inferred rule (pattern-derived addresses are allowed only when the
domain is already present in the ledger, and the row must carry the
`inferred` tag).

**How checked:** Collect every email address from Verified Emails.md and
every email/domain from the ledger; for each verified-emails address, assert
it appears in the ledger address set OR its domain (the part after `@`)
appears in the ledger domain set.
