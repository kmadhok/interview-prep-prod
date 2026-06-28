# Two-Orchestrator E2E Test Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `two-orchestrator-e2e-test` skill that runs one real role through all 7 pipeline skills via sequential sub-agents in an isolated `_jd-to-ready-test/` clone, verifies each artifact deterministically, and emits a `TEST REPORT.md`.

**Architecture:** A `SKILL.md` orchestration procedure (the main agent launches one sub-agent per skill, sequentially) plus a stdlib-only `verify_artifacts.py` that runs every per-skill assertion and emits structured pass/fail JSON. Real `Roles/` and `Pipeline.md` are never touched — the apply gate is simulated against a local `_pipeline-fixture.md`. The verifier is built first, fully TDD'd, because it is the deterministic core; the SKILL.md composes it last.

**Tech Stack:** Python 3 (stdlib only — `argparse`, `json`, `re`, `pathlib`), pytest, Markdown SKILL.md.

**Spec:** `docs/superpowers/specs/2026-06-28-two-orchestrator-e2e-test-design.md`
**Origin/reference:** the manual run this codifies — `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`.

**Key existing files to mirror (read before starting):**
- `scripts/drip_runner/dedupe.py` — the canonical "pure function + thin CLI, `utf-8-sig` reads, stdlib-only" shape the verifier follows.
- `scripts/drip_runner/outreach_worklist.py` — the Pass B reader the skill runs against the fixture for the gate check.
- `.claude/skills/jd-to-ready/SKILL.md` — the classification vocab (themes/archetype, lines ~113–141) the verifier hard-codes, and the `~/.claude/skills/...` path style.

## Global Constraints

Every task implicitly includes these (verbatim from the spec):
- **Verifier is stdlib-only** — `argparse`, `json`, `re`, `pathlib`. No third-party imports in `verify_artifacts.py`.
- **All verifier paths are arguments** — no hardcoded `G:\…` or `/Users/…`; portable across Mac/PC.
- **File reads use `encoding="utf-8-sig", errors="ignore"`** (handles BOM, matches `dedupe.py`).
- **Python invocation:** `python3` in commands; Windows alternative is `py -3`.
- **The skill never writes real `Roles/` or `Pipeline.md`** — only the `_jd-to-ready-test/<clone>/` folder and its local `_pipeline-fixture.md`.
- **Human-gated:** Gmail draft via `create_draft` only, never send. **LinkedIn:** sequential calls only; preflight before scraping; STOP if the daemon is down.
- **No `jd-to-ready` trace run** is opened by the skill (avoids the Stop-hook vs async-sub-agent conflict).

## File Structure

```
.claude/skills/two-orchestrator-e2e-test/
├── SKILL.md                          # Task 9 — orchestration procedure
└── scripts/
    ├── verify_artifacts.py           # Tasks 1–8 — per-skill checks + CLI
    └── test_verify_artifacts.py      # Tasks 1–8 — pytest
```

The verifier emits one JSON object:
```json
{
  "skills": { "<skill>": {"status": "pass|warn|fail|blocked",
                          "checks": [{"name","ok","detail","severity"}],
                          "notes": ""} },
  "summary": {"pass": N, "warn": N, "fail": N, "overall": "pass|warn|fail"}
}
```

---

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

## Task 8: CLI assembly + full-fixture integration test

**Files:**
- Modify: `verify_artifacts.py` · Test: `test_verify_artifacts.py`

**Interfaces:**
- Consumes: every `check_*` function above.
- Produces: `build_parser() -> ArgumentParser`; `run_all(args) -> dict`; `main(argv=None) -> int`.

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_run_all_full_fixture_overall_pass():
    files = {
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Kanu Madhok Resume - Snowflake FDE.md": _RESUME_OK,
        "Kanu Madhok Resume - Snowflake FDE.pdf": "%PDF-1.4",
        ".contacts-ledger.md": _LEDGER,
        "Verified Emails.md": _VERIFIED_OK,
        "Cold Outreach.md": "Hi Brad,",
    }
    clone = _clone_with(files)
    worklist = clone / "_worklist.txt"
    worklist.write_text("Snowflake\tForward Deployed Analytics Engineer\n", encoding="utf-8")
    draft = clone / "_draft.json"
    draft.write_text(json.dumps({"id": "r1", "toRecipients": ["brad.mallmann@snowflake.com"]}), encoding="utf-8")

    args = va.build_parser().parse_args([
        "--clone", str(clone), "--company", "Snowflake",
        "--worklist-out", str(worklist), "--pages", "1", "--title-leak", "0",
        "--draft-json", str(draft), "--expected-recipient", "brad.mallmann@snowflake.com",
    ])
    report = va.run_all(args)
    assert report["summary"]["overall"] == "pass", json.dumps(report, indent=2)
    assert set(report["skills"]) >= {
        "interview-prep-intake", "classify", "tailor-resume", "pdf", "apply-gate",
        "find-contacts", "enrich-contacts", "verify-emails", "write-outreach",
    }


