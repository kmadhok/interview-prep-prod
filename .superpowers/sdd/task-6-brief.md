## Task 6: verify-emails check (the Issue-1 catcher)

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: `_ledger_contact_rows` (Task 5), `skill_result`, `check`, `_read`.
- Produces: `_verified_email_rows(text: str) -> int`; `check_verify_emails(clone: Path) -> dict`.

This is the check that earns the skill its keep: a ledger with contacts but an empty `Verified Emails.md` is the exact production bug (Issue 1) the manual test found — it must FAIL loudly.

- [ ] **Step 1: Write the failing test**

Append:

```python
_VERIFIED_OK = "\n".join([
    "# Verified Emails",
    "| Name | Email | Confidence |",
    "|---|---|---|",
    "| Brad Mallmann | brad.mallmann@snowflake.com | High |",
])


def test_verify_emails_pass():
    clone = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": _VERIFIED_OK})
    assert va.check_verify_emails(clone)["status"] == "pass"


def test_verify_emails_issue1_empty_with_contacts_fails():
    # ledger HAS contacts but verification produced zero rows -> the Issue 1 regression
    empty = "# Verified Emails\n\n_no rows_\n"
    clone = _clone_with({".contacts-ledger.md": _LEDGER, "Verified Emails.md": empty})
    res = va.check_verify_emails(clone)
    assert res["status"] == "fail"
    assert any("issue1" in c["name"] for c in res["checks"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k verify_emails -v`
Expected: FAIL — missing `check_verify_emails`

- [ ] **Step 3: Write minimal implementation**

Append:

```python
def _verified_email_rows(text: str) -> int:
    rows = 0
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if any("@" in c and "." in c for c in cells):
            rows += 1
    return rows


def check_verify_emails(clone: Path) -> dict:
    f = clone / "Verified Emails.md"
    if not f.exists():
        return skill_result([check("verified-emails-present", False, str(f))])
    rows = _verified_email_rows(_read(f))
    ledger = clone / ".contacts-ledger.md"
    ledger_contacts = _ledger_contact_rows(_read(ledger)) if ledger.exists() else 0
    checks = [
        check("verified-emails-present", True),
        check("verified-rows-present", rows >= 1, f"{rows} verified row(s)"),
    ]
    if ledger_contacts >= 1 and rows == 0:
        checks.append(check(
            "issue1-ledger-parsed", False,
            f"ledger has {ledger_contacts} contacts but Verified Emails.md is empty — "
            "find-contacts→verify-emails format mismatch (Issue 1)",
        ))
    return skill_result(checks)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k verify_emails -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): verify-emails check — loud fail on empty-with-contacts (Issue 1)"
```

---

