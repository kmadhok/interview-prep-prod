# Task 3 Report: tailor-resume check ([VERIFY] leak + header)

## TDD Workflow

### RED Phase: Append Failing Tests
Appended 3 tests to `test_verify_artifacts.py`:
- `test_tailor_resume_pass`: Resume without leaks → pass
- `test_tailor_resume_verify_leak_fails`: Resume with `[VERIFY]` tag → fail on no-verify-leak check
- `test_tailor_resume_missing_fails`: Missing resume file → fail

Command:
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k tailor -v
```

Output:
```
collected 8 items / 5 deselected / 3 selected
test_tailor_resume_pass FAILED
test_tailor_resume_verify_leak_fails FAILED
test_tailor_resume_missing_fails FAILED

AttributeError: module 'verify_artifacts' has no attribute 'check_tailor_resume'
```

### GREEN Phase: Implement Functions
Appended `find_resume(clone: Path) -> Path | None` and `check_tailor_resume(clone: Path) -> dict` to `verify_artifacts.py`:
- `find_resume`: Globs for "Kanu Madhok Resume - *.md" and returns first match or None
- `check_tailor_resume`: 4 checks:
  - `resume-md-present`: File exists
  - `resume-nontrivial`: Text > 400 chars
  - `no-verify-leak`: No `[VERIFY]` or `[NUMBER?]` markers found via regex
  - `contact-header-present`: Contains "madhok.kanu@gmail.com"

Command:
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k tailor -v
```

Output:
```
collected 8 items / 5 deselected / 3 selected
test_tailor_resume_pass PASSED
test_tailor_resume_verify_leak_fails PASSED
test_tailor_resume_missing_fails PASSED

3 passed in 0.05s
```

### Full Suite Validation
Ran all tests to confirm no regressions:

Command:
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v
```

Output:
```
collected 8 items
test_rollup_severities PASSED
test_intake_pass_and_fail PASSED
test_classify_pass PASSED
test_classify_off_vocab_theme_fails PASSED
test_classify_missing_file_fails PASSED
test_tailor_resume_pass PASSED
test_tailor_resume_verify_leak_fails PASSED
test_tailor_resume_missing_fails PASSED

8 passed in 0.04s
```

## Files Changed
1. `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`
   - Added: `find_resume(clone: Path) -> Path | None` (3 lines)
   - Added: `check_tailor_resume(clone: Path) -> dict` (11 lines)
   - Total insertions: 14 lines

2. `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`
   - Added: `_RESUME_OK` constant (2 lines)
   - Added: `test_tailor_resume_pass` (3 lines)
   - Added: `test_tailor_resume_verify_leak_fails` (6 lines)
   - Added: `test_tailor_resume_missing_fails` (2 lines)
   - Total insertions: 13 lines + blank line = 14 lines

## Self-Review

**Correctness:**
- Transcribed implementation verbatim from brief (byte-for-byte match)
- No modifications to existing code (append-only)
- Regex pattern `r"\[VERIFY|\[NUMBER\?"` correctly targets leak markers
- Uses existing helpers: `check()`, `skill_result()`, `_read()`, `re` module

**Test Coverage:**
- Pass case: valid resume with contact header
- Fail case: leak detection (real negative case)
- Fail case: missing file (boundary condition)
- All 3 tests exercise the 4 checks in various combinations

**Style:**
- Matches existing code style (function signatures, formatting, return type hints)
- Consistent with other `check_*` functions in the file
- Pure functions, stdlib only

## Concerns
None. Implementation follows the brief exactly, passes all tests including 5 pre-existing tests, and commits cleanly.

## Commit
```
e540d9e feat(e2e-test): tailor-resume check (no [VERIFY] leak, contact header)
```