def test_run_all_flags_issue1_overall_fail():
    files = dict({
        "Job Description.md": "# Role\n" + "x" * 80,
        ".classification.json": _GOOD_CLASS,
        "Kanu Madhok Resume - Snowflake FDE.md": _RESUME_OK,
        "Kanu Madhok Resume - Snowflake FDE.pdf": "%PDF-1.4",
        ".contacts-ledger.md": _LEDGER,
        "Verified Emails.md": "# Verified Emails\n_no rows_\n",  # <- Issue 1
        "Cold Outreach.md": "Hi Brad,",
    })
    clone = _clone_with(files)
    args = va.build_parser().parse_args(["--clone", str(clone), "--company", "Snowflake"])
    report = va.run_all(args)
    assert report["summary"]["overall"] == "fail"
    assert report["skills"]["verify-emails"]["status"] == "fail"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -k run_all -v`
Expected: FAIL — missing `build_parser` / `run_all`

- [ ] **Step 3: Write minimal implementation**

Append:

```python
def run_all(args) -> dict:
    clone = Path(args.clone)
    worklist_text = _read(Path(args.worklist_out)) if args.worklist_out else ""
    draft = json.loads(_read(Path(args.draft_json))) if args.draft_json else None
    skills = {
        "interview-prep-intake": check_intake(clone),
        "classify": check_classify(clone),
        "tailor-resume": check_tailor_resume(clone),
        "pdf": check_pdf(clone, args.pages, args.title_leak),
        "apply-gate": check_gate(worklist_text, args.company),
        "find-contacts": check_find_contacts(clone),
        "enrich-contacts": check_enrich_contacts(clone),
        "verify-emails": check_verify_emails(clone),
        "write-outreach": check_write_outreach(clone, draft, args.expected_recipient or ""),
    }
    statuses = [s["status"] for s in skills.values()]
    overall = "fail" if "fail" in statuses else ("warn" if "warn" in statuses else "pass")
    summary = {
        "pass": statuses.count("pass"), "warn": statuses.count("warn"),
        "fail": statuses.count("fail"), "overall": overall,
    }
    return {"skills": skills, "summary": summary}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Two-orchestrator E2E artifact verifier")
    p.add_argument("--clone", required=True)
    p.add_argument("--company", default="")
    p.add_argument("--worklist-out", default="")
    p.add_argument("--pages", type=int, default=None)
    p.add_argument("--title-leak", type=int, default=None)
    p.add_argument("--draft-json", default="")
    p.add_argument("--expected-recipient", default="")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    report = run_all(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["summary"]["overall"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the full suite**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v`
Expected: PASS (all tests across Tasks 1–8 green)

- [ ] **Step 5: Smoke-test the CLI against the committed real test record**

Run:
```bash
python3 ".claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" \
  --clone "_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/produced-artifacts" \
  --company "Snowflake" --pages 2 --title-leak 0
```
Expected: prints the JSON report. `verify-emails` should be **pass** (that snapshot's `Verified Emails.md` has 3 rows), `pdf` should be **warn** (PAGES=2). Eyeball that the 9 skills appear.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/scripts/
git commit -m "feat(e2e-test): CLI assembly + summary rollup + full-fixture integration test"
```

---

## Task 9: Author SKILL.md (the orchestration procedure)

**Files:**
- Create: `.claude/skills/two-orchestrator-e2e-test/SKILL.md`

**Interfaces:**
- Consumes: `verify_artifacts.py` (Tasks 1–8), `scripts/build_resume_pdf.py`, `scripts/drip_runner/outreach_worklist.py`, the `linkedin-mcp-operations` skill, the 7 pipeline skills.

- [ ] **Step 1: Write the SKILL.md**

Create `.claude/skills/two-orchestrator-e2e-test/SKILL.md` with this content (strip the zero-width guards `​` before the inner fences when writing):

````markdown
---
name: two-orchestrator-e2e-test
description: Use this skill to run the full two-orchestrator end-to-end pipeline test — take ONE real role through all 7 skills (interview-prep-intake → classify → tailor-resume → PDF → [apply gate] → find-contacts → enrich-contacts → verify-emails → write-outreach) via sequential sub-agents in an isolated _jd-to-ready-test/ clone, verify each artifact deterministically with verify_artifacts.py, and write a TEST REPORT.md. Trigger on "run the e2e pipeline test", "end-to-end test the two-orchestrator pipeline", "test the whole jd-to-ready + stage-outreach flow on <role>". FULL LIVE RUN (real LinkedIn scraping + real Gmail draft, never sent). Does NOT touch real Roles/ or Pipeline.md. Do NOT trigger to file a JD (interview-prep-intake), prep a resume (jd-to-ready), or stage real outreach (stage-outreach).
---

# Two-Orchestrator E2E Test (full live, per-skill, isolated clone)

Runs one real role through all 7 pipeline skills, one sub-agent per skill, **sequentially**, in a throwaway clone. Real `Roles/` and `Pipeline.md` are never touched; the apply gate is simulated on a local fixture. The only real external side effect is one unsent Gmail draft. Read root `AGENTS.md`/`CLAUDE.md` first; it overrides anything here.

`<repo root>` = the Interview Prep workspace root (cwd). Use `python3` (Windows: `py -3`).

## What this skill does NOT do
No real Pipeline/Roles writes. No `jd-to-ready` trace run (an open trace step trips the Stop hook on every async sub-agent yield; the trace contract is covered by `test_trace_step.py`). Never sends — Gmail `create_draft` only.

## Step 0 — Setup
1. Pick the target: a real `Company - Role` whose JD is available (an existing `Roles/<role>/Job Description.md`, a saved job, or pasted JD). Must be a real company (full-live apply side needs a LinkedIn presence).
2. Create `<repo root>/_jd-to-ready-test/<Company - Role> (e2e <YYYY-MM-DD>)/` (the clone).
3. Write the JD to `<clone>/Job Description.md` is the intake sub-agent's job — for now save the source JD to a scratch file the intake sub-agent will read.
4. Write `<clone>/_pipeline-fixture.md` — a minimal pipeline with the role under `## Considering / not yet applied`:
   ```
   ## Active

   | Role | Stage | Next action | Date | Contacts | Folder |
   |------|-------|-------------|------|----------|--------|

   ## Considering / not yet applied

   | Role | Stage | Next action | Date | Contacts | Folder |
   | **<Company> — <Role>** | Considering — not yet applied | — | — | — | — |
   ```
5. Every sub-agent prompt below MUST include: "Operate ONLY in `<clone>`. Do NOT touch real Roles/ or Pipeline.md. Do NOT run trace_step.py. Do NOT send anything."

## Steps 1–3 — Prep sub-agents (sequential)
Launch a fresh `general-purpose` sub-agent per skill; wait for each, then run its verifier check before the next.
1. **interview-prep-intake** → writes `<clone>/Job Description.md`. (Tell it to skip the Pipeline row — the fixture already has it.)
2. **classify** (jd-to-ready Step 2) → writes `<clone>/.classification.json`. Give it the theme/archetype vocab from `.claude/skills/jd-to-ready/SKILL.md` Step 2.
3. **tailor-resume** → writes `<clone>/Kanu Madhok Resume - <Company> <Short Role>.md` (canonical-only).

## Step 3.5 — PDF (main loop)
​```
python3 "<repo root>/scripts/build_resume_pdf.py" "<clone>/Kanu Madhok Resume - <Company> <Short Role>.md"
​```
Capture the `PAGES=<n> TITLE_LEAK=<0|1>` line.

## Step 3.6 — Simulated apply gate (main loop)
In `<clone>/_pipeline-fixture.md`, move the role row to `## Active` and set its stage to `Applied <YYYY-MM-DD>`. Then:
​```
python3 "<repo root>/scripts/drip_runner/outreach_worklist.py" --pipeline "<clone>/_pipeline-fixture.md" > "<clone>/_worklist.txt"
​```
Confirm the role appears (this exercises the Pass B reader without touching real state).

## Step 3.7 — LinkedIn preflight (main loop)
Invoke `linkedin-mcp-operations`. Handshake:
​```
curl -s -o /dev/null -w '%{http_code}\n' -m 6 -X POST http://127.0.0.1:8765/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"diag","version":"0.1"}}}'
​```
If not `200` → STOP the apply side; mark steps 4–7 `blocked` in the report; jump to Step 8.

## Steps 4–7 — Apply sub-agents (sequential — one LinkedIn stream at a time, never parallel)
4. **find-contacts** → `<clone>/.contacts-ledger.md` (real LinkedIn, read-only).
5. **enrich-contacts** → updates the ledger with hooks (real LinkedIn, read-only).
6. **verify-emails** → `<clone>/Verified Emails.md` (real EmailFinder; degrade to inferred if unavailable).
7. **write-outreach** → `<clone>/Cold Outreach.md` + a Gmail draft via `create_draft` to the resolved recruiter. **NEVER send.** Capture the draft id + recipient.

## Step 8 — Verify + report (main loop)
1. Confirm the draft: `mcp__claude_ai_Gmail__list_drafts` with `query: "to:<recipient>"`; save the matched draft object to `<clone>/_draft.json`.
2. Run the verifier:
​```
python3 "<repo root>/.claude/skills/two-orchestrator-e2e-test/scripts/verify_artifacts.py" --clone "<clone>" --company "<Company>" --worklist-out "<clone>/_worklist.txt" --pages <n> --title-leak <0|1> --draft-json "<clone>/_draft.json" --expected-recipient "<recipient>"
​```
3. Write `<clone>/TEST REPORT.md` from the verifier JSON + each sub-agent's report + the PDF/gate/draft results. Use the same sections as `_jd-to-ready-test/Two-Orchestrator Split E2E - Snowflake FDE 2026-06-28/TEST REPORT.md`: summary table, per-skill detail, findings (your narrative on top of the verifier's deterministic pass/fail), environment notes, cleanup record (the Gmail draft id + a one-line "delete in Gmail Drafts if unwanted").

## Cleanup
Real data is untouched, so the clone folder IS the test record (commit it if wanted). Surface the Gmail draft id for deletion. Nothing to restore.
````

- [ ] **Step 2: Verify the SKILL.md is self-consistent**

Run:
```bash
test -f ".claude/skills/two-orchestrator-e2e-test/SKILL.md" && \
grep -q "verify_artifacts.py" ".claude/skills/two-orchestrator-e2e-test/SKILL.md" && \
grep -q "Do NOT touch real Roles/ or Pipeline.md" ".claude/skills/two-orchestrator-e2e-test/SKILL.md" && \
grep -q "never sent\|NEVER send" ".claude/skills/two-orchestrator-e2e-test/SKILL.md" && \
echo OK
```
Expected: prints `OK`. Confirm no zero-width guard characters (`​`) remain: `grep -c $'​' ".claude/skills/two-orchestrator-e2e-test/SKILL.md"` → expect `0`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/two-orchestrator-e2e-test/SKILL.md
git commit -m "feat(e2e-test): SKILL.md orchestration procedure (7 sequential sub-agents, isolated clone)"
```

---

## Task 10: Final regression sweep

- [ ] **Step 1: Full verifier suite**

Run: `python3 -m pytest ".claude/skills/two-orchestrator-e2e-test/scripts/test_verify_artifacts.py" -v`
Expected: all PASS.

- [ ] **Step 2: Confirm no repo regressions in neighboring suites**

Run: `python3 -m pytest ".claude/skills/jd-to-ready/scripts/test_trace_step.py" -q` and `cd scripts/drip_runner && python3 -m pytest -q`
Expected: both green (this skill adds files only; it must not touch those).

- [ ] **Step 3: Commit (if any fixups were needed)**

```bash
git add -A
git commit -m "test(e2e-test): full regression sweep green"
```

---

## Self-Review notes (already applied)

- **Spec coverage:** §4 file structure → Tasks 1–9. §5 run flow → SKILL.md (Task 9) Steps 0–8. §6 verifier checks → Tasks 1–8 (one task per skill-check, plus CLI). The Issue-1 catcher (§6 verify-emails) → Task 6 with an explicit regression test. §7 no-trace + light-cleanup → SKILL.md "What this skill does NOT do" + Cleanup. §8 portability → Global Constraints + Task 9 `<repo root>`/`~/.claude` style + verifier paths-as-args. §9 canary reuse → verifier is import-friendly pure functions.
- **Type/name consistency:** `check`, `rollup`, `skill_result`, `_read`, `_ledger_contact_rows` (defined Task 5, reused Task 6), `find_resume`, `check_intake/classify/tailor_resume/pdf/gate/find_contacts/enrich_contacts/verify_emails/write_outreach`, `run_all`, `build_parser`, `main` — used identically across tasks and tests. CLI flags (`--clone --company --worklist-out --pages --title-leak --draft-json --expected-recipient`) match between Task 8 impl and its test and the SKILL.md Step 8 invocation.
- **Known soft spot:** `_ledger_contact_rows` and `_verified_email_rows` are heuristic markdown-table parsers; they are validated against both the controlled fixtures and (Task 8 Step 5) the committed real Snowflake ledger snapshot, so a real-format drift is caught by the smoke test.
```
