## Task 2: classify check (vocab validation)

**Files:**
- Modify: `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`
- Test: `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`

**Interfaces:**
- Consumes: `THEME_VOCAB`, `ARCHETYPE_VOCAB`, `skill_result`, `check`, `_read`.
- Produces: `check_classify(clone: Path) -> dict`.

- [ ] **Step 1: Write the failing test**

Append to `test_verify_artifacts.py`:

```python
_GOOD_CLASS = json.dumps({
    "themes": [
        {"tag": "NL→SQL", "evidence": "expose tables to natural language"},
        {"tag": "agents", "evidence": "data agents need to reason"},
        {"tag": "end-to-end", "evidence": "source ingestion to semantic layer"},
        {"tag": "business-translation", "evidence": "translate business requirements"},
    ],
    "archetype": "FDE / client-facing",
    "archetype_rationale": "embeds with customers",
    "notes": "",
    "classified_ts": "2026-06-28",
})


def test_classify_pass():
    clone = _clone_with({".classification.json": _GOOD_CLASS})
    assert va.check_classify(clone)["status"] == "pass"


def test_classify_off_vocab_theme_fails():
    bad = json.loads(_GOOD_CLASS)
    bad["themes"][0]["tag"] = "made-up-tag"
    clone = _clone_with({".classification.json": json.dumps(bad)})
    res = va.check_classify(clone)
    assert res["status"] == "fail"
    assert any(c["name"] == "themes-in-vocab" and not c["ok"] for c in res["checks"])


def test_classify_missing_file_fails():
    assert va.check_classify(_clone_with({}))["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k classify -v`
Expected: FAIL — `AttributeError: module 'verify_artifacts' has no attribute 'check_classify'`

- [ ] **Step 3: Write minimal implementation**

Append to `verify_artifacts.py`:

```python
def check_classify(clone: Path) -> dict:
    f = clone / ".classification.json"
    if not f.exists():
        return skill_result([check("classification-present", False, str(f))])
    try:
        data = json.loads(_read(f))
    except ValueError as exc:
        return skill_result([check("classification-parses", False, str(exc))])
    themes = data.get("themes", []) if isinstance(data.get("themes"), list) else []
    tags = [t.get("tag") for t in themes if isinstance(t, dict)]
    off = [t for t in tags if t not in THEME_VOCAB]
    no_ev = [t for t in themes if isinstance(t, dict) and not str(t.get("evidence", "")).strip()]
    return skill_result([
        check("classification-parses", True),
        check("theme-count-4-6", 4 <= len(tags) <= 6, f"{len(tags)} themes"),
        check("themes-in-vocab", not off, f"off-vocab: {off}"),
        check("archetype-in-vocab", data.get("archetype") in ARCHETYPE_VOCAB, str(data.get("archetype"))),
        check("evidence-present", not no_ev, f"{len(no_ev)} theme(s) missing evidence"),
        check("classified-ts-present", bool(str(data.get("classified_ts", "")).strip())),
    ])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k classify -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py
git commit -m "feat(e2e-test): classify check (in-vocab themes + archetype)"
```

---

