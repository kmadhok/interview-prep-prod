# classify — Behavior Contract

The classify step reads the JD and writes `.classification.json` in the role
folder: themes, archetype, and evidence. This contract pins the observable
end-state of a completed classify run.

## Clauses

### classify-C1: .classification.json exists in role folder

`.classification.json` exists in the selected role.

**How checked:** `Path(role / ".classification.json").exists()`.

### classify-C2: JSON with non-empty themes + archetype + evidence

The file parses as JSON and has a non-empty `themes` array, a string
`archetype`, and every theme carries non-empty `evidence`.

**How checked:** `json.loads`; `themes` is a list with len > 0; `archetype` is
a non-empty string; every theme dict has `evidence` with stripped len > 0.

### classify-C3: Themes within the vocab

Every theme tag is a member of `THEME_VOCAB` in `evals/common.py`.

**How checked:** For each theme tag, assert `tag in THEME_VOCAB`.

### classify-C4: Archetype is within the stable vocabulary

The archetype is a member of `ARCHETYPE_VOCAB` in `evals/common.py`. The E2E
verifier delegates to this contract verifier; it is not a second authority.

### classify-C5: Classification contains 4–6 themes

The `themes` list has between four and six entries, inclusive.

### classify-C6: Every theme evidence quote resolves against Job Description.md

After case-folding and collapsing whitespace, each non-empty theme `evidence`
string occurs in the selected role's `Job Description.md`.

### classify-C7: Archetype rationale is present

`archetype_rationale` is a non-empty string.

### classify-C8: classified_ts is a valid ISO timestamp/date

`classified_ts` is a non-empty ISO-8601 date or timestamp parseable by the
stdlib datetime parser.
