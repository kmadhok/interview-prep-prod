# Task 6 Report: verify-emails Check (Issue-1 Catcher)

## TDD: RED → GREEN → REFACTOR

### Step 1: Failing Tests (RED)

Appended to `test_verify_artifacts.py`:
- `test_verify_emails_pass()` — verifies artifacts pass when ledger has contacts and Verified Emails.md contains rows
- `test_verify_emails_issue1_empty_with_contacts_fails()` — the critical regression catcher: ledger HAS contacts but Verified Emails.md is empty → FAIL with "issue1" check

**Initial test run output:**
```
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_verify_emails_pass
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_verify_emails_issue1_empty_with_contacts_fails

AttributeError: module 'verify_artifacts' has no attribute 'check_verify_emails'
```

### Step 2: Minimal Implementation (GREEN)

Appended two functions to `verify_artifacts.py`:

#### `_verified_email_rows(text: str) -> int`
Counts valid email rows in Verified Emails.md markdown table.
- Iterates through lines starting with `|`
- Counts cells containing both `@` and `.` (email indicators)
- Returns row count

#### `check_verify_emails(clone: Path) -> dict`
Verifies Verified Emails.md artifact, with Issue 1 regression check:
1. Checks file existence
2. Counts verified email rows via `_verified_email_rows`
3. Gets ledger contact count via `_ledger_contact_rows` (Task 5)
4. **Issue 1 check:** If ledger has ≥1 contact AND verified rows == 0, appends a hard "fail" severity check with diagnostic message

Returns `skill_result` dict with status rollup per `rollup()` function.

**Test run after implementation:**
```
PASSED test_verify_emails_pass [ 50%]
PASSED test_verify_emails_issue1_empty_with_contacts_fails [100%]

2 passed in 0.05s
```

### Step 3: Full Test Suite (Regression Check)

Ran full `test_verify_artifacts.py` to confirm no breakage:
```
15 passed in 0.05s
```

All existing tests continue to pass:
- rollup severities ✓
- intake pass/fail ✓
- classify validation ✓
- resume checks ✓
- PDF checks ✓
- gate checks ✓
- find_contacts checks ✓
- enrich_contacts hooks check ✓
- **NEW: verify_emails pass/fail checks** ✓

---

## Files Changed

| File | Changes |
|------|---------|
| `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` | +38 lines: `_verified_email_rows()`, `check_verify_emails()` |
| `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py` | +27 lines: `_VERIFIED_OK`, `test_verify_emails_pass()`, `test_verify_emails_issue1_empty_with_contacts_fails()` |

---

## Commit

**SHA:** `fda2eff`  
**Message:** `feat(e2e-test): verify-emails check — loud fail on empty-with-contacts (Issue 1)`

---

## Self-Review

✓ **Follows brief exactly:** All code transcribed verbatim from task-6-brief.md  
✓ **Reuses Task 5 code:** Calls `_ledger_contact_rows()` (defined in Task 5), not redefined  
✓ **Reuses test fixtures:** Uses `_LEDGER` from test file (defined in Task 5), not redefined  
✓ **STDLIB only:** Uses only pathlib, string ops, no external deps  
✓ **TDD flow:** RED → GREEN → full suite pass  
✓ **No existing code modified:** Only appended  
✓ **Issue 1 is the hard fail:** When ledger has contacts but verified emails is empty, `issue1-ledger-parsed` check is added with severity="fail", causing rollup() to return "fail"

---

## Concerns

None. Implementation is minimal, focused, and passes all tests.

---

## Test Commands Used

```bash
# RED (confirm failure)
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k verify_emails -v

# GREEN (after implementation)
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k verify_emails -v

# Regression (full suite)
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v

# Commit
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): verify-emails check — loud fail on empty-with-contacts (Issue 1)"
```
