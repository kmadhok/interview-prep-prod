# interview-prep-intake — Behavior Contract

The intake skill files a JD into the workspace: creates the role folder,
writes `Job Description.md`, and adds a Pipeline row. This contract pins the
observable end-state of a completed intake run.

## Clauses

### intake-C1: Role folder exists

The selected role directory exists. The verifier accepts `--role`; otherwise
the isolated workspace must contain exactly one role directory.

**How checked:** Resolve the selected role and assert `is_dir()`.

### intake-C2: Job Description.md is non-empty

`Job Description.md` in the selected role exists and is non-empty.

**How checked:** Read the file; assert it exists and `len(text.strip()) > 0`.

### intake-C3: Pipeline row under Considering

`Pipeline.md` contains the selected folder name, normalized from ` - ` to
` — `, under a `## Considering` section.

**How checked:** Read `workspace/Pipeline.md`; find the `## Considering`
section (until the next `## ` heading or EOF); assert it contains that role.

### intake-C4: Exactly one Pipeline row links the selected role path

Across the entire Pipeline there is exactly one data row for the selected
company/role, and that row links the selected role folder name. This makes
repeated intake idempotent without assuming the real workspace has one role.

**How checked:** Count table rows containing the normalized role label and
require exactly one; require that row to contain the selected folder name.
Workspace isolation is an E2E harness audit, not an intake behavior clause.
