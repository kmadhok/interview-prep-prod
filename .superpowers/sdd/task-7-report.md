# Task 7 Report: write-outreach check (Gmail draft)

## TDD Workflow Summary

### RED Phase
**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k write_outreach -v
```

**Output:**
```
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_pass
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_recipient_mismatch_fails
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_no_draft_fails

3 failed, 15 deselected in 0.11s
```

Error: `AttributeError: module 'verify_artifacts' has no attribute 'check_write_outreach'` (expected)

### GREEN Phase
**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k write_outreach -v
```

**Output:**
```
.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_pass PASSED [ 33%]
.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_recipient_mismatch_fails PASSED [ 66%]
.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_write_outreach_no_draft_fails PASSED [100%]

3 passed, 15 deselected in 0.03s
```

### Full Test Run
**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v
```

**Output:**
```
18 passed in 0.06s
```

All tests pass (15 existing + 3 new). No regressions.

## Files Changed

### 1. `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`
- **Added 3 test functions** (appended at EOF, no existing code modified):
  - `test_write_outreach_pass()` — verifies pass case with matching recipient
  - `test_write_outreach_recipient_mismatch_fails()` — verifies fail when recipient doesn't match
  - `test_write_outreach_no_draft_fails()` — verifies fail when draft is None

### 2. `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`
- **Added 1 function** (appended at EOF, no existing code modified):
  - `check_write_outreach(clone: Path, draft: dict | None, expected_recipient: str) -> dict`
    - Checks Cold Outreach.md file exists
    - Checks Gmail draft present (has id)
    - Validates recipient matches expected email (case-insensitive)
    - Confirms draft is unsent (drafts listing = unsent by definition)
    - Returns dict with status (pass/fail) and checks list

## Implementation Details

The function follows the established pattern in `verify_artifacts.py`:
- Uses `check()` helper to record individual assertions with name, ok, detail, severity
- Uses `skill_result()` to aggregate checks and determine rollup status
- Reuses `_read()` for safe file reading
- Handles None draft gracefully (returns fail status)
- Case-insensitive email comparison (lowercases both actual and expected recipients)
- No external dependencies — STDLIB only

## Self-Review

✓ Function signature matches brief specification exactly
✓ Tests verify all three key behaviors: pass case, recipient mismatch, no draft
✓ Email validation is case-insensitive (matches realistic behavior)
✓ Draft dict shape matches Gmail MCP `list_drafts` response
✓ Reuses existing `check()` and `skill_result()` primitives
✓ No modifications to existing code (appended only)
✓ All tests pass with no regressions

## Concerns

None. Implementation is minimal, focused, and follows established patterns.

## Commit

```
fc3bb82 feat(e2e-test): write-outreach check (draft present + recipient)
```

Two files changed, 32 insertions (+), 0 deletions (-).
