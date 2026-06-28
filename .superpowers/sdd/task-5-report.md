# Task 5: contacts checks (find + enrich) — Report

## Status
**COMPLETE** — All tests passing, implementation committed.

---

## TDD Cycle

### Step 1: Failing Tests (RED)
Appended 3 tests to `test_verify_artifacts.py`:
- `test_find_contacts_counts_rows` — verifies `_ledger_contact_rows()` counts exactly 2 rows in a fixture ledger
- `test_find_contacts_missing_fails` — verifies `check_find_contacts()` fails when ledger is absent
- `test_enrich_requires_hooks_section` — verifies `check_enrich_contacts()` requires "hooks" in text

**Run command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "find_contacts or enrich" -v
```

**Output:**
```
collected 13 items / 10 deselected / 3 selected

test_find_contacts_counts_rows FAILED [ 33%]
test_find_contacts_missing_fails FAILED [ 66%]
test_enrich_requires_hooks_section FAILED [100%]

================================== FAILURES ===================================
AttributeError: module 'verify_artifacts' has no attribute 'check_find_contacts'
AttributeError: module 'verify_artifacts' has no attribute 'check_find_contacts'
AttributeError: module 'verify_artifacts' has no attribute 'check_enrich_contacts'

======================== 3 failed, 10 deselected in 0.10s =========================
```

### Step 2: Implementation (GREEN)
Appended 3 functions to `verify_artifacts.py`:

**`_ledger_contact_rows(text: str) -> int`**
- Parses markdown table rows line-by-line
- Skips non-table lines, dividers (`|--|`), and header rows (containing "rank" or "name")
- Returns count of valid contact rows
- Used by both `check_find_contacts()` and Task 6 later

**`check_find_contacts(clone: Path) -> dict`**
- Checks for `.contacts-ledger.md` existence
- Counts rows via `_ledger_contact_rows()`
- Returns 2-check result: ledger-present, ledger-has-contacts (≥1 row)

**`check_enrich_contacts(clone: Path) -> dict`**
- Checks for `.contacts-ledger.md` existence
- Requires "hooks" section (case-insensitive)
- Returns 1-check result: ledger-has-hooks

**Run focused tests again:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "find_contacts or enrich" -v
```

**Output:**
```
collected 13 items / 10 deselected / 3 selected

test_find_contacts_counts_rows PASSED [ 33%]
test_find_contacts_missing_fails PASSED [ 66%]
test_enrich_requires_hooks_section PASSED [100%]

===================== 3 passed, 10 deselected in 0.05s ======================
```

### Step 3: Full Suite (Regression)
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v
```

**Output:**
```
collected 13 items

test_rollup_severities PASSED
test_intake_pass_and_fail PASSED
test_classify_pass PASSED
test_classify_off_vocab_theme_fails PASSED
test_classify_missing_file_fails PASSED
test_tailor_resume_pass PASSED
test_tailor_resume_verify_leak_fails PASSED
test_tailor_resume_missing_fails PASSED
test_pdf_clean_and_overflow PASSED
test_gate_surfaces_role PASSED
test_find_contacts_counts_rows PASSED
test_find_contacts_missing_fails PASSED
test_enrich_requires_hooks_section PASSED

===================== 13 passed in 0.05s ======
```

All existing tests still pass. No regressions.

---

## Commit
**SHA:** `641ed20`  
**Message:** `feat(e2e-test): find-contacts (>=1 row) + enrich-contacts (hooks) checks`

Files changed:
- `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` — +38 lines (3 functions)
- `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py` — +28 lines (3 tests + fixture)

---

## Self-Review

### Implementation Correctness
- **`_ledger_contact_rows()`:** Correctly parses markdown tables, skips headers and dividers, counts data rows. Handles edge cases: empty text, non-table lines, short cells.
- **`check_find_contacts()`:** Follows existing pattern (e.g., `check_intake`, `check_tailor_resume`), early exit on missing file, delegates row counting to helper.
- **`check_enrich_contacts()`:** Uses simple case-insensitive substring check for "hook", aligns with spec ("expected a hooks section from enrich-contacts").

### Consistency
- Uses existing utilities (`check()`, `skill_result()`, `_read()`, `re`), same as all existing checks.
- Returns `dict` with `status` key, consistent with other checks.
- Error handling via `check()` severity defaults, no exceptions leaked.

### Test Coverage
- **Happy path:** `test_find_contacts_counts_rows` verifies row counting on a valid ledger with 2 contacts.
- **Sad paths:** `test_find_contacts_missing_fails` (no ledger), `test_enrich_requires_hooks_section` (ledger present but no hooks).
- Test fixtures follow existing pattern (`_clone_with()`, `_LEDGER` constant).

### Signature Fidelity
- `_ledger_contact_rows(text: str) -> int` — matches brief exactly; Task 6 will reuse this.
- `check_find_contacts(clone: Path) -> dict` — matches brief exactly.
- `check_enrich_contacts(clone: Path) -> dict` — matches brief exactly.

---

## Concerns
None. Implementation is minimal, stdlib-only, tested, and ready for Task 6 to reuse `_ledger_contact_rows()`.

---

## Files Modified
- `G:\projects\interview-prep\.claude\skills\two-orchestrator-e2e-test\scripts\verify_artifacts.py` (appended 3 functions)
- `G:\projects\interview-prep\.claude\skills\two-orchestrator-e2e-test\scripts\test_verify_artifacts.py` (appended 3 tests + fixture)
