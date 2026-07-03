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


def blocked_result(note: str = "") -> dict:
    return {"status": "blocked", "checks": [], "notes": note}


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


def check_pdf(clone: Path, pages, title_leak) -> dict:
    checks = [check("resume-pdf-present", bool(list(clone.glob("Kanu Madhok Resume - *.pdf"))), "glob: *.pdf")]
    if pages is not None:
        checks.append(check("pdf-one-page", pages == 1, f"PAGES={pages}", severity="warn"))
    if title_leak is not None:
        checks.append(check("pdf-no-title-leak", title_leak == 0, f"TITLE_LEAK={title_leak}"))
    if pages is None or title_leak is None:
        # A missing export contract must surface as a warn, not silently skip checks.
        checks.append(check("pdf-contract-provided", False,
                            "PAGES/TITLE_LEAK not captured from build_resume_pdf.py",
                            severity="warn"))
    return skill_result(checks)


def check_packet(clone: Path) -> dict:
    """Apply-packet artifacts: record exists, parses, and — non-negotiable —
    points at a _test remote, never the real Apply Queue."""
    f = clone / ".apply-packet.json"
    if not f.exists():
        return skill_result([check("packet-present", False, str(f))])
    try:
        rec = json.loads(f.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return skill_result([check("packet-parses", False, str(exc))])
    return skill_result([
        check("packet-parses", True),
        check("packet-state-queued", rec.get("state") == "queued", str(rec.get("state"))),
        check("packet-remote-is-test", "_test" in str(rec.get("remote_dir", "")),
              rec.get("remote_dir", "")),
        check("answers-md-present", (clone / "Application Answers.md").exists()),
    ])


def check_gate(worklist_text: str, company: str) -> dict:
    ok = bool(company) and company.lower() in (worklist_text or "").lower()
    return skill_result([check("worklist-surfaces-role", ok, f"company={company!r}")])


# NOTE: the header-skip below is keyed to find-contacts' current "| Rank | Name | ... |"
# column wording. If those names change, the data-bearing requirement (an email or a
# bare-integer Rank/Total cell) still keeps a header-only ledger from counting as 1 contact.
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
        # A contact row must carry data: an email or a bare-integer (Rank/Total) cell.
        if not any("@" in c or re.fullmatch(r"\d+", c) for c in cells):
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
    text = _read(f)
    # The heading enrich-contacts actually writes ("## hooks[]"), not a bare substring —
    # "hook" appears in find-contacts column wording and would silently pass pre-enrich.
    has_heading = bool(re.search(r"^##\s*hooks", text, re.MULTILINE | re.IGNORECASE))
    checks = [check("ledger-has-hooks-section", has_heading,
                    "expected a '## hooks' section from enrich-contacts")]
    # Whole-cell match: the header cell "Source (search/enrich)" must not count.
    enrich_rows = any(
        "enrich" in (c.strip().lower() for c in line.strip().strip("|").split("|"))
        for line in text.splitlines() if line.strip().startswith("|"))
    checks.append(check("enrich-rows-present", enrich_rows,
                        "no 'Source: enrich' rows — enrich ran but appended no new people",
                        severity="warn"))
    return skill_result(checks)


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
    text = _read(f)
    rows = _verified_email_rows(text)
    ledger = clone / ".contacts-ledger.md"
    ledger_contacts = _ledger_contact_rows(_read(ledger)) if ledger.exists() else 0
    checks = [
        check("verified-emails-present", True),
        check("verified-rows-present", rows >= 1, f"{rows} verified row(s)"),
    ]
    if rows >= 1:
        # An EmailFinder-down run degrades every row to "inferred" — that must warn,
        # not read identically to a fully SMTP-verified run (fail-loud invariant).
        email_lines = [ln for ln in text.splitlines()
                       if ln.strip().startswith("|")
                       and any("@" in c and "." in c for c in ln.split("|"))]
        all_inferred = all("inferred" in ln.lower() for ln in email_lines)
        checks.append(check("not-all-inferred", not all_inferred,
                            "every row is inferred — EmailFinder likely unavailable (degraded run)",
                            severity="warn"))
    if ledger_contacts >= 1 and rows == 0:
        checks.append(check(
            "issue1-ledger-parsed", False,
            f"ledger has {ledger_contacts} contacts but Verified Emails.md is empty — "
            "find-contacts→verify-emails format mismatch (Issue 1)",
        ))
    return skill_result(checks)


def _draft_recipients(draft: dict) -> list[str]:
    return [str(r).lower() for r in (draft or {}).get("toRecipients", [])]


def _load_drafts(path_str: str) -> list[dict]:
    """Parse --draft-json, which may hold a single draft object or a list of them."""
    if not path_str:
        return []
    try:
        data = json.loads(_read(Path(path_str)))
    except ValueError:
        return []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [d for d in data if isinstance(d, dict)]
    return []


def check_write_outreach(clone: Path, drafts, expected_recipient: str,
                         expected_lead_recipient: str = "") -> dict:
    """write-outreach drip mode produces TWO Gmail drafts (recruiter #1 + the
    HM/peer-IC lead). `drafts` accepts a single draft dict (back-compat) or a
    list of draft dicts; every draft must be unsent."""
    f = clone / "Cold Outreach.md"
    checks = [check("cold-outreach-present", f.exists(), str(f))]
    if isinstance(drafts, dict):
        drafts = [drafts]
    drafts = [d for d in (drafts or []) if isinstance(d, dict)]
    if not drafts:
        checks.append(check("gmail-draft-present", False, "no draft provided"))
        return skill_result(checks)
    with_id = [d for d in drafts if d.get("id")]
    checks.append(check("gmail-draft-present", bool(with_id), f"{len(with_id)} draft(s) with id"))
    all_recips = [r for d in drafts for r in _draft_recipients(d)]
    if expected_recipient:
        checks.append(check("recruiter-draft-recipient-matches",
                            expected_recipient.lower() in all_recips, f"to={all_recips}"))
    if expected_lead_recipient:
        checks.append(check("lead-draft-recipient-matches",
                            expected_lead_recipient.lower() in all_recips, f"to={all_recips}"))
        # drip should draft both; <2 is a gap-with-note (the same-company guard or
        # a missing HM can legitimately yield one), not a hard failure.
        checks.append(check("both-drafts-present", len(with_id) >= 2,
                            f"{len(with_id)} draft(s) with id; recruiter + HM/peer expected",
                            severity="warn"))
    checks.append(check("all-drafts-unsent",
                        all(not d.get("sent", False) for d in drafts),
                        f"{len(drafts)} draft(s)"))
    return skill_result(checks)


def run_all(args) -> dict:
    clone = Path(args.clone)
    worklist_text = _read(Path(args.worklist_out)) if args.worklist_out else ""
    drafts = _load_drafts(args.draft_json)
    skills = {
        "interview-prep-intake": check_intake(clone),
        "classify": check_classify(clone),
        "tailor-resume": check_tailor_resume(clone),
        "pdf": check_pdf(clone, args.pages, args.title_leak),
        "apply-packet": check_packet(clone),
        "apply-gate": check_gate(worklist_text, args.company),
        "find-contacts": check_find_contacts(clone),
        "enrich-contacts": check_enrich_contacts(clone),
        "verify-emails": check_verify_emails(clone),
        "write-outreach": check_write_outreach(
            clone, drafts, args.expected_recipient or "",
            getattr(args, "expected_lead_recipient", "") or ""),
    }
    # Ordering signal (invariant 2): the gate writes _worklist.txt; the apply side's
    # first artifact is the ledger. A ledger older than the worklist suggests LinkedIn
    # was spent before the apply gate — warn, don't fail (mtimes are edit-sensitive).
    wl = Path(args.worklist_out) if args.worklist_out else None
    ledger = clone / ".contacts-ledger.md"
    if wl is not None and wl.exists() and ledger.exists():
        ordered = ledger.stat().st_mtime >= wl.stat().st_mtime - 2
        gate = skills["apply-gate"]
        gate["checks"].append(check(
            "apply-after-gate", ordered,
            "ledger predates the apply-gate worklist — apply side may have run before the gate",
            severity="warn"))
        gate["status"] = rollup(gate["checks"])
    if getattr(args, "blocked_apply", False):
        note = "apply side not run (LinkedIn daemon down at preflight)"
        for name in ("find-contacts", "enrich-contacts", "verify-emails", "write-outreach"):
            skills[name] = blocked_result(note)
    statuses = [s["status"] for s in skills.values()]
    if "fail" in statuses:
        overall = "fail"
    elif "warn" in statuses:
        overall = "warn"
    elif "blocked" in statuses:
        overall = "blocked"
    else:
        overall = "pass"
    summary = {
        "pass": statuses.count("pass"), "warn": statuses.count("warn"),
        "fail": statuses.count("fail"), "blocked": statuses.count("blocked"),
        "overall": overall,
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
    p.add_argument("--expected-recipient", default="",
                   help="recruiter #1 draft recipient email")
    p.add_argument("--expected-lead-recipient", default="",
                   help="HM/peer-IC lead draft recipient email (drip mode drafts two)")
    p.add_argument("--blocked-apply", action="store_true",
                   help="LinkedIn was down at preflight; mark apply-side skills blocked and exclude from fail/warn rollup")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    report = run_all(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["summary"]["overall"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
