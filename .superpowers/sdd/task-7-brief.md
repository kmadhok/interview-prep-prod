## Task 7: write-outreach check (Gmail draft)

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: `skill_result`, `check`.
- Produces: `check_write_outreach(clone: Path, draft: dict | None, expected_recipient: str) -> dict`.

The Gmail draft object is the shape returned by the Gmail MCP `list_drafts` — `{"id","toRecipients":[...],"subject","plaintextBody"}`. A draft in the drafts listing is unsent by definition; the check asserts presence + recipient.

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_write_outreach_pass():
    clone = _clone_with({"Cold Outreach.md": "## Recruiter email\nHi Brad,"})
    draft = {"id": "r123", "toRecipients": ["brad.mallmann@snowflake.com"], "subject": "Re: ..."}
    assert va.check_write_outreach(clone, draft, "brad.mallmann@snowflake.com")["status"] == "pass"


def test_write_outreach_recipient_mismatch_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    draft = {"id": "r123", "toRecipients": ["someone.else@snowflake.com"]}
    res = va.check_write_outreach(clone, draft, "brad.mallmann@snowflake.com")
    assert res["status"] == "fail"


def test_write_outreach_no_draft_fails():
    clone = _clone_with({"Cold Outreach.md": "x"})
    assert va.check_write_outreach(clone, None, "")["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k write_outreach -v`
Expected: FAIL — missing `check_write_outreach`

- [ ] **Step 3: Write minimal implementation**

Append:

```python
def check_write_outreach(clone: Path, draft: dict | None, expected_recipient: str) -> dict:
    f = clone / "Cold Outreach.md"
    checks = [check("cold-outreach-present", f.exists(), str(f))]
    if not draft:
        checks.append(check("gmail-draft-present", False, "no draft provided"))
        return skill_result(checks)
    recips = [str(r).lower() for r in draft.get("toRecipients", [])]
    checks.append(check("gmail-draft-present", bool(draft.get("id")), draft.get("id", "")))
    if expected_recipient:
        checks.append(check("draft-recipient-matches", expected_recipient.lower() in recips, f"to={recips}"))
    checks.append(check("draft-unsent", not draft.get("sent", False), "drafts listing = unsent"))
    return skill_result(checks)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k write_outreach -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): write-outreach check (draft present + recipient)"
```

---

