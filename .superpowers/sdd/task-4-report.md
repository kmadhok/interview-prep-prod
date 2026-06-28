# Task 4 Report: PDF + Gate Checks

## TDD Workflow

### RED Phase
Appended two failing tests to `test_verify_artifacts.py`:
- `test_pdf_clean_and_overflow()` — expects `check_pdf` function to validate PDF presence, page count (1 page = pass, 2 pages = warn), and title leak (0 = pass, >0 = fail).
- `test_gate_surfaces_role()` — expects `check_gate` function to search for company name in worklist output (case-insensitive).

**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "pdf or gate" -v
```

**Output (FAILED):**
```
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_pdf_clean_and_overflow - AttributeError: module 'verify_artifacts' has no attribute 'check_pdf'
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_gate_surfaces_role - AttributeError: module 'verify_artifacts' has no attribute 'check_gate'
2 failed, 8 deselected in 0.10s
```

### GREEN Phase
Appended implementations to `verify_artifacts.py`:

```python
def check_pdf(clone: Path, pages, title_leak) -> dict:
    checks = [check("resume-pdf-present", bool(list(clone.glob("Kanu Madhok Resume - *.pdf"))), "glob: *.pdf")]
    if pages is not None:
        checks.append(check("pdf-one-page", pages == 1, f"PAGES={pages}", severity="warn"))
    if title_leak is not None:
        checks.append(check("pdf-no-title-leak", title_leak == 0, f"TITLE_LEAK={title_leak}"))
    return skill_result(checks)


def check_gate(worklist_text: str, company: str) -> dict:
    ok = bool(company) and company.lower() in (worklist_text or "").lower()
    return skill_result([check("worklist-surfaces-role", ok, f"company={company!r}")])
```

**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "pdf or gate" -v
```

**Output (PASSED):**
```
test_pdf_clean_and_overflow PASSED [ 50%]
test_gate_surfaces_role PASSED [100%]
2 passed, 8 deselected in 0.03s
```

### Full Suite Regression Check
**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v
```

**Output (ALL PASS):**
```
10 passed in 0.04s
```
- test_rollup_severities PASSED
- test_intake_pass_and_fail PASSED
- test_classify_pass PASSED
- test_classify_off_vocab_theme_fails PASSED
- test_classify_missing_file_fails PASSED
- test_tailor_resume_pass PASSED
- test_tailor_resume_verify_leak_fails PASSED
- test_tailor_resume_missing_fails PASSED
- test_pdf_clean_and_overflow PASSED ✓ (NEW)
- test_gate_surfaces_role PASSED ✓ (NEW)

## Files Changed
- `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py` — appended `check_pdf()` and `check_gate()` (19 lines).
- `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py` — appended two test functions (15 lines).

## Commit
**SHA:** `cba31f8`
**Message:** `feat(e2e-test): PDF (overflow=warn, leak=fail) + apply-gate checks`

## Self-Review

**Implementation Correctness:**
- `check_pdf()` correctly reuses `check()` and `skill_result()` helpers.
- PDF glob matches spec: `Kanu Madhok Resume - *.pdf`.
- Page check uses `severity="warn"` for 2-page case (overflow pass-with-gap).
- Title leak check uses default `severity="fail"` (hard fail).
- All arguments passed in (no file reads beyond glob).

**Test Coverage:**
- PDF tests cover: pass (1 page, no leak), warn (2 pages, no leak), fail (title leak).
- Gate test covers: pass (company in worklist), fail (company not in worklist).
- Case-insensitive search verified by test assertion.

**Constraints Satisfied:**
- Stdlib only ✓
- No file I/O beyond glob ✓
- Reused existing `check`, `skill_result` ✓
- Appended, did not modify existing code ✓
- TDD: RED → GREEN → COMMIT ✓

**Concerns:** None. Implementation is minimal, idiomatic, and tests confirm all edge cases.
