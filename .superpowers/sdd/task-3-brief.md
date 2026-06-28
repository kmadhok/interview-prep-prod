## Task 3: tailor-resume check ([VERIFY] leak + header)

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: `skill_result`, `check`, `_read`.
- Produces: `find_resume(clone: Path) -> Path | None`; `check_tailor_resume(clone: Path) -> dict`.

- [ ] **Step 1: Write the failing test**

Append:

```python
_RESUME_OK = ("# Kanu Madhok\n\nmadhok.kanu@gmail.com\n\n" +
              "## EXPERIENCE\n- Built a registry-governed semantic layer over 67 tables.\n" * 6)


def test_tailor_resume_pass():
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": _RESUME_OK})
    assert va.check_tailor_resume(clone)["status"] == "pass"


def test_tailor_resume_verify_leak_fails():
    leaked = _RESUME_OK + "\n- Drove [VERIFY: 95% accuracy] across the org.\n"
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.md": leaked})
    res = va.check_tailor_resume(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "no-verify-leak" and not c["ok"] for c in res["checks"])


def test_tailor_resume_missing_fails():
    assert va.check_tailor_resume(_clone_with({}))["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k tailor -v`
Expected: FAIL — `AttributeError: ... 'check_tailor_resume'`

- [ ] **Step 3: Write minimal implementation**

Append:

```python
def find_resume(clone: Path) -> Path | None:
    matches = sorted(clone.glob("Kanu Madhok Resume - *.md"))
    return matches[0] if matches else None


def check_tailor_resume(clone: Path) -> dict:
    r = find_resume(clone)
    if r is None:
        return skill_result([check("resume-md-present", False, "glob: Kanu Madhok Resume - *.md")])
    text = _read(r)
    leaks = re.findall(r"\[VERIFY|\[NUMBER\?", text)
    return skill_result([
        check("resume-md-present", True, r.name),
        check("resume-nontrivial", len(text.strip()) > 400, f"{len(text)} chars"),
        check("no-verify-leak", not leaks, f"{len(leaks)} leak(s)"),
        check("contact-header-present", "madhok.kanu@gmail.com" in text),
    ])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k tailor -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): tailor-resume check (no [VERIFY] leak, contact header)"
```

---

