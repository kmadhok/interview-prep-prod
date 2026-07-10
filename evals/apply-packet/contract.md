# apply-packet — Behavior Contract

The apply-packet step writes `Application Answers.md` (answers traceable to
the canonical `Application Profile.md`), records the upload in
`.apply-packet.json`, and points the upload at a `_test` remote in fixture
mode. This contract pins the observable end-state of a completed
apply-packet run.

## Clauses

### apply-packet-C1: Application Answers.md exists + answers traceable

`workspace/Roles/Acme - Senior Agent Builder/Application Answers.md` exists
and every answer line is traceable to the fixture `Application Profile.md`.

Traceability is checked as a pragmatic proxy: no digits or dollar amounts
appear in the answers file that do not also appear in the profile fixture.
This catches fabricated numbers (a salary of $200k invented when the profile
says $X) without requiring semantic matching. The proxy is documented here
so it is not mistaken for full provenance checking.

**How checked:** Read both files; extract every digit-sequence and `$…`
amount from the answers file; assert each one appears verbatim in the profile
fixture text.

### apply-packet-C2: .apply-packet.json valid per verify_artifacts

`workspace/Roles/Acme - Senior Agent Builder/.apply-packet.json` parses and
passes `verify_artifacts.check_packet` — the same schema check the e2e
verifier runs (state == queued, answers-md-present, etc.).

**How checked:** Import `check_packet` from verify_artifacts; call it with
the role folder; assert every check has `ok=True`.

### apply-packet-C3: Recorded remote dir contains "_test"

The `remote_dir` recorded in `.apply-packet.json` contains the substring
`"_test"` — the fixture-mode marker that the upload landed in a test remote,
never the real Apply Queue.

**How checked:** Parse `.apply-packet.json`; assert `"_test" in
rec.get("remote_dir", "")`. (This is also one of check_packet's checks, but
called out as its own clause because it is the safety-critical invariant.)
