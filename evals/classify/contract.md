# classify — Behavior Contract

The classify step reads the JD and writes `.classification.json` in the role
folder: themes, archetype, and evidence. This contract pins the observable
end-state of a completed classify run.

## Clauses

### classify-C1: .classification.json exists in role folder

The file `workspace/Roles/Acme - Senior Agent Builder/.classification.json`
exists in the eval workspace.

**How checked:** `Path(role / ".classification.json").exists()`.

### classify-C2: JSON with non-empty themes + archetype + evidence

The file parses as JSON and has a non-empty `themes` array, a string
`archetype`, and every theme carries non-empty `evidence`.

**How checked:** `json.loads`; `themes` is a list with len > 0; `archetype` is
a non-empty string; every theme dict has `evidence` with stripped len > 0.

### classify-C3: Themes within the vocab

Every theme tag is a member of `THEME_VOCAB` from
`.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` — the
single source of truth for the classification vocabulary.

**How checked:** For each theme tag, assert `tag in THEME_VOCAB`.

### classify-C4: Passes verify_artifacts's classification check

The file passes `verify_artifacts.check_classify(role_folder)` — the same
schema check the e2e verifier runs. This reuses the e2e authority so the
per-skill tier and the e2e tier agree on what a valid classification is.

**How checked:** Import `check_classify` from verify_artifacts (path-based
import via the e2e scripts dir); call it with the role folder; assert every
check in the returned `checks` list has `ok=True`.
