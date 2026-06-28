## Task 1: Verifier core — schema, vocab, intake check

**Files:**
- Create: `.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py`
- Test: `.claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py`

**Interfaces:**
- Produces: `check(name, ok, detail="", severity="fail") -> dict`; `rollup(checks) -> str`; `skill_result(checks, notes="") -> dict`; `THEME_VOCAB: set[str]`; `ARCHETYPE_VOCAB: set[str]`; `check_intake(clone: Path) -> dict`.

- [ ] **Step 1: Write the failing test**

Create `test_verify_artifacts.py`:

```python
import sys, json, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import verify_artifacts as va


def _clone_with(files: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for name, content in files.items():
        p = d / name
        p.write_text(content, encoding="utf-8")
    return d


def test_rollup_severities():
    assert va.rollup([va.check("a", True)]) == "pass"
    assert va.rollup([va.check("a", False, severity="warn")]) == "warn"
    assert va.rollup([va.check("a", False, severity="fail")]) == "fail"
    # a hard fail dominates a warn
    assert va.rollup([va.check("a", False, "", "warn"), va.check("b", False, "", "fail")]) == "fail"


def test_intake_pass_and_fail():
    good = _clone_with({"Job Description.md": "# Role\n\n" + "x" * 100})
    res = va.check_intake(good)
    assert res["status"] == "pass", res

    empty = _clone_with({})  # no Job Description.md
    assert va.check_intake(empty)["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'verify_artifacts'`

- [ ] **Step 3: Write minimal implementation**

Create `verify_artifacts.py`:

```python
"""Deterministic per-skill artifact verifier for the two-orchestrator E2E test.

Pure functions + a thin CLI, same shape as dedupe.py. Stdlib only. Cannot reach
MCP servers — Gmail-draft state and PDF/worklist results are passed in as args.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

# Classification vocab — must match jd-to-ready/SKILL.md (themes ~line 115, archetypes ~118).
THEME_VOCAB = {
    "agents", "RAG", "NL→SQL", "MCP", "LLM-orchestration", "ML-pipeline", "platform",
    "business-translation", "end-to-end", "RPA", "experimentation", "dashboards",
    "consulting", "simplification", "leverage", "cross-functional", "engineering-rigor", "evaluation",
}
ARCHETYPE_VOCAB = {
    "agent-builder", "FDE / client-facing", "consulting / product-builder",
    "platform / ML engineering", "data-engineering / analytics",
}


def check(name: str, ok: bool, detail: str = "", severity: str = "fail") -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail, "severity": severity}


def rollup(checks: list[dict]) -> str:
    failed = [c for c in checks if not c["ok"]]
    if any(c["severity"] == "fail" for c in failed):
        return "fail"
    if failed:
        return "warn"
    return "pass"


def skill_result(checks: list[dict], notes: str = "") -> dict:
    return {"status": rollup(checks), "checks": checks, "notes": notes}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore") if path.exists() else ""


def check_intake(clone: Path) -> dict:
    jd = clone / "Job Description.md"
    text = _read(jd)
    return skill_result([
        check("clone-folder-exists", clone.is_dir(), str(clone)),
        check("job-description-present", jd.exists(), str(jd)),
        check("job-description-nonempty", len(text.strip()) > 50, f"{len(text)} chars"),
    ])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py .claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py
git commit -m "feat(e2e-test): verifier core — schema, vocab, intake check"
```

---

