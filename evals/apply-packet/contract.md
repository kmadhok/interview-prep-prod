# apply-packet — Behavior Contract

The apply-packet step writes `Application Answers.md` (answers traceable to
the canonical `Application Profile.md`), records the upload in
`.apply-packet.json`, and points the upload at a `_test` remote in fixture
mode. This contract pins the observable end-state of a completed
apply-packet run.

## Clauses

### apply-packet-C1: Application Answers.md exists + answers traceable

`Application Answers.md` exists in the selected role and every numeric answer
is traceable to the profile supplied with `--profile` (default: fixture).

Traceability is checked as a pragmatic proxy: no digits or dollar amounts
appear in the answers file that do not also appear in the profile fixture.
This catches fabricated numbers (a salary of $200k invented when the profile
says $X) without requiring semantic matching. The proxy is documented here
so it is not mistaken for full provenance checking.

**How checked:** Read both files; extract every digit-sequence and `$…`
amount from the answers file; assert each one appears verbatim in the profile
fixture text.

### apply-packet-C2: .apply-packet.json is complete and queued

The runtime record parses, has `state == "queued"`, a non-empty `remote_dir`,
and the referenced answers artifact exists.

### apply-packet-C3: Recorded remote dir contains "_test"

The `remote_dir` recorded in `.apply-packet.json` contains the substring
`"_test"` — the fixture-mode marker that the upload landed in a test remote,
never the real Apply Queue.

**How checked:** Parse `.apply-packet.json`; assert `"_test" in
rec.get("remote_dir", "")`. (This is also one of check_packet's checks, but
called out as its own clause because it is the safety-critical invariant.)
