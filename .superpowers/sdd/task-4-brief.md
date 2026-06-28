## Task 4: PDF + gate checks (passed-in values)

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: `skill_result`, `check`.
- Produces: `check_pdf(clone: Path, pages, title_leak) -> dict`; `check_gate(worklist_text: str, company: str) -> dict`.

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_pdf_clean_and_overflow():
    clone = _clone_with({"Kanu Madhok Resume - Snowflake FDE.pdf": "%PDF-1.4"})
    assert va.check_pdf(clone, pages=1, title_leak=0)["status"] == "pass"
    # 2 pages = warn (pass-with-gap), not fail
    assert va.check_pdf(clone, pages=2, title_leak=0)["status"] == "warn"
    # title leak = hard fail
    assert va.check_pdf(clone, pages=1, title_leak=1)["status"] == "fail"


def test_gate_surfaces_role():
    out = "Snowflake\tForward Deployed Analytics Engineer\nMeta\tBusiness Engineer\n"
    assert va.check_gate(out, "Snowflake")["status"] == "pass"
    assert va.check_gate(out, "Datadog")["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "pdf or gate" -v`
Expected: FAIL — missing `check_pdf` / `check_gate`

- [ ] **Step 3: Write minimal implementation**

Append:

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

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "pdf or gate" -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): PDF (overflow=warn, leak=fail) + apply-gate checks"
```

---

