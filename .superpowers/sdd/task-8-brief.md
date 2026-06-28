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

