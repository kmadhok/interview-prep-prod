# Task 2 Report: classify check (vocab validation)

## Summary
Successfully implemented `check_classify()` verifier function with vocab validation for `.classification.json` artifact in the two-orchestrator E2E test harness. All tests pass.

---

## TDD Cycle

### RED: Failing Test Append
Appended 3 test cases to `test_verify_artifacts.py`:
- `test_classify_pass` — valid .classification.json passes
- `test_classify_off_vocab_theme_fails` — off-vocab theme tag fails
- `test_classify_missing_file_fails` — missing file fails

**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k classify -v
```

**Output (RED):**
```
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_classify_pass
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_classify_off_vocab_theme_fails
FAILED .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py::test_classify_missing_file_fails

3 failed — AttributeError: module 'verify_artifacts' has no attribute 'check_classify'
```

### GREEN: Implementation
Appended `check_classify(clone: Path) -> dict` to `verify_artifacts.py` with 6 checks:
1. `classification-parses` — valid JSON
2. `theme-count-4-6` — 4–6 themes
3. `themes-in-vocab` — all theme tags in THEME_VOCAB
4. `archetype-in-vocab` — archetype in ARCHETYPE_VOCAB
5. `evidence-present` — all themes have non-empty evidence field
6. `classified-ts-present` — non-empty classified_ts

**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k classify -v
```

**Output (GREEN):**
```
test_classify_pass PASSED [ 33%]
test_classify_off_vocab_theme_fails PASSED [ 66%]
test_classify_missing_file_fails PASSED [100%]

3 passed
```

### Full Suite Verification
**Command:**
```bash
python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v
```

**Output:**
```
test_rollup_severities PASSED [ 20%]
test_intake_pass_and_fail PASSED [ 40%]
test_classify_pass PASSED [ 60%]
test_classify_off_vocab_theme_fails PASSED [ 80%]
test_classify_missing_file_fails PASSED [100%]

5 passed in 0.04s
```

---

## Files Changed

### Modified
- `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`
  - Added 3 test cases + `_GOOD_CLASS` constant (38 lines)
  
- `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`
  - Added `check_classify()` function (16 lines)

### Total
- +54 lines across 2 files
- No deletions or rewrites

---

## Self-Review

✓ **Correct interface**: Takes `Path`, returns dict with "status" and "checks" keys  
✓ **Reused existing patterns**: Uses `check()`, `skill_result()`, `_read()`, THEME_VOCAB, ARCHETYPE_VOCAB (all pre-defined)  
✓ **Stdlib only**: No external imports beyond json, pathlib, argparse (already imported)  
✓ **Error handling**: JSON parse errors caught, missing file detected  
✓ **Vocab validation**: Theme tags and archetype checked against define lists  
✓ **Evidence enforcement**: Detects empty evidence strings  
✓ **Test coverage**: Happy path, off-vocab failure, missing file failure  
✓ **TDD discipline**: Red → Green → Full suite pass before commit  

---

## Concerns

None. Implementation directly follows brief verbatim; logic is sound; test suite complete and passing.

---

## Commit

**SHA**: a86e60b  
**Message**: `feat(e2e-test): classify check (in-vocab themes + archetype)`

---

## Acceptance Criteria

- [x] Failing test appended and confirmed RED
- [x] Implementation appended (not rewritten)
- [x] Tests confirmed GREEN
- [x] Full suite passes
- [x] Commit created
- [x] Report written
