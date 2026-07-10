# interview-prep-intake — Behavior Contract

The intake skill files a JD into the workspace: creates the role folder,
writes `Job Description.md`, and adds a Pipeline row. This contract pins the
observable end-state of a completed intake run.

## Clauses

### intake-C1: Role folder exists

The directory `workspace/Roles/Acme - Senior Agent Builder/` exists in the
eval workspace.

**How checked:** `Path(workspace / "Roles" / "Acme - Senior Agent Builder").is_dir()`.

### intake-C2: Job Description.md is non-empty

The file `workspace/Roles/Acme - Senior Agent Builder/Job Description.md`
exists and is non-empty (stripped length > 0).

**How checked:** Read the file; assert it exists and `len(text.strip()) > 0`.

### intake-C3: Pipeline row under Considering

The workspace `Pipeline.md` contains a row mentioning
"Acme — Senior Agent Builder" under a `## Considering` section.

**How checked:** Read `workspace/Pipeline.md`; find the `## Considering`
section (lines from a heading starting with `## Considering` until the next
`## ` heading or EOF); assert the section contains "Acme — Senior Agent Builder".

### intake-C4: No other role folder created

No directory other than `Acme - Senior Agent Builder` exists under
`workspace/Roles/` in the eval workspace. The fixture workspace starts with
zero roles, so intake must create exactly one.

**How checked:** List `workspace/Roles/`; assert the only entry is
`Acme - Senior Agent Builder`.
