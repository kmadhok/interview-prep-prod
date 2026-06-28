## Task 5: contacts checks (find + enrich)

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: `skill_result`, `check`, `_read`.
- Produces: `_ledger_contact_rows(text: str) -> int`; `check_find_contacts(clone: Path) -> dict`; `check_enrich_contacts(clone: Path) -> dict`. (`_ledger_contact_rows` is reused by Task 6.)

- [ ] **Step 1: Write the failing test**

Append:

```python
_LEDGER = "\n".join([
    "# Contacts Ledger",
    "## Recruiters (ranked)",
    "| Rank | Name | Practice | Email (inferred) |",
    "|------|------|----------|------------------|",
    "| 1 | Brad Mallmann | GTM | brad.mallmann@snowflake.com |",
    "| 2 | Diane Nguyen | Cortex | diane.nguyen@snowflake.com |",
    "## hooks[]",
    "- Brad: posted about data-foundation governance.",
])


def test_find_contacts_counts_rows():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    res = va.check_find_contacts(clone)
    assert res["status"] == "pass"
    assert va._ledger_contact_rows(_LEDGER) == 2


def test_find_contacts_missing_fails():
    assert va.check_find_contacts(_clone_with({}))["status"] == "fail"


def test_enrich_requires_hooks_section():
    clone = _clone_with({".contacts-ledger.md": _LEDGER})
    assert va.check_enrich_contacts(clone)["status"] == "pass"
    no_hooks = _clone_with({".contacts-ledger.md": "| Rank | Name |\n| 1 | X |"})
    assert va.check_enrich_contacts(no_hooks)["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "find_contacts or enrich" -v`
Expected: FAIL — missing functions

- [ ] **Step 3: Write minimal implementation**

Append:

```python
def _ledger_contact_rows(text: str) -> int:
    rows = 0
    for line in (text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if all(re.fullmatch(r":?-{2,}:?", (c or "-")) for c in cells):  # divider
            continue
        lowered = {c.lower() for c in cells}
        if "name" in lowered and "rank" in lowered:  # header row
            continue
        rows += 1
    return rows


def check_find_contacts(clone: Path) -> dict:
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    n = _ledger_contact_rows(_read(f))
    return skill_result([
        check("ledger-present", True),
        check("ledger-has-contacts", n >= 1, f"{n} contact row(s)"),
    ])


def check_enrich_contacts(clone: Path) -> dict:
    f = clone / ".contacts-ledger.md"
    if not f.exists():
        return skill_result([check("ledger-present", False, str(f))])
    return skill_result([check("ledger-has-hooks", "hook" in _read(f).lower(),
                               "expected a hooks section from enrich-contacts")])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k "find_contacts or enrich" -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): find-contacts (>=1 row) + enrich-contacts (hooks) checks"
```

---

