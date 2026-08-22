# Documentation audit log

## Evidence reviewed

Inspected all 20 ADR source commits with `git show`/parent history, current `scripts/`, `evals/`, skill contracts, `docs/trace/`, `templates/profile.yaml`, and the live run/config readers. The very large `98c6d87` diff is a real path migration: root instance files were deleted and re-added below `workspace/`; it was not interpreted from the subject alone.

## Contradictions and drift

- `scripts/config.py` has no workspace environment override: `WORKSPACE` and `PROFILE_PATH` are fixed repo-relative paths. Earlier runbook wording claiming a supported override was removed.
- A clean clone lacks root `profile.yaml`/`workspace/`; therefore fixture generation or `/onboard`, not an existing personal workspace, is the safe setup path.
- LinkedIn and Gmail credentials are owned by external clients. `infra/` describes automation, but host task registration/service health cannot be proven from tracked files.
- Plan-only commits (`0ec6b85`, `865baed`) are retained as decision records only because later commits implement their exact trace/eval contracts; their ADRs cite that later/current evidence.

## Verification

- `python3 -m compileall -q scripts evals` — exit 0.
- `python3 scripts/test_no_personal_refs.py` — exit 0, `PASS: no personal references found in template-side files`.
- Cross-repository Markdown relative-link checker — exit 0, zero broken links.
- No live workspace, LinkedIn, Gmail, browser, or paid action was run.

## Questions for Kanu

- Should sanitized Windows task definitions for Pass A/Pass B be checked into `infra/`, or remain host-owned?
